# Irradiance

This repository uses the Amphoradata Python SDK to retrieve weatherzone data and perform relevant calculations to calculate Global Horizontal Irradiance at specified locations


### Prerequisites

* Have an Amphora Data account.
* Have Python installed.


### Adding new towns to create Amphorae

First Add a town in the town_info() function in src/towns.py

The 'weather_id' entry should contain the Amphora id of a weather zone Amphora close to the area you would like to add.

It is essential that there already exists a weather Amphora before creating the irradiance one.

Abide by the format of the existing towns, shown below:

```
{'name': 'Mitcham', 'lat': -37.8174, 'long': 145.1938,
    'state': 'VIC', 'timezone': 'Australia/Melbourne',
    'weather_id': '684997e2-61e4-4a90-9ac8-ffabad056e52'}
```

Run index.py

```
python index.py
```

This will automatically create a new Amphora for the location entered from the weatherzone data and save the postcode and new Amphora id in the 'cache.p' file

Commit the updated towns.py and cache.p files to ensure 1 Amphorae is regularly updated
