from dotenv import load_dotenv
load_dotenv(verbose=True)

import os
import json
import amphora_client

from src.towns import town_info
from src.operations import create_or_update_amphorae, upload_signals_to_amphora
from src.solar_irradiance import get_signals
from src.mapping import ghi_save, ghi_load
from src.signals import signals

towns = town_info()
ghi_locations = dict()
location_infos = dict()
# check we have all the amphora we need
for key,value in towns.items():
    store = dict()
    location_info = dict()

    code = key
    store[code] = None
    location_info[code] = towns[key]

    ghi_locations.update(store)
    location_infos.update(location_info)

amphora_map = ghi_load()

ghi_locations.update(amphora_map)
print(ghi_locations)

#create new Amphorae as necessary
new_store = create_or_update_amphorae(ghi_locations, location_infos)
ghi_save(new_store)

for postcode, amphora_id in new_store.items():
    info_dict = towns[postcode]
    signals = get_signals(info_dict['weather_id'], info_dict['lat'],
        info_dict['long'], info_dict['timezone'])

    upload_signals_to_amphora(amphora_id, signals)
