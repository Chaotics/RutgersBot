from enum import Enum
from typing import List, Union


class BusingDataType(Enum):
    STOP = 0
    ROUTE = 1

    def __repr__(self):
        return str(self)


class BusingData:
    def __init__(self, internal_id: int, api_id: int, name: str, aliases: List[str]):
        self.internal_id = internal_id
        self.api_id = api_id
        self.name = name
        self.aliases = aliases

    def __repr__(self):
        return self.name

    def __str__(self):
        return f"[{self.internal_id}]  \u200b  {self.name}" + (
            f"  \u200b  ({self.aliases[0]})" if len(self.aliases) > 0 else "")


STOPS_LIST: List[BusingData] = [
    BusingData(internal_id=0, api_id=4229492, name="College Avenue Student Center", aliases=["casc", "rsc"]),
    BusingData(internal_id=1, api_id=4229496, name="Student Activities Center Northbound", aliases=["sac"]),
    BusingData(internal_id=2, api_id=4229500, name="Stadium", aliases=["sm", "hal"]),
    BusingData(internal_id=3, api_id=4229504, name="Werblin Back Entrance", aliases=["wbe"]),
    BusingData(internal_id=4, api_id=4229508, name="Hill Center (NB)", aliases=["hcn", "hlln"]),
    BusingData(internal_id=5, api_id=4229512, name="Science Building", aliases=["sb", "sci"]),
    BusingData(internal_id=6, api_id=4229516, name="Library of Science", aliases=["los", "lsm"]),
    BusingData(internal_id=7, api_id=4229520, name="Busch Suites", aliases=["bs"]),
    BusingData(internal_id=8, api_id=4229524, name="Busch Student Center", aliases=["bsc"]),
    BusingData(internal_id=9, api_id=4229528, name="Buell Apartments", aliases=["ba"]),
    BusingData(internal_id=10, api_id=4229532, name="New Brunswick Train Station-George Street stop", aliases=["trg"]),
    BusingData(internal_id=11, api_id=4229536, name="New Brunswick Train Station-Somerset Street stop",
               aliases=["trs"]),
    BusingData(internal_id=12, api_id=4229538, name="Red Oak Lane", aliases=["rol"]),
    BusingData(internal_id=13, api_id=4229542, name="Food Sciences Building", aliases=["fs", "fsb"]),
    BusingData(internal_id=14, api_id=4229546, name="Katzenbach", aliases=["kh"]),
    BusingData(internal_id=15, api_id=4229550, name="College Hall", aliases=["ch"]),
    BusingData(internal_id=16, api_id=4229554, name="Northbound Public Safety Building on George Street",
               aliases=["psbn"]),
    BusingData(internal_id=17, api_id=4229558, name="Zimmerli Arts Museum", aliases=["zam"]),
    BusingData(internal_id=18, api_id=4229562, name="Werblin Main Entrance", aliases=["wme"]),
    BusingData(internal_id=19, api_id=4229566, name="Davidson Hall", aliases=["dh"]),
    BusingData(internal_id=20, api_id=4229570, name="Livingston Plaza", aliases=["lp"]),
    BusingData(internal_id=21, api_id=4229574, name="Livingston Student Center", aliases=["lsc"]),
    BusingData(internal_id=22, api_id=4229576, name="Quads", aliases=["qs"]),
    BusingData(internal_id=23, api_id=4229578, name="Allison Road Classrooms", aliases=["arc"]),
    BusingData(internal_id=24, api_id=4229582, name="Bravo Supermarket", aliases=["bsu"]),
    BusingData(internal_id=25, api_id=4229584, name="Colony House", aliases=["coh"]),
    BusingData(internal_id=26, api_id=4229588, name="Rockoff Hall - 290 George Street", aliases=["rh"]),
    BusingData(internal_id=27, api_id=4229592, name="Southbound Public Safety Building on George Street",
               aliases=["psbsg"]),
    BusingData(internal_id=28, api_id=4229596, name="Lipman Hall", aliases=["lh"]),
    BusingData(internal_id=29, api_id=4229600, name="Biel Road", aliases=["br"]),
    BusingData(internal_id=30, api_id=4229604, name="Henderson", aliases=["hn"]),
    BusingData(internal_id=31, api_id=4229608, name="Gibbons", aliases=["gs"]),
    BusingData(internal_id=32, api_id=4229612, name="George Street Northbound at Liberty Street", aliases=["gsnl"]),
    BusingData(internal_id=33, api_id=4229616, name="George Street Northbound at Paterson Street", aliases=["gsnp"]),
    BusingData(internal_id=34, api_id=4229620, name="Scott Hall", aliases=["sh"]),
    BusingData(internal_id=35, api_id=4229624, name="Nursing School", aliases=["ns"]),
    BusingData(internal_id=36, api_id=4229626, name="Visitor Center", aliases=["vc"]),
    BusingData(internal_id=37, api_id=4229630, name="Golden Dome", aliases=["gd"]),
    BusingData(internal_id=38, api_id=4229634, name="180 W Market St", aliases=["mas"]),
    BusingData(internal_id=39, api_id=4229636, name="Bergen Building", aliases=["bb"]),
    BusingData(internal_id=40, api_id=4229638, name="Blumenthal Hall", aliases=["blh"]),
    BusingData(internal_id=41, api_id=4229640, name="Boyden Hall", aliases=["boh"]),
    BusingData(internal_id=42, api_id=4229642, name="Boyden Hall (Arrival)", aliases=["bha"]),
    BusingData(internal_id=43, api_id=4229644, name="CLJ", aliases=[]),
    BusingData(internal_id=44, api_id=4229646, name="Clinical Academic Building", aliases=["cab"]),
    BusingData(internal_id=45, api_id=4229648, name="Dental School", aliases=["ds"]),
    BusingData(internal_id=46, api_id=4229650, name="ECC", aliases=[]),
    BusingData(internal_id=47, api_id=4229652,
               name="Frank E. Rodgers Blvd and Cleveland Ave", aliases=["rbca"]),
    BusingData(internal_id=48, api_id=4229654, name="Hospital", aliases=["hl"]),
    BusingData(internal_id=49, api_id=4229656, name="Harrison Ave & Passaic Ave", aliases=["hapa"]),
    BusingData(internal_id=50, api_id=4229658, name="ICPH", aliases=[]),
    BusingData(internal_id=51, api_id=4229660, name="Kearny Ave & Dukes St.", aliases=["kyd"]),
    BusingData(internal_id=52, api_id=4229662, name="Kearny Ave and Bergen Ave", aliases=["kyb"]),
    BusingData(internal_id=53, api_id=4229664, name="Kearny Ave and Midland Ave", aliases=["kym"]),
    BusingData(internal_id=54, api_id=4229666, name="Kearny Ave and Quincy St", aliases=["kyq"]),
    BusingData(internal_id=55, api_id=4229668, name="Kmart", aliases=["kt"]),
    BusingData(internal_id=56, api_id=4229670, name="Medical School", aliases=["ms"]),
    BusingData(internal_id=57, api_id=4229672, name="Medical School (Arrival)", aliases=["msa"]),
    BusingData(internal_id=58, api_id=4229674, name="NJIT", aliases=[]),
    BusingData(internal_id=59, api_id=4229676, name="Penn Station", aliases=["ps"]),
    BusingData(internal_id=60, api_id=4229678, name="Physical Plant", aliases=["pp"]),
    BusingData(internal_id=61, api_id=4229680, name="RBHS Piscataway Hoes Lane", aliases=["phl"]),
    BusingData(internal_id=62, api_id=4229682, name="RBHS Piscataway Hoes Lane (hidden arrival)", aliases=["phla"]),
    BusingData(internal_id=63, api_id=4229684, name="ShopRite", aliases=["se"]),
    BusingData(internal_id=64, api_id=4229686, name="University North", aliases=["un"]),
    BusingData(internal_id=65, api_id=4229688, name="Washington Park", aliases=["wp"]),
    BusingData(internal_id=66, api_id=4229690, name="Broad St", aliases=["bst"]),
    BusingData(internal_id=67, api_id=4229692, name="New Street", aliases=["nes"]),
    BusingData(internal_id=68, api_id=4229694, name="Public Safety Building on Commercial Southbound",
               aliases=["psbsc"]),
    BusingData(internal_id=69, api_id=4229696, name="Student Activities Center Southbound", aliases=["sacs"]),
    BusingData(internal_id=70, api_id=4229698, name="George Street Southbound at Paterson Street", aliases=["gssp"]),
    BusingData(internal_id=71, api_id=4230628, name="Livingston Health Center", aliases=["lhc"]),
    BusingData(internal_id=72, api_id=4231636, name="Hill Center (SB)", aliases=["hcs", "hlls"]),
    BusingData(internal_id=73, api_id=4231784, name="City Lot 15", aliases=["l15"]),
    BusingData(internal_id=74, api_id=4231786, name="City Lot 16", aliases=["l16"]),
    BusingData(internal_id=75, api_id=4231788, name="Law School (5th Street Under the Law Bridge)", aliases=["ls"]),
    BusingData(internal_id=76, api_id=4231790, name="Nursing and Science Building [NSB]", aliases=["nsb"]),
    BusingData(internal_id=77, api_id=4231792, name="Business and Science Building [BSB]", aliases=["bsb"])]
ROUTES_LIST: List[BusingData] = [
    BusingData(internal_id=0, api_id=4012660, name="Knight Mover 1", aliases=["km1"]),
    BusingData(internal_id=1, api_id=4012662, name="Knight Mover 2", aliases=["km2"]),
    BusingData(internal_id=2, api_id=4012616, name="Route A", aliases=["a"]),
    BusingData(internal_id=3, api_id=4012618, name="Route B", aliases=["b"]),
    BusingData(internal_id=4, api_id=4012620, name="Route C", aliases=["c"]),
    BusingData(internal_id=5, api_id=4012622, name="Route RBHS", aliases=["rbhs"]),
    BusingData(internal_id=6, api_id=4012624, name="Route EE", aliases=["ee"]),
    BusingData(internal_id=7, api_id=4012626, name="Route F", aliases=["f"]),
    BusingData(internal_id=8, api_id=4012628, name="Route H", aliases=["h"]),
    BusingData(internal_id=9, api_id=4012630, name="Route LX", aliases=["lx"]),
    BusingData(internal_id=10, api_id=4012632, name="Route REXB", aliases=["rexb"]),
    BusingData(internal_id=11, api_id=4012634, name="Route REXL", aliases=["rexl"]),
    BusingData(internal_id=12, api_id=4012636, name="Route New BrunsQuick 1 Shuttle", aliases=["q1"]),
    BusingData(internal_id=13, api_id=4012638, name="Route New BrunsQuick 2 Shuttle", aliases=["q2"]),
    BusingData(internal_id=14, api_id=4012640, name="Newark Penn Station", aliases=["ps"]),
    BusingData(internal_id=15, api_id=4012642, name="Newark Campus Connect", aliases=["cc"]),
    BusingData(internal_id=16, api_id=4012644, name="Newark Kearny", aliases=["ky"]),
    BusingData(internal_id=17, api_id=4012646, name="Newark Penn Station Express", aliases=["pse"]),
    BusingData(internal_id=18, api_id=4012648, name="Newark Campus Connect Express", aliases=["cce"]),
    BusingData(internal_id=19, api_id=4012650, name="Route Weekend 1", aliases=["w1"]),
    BusingData(internal_id=20, api_id=4012652, name="Route Weekend 2", aliases=["w2"]),
    BusingData(internal_id=21, api_id=4012654, name="Route All Campuses", aliases=["all"]),
    BusingData(internal_id=22, api_id=4012656, name="Newark Run Run Express", aliases=["rre"]),
    BusingData(internal_id=23, api_id=4012658, name="Newark Run Run", aliases=["rr"]),
    BusingData(internal_id=24, api_id=4012664, name="Summer 1", aliases=["s1"]),
    BusingData(internal_id=25, api_id=4012666, name="Summer 2", aliases=["s2"]),
    BusingData(internal_id=26, api_id=4012668, name="Weekend 1", aliases=["end1"]),
    BusingData(internal_id=27, api_id=4012670, name="Weekend 2", aliases=["end2"]),
    BusingData(internal_id=28, api_id=4013328, name="Camden Shuttle", aliases=["csh"])]


def fetch_data_list(query_data_type: BusingDataType) -> List[BusingData]:
    return STOPS_LIST if query_data_type == BusingDataType.STOP else ROUTES_LIST


def find_by_internal_id(query_data_type: BusingDataType, internal_id: int) -> Union[BusingData, None]:
    try:
        return fetch_data_list(query_data_type)[internal_id]
    except IndexError:
        return None


def find_by_api_id(query_data_type: BusingDataType, api_id: int) -> Union[BusingData, None]:
    return next((data for data in fetch_data_list(query_data_type) if data.api_id == api_id), None)


def find_by_name(query_data_type: BusingDataType, name: str) -> Union[BusingData, None]:
    return next((data for data in fetch_data_list(query_data_type) if
                 name.lower() == data.name.lower() or name.lower() in map(str.lower, data.aliases)), None)


def find_bus_data(query_data_type: BusingDataType, search_str: str) -> Union[BusingData, None]:
    search_list = fetch_data_list(query_data_type)
    try:
        parsed_id = int(search_str)
        if parsed_id < len(search_list):
            return find_by_internal_id(query_data_type, parsed_id)
        else:
            return find_by_api_id(query_data_type, parsed_id)
    except ValueError:
        return find_by_name(query_data_type, search_str)
