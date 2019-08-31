import discord
import requests
from discord.ext import commands

from api_utils import create_api_url, append_campus_coords, API_REQUEST_HEADERS, API_AGENCIES, CAMPUS_FULL_NAMES, \
    attach_api_error


class Busing(commands.Cog):
    _STOPS_API_URL = create_api_url("stops")
    _ROUTES_API_URL = create_api_url("routes")
    _VALID_CAMPUSES_FOR_STOPS = [stop_name for stop_name in CAMPUS_FULL_NAMES.keys() if stop_name != "nb"]
    _VALID_CAMPUSES_FOR_ROUTES = ["nb", "nk", "cn"]

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def Stops(self, ctx, campus="ca"):
        embed = discord.Embed(title="Stops", description="", color=0xff1300)
        if campus not in Busing._VALID_CAMPUSES_FOR_STOPS:
            embed.add_field(name="**ERROR**", value=f"Please provide a correct value for campus. It has to be "
                                                    f"one of {Busing._VALID_CAMPUSES_FOR_STOPS}",
                            inline=False)
            await ctx.send(embed=embed)
        response = requests.get(url=Busing._STOPS_API_URL, headers=API_REQUEST_HEADERS,
                                params=append_campus_coords(campus))

        if response.status_code == requests.codes.ok:
            stop_names = "\n".join([stop_info["name"] for stop_info in response.json()["data"]])
            embed.add_field(name=CAMPUS_FULL_NAMES[campus] + " Stops: ", value=stop_names,
                            inline=False)
        else:
            attach_api_error(embed=embed, err_code=response.status_code, err_type=response.reason,
                             err_msg=response.text)

        await ctx.send(embed=embed)

    @commands.command()
    async def Routes(self, ctx, campus="nb"):
        embed = discord.Embed(title="Routes", description="", color=0xff1300)

        if campus not in Busing._VALID_CAMPUSES_FOR_ROUTES:
            embed.add_field(name="**ERROR**", value=f"Please provide a correct value for campus. It has to be "
                                                    f"one of {Busing._VALID_CAMPUSES_FOR_ROUTES}",
                            inline=False)
        else:
            response = requests.get(url=Busing._ROUTES_API_URL, headers=API_REQUEST_HEADERS,
                                    params=append_campus_coords(campus))

            if response.status_code == requests.codes.ok:
                route_names = "\n".join(
                    [route_info["long_name"] for route_info in response.json()["data"][API_AGENCIES] if
                     route_info["is_active"]])

                if not route_names:
                    route_names = "No routes currently active on this campus"
                embed.add_field(name=CAMPUS_FULL_NAMES[campus] + " Routes: ", value=route_names,
                                inline=False)
            else:
                attach_api_error(embed=embed, err_code=response.status_code, err_type=response.reason,
                                 err_msg=response.text)
        await ctx.send(embed=embed)

    @commands.command()
    async def BusTime(self, ctx, route, stop):

        msg = ""  # fill this with the estimated arrival time to be sent to the server

        if not msg:
            msg = "Could not find estimated arrival time for route " + route + " on stop " + stop + "."

        await ctx.send(msg)


def setup(client):
    client.add_cog(Busing(client))
    return
