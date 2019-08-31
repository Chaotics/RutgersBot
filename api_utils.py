from secret import X_RAPIDAPI_KEY

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
CAMPUS_FULL_NAMES = {
    "nb": "New Brunswick",
    "nk": "Newark",
    "cn": "Camden",
    "li": "Livingston",
    "bu": "Busch",
    "cd": "Cook/Douglass",
    "ca": "College Avenue"
}

CAMPUS_COORDINATES = {
    "nb": "40.500820,-74.447398|3500.0",
    "nk": "40.741050,-74.173206|1000.0",
    "cn": "39.948508,-75.122122|1000.0",
    "li": "40.524199,-74.435495|800.0",
    "bu": "40.521196,-74.462281|800.0",
    "cd": "40.521196,-74.462281|1500.0",
    "ca": "40.500823,-74.447407|1000.0"
}


def create_api_url(endpoint):
    return API_URL_PROTOCOL + API_HOST + endpoint + "." + API_RESPONSE_FORMAT


def attach_api_error(embed, err_code, err_type, err_msg):
    embed.add_field(name="**Error (please show this to the server admin)**",
                    value=f"Error Code: {err_code}\nError Type: {err_type}\n"
                          f"Error Message: {err_msg}",
                    inline=False)


def append_campus_coords(campus):
    new_params = API_REQUEST_PARAMS.copy()
    new_params["geo_area"] = CAMPUS_COORDINATES[campus]
    return new_params
