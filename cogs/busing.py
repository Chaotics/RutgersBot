from datetime import datetime, timedelta

import discord
from aiohttp import ClientSession
from discord.ext import commands

from api_utils import create_api_url, params_append_coords, API_REQUEST_HEADERS, API_AGENCIES, CAMPUS_FULL_NAMES, \
    attach_api_error, params_append_stop_and_route, convert_api_datetime, is_data_stale
from data_utils import find_by_api_id, BusingDataType, find_bus_data
from turn_on import COLOR_RED, correct_usage_embed, COMMAND_PREFIX


class Busing(commands.Cog):
    # declares some constants
    # represents the API url/endpoint that will be used to retrieve the data
    _STOPS_API_URL = create_api_url("stops")
    _ROUTES_API_URL = create_api_url("routes")
    _ARRIVAL_ESTIMATES_API_URL = create_api_url("arrival-estimates")

    # represents the valid values for the campus field for the stops and routes command
    _VALID_CAMPUSES_FOR_STOPS = [stop_name for stop_name in CAMPUS_FULL_NAMES.keys() if stop_name != "nb"]
    _VALID_CAMPUSES_FOR_ROUTES = ["nb", "nk", "cm"]

    def __init__(self, client):
        self.client = client
        self.cache = {"stops": {}, "routes": {}, "bustimes": {}}

    @staticmethod
    def cache_data(cached_resource, json_response, data_str, expires_in=0):
        expire_datetime = convert_api_datetime(json_response["generated_on"]) + timedelta(
            seconds=json_response["rate_limit"]) + (
                              timedelta(seconds=expires_in) if expires_in > 0 else timedelta(
                                  seconds=json_response["expires_in"]))
        cached_resource["expire_datetime"] = expire_datetime
        cached_resource["data"] = data_str

    # command to retrieve a list of stops for a given campus
    # the default campus (given that no campus is provided), College Avenue is used
    @commands.command()
    async def Stops(self, ctx, campus=None):
        # creates an embed to output the relevant info
        embed = discord.Embed(title="Stops", description="", color=COLOR_RED)
        # starts by first checking if the campus value provided is valid
        if campus not in Busing._VALID_CAMPUSES_FOR_STOPS:
            # if the provided campus is invalid, an error is sent back
            await ctx.send(embed=correct_usage_embed("stops", {
                "campus": f"it has to be one of {Busing._VALID_CAMPUSES_FOR_STOPS}\n"
                          "nk = Newark\n"
                          "cm = Camden\n"
                          "li = Livingston\n"
                          "bu = Busch\n"
                          "cd = Cook\\Douglass\n"
                          "ca = College Avenue"
            }))
            return

        if campus not in self.cache["stops"]:
            self.cache["stops"][campus] = {}
        cached_resource = self.cache["stops"][campus]
        should_request = is_data_stale(cached_resource)
        stop_names = ""
        if should_request:
            # otherwise, a request is made to the API to fetch the bus stops, using the url, required headers,
            # and the required and optional parameters
            async with ClientSession() as session:
                async with session.get(url=Busing._STOPS_API_URL, headers=API_REQUEST_HEADERS,
                                       params=params_append_coords(campus)) as response:
                    # once the response comes back from the API, the status_code is checked to see if it was successful
                    if response.status == 200:
                        json_response = await response.json()
                        stop_list = []
                        for stop_info in json_response["data"]:
                            stop_data = find_by_api_id(BusingDataType.STOP, int(stop_info["stop_id"]))
                            stop_list.append(str(stop_data))
                        # if the request was successful, the data is parsed to filter only the name field, and then
                        # all the stops are concatenated using a new line character to be set into the embed
                        stop_names = "\n".join(stop_list)
                        self.cache_data(cached_resource, json_response, stop_names)
                    else:
                        # if the request was unsuccessful, an error is attached to the embed instead
                        attach_api_error(embed=embed, err_code=response.status, err_type=response.reason,
                                         err_msg=response.text)
                        await ctx.send(embed=embed)
                        return
        else:
            stop_names = cached_resource["data"]
        # first, title is chosen by expanding the campus abbreviation string and the value is set to
        # be the string representing the bus stop names
        embed.add_field(name=CAMPUS_FULL_NAMES[campus] + " Stops: ", value=stop_names, inline=False)

        # finally the embed is sent to the server
        await ctx.send(embed=embed)

    # command to retrieve a list of routes for a given campus
    # the default campus (given that no campus is provided), New Brunswick is used
    @commands.command()
    async def Routes(self, ctx, campus=None):
        # first an embed is created to send the routes back to the server
        embed = discord.Embed(title="Routes", description="", color=COLOR_RED)

        # the campus is validated
        if campus not in Busing._VALID_CAMPUSES_FOR_ROUTES:
            # if its invalid, a list of valid campuses to retrieve routes is attached to the embed
            await ctx.send(embed=correct_usage_embed("routes", {
                "campus": f"it has to be one of {Busing._VALID_CAMPUSES_FOR_ROUTES}\n"
                          "nk = Newark\n"
                          "cm = Camden\n"
                          "nb = New Brunswick"
            }))
            return

        if campus not in self.cache["routes"]:
            self.cache["routes"][campus] = {}
        cached_resource = self.cache["routes"][campus]
        should_request = is_data_stale(cached_resource)
        route_names = ""
        if should_request:
            # a request is made to the API to fetch the list of routes for the provided campus
            async with ClientSession() as session:
                async with session.get(url=Busing._ROUTES_API_URL, headers=API_REQUEST_HEADERS,
                                       params=params_append_coords(campus)) as response:
                    # the response status code is checked to verify if the request was successful
                    if response.status == 200:
                        json_response = await response.json()
                        route_list = []
                        for route_info in json_response["data"][API_AGENCIES]:
                            if not route_info["is_active"]:
                                continue
                            route_data = find_by_api_id(BusingDataType.ROUTE, int(route_info["route_id"]))
                            route_list.append(str(route_data))
                        # if the request was successful, the relevant data from the response is extracted
                        # the data is further filtered to only include the active one"s
                        route_names = "\n".join(route_list)
                        # if the returned list of routes is empty, an appropriate message is conveyed
                        if not route_names:
                            route_names = "No routes currently active on this campus"
                        self.cache_data(cached_resource, json_response, route_names)
                    else:
                        # otherwise, if the request failed, error is attached to the embed instead
                        attach_api_error(embed=embed, err_code=response.status, err_type=response.reason,
                                         err_msg=response.text)
                        await ctx.send(embed=embed)
                        return
        else:
            route_names = cached_resource["data"]
        # the relevant data is attached to the embed in order to send it to the server
        embed.add_field(name=CAMPUS_FULL_NAMES[campus] + " Routes: ", value=route_names,
                        inline=False)
        # finally, the embed is sent back to the server
        await ctx.send(embed=embed)

    @commands.command()
    async def Bus(self, ctx, stop="", route=""):
        # first an embed is created to convey the arrival estimates back to the server
        embed = discord.Embed(title="Arrival Times", description="", color=COLOR_RED)
        # validates the input stop string passed
        stop_data = find_bus_data(BusingDataType.STOP, stop)
        if stop_data is None:
            await ctx.send(embed=correct_usage_embed("bus", {
                "stop": f"a valid Rutgers stop, fetched from {COMMAND_PREFIX}stops [campus]",
                "route": f"a valid Rutgers route, fetched from {COMMAND_PREFIX}routes [campus]"
            }))
            return
        # validates the input route string passed
        route_data = find_bus_data(BusingDataType.ROUTE, route)
        if route_data is None:
            await ctx.send(embed=correct_usage_embed("bus", {
                "stop": f"a valid Rutgers stop, fetched from {COMMAND_PREFIX}stops [campus]",
                "route": f"a valid Rutgers route, fetched from {COMMAND_PREFIX}routes [campus]"
            }))
            return
        search_str = f"{stop_data.internal_id}{route_data.internal_id}"
        if search_str not in self.cache["bustimes"]:
            self.cache["bustimes"][search_str] = {}
        cached_resource = self.cache["bustimes"][search_str]
        should_request = is_data_stale(cached_resource)
        times_str = ""
        if should_request:
            # makes a request to fetch the arrival estimates for the given route and stop
            async with ClientSession() as session:
                async with session.get(url=Busing._ARRIVAL_ESTIMATES_API_URL, headers=API_REQUEST_HEADERS,
                                       params=params_append_stop_and_route(str(stop_data.api_id),
                                                                           str(route_data.api_id))) as response:
                    # checks the status code to determine if the request was successful
                    if response.status == 200:
                        json_response = await response.json()
                        response_data = json_response["data"]
                        # if the returned data is empty, then it must be that no buses are set to arrive there
                        if not response_data:
                            times_str = f"Currently there are no buses set to arrive here"
                        else:
                            # the arrival times from the JSON parsed data is extracted
                            arrival_times = response_data[0]["arrivals"]
                            # for every arrival time, the time difference is calculated
                            for time_info in arrival_times:
                                # first the datetime string from the API is parsed into Python datetime
                                time = convert_api_datetime(time_info["arrival_at"])
                                # then the difference is calculated from the current time in seconds
                                time_diff = (time - datetime.utcnow()).seconds
                                # the time string to be sent back is either converted to minutes or seconds depending
                                # on the time difference calculated
                                times_str += ((str(round(time_diff)) + " seconds") if time_diff < 60 else (
                                        str(round(time_diff / 60)) + " minutes")) + "\n"
                        self.cache_data(cached_resource, json_response, times_str, 30)
                    else:
                        # otherwise, if the request failed, error is attached to the embed instead
                        attach_api_error(embed=embed, err_code=response.status, err_type=response.reason,
                                         err_msg=response.text)
                        await ctx.send(embed=embed)
                        return
        else:
            times_str = cached_resource["data"]

        # all the arrival times are finally added as a field value
        embed.add_field(name=f"'{route_data.name}' buses arriving at {stop_data.name} in: ", value=times_str,
                        inline=False)
        # the embed created with the relevant data is sent back to the server
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Busing(client))
    return


def help(COMMAND_PREFIX):
    return ["Busing Commands", f"{COMMAND_PREFIX}Routes [school] (gives available routes)\n"
                               f"{COMMAND_PREFIX}Stops [campus] (gives available stops)\n"
                               f"{COMMAND_PREFIX}Bus [stop] [route] (gives estimated arrival time) "]
