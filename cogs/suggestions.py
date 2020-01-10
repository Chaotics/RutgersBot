import discord
import pymongo
from discord import Embed
from discord.ext import commands

import config
from turn_on import correct_usage_embed, admins


class Suggestions(commands.Cog):
    def __init__(self, client):

        self.client = client

        # mongodb database connection
        self.dbclient = pymongo.MongoClient(config.MONGO_KEY)

    @commands.command()
    async def report(self, ctx, report_info=None):
        if report_info is None:
            await ctx.send(embed=correct_usage_embed("Report", {
                "report_info": "Information on the bug to be reported to the developers."}))
            return

        self.dbclient.bot.reports.insert({"report_info": report_info,
                                          "reporter_id": ctx.author.id,
                                          "status": "non-critical"})

        await ctx.send("Report successfully sent to the bot developers.")

    @commands.command()
    @commands.has_any_role(*config.MODERATOR_ROLES)
    async def criticalreport(self, ctx, report_info=None):
        if report_info is None:
            await ctx.send(embed=correct_usage_embed("CriticalReport", {
                "report_info": "Information on the bug to be reported to the developers."}))
            return

        self.dbclient.bot.reports.insert({"report_info": report_info,
                                          "reporter_id": ctx.author.id,
                                          "status": "critical"})
        for admin in admins:
            bot_dev = self.client.get_user(admin)
            await bot_dev.send("Critical report: " + report_info)

        await ctx.send("Successfully reported the critical issue to the bot developers.")


def setup(client):
    client.add_cog(Suggestions(client))
    return


def help(COMMAND_PREFIX):
    return ["Suggestions",
            f"{COMMAND_PREFIX}Report [report_info] (sends a suggestion/bug to the bot developers)\n"
            f"{COMMAND_PREFIX}CriticalReport [report_info] (sends a critical suggestion/bug to the bot developers, "
            f"can only be used by mods"]
