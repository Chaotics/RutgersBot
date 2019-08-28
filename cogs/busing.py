import discord
from discord.ext import commands


class Busing(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def Buses(self, ctx):
        embed = discord.Embed(title="Busing", description="", color=0xff1300)
        embed.add_field(name="These are the times: ", value="Route A", inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Busing(client))
    return
