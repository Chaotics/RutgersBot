import discord
import requests
from discord.ext import commands

from api_utils import create_api_url, append_campus_coords, API_REQUEST_HEADERS, API_AGENCIES, CAMPUS_FULL_NAMES, \
    attach_api_error


class Busing(commands.Cog):
    # declares some constants

    # represents the API url/endpoint that will be used to retrieve the data
    _STOPS_API_URL = create_api_url("stops")
    _ROUTES_API_URL = create_api_url("routes")

    # represents the valid values for the campus field for the stops and routes command
    _VALID_CAMPUSES_FOR_STOPS = [stop_name for stop_name in CAMPUS_FULL_NAMES.keys() if stop_name != "nb"]
    _VALID_CAMPUSES_FOR_ROUTES = ["nb", "nk", "cn"]

    def __init__(self, client):
        self.client = client

    # command to retrieve a list of stops for a given campus
    # the default campus (given that no campus is provided), College Avenue is used
    @commands.command()
    async def Stops(self, ctx, campus="ca"):
        # creates an embed to output the info fetched from the API
        embed = discord.Embed(title="Stops", description="", color=0xff1300)

        # starts by first checking if the campus value provided is valid
        if campus not in Busing._VALID_CAMPUSES_FOR_STOPS:
            # if the provided campus is invalid, an error is sent back
            embed.add_field(name="**ERROR**", value=f"Please provide a correct value for campus. It has to be "
                                                    f"one of {Busing._VALID_CAMPUSES_FOR_STOPS}",
                            inline=False)
            await ctx.send(embed=embed)
        # otherwise, a request is made to the API to fetch the bus stops, using the url, required headers, and the
        # required and optional parameters
        response = requests.get(url=Busing._STOPS_API_URL, headers=API_REQUEST_HEADERS,
                                params=append_campus_coords(campus))

        # once the response comes back from the API, the status_code is checked to see if it was successful
        if response.status_code == requests.codes.ok:
            # if the request was successful, the data is parsed to filter only the name field, and then
            # all the stops are concatenated using a new line character to be set into the embed
            stop_names = "\n".join([stop_info["name"] for stop_info in response.json()["data"]])

            # first, title is chosen by expanding the campus abbreviation string and the value is set to
            # be the string representing the bus stop names
            embed.add_field(name=CAMPUS_FULL_NAMES[campus] + " Stops: ", value=stop_names,
                            inline=False)
        else:
            # if the request was unsuccessful, an error is attached to the embed instead
            attach_api_error(embed=embed, err_code=response.status_code, err_type=response.reason,
                             err_msg=response.text)

        # finally the embed is sent to the server
        await ctx.send(embed=embed)

    # command to retrieve a list of routes for a given campus
    # the default campus (given that no campus is provided), New Brunswick is used
    @commands.command()
    async def Routes(self, ctx, campus="nb"):
        # first an embed is created to send the routes back to the server
        embed = discord.Embed(title="Routes", description="", color=0xff1300)

        # the campus is validated
        if campus not in Busing._VALID_CAMPUSES_FOR_ROUTES:
            # if its invalid, a list of valid campuses to retrieve routes is attached to the embed
            embed.add_field(name="**ERROR**", value=f"Please provide a correct value for campus. It has to be "
                                                    f"one of {Busing._VALID_CAMPUSES_FOR_ROUTES}",
                            inline=False)
        else:
            # otherwise, a request is made to the API to fetch the list of routes for the provided campus
            response = requests.get(url=Busing._ROUTES_API_URL, headers=API_REQUEST_HEADERS,
                                    params=append_campus_coords(campus))

            # the response status code is checked to verify if the request was successful
            if response.status_code == requests.codes.ok:
                # if the request was successful, the relevant data from the response is extracted
                # the data is further filtered to only include the active one's
                route_names = "\n".join(
                    [route_info["long_name"] for route_info in response.json()["data"][API_AGENCIES] if
                     route_info["is_active"]])

                # if the returned list of routes is empty, an appropriate message is conveyed
                if not route_names:
                    route_names = "No routes currently active on this campus"

                # next, the relevant data is attached to the embed in order to send it to the server
                embed.add_field(name=CAMPUS_FULL_NAMES[campus] + " Routes: ", value=route_names,
                                inline=False)
            else:
                # otherwise, if the request failed, error is attached to the embed instead
                attach_api_error(embed=embed, err_code=response.status_code, err_type=response.reason,
                                 err_msg=response.text)
        # finally, the embed is sent back to the server
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
