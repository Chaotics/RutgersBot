from datetime import datetime, time

import discord
import pytz
from discord.ext import commands

from turn_on import COLOR_RED


class Dining(commands.Cog):
    eastern_timezone = pytz.timezone("US/Eastern")
    time_format = "%I:%M %p"
    takeout_times = {
        "breakfast_start": time(hour=7, tzinfo=eastern_timezone),
        "breakfast_end": time(hour=10, minute=30, tzinfo=eastern_timezone),
        "lunch_start": time(hour=11, minute=30, tzinfo=eastern_timezone),
        "lunch_end": time(hour=16, tzinfo=eastern_timezone),
        "weekday_dinner_start": time(hour=17, tzinfo=eastern_timezone),
        "weekday_dinner_end": time(hour=0, tzinfo=eastern_timezone),
        "sunday_dinner_start": time(hour=17, minute=30, tzinfo=eastern_timezone),
        "sunday_dinner_end": time(hour=22, tzinfo=eastern_timezone),
        "breakfast_time": None,
        "lunch_time": None,
        "weekday_dinner_time": None,
        "sunday_dinner_time": None
    }
    takeout_times[
        "breakfast_time"] = f"Monday-Friday: {takeout_times['breakfast_start'].strftime(time_format)} - " \
                            f"{takeout_times['breakfast_end'].strftime(time_format)}"
    takeout_times[
        "lunch_time"] = f"Monday-Friday: {takeout_times['lunch_start'].strftime(time_format)} - " \
                        f"{takeout_times['lunch_end'].strftime(time_format)}"
    takeout_times[
        "weekday_dinner_time"] = f"Monday-Thursday: {takeout_times['weekday_dinner_start'].strftime(time_format)} - " \
                                 f"{takeout_times['weekday_dinner_end'].strftime(time_format)} "
    takeout_times[
        "sunday_dinner_time"] = f"Sunday: {takeout_times['sunday_dinner_start'].strftime(time_format)} - " \
                                f"{takeout_times['sunday_dinner_end'].strftime(time_format)}"

    dinein_times = {
        "weekday_breakfast_start": time(hour=7, tzinfo=eastern_timezone),
        "weekday_breakfast_end": time(hour=11, tzinfo=eastern_timezone),
        "weekday_lunch_start": time(hour=11, tzinfo=eastern_timezone),
        "weekday_lunch_end": time(hour=16, tzinfo=eastern_timezone),
        "weekday_dinner_start": time(hour=16, tzinfo=eastern_timezone),
        "weekday_dinner_end": time(hour=21, tzinfo=eastern_timezone),
        "weekend_brunch_start": time(hour=9, minute=30, tzinfo=eastern_timezone),
        "weekend_brunch_end": time(hour=16, tzinfo=eastern_timezone),
        "weekend_dinner_start": time(hour=16, tzinfo=eastern_timezone),
        "weekend_dinner_end": time(hour=20, tzinfo=eastern_timezone),
        "weekday_times": {
            "weekday_breakfast_time": None,
            "weekday_lunch_time": None,
            "weekday_dinner_time": None
        },
        "weekend_times": {
            "weekend_brunch_time": None,
            "weekend_dinner_time": None
        }
    }
    dinein_times["weekday_times"][
        "weekday_breakfast_time"] = f"Breakfast: {dinein_times['weekday_breakfast_start'].strftime(time_format)} - " \
                                    f"{dinein_times['weekday_breakfast_end'].strftime(time_format)}"
    dinein_times["weekday_times"][
        "weekday_lunch_time"] = f"Lunch: {dinein_times['weekday_lunch_start'].strftime(time_format)} - " \
                                f"{dinein_times['weekday_lunch_end'].strftime(time_format)}"
    dinein_times["weekday_times"][
        "weekday_dinner_time"] = f"Dinner: {dinein_times['weekday_dinner_start'].strftime(time_format)} - " \
                                 f"{dinein_times['weekday_dinner_end'].strftime(time_format)}"
    dinein_times["weekend_times"][
        "weekend_brunch_time"] = f"Brunch: {dinein_times['weekend_brunch_start'].strftime(time_format)} - " \
                                 f"{dinein_times['weekend_brunch_end'].strftime(time_format)}"
    dinein_times["weekend_times"][
        "weekend_dinner_time"] = f"Dinner: {dinein_times['weekend_dinner_start'].strftime(time_format)} - " \
                                 f"{dinein_times['weekend_dinner_end'].strftime(time_format)}"

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def Takeout(self, ctx):
        current_datetime = datetime.now(tz=pytz.utc).astimezone(self.eastern_timezone)
        rightnow = current_datetime.time()
        breakfast_time = self.takeout_times["breakfast_time"]
        lunch_time = self.takeout_times["lunch_time"]
        weekday_dinner_time = self.takeout_times["weekday_dinner_time"]
        sunday_dinner_time = self.takeout_times["sunday_dinner_time"]
        if 4 >= current_datetime.weekday() >= 0:
            if self.takeout_times["breakfast_start"] <= rightnow <= self.takeout_times["breakfast_end"]:
                breakfast_time = f"**{breakfast_time}**"
            elif self.takeout_times["lunch_start"] <= rightnow <= self.takeout_times["lunch_end"]:
                lunch_time = f"**{lunch_time}**"
            elif current_datetime.weekday() != 4 and self.takeout_times["weekday_dinner_start"] <= rightnow <= \
                    self.takeout_times["weekday_dinner_end"]:
                weekday_dinner_time = f"**{weekday_dinner_time}**"
        elif current_datetime.weekday() == 6 and self.takeout_times["sunday_dinner_start"] <= rightnow <= \
                self.takeout_times["sunday_dinner_end"]:
            sunday_dinner_time = f"**{sunday_dinner_time}**"
        embed = discord.Embed(title="Takeout Times", description="", color=COLOR_RED)
        embed.add_field(name="Breakfast", value=breakfast_time, inline=False)
        embed.add_field(name="Lunch", value=lunch_time, inline=False)
        embed.add_field(name="Dinner", value=weekday_dinner_time + "\n" + sunday_dinner_time, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def DineIn(self, ctx):
        embed = discord.Embed(title="Dining Times", description="", color=COLOR_RED)
        current_datetime = datetime.now(tz=pytz.utc).astimezone(self.eastern_timezone)
        rightnow = current_datetime.time()
        weekday_times = self.dinein_times["weekday_times"].copy()
        weekend_times = self.dinein_times["weekend_times"].copy()
        if 4 >= current_datetime.weekday() >= 0:
            if self.dinein_times["weekday_breakfast_start"] <= rightnow <= self.dinein_times["weekday_breakfast_end"]:
                weekday_times["weekday_breakfast_time"] = f"**{weekday_times['weekday_breakfast_time']}**"
            elif self.dinein_times["weekday_lunch_start"] <= rightnow <= self.dinein_times["weekday_lunch_end"]:
                weekday_times["weekday_lunch_time"] = f"**{weekday_times['weekday_lunch_time']}**"
            elif self.dinein_times["weekday_dinner_start"] <= rightnow <= self.dinein_times["weekday_dinner_end"]:
                weekday_times["weekday_dinner_time"] = f"**{weekday_times['weekday_dinner_time']}**"
        else:
            if self.dinein_times["weekend_brunch_start"] <= rightnow <= self.dinein_times["weekend_brunch_end"]:
                weekend_times["weekend_brunch_time"] = f"**{weekend_times['weekend_brunch_time']}**"
            elif self.dinein_times["weekend_dinner_start"] <= rightnow <= self.dinein_times["weekend_dinner_end"]:
                weekend_times["weekend_dinner_time"] = f"**{weekend_times['weekend_dinner_time']}**"
        weekday_str = ""
        weekend_str = ""
        for key, val in weekday_times.items():
            weekday_str += val + "\n"
        for key, val in weekend_times.items():
            weekend_str += val + "\n"
        embed.add_field(name="Weekdays", value=weekday_str, inline=False)
        embed.add_field(name="Weekends", value=weekend_str, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Dining(client))
    return


def get_help():
    return ["Dining Commands", f"`takeout` (gives the times takeout is open)\n"
                               f"`dinein` (gives the times the dining hall is open)"]
