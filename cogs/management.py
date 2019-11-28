from datetime import datetime

import discord
import pymongo
from discord import Embed
from discord.ext import commands

import config
from turn_on import COMMAND_PREFIX, COLOR_RED


class Management(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dbclient = pymongo.MongoClient(config.MONGO_KEY)

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def warn(self, ctx=None, user: discord.Member = None, *, warning_reason=None):
        if ctx is None or user is None or warning_reason is None:
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


def setup(client):
    client.add_cog(Management(client))
    return


def help(COMMAND_PREFIX):
    return ["Management Commands",
            f"{COMMAND_PREFIX}Warn [user] [reason]"]
