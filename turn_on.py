import importlib
import os
import signal
import sys

import discord
import pymongo
from discord import Embed
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded, ExtensionAlreadyLoaded

import config

TOKEN = config.LOGIN_TOKEN
command_prefixes = {}
COLOR_RED = 0xff1300
dbclient = pymongo.MongoClient(config.MONGO_KEY)
admins = [93121870949281792, 126420592579706880]
loaded_help_data = [[]]


def fetch_command_prefix(guild):
    global command_prefixes, dbclient
    if guild.id not in command_prefixes:
        prefix = dbclient.bot[str(guild.id)].find_one({"prefix": {"$exists": 1}}, {"_id": 0, "prefix": 1})
        if prefix is not None:
            command_prefixes[guild.id] = prefix["prefix"]
        else:
            command_prefixes[guild.id] = config.DEFAULT_COMMAND_PREFIX
    print("Current Prefix: " + command_prefixes[guild.id])
    return command_prefixes[guild.id]


client = commands.Bot(command_prefix=lambda bot, msg: fetch_command_prefix(msg.guild), case_insensitive=True)
client.remove_command("help")


# check for bot admins
def is_bot_admin(id):
    if id in admins:
        return True
    return False


# a signal handler to handle shutdown of the bot from the terminal
def signal_handler(sig, frame):
    print("Closing bot...")
    sys.exit(0)


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help",
                          description=f"A general list of commands provided. Use `{fetch_command_prefix(ctx.guild)}"
                                      f"[command]`, where `command` is a valid command from below. "
                                      f"Run it without any inputs to get further details about correct usage",
                          color=COLOR_RED)
    for data in loaded_help_data:
        embed.add_field(name=data[0], value=data[1], inline=False)
    user = ctx.author
    try:
        await user.send(embed=embed)
    except:
        await ctx.send("Failed to send you a help message. You may have your DMs blocked.")
        return
    await ctx.send("Sent you a help message!")


@client.command()
async def repo(ctx):
    desc = "Our repository is available [here!](https://github.com/Chaotics/RutgersBot)"

    embed = discord.Embed(
            title="RutgersBot Repository",
            description=desc,
            color=COLOR_RED
    )
    await ctx.send(embed=embed)


@client.command()
@commands.has_any_role(*config.MODERATOR_ROLES)
async def changeprefix(ctx, *, new_prefix: str = None):
    """
    Method that is used to change the prefix for commands for the bot in a given server
    :param ctx: context under which the command is called under
    :param new_prefix: the new prefix for invoking the bot's commands
    :return: None
    """
    if new_prefix is None or not new_prefix:
        await ctx.send(embed=correct_usage_embed(ctx.guild, "changeprefix", {
            "new_prefix": "the new non-empty prefix that is desired to be used to invoke the bot's commands. "
                          "Note: The default prefix is `r!`"
        }))
        return
    command_prefixes[ctx.guild.id] = new_prefix
    dbclient.bot[str(ctx.guild.id)].update({"prefix": {"$exists": 1}}, {"$set": {"prefix": new_prefix}}, upsert=True)
    await ctx.send(f"The prefix has successfully been changed to: `{new_prefix}`")


# Function that prints the Discord Websocket protocol latency
@client.command()
async def ping(ctx):
    str_to_send = "Pong! "
    if client.latency < 1:
        str_to_send += "%.2f ms" % (client.latency * 1000)
    else:
        str_to_send += "%.2f s" % client.latency
    await ctx.send(str_to_send)


# Function that is run when the Management cog is loaded
async def perform_management_load():
    # checks if the cog is loaded, and if it is, the instance of that Cog is captured
    # and then the temporarily muted users are loaded into that instance
    if "Management" in client.cogs:
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
            client.unload_extension(f"cogs.{extension}")
            msg = "Extension unloaded successfully."
        except ExtensionNotLoaded:
            msg = "Extension failed to unload."

        await ctx.send(msg)
        return


@client.command()
async def reload(ctx, extension):
    user_id = ctx.author.id
    if not is_bot_admin(user_id):
        await ctx.send("Oops! You can\'t do that.")
    else:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.send("Cog reloaded.")
        return


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("the Rutgers buses"))
    await perform_management_load()
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


class InvalidConfigurationException(Exception):
    pass


# function to display correct usage of a command
def correct_usage_embed(guild: discord.Guild, command_name: str, args: dict):
    arg_list = ""
    for arg_name in args.keys():
        arg_list = arg_list + f"[{arg_name}]"
    arg_explanation_str = ""
    for arg_name, arg_desc in args.items():
        arg_explanation_str = arg_explanation_str + f"**{arg_name}** = {arg_desc}\n"
    return Embed(title="Incorrect usage",
                 description=f"**Correct usage**: {fetch_command_prefix(guild)}{command_name} {arg_list}\n{arg_explanation_str}",
                 color=COLOR_RED)


if __name__ == "__main__":
    # sets up signal to be recognized by user
    signal.signal(signal.SIGINT, signal_handler)
    loaded_help_data = [["Admin Commands", "`load` (loads a set of commands\n"
                                           "`unload` (unloads a set of commands)"],
                        ["Basic Commands", "`repo` (provides a link to the open source repository)"]]
    # for every filename in the cogs directory...
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # load the cog
            client.load_extension(f"cogs.{filename[:-3]}")

            # What is a cog? A cog is a set of commands that go together, they can be unloaded or loaded using
            # a set of commands

            # here we are loading separate help data per cog, in order to deal with changing this core file less
            # and to allow for expandability
            lib = importlib.import_module(f"cogs.{filename[:-3]}")
            help_data = getattr(lib, "get_help")
            current_data = help_data()
            data_to_add = [current_data[0], current_data[1]]
            loaded_help_data.append(data_to_add)
    client.run(TOKEN)
