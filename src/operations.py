from dotenv import load_dotenv
load_dotenv()
import amphora_client
from amphora_client.rest import ApiException
from amphora_client.configuration import Configuration
import os
from src.signals import signals

import datetime
from pvlib.forecast import ForecastModel
from pvlib.location import Location

def upload_signals_to_amphora(irradiation_amphora_id, signals):

    #upload data to amphora data website
    configuration = Configuration()
    auth_api = amphora_client.AuthenticationApi(amphora_client.ApiClient(configuration))
    token_request = amphora_client.TokenRequest(username=os.getenv('username'), password=os.getenv('password'))

    try:
        # Gets a token
        res = auth_api.authentication_request_token(token_request = token_request)
        configuration.api_key["Authorization"] = "Bearer " + res
        # create an instance of the Users API, now with Bearer token
        users_api = amphora_client.UsersApi(amphora_client.ApiClient(configuration))
        me = users_api.users_read_self()
        print(me)
    except ApiException as e:
        print("Exception when calling AuthenticationAPI: %s\n" % e)

    amphora_api = amphora_client.AmphoraeApi(amphora_client.ApiClient(configuration))

    try:
        print(signals)
        amphora_api.amphorae_signals_upload_signal_batch(irradiation_amphora_id, request_body = signals)

    except ApiException as e:
        print("Exception when calling AmphoraeApi: %s\n" % e)


def create_or_update_amphorae(amphora_map, location_info):
    # LOAD
    configuration = Configuration()

    # Create an instance of the Authentication class
    auth_api = amphora_client.AuthenticationApi(amphora_client.ApiClient(configuration))
    token_request = amphora_client.TokenRequest(username=os.getenv('username'), password=os.getenv('password'))

    new_map = dict()
    try:
        print("Logging in")
        token = auth_api.authentication_request_token(token_request = token_request)
        configuration.api_key["Authorization"] = "Bearer " + str(token)
        print("Logged in")
        client=amphora_client.ApiClient(configuration)
        amphora_api = amphora_client.AmphoraeApi(client)
        #keys are postcodes
        for key in amphora_map:
            id = amphora_map[key]
            if(id == None):
                # we have to create an Amphora
                ghiloc = location_info[key]
                locname = ghiloc['name']
                print(f'Creating new Amphora for location {locname}')
                # create the details of the Amphora
                name = 'Solar Irradiance GHI: ' + ghiloc['name'] + ' (' + ghiloc['state'] + ')'
                desc = 'Calculated data, from ' + ghiloc['name'] + \
                    '. PostCode: ' + str(key) + '\r\n' + \
                    'Properties include: \r\n- temperature (degrees C)\r\n' + \
                    '- Solar Zenith Angle\r\n- Global Horizontal Irradiance (W/m^2)\r\n' + \
                    '- Cloud Cover (%)\r\nTemperature and cloud cover signals supplied by Weatherzone'
                labels = 'Weather,forecast,solar,timeseries'

                #TODO: add terms_and_conditions_id when it's on the website
                #terms_and_conditions_id = ''


                dto = amphora_client.CreateAmphora(name=name, description=desc, price=0, lat=ghiloc['lat'], lon=ghiloc['long'], labels=labels)

                res = amphora_api.amphorae_create(create_amphora=dto)
                # now create the signals
                print("Creating Signals")
                for s in signals():
                    amphora_api.amphorae_signals_create_signal(res.id, signal=s)

                new_map[key] = res.id
            else:
                a = amphora_api.amphorae_read(id)
                print(f'Using existing amphora: {a.name}')
                new_map[key] = id
                existing_signals = amphora_api.amphorae_signals_get_signals(id)
                if(len(existing_signals) > 0):
                    print('Signals exist already')
                else:
                    print('Adding signals')
                    for s in signals():
                        amphora_api.amphorae_signals_create_signal(id, signal= s)

    except ApiException as e:
        print("Error Create or update amphorae: %s\n" % e)
        raise e

    return new_map
