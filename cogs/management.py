import discord
from discord.ext import commands
import pymongo
import secret


class Management(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dbclient = pymongo.MongoClient(secret.MONGO_KEY)

    @commands.command()
    async def warn(self, ctx, user: discord.User, *, WarningInformation):
        userID = user.id
        userData = self.dbclient.bot.profile.find_one({"_id": userID})

        if userData is None:
            self.dbclient.bot.profile.insert({"_id": userID})
        try:
            warnings = userData['Warnings']
            # warnings already exists
            warnings.append(WarningInformation)
            self.dbclient.bot.profile.update({"_id": userID}, {"$set": {"Warnings": warnings}})

        except:
            #warning does not yet exist
            warnings = [WarningInformation]
            self.dbclient.bot.profile.update({"_id": userID}, {"$set": {"Warnings": warnings}})
        ExtraWarningInfo = "You have received a warning with the following reasoning: " + WarningInformation
        await ctx.send(WarningInformation)
        await user.send(ExtraWarningInfo)


def setup(client):
    client.add_cog(Management(client))
    return


def help(COMMAND_PREFIX):
    return ["Management Commands", f"{COMMAND_PREFIX}Warn (warns a specific user)"]
