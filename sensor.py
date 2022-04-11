from homeassistant import core
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .const import (
    CONF_STATIONID
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_STATIONID): cv.string
    }
)

import logging
_LOGGER = logging.getLogger(__name__) 

import requests
from datetime import datetime, timedelta

SCAN_INTERVAL = timedelta(minutes=60)

def setup_platform(hass: core.HomeAssistant, config: dict, add_entities, discovery_info=None) -> bool:
    """Set up the GasBuddy component."""

    r = requests.post("https://www.gasbuddy.com/gaspricemap/station", data={'id': config[CONF_STATIONID], 'fuelTypeId': '1'})

    # Get dictionary to convert fuel types to names
    fuels = {}
    for fuel in r.json()['station']['APIFuel']:
        if fuel['Available']:
            fuels[str(fuel['Id'])] = fuel['DisplayName']

    sensors = []
    for fuel in r.json()['station']['Fuels']:
        if str(fuel['FuelType']) in fuels.keys():
            name = fuels[str(fuel['FuelType'])]
            _LOGGER.debug(f"Setting up GasBuddySensor {r.json()['station']['Name']+' - '+str(config[CONF_STATIONID])}")
            sensors.append(GasBuddySensor(str(config[CONF_STATIONID])+"_"+name.lower(), r.json()['station']['Name']+" - "+str(config[CONF_STATIONID])+" - "+name, config[CONF_STATIONID], fuel['FuelType']))

    add_entities(sensors, True)

class GasBuddySensor(Entity):
    def __init__(self, device, label, stationid, fueltype):
        self.device = device
        self._state = None
        self._available = True
        self.label = label
        self.stationid = stationid
        self.fueltype = fueltype
        self.attrs = None

    @property
    def name(self):
        return "GasBuddy "+self.label

    @property
    def unique_id(self):
        return "gasbuddy_"+self.device

    @property
    def available(self):
        return self._available

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self.attrs

    def update(self):
        r = requests.post("https://www.gasbuddy.com/gaspricemap/station", data={'id': self.stationid, 'fuelTypeId': '1'})
        if r.ok:
            for fuel in r.json()['station']['Fuels']:
                if fuel['FuelType'] == self.fueltype:
                    try:
                        self._state = fuel['CreditPrice']['Amount']
                        self._available = True
                    except:
                        _LOGGER.warning(f"No price found for fuel type {fuel['FuelType']}")
                        self._state = -1
                        self._available = False

                    self.attrs = {
                        'name': r.json()['station']['Name'],
                        'address': r.json()['station']['Address'],
                        'city': r.json()['station']['City'],
                        'state': r.json()['station']['State'],
                        'zipcode': r.json()['station']['ZipCode'],
                        'lat': r.json()['station']['Lat'],
                        'lng': r.json()['station']['Lng'],
                    }

                    try:
                        self.attrs['last_updated'] = datetime.fromtimestamp(float(fuel['CreditPrice']['TimePosted'].split('(')[1].split(')')[0]) / 1000)
                    except:
                        _LOGGER.warning(f"No update time found for fuel type {fuel['FuelType']}")
                        self.attrs['last_updated'] = -1
                        if self._state == -1:
                            self._available = False

