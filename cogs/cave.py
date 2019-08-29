import discord
from discord.ext import commands


class Cave(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def CaveTimes(self, ctx):
        embed = discord.Embed(title="Cave Times", description="", color=0xff1300)
        mon_time_str = "Monday: 1PM - 11PM\n"
        tues_time_str = " Tuesday: 1PM - 11PM\n"
        wed_time_str = " Wednesday: 1PM - 11PM\n"
        thurs_time_str = " Thursday: 1PM - 11PM\n"
        fri_time_str = " Friday: 1PM - 6PM\n"
        sat_time_str = " Saturday: Closed\n"
        sun_time_str = " Sunday: 3PM - 11PM\n"
        str_to_send = mon_time_str + tues_time_str + wed_time_str + thurs_time_str + fri_time_str + sat_time_str + sun_time_str

        embed.add_field(name="These are the times:", value=str_to_send, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Cave(client))
    return
