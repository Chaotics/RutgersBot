import discord
from discord.ext import commands


class Cave(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def CaveTimes(self, ctx):
        embed = discord.Embed(title="Cave Times", description="", color=0xff1300)
        strMonTime = "Monday: 1PM - 11PM\n"
        strTuesTime = " Tuesday: 1PM - 11PM\n"
        strWedTime = " Wednesday: 1PM - 11PM\n"
        strThursTime = " Thursday: 1PM - 11PM\n"
        strFriTime = " Friday: 1PM - 6PM\n"
        strSunTime = " Sunday: 3PM - 11PM\n"
        strToSend = strMonTime + strTuesTime + strWedTime + strThursTime + strFriTime + strSunTime

        embed.add_field(name="These are the times:", value=strToSend, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Cave(client))
    return
