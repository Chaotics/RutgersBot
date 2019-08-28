import discord
from discord.ext import commands


class Cave(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def CaveTimes(self, ctx):
        embed = discord.Embed(title="Cave Times", description="", color=0xff1300)
        strMonTime = "Monday: \n"
        strTuesTime = " Tuesday: \n"
        strWedTime = " Wednesday: \n"
        strThursTime = " Thursday: \n"
        strFriTime = " Friday: \n "

        strToSend = strMonTime + strTuesTime + strWedTime + strThursTime + strFriTime


        embed.add_field(name="These are the times:", value=strToSend, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Cave(client))
    return
