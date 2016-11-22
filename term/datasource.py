import requests
from trip import Trip, Geometry

RT_API_URL = "http://dev.hsl.fi/hfp/journey/bus/"
HSL_API = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"


def get_rt_data(veh_id='', line=0):
    """
    Fetches real time data from the HSL api.
    :param veh_id: The unique vehicle id
    :param line: The route number of the vehicle is running
    :return: A list of Trips for each vehicle
    """
    a = []
    r = requests.get(RT_API_URL + (veh_id + "/" if veh_id else ""))
    r.raise_for_status()
    o = r.json()
    for k in o.keys():
        fields = k.split('/')
        if veh_id != fields[4] and line != fields[5]:
            continue
        nxt = fields[9]
        trip = o[k]["VP"]
        trip["next"] = nxt
        t = Trip(trip) # FIXME: handle exceptions
        a.append(t)
    return a


def get_graphql_data(trip):
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
    }}""".format(trip.line, trip.dir, trip.date(), trip.start_in_secs())
    headers = {'Content-type': "application/graphql"}
    r = requests.post(HSL_API, data=query, headers=headers)
    r.raise_for_status() # Let the controller handle that
    d =  r.json()["data"]["fuzzyTrip"]
    if d != None:
        trip.copy_data(d)
    else:
        pass # FIXME: throw exception?
    return trip