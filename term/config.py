import configparser


class Config:
    """
    Loads data from the config.ini file
    """
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')

        # API paths
        self.STOP_API = config.get('API', 'STOP_API')
        self.RT_API_URL = config.get('API', 'RT_API_URL')
        self.HSL_API = config.get('API', 'HSL_API')
        self.MQTT_BROKER = config.get('API', 'MQTT_BROKER')
        self.MQTT_CHANNEL = config.get('API', 'MQTT_CHANNEL')

        # Other values
        self.TEST_VEH_ID = config.get('Others', 'TEST_VEH_ID')
        self.DEBUG_MODE = config.get('Others', 'DEBUG_MODE')
        self.RPI_MODE = config.get('Others', 'RPI_MODE')
        self.UPDATE_INTERVAL = config.get('Others', 'UPDATE_INTERVAL')
        self.DEVIATION = config.get('Others', 'DEVIATION')
