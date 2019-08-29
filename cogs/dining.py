import discord
from discord.ext import commands


class Dining(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def TakeoutTimes(self, ctx):
        embed = discord.Embed(title="Takeout Times", description="", color=0xff1300)

        breakfast_time_str = "Breakfast (Mon–Fri): 7 AM – 11:30 AM \n"
        lunch_time_str = "Lunch (Mon–Fri): 11:30 AM – 4 PM \n"
        dinner_time_str = "Dinner (Mon–Thurs): 4 PM – Midnight \n"
        sunday_time_str = "Sunday: 5:30 PM – 10 PM \n"

        str_to_send = breakfast_time_str + lunch_time_str + dinner_time_str + sunday_time_str

        embed.add_field(name="These are the times:", value=str_to_send, inline=False)
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

        weekdays_str = "__Weekdays:__ 7 AM – 9 PM\n"
        week_breakfast_str = "Breakfast: 7 AM – 11 AM\n"
        week_lunch_str = "Lunch: 11 AM – 4 PM\n"
        week_dinner_str = "Dinner: 4 PM – 9 PM\n"

        weekends_str = "__Weekends:__ 9:30 AM – 8 PM\n"
        weekend_brunch_str = "Brunch: 9:30 AM – 4 PM\n"
        weekend_dinner_str = "Dinner: 4 PM – 8 PM\n"

        str_to_send = weekdays_str + week_breakfast_str + week_lunch_str + week_dinner_str + "\n"
        str_to_send = str_to_send + weekends_str + weekend_brunch_str + weekend_dinner_str

        embed.add_field(name="These are the times:", value=str_to_send, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Dining(client))
    return
