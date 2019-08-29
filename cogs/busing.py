import discord
from discord.ext import commands


class Busing(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def Stops(self, ctx):
        embed = discord.Embed(title="Stops", description="", color=0xff1300)
        stops = ""  # fill this with all the available stops
        # make sure to add a new line between each in the string
        # ex: Stop1 \n Stop2....

        if not stops:
            stops = "N/A"

        embed.add_field(name="These are the available stops: ", value=stops, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def BusTime(self, ctx, route, stop):

        msg = ""  # fill this with the estimated arrival time to be sent to the server

        if not msg:
            msg = "Could not find estimated arrival time for route " + route + " on stop " + stop + "."

        await ctx.send(msg)

    @commands.command()
    async def Routes(self, ctx):
        embed = discord.Embed(title="Routes", description="", color=0xff1300)
        routes = ""  # fill this with all the available routes
        # follows the same new line scheme as stops

        if not routes:
            routes = "N/A"

        embed.add_field(name="These are the available routes: ", value=routes, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Busing(client))
    return
