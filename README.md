# GasBuddy Component for Home Assistant (Unofficial)

To find the id for the stations you want to check, go to the GasBuddy map here: https://www.gasbuddy.com/gaspricemap

Find a station and click on the price bubble. A "card" about that station with the price, name, address, etc will be displayed at the top of the map. Click on the name of the station to go to its page, and the station id is at the end of the url. (example: https://www.gasbuddy.com/station/1234567)

After installing this component, add stations to your configuration.yaml in the "sensor:" section as shown below:

```
sensor:
  - platform: gasbuddy
    stationid: 1234567

  - platform: gasbuddy
    stationid: 2345678

  - platform: gasbuddy
    stationid: 3456789
```

After restarting Home Assistant to reload the configuration, search for "GasBuddy" in your Entities list, and you should have a sensor item for each available fuel type at each configured station.