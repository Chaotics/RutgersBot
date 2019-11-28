from datetime import datetime

import discord
from discord.ext import commands

from turn_on import COLOR_RED


class Dining(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def Takeout(self, ctx):
        embed = discord.Embed(title="Takeout Times", color=COLOR_RED, description="")
        currentDT = datetime.today().strftime('%A')

        breakfast_time_str = "Breakfast: 7 AM – 11:30 AM \n"
        lunch_time_str = "Lunch: 11:30 AM – 4 PM \n"
        dinner_time_str = "Dinner: 4 PM – Midnight \n"
        str_to_send = breakfast_time_str + lunch_time_str

        if currentDT == "Monday":
            str_to_send += dinner_time_str
        elif currentDT == "Tuesday":
            str_to_send += dinner_time_str
        elif currentDT == "Wednesday":
            str_to_send += dinner_time_str
        elif currentDT == "Thursday":
            str_to_send += dinner_time_str
        elif currentDT == "Friday":
            pass
        elif currentDT == "Saturday":
            str_to_send = "Saturday: Closed\n"
        else:
            str_to_send = "Sunday: 5:30 PM – 10 PM \n"

        # str_to_send = breakfast_time_str + lunch_time_str + dinner_time_str + sunday_time_str

        embed.add_field(name="These are the times:", value=str_to_send, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def DineIn(self, ctx):
        """
        Weekdays: 7:00AM – 9:00PM
        Breakfast: 7:00 – 11:00AM
        Lunch: 11:00AM – 4:00PM
        Dinner: 4:00 – 9:00PM

        Weekends: 9:30AM – 8:00PM
        Brunch: 9:30AM – 4:00PM
        Dinner: 4:00 – 8:00PM
        """
        embed = discord.Embed(title="Dining Times", description="", color=COLOR_RED)

        currentDT = datetime.today().strftime('%A')
        week_breakfast_str = "Breakfast: 7 AM – 11 AM\n"
        week_lunch_str = "Lunch: 11 AM – 4 PM\n"
        week_dinner_str = "Dinner: 4 PM – 9 PM\n"

        weekend_brunch_str = "Brunch: 9:30 AM – 4 PM\n"
        weekend_dinner_str = "Dinner: 4 PM – 8 PM\n"

        if currentDT == "Saturday":
            str_to_send = weekend_brunch_str + weekend_dinner_str
        elif currentDT == "Sunday":
            str_to_send = weekend_brunch_str + weekend_dinner_str
        else:
            str_to_send = week_breakfast_str + week_lunch_str + week_dinner_str

        embed.add_field(name="These are the times:", value=str_to_send, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Dining(client))
    return


def help(COMMAND_PREFIX):
    return ["Dining Commands", f"{COMMAND_PREFIX}Takeout (gives the times takeout is open) \n {COMMAND_PREFIX}"
                               f"DineIn (gives the times the dining hall is open)"]
