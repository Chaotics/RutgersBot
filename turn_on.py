import os
import signal
import sys

import discord
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded, ExtensionAlreadyLoaded

import secret

TOKEN = secret.LOGIN_TOKEN
client = commands.Bot(command_prefix="r!", case_insensitive=True)
client.remove_command('help')


# a signal handler to handle shutdown of the bot from the terminal
def signal_handler(sig, frame):
    print('Closing bot...')
    sys.exit(0)


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help", description="A general list of commands provided", color=0xff1300)
    embed.add_field(name="Basic Commands", value="r!help", inline=False)
    embed.add_field(name="Admin Commands", value="r!load (loads a set of commands) \n r!unload (unloads a set of "
                                                 "commands)", inline=False)
    embed.add_field(name="Cave Commands",
                    value="r!CaveTimes (gives the times the cave is open)", inline=False)
    embed.add_field(name="Dining Commands",
                    value="r!TakeoutTimes (gives the times takeout is open) \n r!DineInTimes (gives the times"
                          "the dining hall is open)", inline=False)
    embed.add_field(name="Busing Commands",
                    value="r!Routes (gives available routes) \n"
                          "r!Stops (gives available stops) \n"
                          "r!BusTime [stop] [route] (gives estimated arrival time) "
                    , inline=False)
    await ctx.send(embed=embed)


@client.command()
async def load(ctx, extension):
    # currently for loading and unloading commands, I only check if it matches my ID
    # to load or unload the cog, this can be changed  once we find a more permanent storage method
    result = False
    user_id = ctx.author.id
    if user_id in [93121870949281792, 126420592579706880]:
        result = True

    if result is False:
        msg = "You do not have permission to load commands!"
        await ctx.send(msg)
        return
    else:
        msg = ""
        try:
            client.load_extension(f"cogs.{extension}")
            msg = "Extension loaded successfully."
        except ExtensionAlreadyLoaded:
            msg = "Extension failed to load."

        await ctx.send(msg)
        return


@client.command()
async def unload(ctx, extension):
    result = False
    user_id = ctx.author.id
    if user_id in [93121870949281792, 126420592579706880]:
        result = True

    if result is False:
        msg = "You do not have permission to unload commands!"
        await ctx.send(msg)
        return
    else:
        msg = ""
        try:
            client.unload_extension(f'cogs.{extension}')
            msg = "Extension unloaded successfully."
        except ExtensionNotLoaded:
            msg = "Extension failed to unload."

        await ctx.send(msg)
        return


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('The Rutgers buses...'))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


if __name__ == '__main__':
    # sets up signal to be recognized by user
    signal.signal(signal.SIGINT, signal_handler)
    # for every filename in the cogs directory...
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            # load the cog
            client.load_extension(f'cogs.{filename[:-3]}')

            # What is a cog? A cog is a set of commands that go together, they can be unloaded or loaded using
            # a set of commands

    client.run(TOKEN)
