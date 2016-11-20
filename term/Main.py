import NetworkHandler

STOP_API = "http://stop20.herokuapp.com"
RT_API_URL = "http://dev.hsl.fi/hfp/journey/bus/"
HSL_API = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
DEBUG_MODE = True
UPDATE_INTERVAL = 2000

# Initialization
NetworkHandler.init()