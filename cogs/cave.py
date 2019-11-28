from datetime import datetime

import discord
from discord.ext import commands

from turn_on import COLOR_RED


class Cave(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def Cave(self, ctx):
        currentDT = datetime.today().strftime('%A')
        # print(currentDT)
        embed = discord.Embed(title="Cave Times", description="", color=COLOR_RED)
        if currentDT == "Monday":
            str_to_send = "Monday: 1PM - 11PM\n"
        elif currentDT == "Tuesday":
            str_to_send = " Tuesday: 1PM - 11PM\n"
        elif currentDT == "Wednesday":
            str_to_send = " Wednesday: 1PM - 11PM\n"
        elif currentDT == "Thursday":
            str_to_send = " Thursday: 1PM - 11PM\n"
        elif currentDT == "Friday":
            str_to_send = " Friday: 1PM - 6PM\n"
        elif currentDT == "Saturday":
            str_to_send = " Saturday: Closed\n"
        else:
            str_to_send = " Sunday: 3PM - 11PM\n"

        # old string to send str_to_send = mon_time_str + tues_time_str + wed_time_str + thurs_time_str +
        # fri_time_str + sat_time_str + sun_time_str

        embed.add_field(name="The hours for today are:", value=str_to_send, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Cave(client))
    return


def help(COMMAND_PREFIX):
    return ["Cave Commands", f"{COMMAND_PREFIX}Cave (gives the times the cave is open)"]
