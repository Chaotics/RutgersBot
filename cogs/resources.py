import discord
from discord.ext import commands


class Resources(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def cs111(self, ctx):
        desc = '[Kate\'s CS111 Guide](https://docs.google.com/document/d/1KhMrYhTlCrKRX5IyQuLtOVcW7fZoBcnAWiAgetr4jQ)'
        desc += '\n[Joseph\'s Midterm 1 Review](https://goo.gl/Yqwo1s)'
        desc += '\n[Joseph\'s Final Review](http://joeb3219.github.io/cs111/final.pdf)'

        embed = discord.Embed(
            title='CS111 Resources',
            description=desc
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def cs112(self, ctx):
        desc = '[Auride\'s Expression Evaluator Tester](https://dshepsis.github.io/ExpressionGenerator/)'
        desc += '\n[Auride\'s Minimum Spanning Tree Tester](https://dshepsis.github.io/MSTGenerator/)'

        embed = discord.Embed(
            title='C112 Resources',
            description=desc
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def cs214(self, ctx):
        desc = '[Qasim\'s Systems Programming Guide](http://qasimabbas.github.io/2016-10-31-systems-notes)'

        embed = discord.Embed(
            title='CS214 Resources',
            description=desc
        )

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Resources(client))
    return


def help(COMMAND_PREFIX):
    return ["Resources", f"If available, do {COMMAND_PREFIX}coursename to get useful course resources.\n"
                         f"Currently only {COMMAND_PREFIX}cs111, {COMMAND_PREFIX}cs112 and {COMMAND_PREFIX}cs214 "
                         f"are available."]
