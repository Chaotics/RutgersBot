from datetime import datetime

import discord
from discord.ext import commands

from turn_on import COLOR_RED


class Cave(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def Cave(self, ctx):
        today = datetime.today().weekday()
        times = ["Monday: 1PM - 11PM", "Tuesday: 1PM - 11PM", "Wednesday: 1PM - 11PM", "Thursday: 1PM - 11PM",
                 "Friday: 1PM - 6PM", "Saturday: Closed", "Sunday: 3PM - 11PM"]
        times[today] = f"**{times[today]}**"
        str_to_send = "\n".join(times)
        embed = discord.Embed(title="Cave Times", description=str_to_send, color=COLOR_RED)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Cave(client))
    return


def help(COMMAND_PREFIX):
    return ["Cave Commands", f"{COMMAND_PREFIX}Cave (gives the times the cave is open)"]
