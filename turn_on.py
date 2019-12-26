import importlib
import os
import signal
import sys

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded, ExtensionAlreadyLoaded

import config

TOKEN = config.LOGIN_TOKEN
COMMAND_PREFIX = "r!"
COLOR_RED = 0xff1300
client = commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitive=True)
client.remove_command('help')


# check for bot admins
def is_bot_admin(id):
    admins = [93121870949281792, 126420592579706880]
    if id in admins:
        return True
    return False


# a signal handler to handle shutdown of the bot from the terminal
def signal_handler(sig, frame):
    print('Closing bot...')
    sys.exit(0)


loadedHelpData = [[]]


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help", description="A general list of commands provided", color=COLOR_RED)
    embed.add_field(name="Basic Commands", value=f"Do {COMMAND_PREFIX}help to see this help screen!\n"
                                                 "For more information about each command simply attempt\n"
                                                 "to perform the command with no inputs."
                    , inline=False)

    embed.add_field(name="Admin Commands",
                    value=f"{COMMAND_PREFIX}load (loads a set of commands) \n {COMMAND_PREFIX}unload (unloads a set of "
                          "commands)", inline=False)
    for data in loadedHelpData:
        embed.add_field(name=data[0], value=data[1], inline=False)

    await ctx.send(embed=embed)


# Function that is run when the Management cog is loaded
async def perform_management_load():
    # checks if the cog is loaded, and if it is, the instance of that Cog is captured
    # and then the temporarily muted users are loaded into that instance
    if 'Management' in client.cogs:
        management_cog = client.cogs["Management"]
        await management_cog.load_temp_muted_users()


@client.command()
async def load(ctx, extension):
    # currently for loading and unloading commands, I only check if it matches my ID
    # to load or unload the cog, this can be changed  once we find a more permanent storage method
    result = False
    user_id = ctx.author.id
    if is_bot_admin(user_id):
        result = True

    if result is False:
        msg = "You do not have permission to load commands!"
        await ctx.send(msg)
        return
    else:
        msg = ""
        try:
            client.load_extension(f"cogs.{extension}")
            await perform_management_load()
            msg = "Extension loaded successfully."
        except ExtensionAlreadyLoaded:
            msg = "Extension failed to load."
        await ctx.send(msg)
        return


@client.command()
async def unload(ctx, extension):
    result = False
    user_id = ctx.author.id
    if is_bot_admin(user_id):
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


@client.command()
async def reload(ctx, extension):
    user_id = ctx.author.id
    if not is_bot_admin(user_id):
        await ctx.send('Oops! You can\'t do that.')
    else:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f"cogs.{extension}")
        await ctx.send('Cog reloaded.')
        return


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('the Rutgers buses'))
    await perform_management_load()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


class InvalidConfigurationException(Exception):
    pass


# function to display correct usage of a command
def correct_usage_embed(command_name: str, args: dict):
    arg_list = ""
    for arg_name in args.keys():
        arg_list = arg_list + f"[{arg_name}]"
    arg_explanation_str = ""
    for arg_name, arg_desc in args.items():
        arg_explanation_str = arg_explanation_str + f"**{arg_name}** = {arg_desc}\n"
    return Embed(title="Incorrect usage",
                 description=f"**Correct usage**: {COMMAND_PREFIX}{command_name} {arg_list}\n{arg_explanation_str}",
                 color=COLOR_RED)


if __name__ == '__main__':
    # sets up signal to be recognized by user
    signal.signal(signal.SIGINT, signal_handler)

    loadedHelpData.clear()
    # for every filename in the cogs directory...
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            # load the cog
            client.load_extension(f'cogs.{filename[:-3]}')

            # What is a cog? A cog is a set of commands that go together, they can be unloaded or loaded using
            # a set of commands

            # here we are loading separate help data per cog, in order to deal with changing this core file less
            # and to allow for expandability
            lib = importlib.import_module(f'cogs.{filename[:-3]}')
            helpData = getattr(lib, 'help')
            currentData = helpData(COMMAND_PREFIX)
            dataToAdd = [currentData[0], currentData[1]]
            loadedHelpData.append(dataToAdd)
    client.run(TOKEN)
