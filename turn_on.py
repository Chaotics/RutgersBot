import os
import signal
import sys

import discord
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded, ExtensionAlreadyLoaded

import secret

TOKEN = secret.LOGIN_TOKEN
COMMAND_PREFIX = "r!"
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


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help", description="A general list of commands provided", color=0xff1300)
    embed.add_field(name="Basic Commands", value=f"Do {COMMAND_PREFIX}help to see this help screen!\n"
                                                 "For more information about each command simply attempt\n"
                                                 "to perform the command with no inputs."
                    , inline=False)
    embed.add_field(name="Admin Commands",
                    value=f"{COMMAND_PREFIX}load (loads a set of commands) \n {COMMAND_PREFIX}unload (unloads a set of "
                          "commands)", inline=False)
    embed.add_field(name="Cave Commands",
                    value=f"{COMMAND_PREFIX}Cave (gives the times the cave is open)", inline=False)
    embed.add_field(name="Dining Commands",
                    value=f"{COMMAND_PREFIX}Takeout (gives the times takeout is open) \n {COMMAND_PREFIX}DineIn (gives "
                          "the times the dining hall is open)", inline=False)
    embed.add_field(name="Busing Commands",
                    value=f"{COMMAND_PREFIX}Routes [school] (gives available routes)\n"
                          f"{COMMAND_PREFIX}Stops [campus] (gives available stops)\n"
                          f"{COMMAND_PREFIX}Bus [stop] [route] (gives estimated arrival time) "
                    , inline=False)
    embed.add_field(name="Resources",
                    value="If available, do r!coursename to get useful course resources.\n"
                          f"Currently only {COMMAND_PREFIX}cs111, {COMMAND_PREFIX}cs112 and {COMMAND_PREFIX}cs214 "
                          f"are available."
                    , inline=False)

    await ctx.send(embed=embed)


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
