import requests
import datetime
from trip import Trip
import json
from config import Config
config = Config()


class NetworkError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# The following function uses an http cache of the MQTT broker used to
# relay the real-time positioning and other data. The real broker can be
# found on host mqtt.hsl.fi (port 1883) and the topic is the same
# (/hfp/journey/..) as in the http cache. The http cache is updated ~ every
# 20 seconds. The MQTT broker gets real-time data.
def get_rt_data(veh_id='', line=0):
    """
    Fetches real time data from the HSL api. If line is the only parameter
    specified, all real time trip data for the route number will be returned.
    If the vehicle id is specified, the result will be an array containing
    the single dict containing trip data (current or next if in between trips)
    for the vehicle in question.
    :param veh_id: The unique vehicle-specific id
    :param line: The route number of the vehicle is running
    :return: A list of dicts with real time data for each vehicle. In case of
        invalid vehicle id or route number an empty array is returned.
    """
    a = []  # There will be multiple Trips for every route.
    r = requests.get(config.RT_API_URL + (veh_id + "/" if veh_id else ""))
    r.raise_for_status()
    o = r.json()
    for k in o.keys():
        fields = k.split('/')
        if veh_id != fields[4] and line != fields[5]:
            continue
        nxt = fields[9]
        route_id = fields[5]
        trip = o[k]["VP"]
        trip["next"] = nxt
        trip["desi"] = trip["line"] = route_id
        trip["dir"] = str(int(trip["dir"]) - 1)
        a.append(trip)
    return a


def hook(dct):
    # Flattens the dict.
    if 'data' in dct:
        return dct["data"]
    elif 'fuzzyTrip' in dct:
        return dct["fuzzyTrip"]
    return dct


def get_graphql_data(dct):
    """
    Fetches the GraphQL data for the current trip from the HSL GraphQL API.
    The trip must be populated with real time data from HSL, which is used
    to make a GraphQL query.
    :param dct: A dictionary containing real time trip data
    :return: The dictionary updated with GraphQL data about the trip.
    :raise: ValueError if the query returns null. This means the query was
    most likely invalid.
    """
    date = Trip.trip_date(dct["tst"])
    start = Trip.secs_past_midnight(dct["start"])
    query = """{{
      fuzzyTrip(route: "HSL:{0}", direction: {1}, date: "{2}", time: {3})
        {{
          gtfsId
          tripHeadsign
          stops
          {{
            code
            gtfsId
            name
            lat
            lon
          }}
          route
          {{
            longName
          }}
          geometry
        }}
    }}""".format(dct["line"], dct["dir"], date, start)
    headers = {'Content-type': "application/graphql"}
    r = requests.post(config.HSL_API, data=query, headers=headers)
    r.raise_for_status()    # Let the controller handle that
    d = json.loads(r.text, object_hook=hook)
    if d is not None:
        dct.update(d)
    else:
        raise NetworkError("Data not received from GraphQL API")
    return dct


def get_trip_data(veh):
    a = get_rt_data(veh_id=veh)
    if not a:
        raise NetworkError("No realtime data for vehicle \"%s\"" % veh)
    return get_graphql_data(a[0])