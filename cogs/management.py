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
from turn_on import COLOR_RED, InvalidConfigurationException, correct_usage_embed

MUTED_USERS_FILE_PATH = "temporarily_muted_users.json"


def is_mute_role_defined():
    """
    Function that checks if the mute role is defined within config.py. If it isn't an InvalidConfigurationException is raised
    :return: None
    """

    async def check(ctx):
        if not config.MUTED_ROLE:
            await ctx.send("The muted role is undefined. Please ask your server administrator to define it")
            raise InvalidConfigurationException(
                "Muted role is undefined. It must be set in order to use the mute related commands")
        return True

    return commands.check(check)


class CouroutineTimer:
    """
    A class that represents a timer that is able to run a coroutine without blocking the main execution flow
    """

    def __init__(self, timeout, callback, callback_args: dict):
        """
        Constructor for the CoroutineTimer class
        :param timeout: the time delay after which the callback will be executed (in seconds)
        :param callback: the callback function that is executed after timeout
        :param callback_args: the arguments that will be passed to the callback function
        """
        self.timeout = max(0, timeout)
        self.callback = callback
        self.callback_args = callback_args
        # creates a task to perform a task in the future
        self.task = asyncio.ensure_future(self.perform_task())

    # the function that is used to run the CoroutineTimer
    async def perform_task(self):
        # sleep is called for the timeout period of time
        await asyncio.sleep(self.timeout)
        # callback is called after the timeout has passed
        await self.callback(**self.callback_args)


async def assign_muted_role(guild, member, mute_reason):
    """
    Function that is responsible for assigning the muted role to a user within a guild for the given reason
    :param guild: the server where mute will happen
    :param member: the user to which the muted role is to be added
    :param mute_reason: the reason for which the mute was assigned
    :return: None
    """
    # tries to find the muted role object within the server and then the role is assigned to the user
    muted_role = next(filter(lambda role: role.name == config.MUTED_ROLE, guild.roles), None)
    await member.add_roles(muted_role, reason=mute_reason)


async def remove_muted_role(guild, member):
    """
    Function that is responsible for removing the muted role from a user within the specified guild
    :param guild: the server where unmute will happen
    :param member: the user from which the muted role is to be removed
    :return: bool that represents whether the role was removed
    """
    was_role_removed = False
    # tries to find the muted role object that is on the member
    muted_role = next(filter(lambda role: role.name == config.MUTED_ROLE, member.roles), None)
    # checks if the muted role was found to be on the user
    if muted_role is not None:
        # the role is removed from the member and a message is sent to them, letting them know that they were unmuted
        await member.remove_roles(muted_role)
        was_role_removed = True
        await member.send(f"You have been unmuted from the server \"{guild.name}\"")
    return was_role_removed


def create_str_from_info(info_dict: dict):
    ret = ""
    # goes through all the dictionary key, value pairs and create a string from it
    for key, value in info_dict.items():
        ret = ret + f"\u21B3 {str(key)}: {str(value)}" + \
              (" seconds" if key == "duration" else "") + "\n"
    return ret


class Management(commands.Cog):
    def __init__(self, client):
        self.client = client
        # lock for performing synchronization on the temporarily muted users
        self.temp_muted_users_file_lock = threading.Lock()
        # in-memory dictionary of the temporarily muted users
        self.temp_muted_users = {}
        # mongodb database connection
        self.dbclient = pymongo.MongoClient(config.MONGO_KEY)
        # all the different info types
        self._INFO_TYPES = {"w": "warnings", "b": "bans", "m": "mutes", "u": "unmutes"}

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def warn(self, ctx, member: discord.Member = None, *, warning_reason=None):
        """
        Method that issues a warning to a user
        :param ctx: the context under which this command was executed
        :param member: the user which is to be warned
        :param warning_reason: the reason for issuing the warning
        :return: None
        """

        # makes sure none of the required arguments are missing
        if member is None or warning_reason is None:
            await ctx.send(embed=correct_usage_embed("warn", {
                "user": "a member of the server to warn",
                "reason": "a brief explanation for why the "
                          "warning was issued"
            }))
            return
        # the time this warning was issued
        issued_datetime = datetime.utcnow()
        # writes to the database warnings array for the user, as well as other important data
        self.dbclient.bot[str(ctx.guild.id)].update({"_id": member.id},
                                                    {"$push":
                                                        {"warnings":
                                                            {
                                                                "issuer": ctx.author.id,
                                                                "reason": warning_reason,
                                                                "issued_datetime": issued_datetime
                                                            }}}, upsert=True)
        await ctx.send(f"User \"{member.name}\" has successfully been warned")
        await member.send(
            f"You have received a warning on the server \"{ctx.guild}\" for the following reasoning: {warning_reason}")

    async def unmute_user_helper(self, guild, user, end_time, perma_mute=False):
        """
        Method that is a helper function for unmuting a temporarily muted user
        :param guild: the server where the unmute will be performed
        :param user: the user to unmute
        :param end_time: the time when the user is to be unmuted
        :param perma_mute: whether or not the function was invoked by permanent mute
        :return: bool representing whether or not the user was removed from the list of temporarily muted users
        """
        was_role_removed = False
        self.temp_muted_users_file_lock.acquire()
        # verifies that the user exists in the in-memory dictionary
        if user.id in self.temp_muted_users[guild.id] and (
                perma_mute or self.temp_muted_users[guild.id][user.id] == end_time):
            # deletes the user from the dictionary and opens the file and writes the updated
            del self.temp_muted_users[guild.id][user.id]
            with open(MUTED_USERS_FILE_PATH, "w") as muted_users_file:
                json.dump(self.temp_muted_users, muted_users_file, default=str)
            was_role_removed = await remove_muted_role(guild, user)
        self.temp_muted_users_file_lock.release()
        return was_role_removed

    @is_mute_role_defined()
    async def load_temp_muted_users(self):
        """
        Method that is called when the Cog is loaded to reload the temporarily muted users from the file
        :return: None
        """
        self.temp_muted_users_file_lock.acquire()
        # if the file exists, its read and a copy of the data is loaded into a dictionary
        if path.exists(MUTED_USERS_FILE_PATH):
            with open(MUTED_USERS_FILE_PATH, "r") as muted_users_file:
                temp_dict = json.load(muted_users_file)
                self.temp_muted_users = {}
                for guild_id, guild_muted_users in temp_dict.items():
                    guild_id = int(guild_id)
                    guild = self.client.get_guild(guild_id)
                    self.temp_muted_users[guild_id] = {}
                    for user_id, end_time in guild_muted_users.items():
                        user_id = int(user_id)
                        user = guild.get_member(user_id)
                        end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")
                        self.temp_muted_users[guild_id][user_id] = end_datetime
                        # creates a CouroutineTimer for users that need to be unmuted in the future
                        CouroutineTimer((end_datetime - datetime.utcnow()).total_seconds(), self.unmute_user_helper,
                                        {"guild": guild, "user": user, "end_time": end_datetime})
        self.temp_muted_users_file_lock.release()

    @commands.command()
    @is_mute_role_defined()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def mute(self, ctx, member: discord.Member = None, duration=None, *, mute_reason=None):
        """
        Method used to mute a user
        :param ctx: the context under which the command was executed
        :param member: the user to be muted
        :param duration: the duration for which the mute will last
        :param mute_reason: the reason why the mute was issued
        :return: None
        """
        # makes sure none of the required arguments are missing
        if member is None or duration is None or mute_reason is None:
            await ctx.send(embed=correct_usage_embed("mute", {
                "user": "a member of the server to mute",
                "duration": "a numerical value >= 0, immediately "
                            "followed by h, m or s for hours, minutes "
                            "and seconds respectively. 0 means permanent "
                            "mute",
                "reason": "a brief explanation for why the mute was "
                          "issued"}))
            return
        # the time when the mute was issued
        issued_datetime = datetime.utcnow()
        # verifies that the format of the duration string is valid
        if re.match("^\\d+[hms]$", duration) is None:
            await ctx.send(
                "The provided duration was invalid. It has to be a number >= 0, followed by a character from the "
                "following: [h]ours, [m]inutes, [s]econds. Note a duration of 0 means permanent mute")
            return
        # converts the duration to a number and serializes to timedelta
        numerical_duration = int(duration[:-1])
        if duration[-1] == 'h':
            timedelta_duration = timedelta(hours=numerical_duration)
        elif duration[-1] == 'm':
            timedelta_duration = timedelta(minutes=numerical_duration)
        else:
            timedelta_duration = timedelta(seconds=numerical_duration)
        seconds_duration = timedelta_duration.total_seconds()

        # checks if the user is already permanently muted
        is_permanently_muted = self.dbclient.bot[str(ctx.guild.id)].find_one(
            {"_id": member.id, "permanently_muted": True},
            {"_id": 1}) is not None
        # if so, the issuer is made aware of this fact
        if is_permanently_muted:
            await ctx.send(f"User \"{member.name}\" is already permanently muted")
        else:
            # if the numerical duration wasn't 0, it is a temporary/timed mute
            if numerical_duration != 0:
                # calculates the time when the mute will end
                mute_end_time = issued_datetime + timedelta_duration
                # updates the temporary muted users file, assigns the mute role to the user and creates a
                # CoroutineTimer to unmute in the future
                self.temp_muted_users_file_lock.acquire()
                if ctx.guild.id not in self.temp_muted_users or member.id not in self.temp_muted_users[ctx.guild.id] or \
                        self.temp_muted_users[ctx.guild.id][member.id] < mute_end_time:
                    if ctx.guild.id not in self.temp_muted_users:
                        self.temp_muted_users[ctx.guild.id] = {}
                    self.temp_muted_users[ctx.guild.id][member.id] = mute_end_time
                    with open(MUTED_USERS_FILE_PATH, "w+") as muted_users_file:
                        json.dump(self.temp_muted_users, muted_users_file, default=str)
                    await assign_muted_role(ctx.guild, member, mute_reason)
                    CouroutineTimer(seconds_duration - ((datetime.utcnow() - issued_datetime).total_seconds()),
                                    self.unmute_user_helper,
                                    {"guild": ctx.guild, "user": member, "end_time": mute_end_time})
                self.temp_muted_users_file_lock.release()
                # sends messages to the server and the user indicating successful mute
                await ctx.send(f"User \"{member.name}\" has successfully been muted for {duration}")
                await member.send(
                    f"You have been muted for {duration} on the server \"{ctx.guild}\" for the following reason: {mute_reason}")
            # otherwise, its a permanent mute
            else:
                # assigns the muted role to the user and if the user was temporarily muted, removes them from
                # the temporary file and the in-memory dictionary
                await assign_muted_role(ctx.guild, member, mute_reason)
                self.temp_muted_users_file_lock.acquire()
                if ctx.guild.id in self.temp_muted_users and member.id in self.temp_muted_users[ctx.guild.id]:
                    del self.temp_muted_users[ctx.guild.id][member.id]
                    with open(MUTED_USERS_FILE_PATH, "w+") as muted_users_file:
                        json.dump(self.temp_muted_users, muted_users_file, default=str)
                self.temp_muted_users_file_lock.release()
                # sends messages to the server and the user indicating a successful permanent mute
                await ctx.send(f"User \"{member.name}\" has successfully been muted permanently")
                await member.send(
                    f"You have been permanently muted on the server \"{ctx.guild}\" for the following reason: {mute_reason}")
        # writes the issued mute data to the database to serve as a log
        self.dbclient.bot[str(ctx.guild.id)].update({"_id": member.id},
                                                    {"$push": {
                                                        "mutes":
                                                            {
                                                                "issuer": ctx.author.id,
                                                                "reason": mute_reason,
                                                                "issued_datetime": issued_datetime,
                                                                "duration": seconds_duration
                                                            }},
                                                        "$set": {
                                                            "permanently_muted": is_permanently_muted or seconds_duration == 0}},
                                                    upsert=True)

    @commands.command()
    @is_mute_role_defined()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def unmute(self, ctx, member: discord.Member = None):
        """
        Method that is used to unmute a user
        :param ctx: the context under which the unmute is issued
        :param member: the user which is to be unmuted
        :return: None
        """
        # makes sure that the required arguments are given
        if member is None:
            await ctx.send(embed=correct_usage_embed("unmute", {
                "user": "a member of the server to unmute"
            }))
            return
        # tries to remove the the muted role from the user and update the database
        if await self.unmute_user_helper(ctx.guild, member, 0, True) or \
                await remove_muted_role(ctx.guild, member):
            self.dbclient.bot[str(ctx.guild.id)].find_one_and_update(
                {"_id": member.id, "permanently_muted": {"$exists": True}},
                {"$set": {"permanently_muted": False}})
        else:
            await ctx.send(f"User \"{member.name}\" isn't currently muted")

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def ban(self, ctx, member: discord.Member = None, delete_days=None, *, ban_reason=None):
        """
        Method that is used to ban a user
        :param ctx: the context under which the ban is issued
        :param member: the user which is to be banned
        :param ban_reason: the reason for which the user is banned
        :return: None
        """
        # makes sure that the required arguments are given and the values are expected
        if member is None or delete_days is None or not delete_days.isnumeric() or not (
                0 <= int(delete_days) <= 7) or ban_reason is None:
            await ctx.send(embed=correct_usage_embed("ban", {
                "user": "a member of the server to ban",
                "delete_days": "number of days worth of messages to delete from the user (from 0-7 inclusive)",
                "reason": "the reason for which the user is getting banned"
            }))
            return
        # sets the issued datetime
        issued_datetime = datetime.utcnow()
        # convert the days to a number
        delete_days = int(delete_days)
        # bans the user from the server
        await ctx.guild.ban(member, delete_message_days=delete_days, reason=ban_reason)
        # reflects the ban into the database
        self.dbclient.bot[str(ctx.guild.id)].update({"_id": member.id},
                                                    {"$push": {
                                                        "bans": {
                                                            "issuer": ctx.author.id,
                                                            "reason": ban_reason,
                                                            "issued_datetime": issued_datetime,
                                                            "deleted_days": delete_days
                                                        }}}, upsert=True)
        # conveys that the ban was successful to the server
        await ctx.send(f"User \"{member.name}\" has successfully been banned from this server")
        # communicates the ban to the user and the reason for it
        try:
            await member.send(f"You have been permanently banned on the server \"{ctx.guild}\" for the following "
                              f"reasoning: {ban_reason}")
        except Exception:
            pass

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def unban(self, ctx, member_id=None, *, unban_reason=None):
        """
        Method that is used to unban a user
        :param ctx: the context under which the unban is issued
        :param member_id: the id of the user which is to be unbanned
        :param unban_reason: the reason for which the user is unbanned
        :return: None
        """
        # ensures that the required parameters are passed in
        if member_id is None or not member_id.isnumeric() or unban_reason is None:
            await ctx.send(embed=correct_usage_embed("unban", {
                "user_id": "the id of the user to unban",
                "reason": "the reason for which the user is being unbanned"
            }))
            return
        # converts the passed in id to a number
        member_id = int(member_id)
        # sets the issued datetime of the unban
        issued_datetime = datetime.utcnow()
        # gets the currently banned users
        currently_banned_users = await ctx.guild.bans()
        # tries to find the user within the list of banned users
        user = next((entry.user for entry in currently_banned_users if entry.user.id == member_id), None)
        # if the user couldn't be found in the list of banned users, then error is communicated to the user
        if user is None:
            await ctx.send(embed=Embed(title="User not found",
                                       description="The specified user id couldn't be resolved to a banned Discord "
                                                   "user in this server. Either the given user id was invalid or the "
                                                   "user id isn't currently banned in this server",
                                       color=COLOR_RED))
            return

        # unbans that the user from the server
        await ctx.guild.unban(user, reason=unban_reason)
        # updates the database with the data from the unban
        self.dbclient.bot[str(ctx.guild.id)].update({"_id": user.id},
                                                    {"$push": {
                                                        "unbans": {
                                                            "issuer": ctx.author.id,
                                                            "reason": unban_reason,
                                                            "issued_datetime": issued_datetime,
                                                        }}}, upsert=True)
        # conveys the unban was successful to the server
        await ctx.send(f"User \"{user.name}\" has successfully been unbanned from this server")
        # communicates the unban to the user and the reason for it
        try:
            await user.send(
                f"You have been unbanned from the server \"{ctx.guild}\" for the following reasoning: {unban_reason}")
        except Exception:
            pass

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def modinfo(self, ctx, info_type=None, mod_id=None):
        """
        Method that is used to receive a list of the warnings, mutes and bans issued by a mod
        :param ctx: context under which the list is called for
        :param info_type: type of the info that will be queried; must be one of [w]arnings, [m]utes, [b]ans, [u]nbans
        :param mod_id: id of the mod for which the info is to be fetched
        :return: None
        """
        # makes sure that the arguments passed in are valid
        if info_type is None or (
                info_type not in self._INFO_TYPES.keys() and info_type not in self._INFO_TYPES.values()) \
                or mod_id is None or not mod_id.isnumeric():
            await ctx.send(embed=correct_usage_embed("modinfo", {
                "info_type": "the type of information you want; must be one of [w]arnings, [m]utes, [b]ans, [u]nbans",
                "mod_id": "the id of the mod for which you want to get the info about"
            }))
            return
        # creates the embed to return back
        embed_to_send = Embed(title="Moderation Info",
                              description="All of the moderation information for " + mod_id, color=COLOR_RED)
        # converts the mod_id to a number
        mod_id = int(mod_id)
        # converts the info_type to the one in the database
        if len(info_type) == 1:
            info_type = self._INFO_TYPES[info_type]
        result = self.dbclient.bot[str(ctx.guild.id)].find({f"{info_type}.issuer": mod_id}, {info_type: 1})
        if result is not None:
            # go through every profile in the collection in order to find the mods associated with each command:
            for document in result:
                # for every document (profile) in the collection, first get the list of information associated
                info_list = document[info_type]
                str_to_send = ""
                for index, info_dict in enumerate(info_list):
                    # now go through and create a string for each warning, mute, ban and unban in the list
                    if info_dict["issuer"] is None or int(info_dict["issuer"]) != mod_id:
                        continue
                    if "issuer" in info_dict:
                        del info_dict["issuer"]
                    str_to_send = str_to_send + f"\n{str(index + 1)}:\n{create_str_from_info(info_dict)}"
                if str_to_send != "":
                    embed_to_send.add_field(name="For user: " + str(document['_id']), value=str_to_send,
                                            inline=False)

        await ctx.send(embed=embed_to_send)

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def info(self, ctx, info_type=None, member_id=None):
        """
        Method that is used to receive a list of warnings issued to a user
        :param ctx: context under which the list is called for
        :param info_type: type of the info that will be queried; must be one of [w]arnings, [m]utes, [b]ans, [u]nbans
        :param member_id: id of the member for which the info is to be fetched
        :return: None
        """
        # ensures that the required parameters are passed in
        if info_type is None or (
                info_type not in self._INFO_TYPES.keys() and info_type not in self._INFO_TYPES.values()) \
                or member_id is None or not member_id.isnumeric():
            await ctx.send(embed=correct_usage_embed("info", {
                "info_type": "the type of information you want;  must be one of [w]arnings, [m]utes, [b]ans, [u]nbans",
                "member_id": "the id for the member you want to know about"
            }))
            return
        embed_to_send = Embed(title="User Moderation Info",
                              description="All of the information for " + member_id, color=COLOR_RED)
        member_id = int(member_id)
        if len(info_type) == 1:
            info_type = self._INFO_TYPES[info_type]
        # get the specific users entire profile
        result = self.dbclient.bot[str(ctx.guild.id)].find_one({"_id": member_id}, {info_type: 1})
        if result is not None:
            info_list = result[info_type]
            info_type = info_type.capitalize()
            str_to_send = ""
            # go through every single item in the list of information and add it to a string
            for index, info_dict in enumerate(info_list):
                str_to_send = str_to_send + f"\n{str(index + 1)}:\n{create_str_from_info(info_dict)}"
            if str_to_send != "":
                embed_to_send.add_field(name=info_type, value=str_to_send, inline=False)
            else:
                embed_to_send.add_field(name=info_type, value="None to display", inline=False)

        await ctx.send(embed=embed_to_send)


def setup(client):
    client.add_cog(Management(client))
    return


def help(COMMAND_PREFIX):
    return ["Management Commands",
            f"{COMMAND_PREFIX}Warn [user] [reason]\n{COMMAND_PREFIX}Mute [user] [duration] [reason]\n"
            f"{COMMAND_PREFIX}Unmute [user]\n{COMMAND_PREFIX}Ban [user] [delete_days] [reason]\n"
            f"{COMMAND_PREFIX}Unban [user_id] [reason]\n{COMMAND_PREFIX}Info [info_type] [user]\n"
            f"{COMMAND_PREFIX}ModInfo [info_type] [user]"]
