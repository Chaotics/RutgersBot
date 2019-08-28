import discord
from discord.ext import commands


class Dining(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def TakeoutTimes(self, ctx):
        embed = discord.Embed(title="Takeout Times", description="", color=0xff1300)

        strBreakfastTime = "Breakfast (Mon–Fri): 7 – 11:30 AM \n"
        strLunchTime = "Lunch (Mon–Fri): 11:30 AM – 4 PM \n"
        strDinnerTime = "Dinner (Mon–Thurs): 4 PM – midnight \n"
        strSundayTime = "Sunday: 5:30 PM – 10 PM \n"

        strToSend = strBreakfastTime + strLunchTime + strDinnerTime + strSundayTime

        embed.add_field(name="These are the times:", value=strToSend, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def DineInTimes(self, ctx):
        """
        Weekdays: 7:00AM – 9:00PM
        Breakfast: 7:00 – 11:00AM
        Lunch: 11:00AM – 4:00PM
        Dinner: 4:00 – 9:00PM

        Weekends: 9:30AM – 8:00PM
        Brunch: 9:30AM – 4:00PM
        Dinner: 4:00 – 8:00PM
        """
        embed = discord.Embed(title="Dining Times", description="", color=0xff1300)

        strWeekdays = "__Weekdays:__ 7:00AM – 9:00PM\n"
        strWeekBreakfast = "Breakfast: 7:00 – 11:00AM\n"
        strWeekLunch = "Lunch: 11:00AM – 4:00PM\n"
        strWeekDinner = "Dinner: 4:00 – 9:00PM\n"

        strWeekends = "__Weekends:__ 9:30AM – 8:00PM\n"
        strDinnerTime = "Brunch: 9:30AM – 4:00PM\n"
        strSundayTime = "Dinner: 4:00 – 8:00PM\n"

        strToSend = strWeekdays + strWeekBreakfast + strWeekLunch + strWeekDinner + "\n"
        strToSend = strToSend + strWeekends + strDinnerTime + strSundayTime

        embed.add_field(name="These are the times:", value=strToSend, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Dining(client))
    return
