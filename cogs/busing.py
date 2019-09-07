from datetime import datetime

import discord
import requests
from discord.ext import commands

from api_utils import create_api_url, params_append_coords, API_REQUEST_HEADERS, \
    API_AGENCIES, CAMPUS_FULL_NAMES, \
    attach_api_error, params_append_stop_and_route, convert_api_datetime


class Busing(commands.Cog):
    # declares some constants
    # represents the API url/endpoint that will be used to retrieve the data
    _STOPS_API_URL = create_api_url("stops")
    _ROUTES_API_URL = create_api_url("routes")
    _ARRIVAL_ESTIMATES_API_URL = create_api_url("arrival-estimates")

    # represents the valid values for the campus field for the stops and routes command
    _VALID_CAMPUSES_FOR_STOPS = [stop_name for stop_name in CAMPUS_FULL_NAMES.keys() if stop_name != "nb"]
    _VALID_CAMPUSES_FOR_ROUTES = ["nb", "nk", "cn"]

    # represents the mapping of a unique index to unique stop and route ID's and their names
    _STOPS_INTERNAL_MAPPING = [("4229492", "College Avenue Student Center"),
                               ("4229496", "Student Activities Center Northbound"),
                               ("4229500", "Stadium"), ("4229504", "Werblin Back Entrance"),
                               ("4229508", "Hill Center (NB)"),
                               ("4229512", "Science Building"), ("4229516", "Library of Science"),
                               ("4229520", "Busch Suites"),
                               ("4229524", "Busch Student Center"), ("4229528", "Buell Apartments"),
                               ("4229532", "New Brunswick Train Station-George Street stop"),
                               ("4229536", "New Brunswick Train Station-Somerset Street stop"),
                               ("4229538", "Red Oak Lane"),
                               ("4229542", "Food Sciences Building"), ("4229546", "Katzenbach"),
                               ("4229550", "College Hall"),
                               ("4229554", "Northbound Public Safety Building on George Street"),
                               ("4229558", "Zimmerli Arts Museum"), ("4229562", "Werblin Main Entrance"),
                               ("4229566", "Davidson Hall"), ("4229570", "Livingston Plaza"),
                               ("4229574", "Livingston Student Center"), ("4229576", "Quads"),
                               ("4229578", "Allison Road Classrooms"), ("4229582", "Bravo Supermarket"),
                               ("4229584", "Colony House"), ("4229588", "Rockoff Hall - 290 George Street"),
                               ("4229592", "Southbound Public Safety Building on George Street"),
                               ("4229596", "Lipman Hall"),
                               ("4229600", "Biel Road"), ("4229604", "Henderson"), ("4229608", "Gibbons"),
                               ("4229612", "George Street Northbound at Liberty Street"),
                               ("4229616", "George Street Northbound at Paterson Street"), ("4229620", "Scott Hall"),
                               ("4229624", "Nursing School"), ("4229626", "Visitor Center"), ("4229630", "Golden Dome"),
                               ("4229634", "180 W Market St"), ("4229636", "Bergen Building"),
                               ("4229638", "Blumenthal Hall"),
                               ("4229640", "Boyden Hall"), ("4229642", "Boyden Hall (Arrival)"), ("4229644", "CLJ"),
                               ("4229646", "Clinical Academic Building"), ("4229648", "Dental School"),
                               ("4229650", "ECC"),
                               ("4229652", "Frank E. Rodgers Blvd and Cleveland Ave"), ("4229654", "Hospital"),
                               ("4229656", "Harrison Ave & Passaic Ave"), ("4229658", "ICPH"),
                               ("4229660", "Kearny Ave & Dukes St."), ("4229662", "Kearny Ave and Bergen Ave"),
                               ("4229664", "Kearny Ave and Midland Ave"), ("4229666", "Kearny Ave and Quincy St"),
                               ("4229668", "Kmart"), ("4229670", "Medical School"),
                               ("4229672", "Medical School (Arrival)"),
                               ("4229674", "NJIT"), ("4229676", "Penn Station"), ("4229678", "Physical Plant"),
                               ("4229680", "RBHS Piscataway Hoes Lane"),
                               ("4229682", "RBHS Piscataway Hoes Lane (hidden arrival)"), ("4229684", "ShopRite"),
                               ("4229686", "University North"), ("4229688", "Washington Park"), ("4229690", "Broad St"),
                               ("4229692", "New Street"),
                               ("4229694", "Public Safety Building on Commercial Southbound"),
                               ("4229696", "Student Activities Center Southbound"),
                               ("4229698", "George Street Southbound at Paterson Street"),
                               ("4230628", "Livingston Health Center"), ("4231636", "Hill Center (SB)"),
                               ("4231784", "City Lot 15"), ("4231786", "City Lot 16"),
                               ("4231788", "Law School (5th Street Under the Law Bridge)"),
                               ("4231790", "Nursing and Science Building [NSB]"),
                               ("4231792", "Business and Science Building [BSB]")]
    _ROUTES_INTERNAL_MAPPING = [("4012660", "Knight Mover 1"), ("4012662", "Knight Mover 2"), ("4012616", "Route A"),
                                ("4012618", "Route B"), ("4012620", "Route C"), ("4012622", "Route RBHS"),
                                ("4012624", "Route EE"), ("4012626", "Route F"), ("4012628", "Route H"),
                                ("4012630", "Route LX"),
                                ("4012632", "Route REXB"), ("4012634", "Route REXL"),
                                ("4012636", "Route New BrunsQuick 1 Shuttle"),
                                ("4012638", "Route New BrunsQuick 2 Shuttle"),
                                ("4012640", "Newark Penn Station"), ("4012642", "Newark Campus Connect"),
                                ("4012644", "Newark Kearny"), ("4012646", "Newark Penn Station Express"),
                                ("4012648", "Newark Campus Connect Express"), ("4012650", "Route Weekend 1"),
                                ("4012652", "Route Weekend 2"), ("4012654", "Route All Campuses"),
                                ("4012656", "Newark Run Run Express"), ("4012658", "Newark Run Run"),
                                ("4012664", "Summer 1"),
                                ("4012666", "Summer 2"), ("4012668", "Weekend 1"), ("4012670", "Weekend 2"),
                                ("4013328", "Camden Shuttle")]

    # represents the dictionary of mapping stop and route ID to the bot's internal ID
    _STOPS_ID_MAPPING = {"4229492": "0", "4229496": "1", "4229500": "2", "4229504": "3", "4229508": "4", "4229512": "5",
                         "4229516": "6", "4229520": "7", "4229524": "8", "4229528": "9", "4229532": "10",
                         "4229536": "11", "4229538": "12", "4229542": "13", "4229546": "14", "4229550": "15",
                         "4229554": "16", "4229558": "17", "4229562": "18", "4229566": "19", "4229570": "20",
                         "4229574": "21", "4229576": "22", "4229578": "23", "4229582": "24", "4229584": "25",
                         "4229588": "26", "4229592": "27", "4229596": "28", "4229600": "29", "4229604": "30",
                         "4229608": "31", "4229612": "32", "4229616": "33", "4229620": "34", "4229624": "35",
                         "4229626": "36", "4229630": "37", "4229634": "38", "4229636": "39", "4229638": "40",
                         "4229640": "41", "4229642": "42", "4229644": "43", "4229646": "44", "4229648": "45",
                         "4229650": "46", "4229652": "47", "4229654": "48", "4229656": "49", "4229658": "50",
                         "4229660": "51", "4229662": "52", "4229664": "53", "4229666": "54", "4229668": "55",
                         "4229670": "56", "4229672": "57", "4229674": "58", "4229676": "59", "4229678": "60",
                         "4229680": "61", "4229682": "62", "4229684": "63", "4229686": "64", "4229688": "65",
                         "4229690": "66", "4229692": "67", "4229694": "68", "4229696": "69", "4229698": "70",
                         "4230628": "71", "4231636": "72", "4231784": "73", "4231786": "74", "4231788": "75",
                         "4231790": "76", "4231792": "77"}
    _ROUTES_ID_MAPPING = {"4012660": "0", "4012662": "1", "4012616": "2", "4012618": "3", "4012620": "4",
                          "4012622": "5", "4012624": "6", "4012626": "7", "4012628": "8", "4012630": "9",
                          "4012632": "10", "4012634": "11", "4012636": "12", "4012638": "13", "4012640": "14",
                          "4012642": "15", "4012644": "16", "4012646": "17", "4012648": "18", "4012650": "19",
                          "4012652": "20", "4012654": "21", "4012656": "22", "4012658": "23", "4012664": "24",
                          "4012666": "25", "4012668": "26", "4012670": "27", "4013328": "28"}

    def __init__(self, client):
        self.client = client

    # command to retrieve a list of stops for a given campus
    # the default campus (given that no campus is provided), College Avenue is used
    @commands.command()
    async def Stops(self, ctx, campus=None):

        # starts by first checking if the campus value provided is valid
        if campus not in Busing._VALID_CAMPUSES_FOR_STOPS:
            # creates an embed to output the error info
            embed = discord.Embed(title="Stops", description="", color=0xff1300)
            # if the provided campus is invalid, an error is sent back
            embed.add_field(name="**ERROR**", value=f"Please provide a campus to pull stops from. It has to be "
                                                    f"one of {Busing._VALID_CAMPUSES_FOR_STOPS}\n"
                                                    f"nk = newark stops\n"
                                                    f"cn = camden stops\n"
                                                    f"li = livingston stops\n"
                                                    f"bu = busch stops\n"
                                                    f"cd = cook douglas stops\n"
                                                    f"ca = college ave stops",
                            inline=False)

        else:
            # creates an embed to output the info fetched from the API
            embed = discord.Embed(title="Stops", description="", color=0xff1300)

            # otherwise, a request is made to the API to fetch the bus stops, using the url, required headers, and the
            # required and optional parameters
            response = requests.get(url=Busing._STOPS_API_URL, headers=API_REQUEST_HEADERS,
                                    params=params_append_coords(campus))

            # once the response comes back from the API, the status_code is checked to see if it was successful
            if response.status_code == requests.codes.ok:
                # if the request was successful, the data is parsed to filter only the name field, and then
                # all the stops are concatenated using a new line character to be set into the embed
                stop_names = "\n".join(
                    [("[" + Busing._STOPS_ID_MAPPING[stop_info["stop_id"]] + "] " + stop_info["name"]) for stop_info in
                     response.json()["data"]])

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
    async def Routes(self, ctx, campus=None):
        # first an embed is created to send the routes back to the server
        embed = discord.Embed(title="Routes", description="", color=0xff1300)

        # the campus is validated
        if campus not in Busing._VALID_CAMPUSES_FOR_ROUTES:
            # if its invalid, a list of valid campuses to retrieve routes is attached to the embed
            embed.add_field(name="**ERROR**", value=f"Please provide a school to pull routes from. It has to be "
                                                    f"one of {Busing._VALID_CAMPUSES_FOR_ROUTES}\n"
                                                    f"nk = newark routes\n"
                                                    f"cn = camden routes\n"
                                                    f"nb = new brunswick routes"
                            ,
                            inline=False)
        else:
            # otherwise, a request is made to the API to fetch the list of routes for the provided campus
            response = requests.get(url=Busing._ROUTES_API_URL, headers=API_REQUEST_HEADERS,
                                    params=params_append_coords(campus))

            # the response status code is checked to verify if the request was successful
            if response.status_code == requests.codes.ok:
                # if the request was successful, the relevant data from the response is extracted
                # the data is further filtered to only include the active one"s
                route_names = "\n".join(
                    [("[" + Busing._ROUTES_ID_MAPPING[route_info["route_id"]] + "] " + route_info["long_name"]) for
                     route_info in response.json()["data"][API_AGENCIES] if
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
    async def Bus(self, ctx, stop=-1, route=-1):
        # first an embed is created to convey the arrival estimates back to the server
        embed = discord.Embed(title="Arrival Times", description="", color=0xff1300)

        if (stop < 0 or stop >= len(self._STOPS_INTERNAL_MAPPING)) and (
                route < 0 or route >= len(self._ROUTES_INTERNAL_MAPPING)):
            embed = discord.Embed(title="**ERROR**", description="Please provide a correct value for both the stop "
                                                                 "and route.\n To find the number that represents "
                                                                 "a specific stop please do r!stops [school]."
                                                                 "\n To find the number for a specific route do "
                                                                 "r!routes [campus]."
                                  , color=0xff1300)
            await ctx.send(embed=embed)
            return

        # validates that the stop internal ID provided is within the bot's recognized bounds
        if stop < 0 or stop >= len(self._STOPS_INTERNAL_MAPPING):
            embed.add_field(name="**ERROR**", value=f"Please provide a correct value for the stop. It has to be a "
                                                    f"number between 0-{len(self._STOPS_INTERNAL_MAPPING) - 1} (inclusive)",
                            inline=False)
            await ctx.send(embed=embed)
            return
        # validates that the route internal ID provided is within the bot's recognized bounds
        if route < 0 or route >= len(self._ROUTES_INTERNAL_MAPPING):
            embed.add_field(name="**ERROR**", value=f"Please provide a correct value for the route. It has to be a "
                                                    f"number in 0-{len(self._ROUTES_INTERNAL_MAPPING) - 1} (inclusive)",
                            inline=False)
            await ctx.send(embed=embed)
            return
        # fetches the relevant data to make the request from application pre-defined mappings
        stop_data = Busing._STOPS_INTERNAL_MAPPING[stop]
        stop_id = stop_data[0]
        route_data = Busing._ROUTES_INTERNAL_MAPPING[route]
        route_id = route_data[0]

        # makes a request to fetch the arrival estimates for the given route and stop
        response = requests.get(url=Busing._ARRIVAL_ESTIMATES_API_URL, headers=API_REQUEST_HEADERS,
                                params=params_append_stop_and_route(str(stop_id), str(route_id)))

        # checks the status code to determine if the request was successful
        if response.status_code == requests.codes.ok:
            # if its successful, the data is parsed as JSON and extracted
            stop_name = stop_data[1]
            route_name = route_data[1]
            response_data = response.json()["data"]
            times_str = ""
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
            # all the arrival times are finally added as a field value
            embed.add_field(name=f"'{route_name}' buses arriving at {stop_name} in: ", value=times_str, inline=False)
        else:
            # otherwise, if the request failed, error is attached to the embed instead
            attach_api_error(embed=embed, err_code=response.status_code, err_type=response.reason,
                             err_msg=response.text)
        # the embed created with the relevant data is sent back to the server
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Busing(client))
    return
