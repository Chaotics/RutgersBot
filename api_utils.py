from datetime import datetime

import pytz as pytz

from secret import X_RAPIDAPI_KEY

# declares constants necessary to make requests to the API
API_URL_PROTOCOL = "https://"
API_HOST = "transloc-api-1-2.p.rapidapi.com/"
API_KEY = X_RAPIDAPI_KEY
API_AGENCIES = "1323"

API_RESPONSE_FORMAT = "json"
API_REQUEST_HEADERS = {
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": None if not API_KEY else API_KEY
}
API_REQUEST_PARAMS = {
    "agencies": API_AGENCIES
}

# the dictionary of mappings from abbreviated campus names to their expanded forms
CAMPUS_FULL_NAMES = {
    "nb": "New Brunswick",
    "nk": "Newark",
    "cn": "Camden",
    "li": "Livingston",
    "bu": "Busch",
    "cd": "Cook/Douglass",
    "ca": "College Avenue"
}

# the dictionary of mappings from campus names to their coordinates
CAMPUS_COORDINATES = {
    "nb": "40.500820,-74.447398|3500.0",
    "nk": "40.741050,-74.173206|1000.0",
    "cn": "39.948508,-75.122122|1000.0",
    "li": "40.524199,-74.435495|800.0",
    "bu": "40.521196,-74.462281|800.0",
    "cd": "40.521196,-74.462281|1500.0",
    "ca": "40.500823,-74.447407|1000.0"
}

API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


# function to create the API url using the provided endpoint
def create_api_url(endpoint):
    return API_URL_PROTOCOL + API_HOST + endpoint + "." + API_RESPONSE_FORMAT


# function to attach an error to the given embed
def attach_api_error(embed, err_code, err_type, err_msg):
    embed.add_field(name="**Error (please show this to the server admin)**",
                    value=f"Error Code: {err_code}\nError Type: {err_type}\n"
                          f"Error Message: {err_msg}",
                    inline=False)


# function used to append coordinates to the API params using the provided campus
def params_append_coords(campus):
    new_params = API_REQUEST_PARAMS.copy()
    new_params["geo_area"] = CAMPUS_COORDINATES[campus]
    return new_params


# function that attaches the stop and route id as appropriate
# parameters to the required request parameters for the API
def params_append_stop_and_route(stop, route):
    new_params = API_REQUEST_PARAMS.copy()
    new_params["stops"] = stop
    new_params["routes"] = route
    return new_params


# function to convert a datetime string from the API to one
# which can be parsed by the Python date-time library
def convert_api_datetime(datetime_str):
    split_index = datetime_str.rfind(":")
    return datetime.strptime(datetime_str[:split_index] + datetime_str[split_index + 1:],
                             API_DATETIME_FORMAT).astimezone(pytz.utc).replace(tzinfo=None)


def is_data_stale(cached_resource):
    if cached_resource:
        return datetime.utcnow() > cached_resource["expire_datetime"]
    else:
        return True
