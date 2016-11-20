import paho.mqtt

class NetworkHandler:
    def getCurrentVehicleData(trip):
        data = this.getHSLRealTimeApiData(trip.veh)
        data = this.parseHSLRealTimeData(data)
        trip.updatePosition([data.long, data.lat], data.nextStopID != None? "HSL:" + data.nextStopId: data.nextStopId)

    def getHSLRealTimeAPIData(vehicleID):
        url = RT_API_URL + (vehicleID? vehicleID + "/": "")
        # Tee http-pyyntö
        return responsetext

    def getActiveTripsByRouteNum(route):
        a = this.getHSLRealTimeAPIData('')
        b = this.parseData(a, None, route)
        this.getAll(b)

    def parseData(data, filterTest, str)
        a = []
        tmp = 