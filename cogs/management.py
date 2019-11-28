import asyncio
import json
import re
import threading
from datetime import datetime, timedelta
from os import path

import discord
import pymongo
from discord import Embed
from discord.ext import commands

import config
from turn_on import COMMAND_PREFIX, COLOR_RED, InvalidConfigurationException

MUTED_USERS_FILE_PATH = "muted_users.json"


def is_mute_role_defined():
    async def check(ctx):
        if not config.MUTED_ROLE:
            await ctx.send("The muted role is undefined. Please ask your server administrator to define it")
            raise InvalidConfigurationException(
                "Muted role is undefined. It must be set in order to use the mute related commands")
        return True

    return commands.check(check)


class CouroutineTimer:
    def __init__(self, timeout, callback, callback_args: dict):
        self.timeout = max(0, timeout)
        self.callback = callback
        self.callback_args = callback_args
        self.task = asyncio.ensure_future(self.perform_task())

    async def perform_task(self):
        await asyncio.sleep(self.timeout)
        await self.callback(**self.callback_args)


class Management(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.muted_users_file_lock = threading.Lock()
        self.muted_users = {}
        self.dbclient = pymongo.MongoClient(config.MONGO_KEY)

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def warn(self, ctx, user: discord.Member = None, *, warning_reason=None):
        if user is None or warning_reason is None:
            await ctx.send(embed=Embed(title="Incorrect usage",
                                       description=f"**Correct usage**: {COMMAND_PREFIX}warn [user] [reason]\n "
                                                   "**user** = a member of the server to warn\n"
                                                   " **reason** = a brief explanation for why the "
                                                   "warning was issued", color=COLOR_RED))
            return
        issued_datetime = datetime.utcnow()
        self.dbclient.bot.profile.update({"_id": user.id},
                                         {"$push":
                                             {"warnings":
                                                 {
                                                     "issuer": ctx.author.id,
                                                     "reason": warning_reason,
                                                     "issued_datetime": issued_datetime
                                                 }}}, upsert=True)
        await ctx.send(f"User \"{user.name}\" has successfully been warned")
        await user.send(
            f"You have received a warning on the server \"{ctx.guild}\" for the following reasoning: {warning_reason}")

    async def unmute_user_helper(self, guild, user, end_time):
        self.muted_users_file_lock.acquire()
        if self.muted_users[guild.id][user.id] == end_time:
            del self.muted_users[guild.id][user.id]
            with open(MUTED_USERS_FILE_PATH, "w") as muted_users_file:
                json.dump(self.muted_users, muted_users_file, default=str)
            muted_role = next(filter(lambda role: role.name == config.MUTED_ROLE, user.roles), None)
            if muted_role is not None:
                await user.remove_roles(muted_role)
                await user.send(f"You have been unmuted from the server \"{guild.name}\"")
        self.muted_users_file_lock.release()

    @is_mute_role_defined()
    async def load_muted_users(self):
        self.muted_users_file_lock.acquire()
        if path.exists(MUTED_USERS_FILE_PATH):
            with open(MUTED_USERS_FILE_PATH, "r") as muted_users_file:
                temp_dict = json.load(muted_users_file)
                self.muted_users = {}
                for guild_id, guild_muted_users in temp_dict.items():
                    guild_id = int(guild_id)
                    guild = self.client.get_guild(guild_id)
                    self.muted_users[guild_id] = {}
                    for user_id, end_time in guild_muted_users.items():
                        user_id = int(user_id)
                        user = guild.get_member(user_id)
                        end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")
                        self.muted_users[guild_id][user_id] = end_datetime
                        CouroutineTimer((end_datetime - datetime.utcnow()).total_seconds(), self.unmute_user_helper,
                                        {"guild": guild, "user": user, "end_time": end_datetime})
        self.muted_users_file_lock.release()

    @commands.command()
    @is_mute_role_defined()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def mute(self, ctx, user: discord.Member = None, duration=None, *, mute_reason=None):
        if user is None or duration is None or mute_reason is None:
            await ctx.send(embed=Embed(title="Incorrect usage",
                                       description=f"**Correct usage**: {COMMAND_PREFIX}mute [user] [duration] ["
                                                   f"reason]\n **user** = a member of the server to mute\n "
                                                   f"**duration** = a numerical value > 0, immediately followed by h, "
                                                   f"m or s for hours, minutes and seconds respectively\n **reason** "
                                                   f"= a brief explanation for why the mute was issued",
                                       color=COLOR_RED))
            return
        issued_datetime = datetime.utcnow()
        if re.match("^[1-9]\\d*[hms]$", duration) is None:
            await ctx.send(
                "The provided duration was invalid. It has to be a number > 0, followed by a character from the "
                "following: [h]ours, [m]inutes, [s]econds")
            return
        numerical_duration = int(duration[:-1])
        if duration[-1] == 'h':
            timedelta_duration = timedelta(hours=numerical_duration)
        elif duration[-1] == 'm':
            timedelta_duration = timedelta(minutes=numerical_duration)
        else:
            timedelta_duration = timedelta(seconds=numerical_duration)

        seconds_duration = timedelta_duration.total_seconds()
        mute_end_time = issued_datetime + timedelta_duration

        self.muted_users_file_lock.acquire()
        if ctx.guild.id not in self.muted_users or user.id not in self.muted_users[ctx.guild.id] or \
                self.muted_users[ctx.guild.id][user.id] < mute_end_time:
            if ctx.guild.id not in self.muted_users:
                self.muted_users[ctx.guild.id] = {}
            self.muted_users[ctx.guild.id][user.id] = mute_end_time
            with open(MUTED_USERS_FILE_PATH, "w+") as muted_users_file:
                json.dump(self.muted_users, muted_users_file, default=str)
            muted_role = next(filter(lambda role: role.name == config.MUTED_ROLE, ctx.guild.roles), None)
            await user.add_roles(muted_role, reason=mute_reason)
            CouroutineTimer(seconds_duration - ((datetime.utcnow() - issued_datetime).total_seconds()),
                            self.unmute_user_helper,
                            {"guild": ctx.guild, "user": user, "end_time": mute_end_time})
        self.muted_users_file_lock.release()

        self.dbclient.bot.profile.update({"_id": user.id},
                                         {"$push": {
                                             "mutes":
                                                 {
                                                     "issuer": ctx.author.id,
                                                     "reason": mute_reason,
                                                     "issued_datetime": issued_datetime,
                                                     "duration": seconds_duration
                                                 }}}, upsert=True)
        await ctx.send(f"User \"{user.name}\" has successfully been muted for {duration}")
        await user.send(
            f"You have been muted for {duration} on the server \"{ctx.guild}\" for the following reason: {mute_reason}")


def setup(client):
    client.add_cog(Management(client))
    return


def help(COMMAND_PREFIX):
    return ["Management Commands",
            f"{COMMAND_PREFIX}Warn [user] [reason]\n{COMMAND_PREFIX}Mute [user] [duration] [reason]"]
