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
        self.MQTT_SUBSCRIPTION_CHANNEL = config.get('API', 'MQTT_SUBSCRIPTION_CHANNEL')

        # Vehicle specific configuration
        self.VEH_ID = config.get('Vehicle', 'VEH_ID')

        # Other values
        self.DEBUG_MODE = config.get('Others', 'DEBUG_MODE')
        self.UPDATE_INTERVAL = config.get('Others', 'UPDATE_INTERVAL')
        self.DEVIATION = float(config.get('Others', 'DEVIATION'))
