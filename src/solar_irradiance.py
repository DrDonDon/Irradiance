from dotenv import load_dotenv
load_dotenv()
import amphora_client as a10a
from amphora_client.rest import ApiException
from amphora_client.configuration import Configuration
import os
import time

import pandas as pd
from pvlib.forecast import ForecastModel
from pvlib.location import Location
import datetime
from pysolar.solar import get_altitude


def get_temps_cloud(id, start_date, end_date, required_data):
    configuration = Configuration()
    configuration.host = "https://beta.amphoradata.com"
    # Create an instance of the auth API class
    auth_api = a10a.AuthenticationApi(a10a.ApiClient(configuration))
    token_request = a10a.TokenRequest(username=os.getenv('username'), password=os.getenv('password') )

    try:
        # Gets a token
        t1_start = time.perf_counter()
        res = auth_api.authentication_request_token(token_request = token_request )
        t1_stop = time.perf_counter()
        print("Elapsed time:", t1_stop - t1_start) # print performance indicator
        configuration.api_key["Authorization"] = "Bearer " + res

        amphora_api = a10a.AmphoraeApi(a10a.ApiClient(configuration))
        print(f'Getting signals for: {amphora_api.amphorae_read(id).name}')
        signals = amphora_api.amphorae_get_signals(id)
        properties=list((s._property for s in signals))
        print(properties)

        ts_api = a10a.TimeSeriesApi(a10a.ApiClient(configuration)) # the API for interacting with time series
        # Create a DateTimeRange to describe over what period we want data.
        time_range = a10a.DateTimeRange(_from = start_date, to= end_date)


        # Create a variable object for getting temperature data
        temperatureVariable = a10a.NumericVariable( kind="numeric",
            value=a10a.Tsx(tsx="$event.temperature"),
            aggregation=a10a.Tsx("avg($value)"))
        get_series = a10a.GetSeries([id], search_span= time_range, inline_variables={"temperature": temperatureVariable})
        time_series_data = ts_api.time_series_query_time_series( a10a.QueryRequest(get_series= get_series))
        print(f'Got {len(time_series_data.timestamps)} datapoints and {len(time_series_data.properties)} properties')
        # access the data in time_series_data.properties
        print("-----------")
        temp_values = next(value for value in time_series_data.properties if value.name == 'temperature')


        # Create a variable object for getting cloudCover data
        cloudCoverVariable = a10a.NumericVariable( kind="numeric",
            value=a10a.Tsx(tsx="$event.cloudCover"),
            aggregation=a10a.Tsx("avg($value)"))
        get_series = a10a.GetSeries([id], search_span= time_range, inline_variables={"cloudCover": cloudCoverVariable})
        time_series_data = ts_api.time_series_query_time_series( a10a.QueryRequest(get_series= get_series))
        print(f'Got {len(time_series_data.timestamps)} datapoints and {len(time_series_data.properties)} properties')
        # access the data in time_series_data.properties
        print("-----------")
        cloudCover_values = next(value for value in time_series_data.properties if value.name == 'cloudCover')


        wtVar = a10a.NumericVariable(kind="numeric",
            value=a10a.Tsx(tsx="$event.wt"),
            aggregation=a10a.Tsx("avg($value)"))

        get_series = a10a.GetSeries([id], search_span= time_range, inline_variables={"wt": wtVar})
        time_series_data = ts_api.time_series_query_time_series( a10a.QueryRequest(get_series= get_series))

        wt_values = next(value for value in time_series_data.properties if value.name == 'wt')

        #create dictionary of signals, with timestamp: [temp, cloud_cover] for each entry if both required
        temp_cloud_dict = {}
        wt_dict = {}

        for i in range(len(temp_values.values)):
            #update the dictionary with the value for the most recent write_time
            #and override wt_dict entries if so
            if time_series_data.timestamps[i] not in temp_cloud_dict.keys() or \
            wt_values.values[i] > wt_dict[time_series_data.timestamps[i]]:
                if required_data == 'both':
                    temp_cloud_dict[time_series_data.timestamps[i]] = [temp_values.values[i], cloudCover_values.values[i]]
                elif required_data == 'cloud_cover':
                    temp_cloud_dict[time_series_data.timestamps[i]] = cloudCover_values.values[i]
                elif required_data == 'temperature':
                    temp_cloud_dict[time_series_data.timestamps[i]] = temp_values.values[i]
                else:
                    raise ValueError("required_data must be 'both', 'temperature' or 'cloud_cover'")
                wt_dict[time_series_data.timestamps[i]] = wt_values.values[i]

    except ApiException as e:
        print("Exception when calling API: %s\n" % e)

    return temp_cloud_dict


def get_signals(weather_amphora_id, lat, long, timezone, end_date=datetime.datetime.now(), date_range=3):

    start_date = end_date-datetime.timedelta(date_range)
    temp_cloud_dict = get_temps_cloud(weather_amphora_id, start_date, end_date, 'both')

    signals = []

    for time,value in temp_cloud_dict.items():

        #value is a tuple of [temp, cloud]\
        temp = float(value[0])
        cloud_cover = float(value[1])
        #get the solar zenith angle & altitude_angle
        altitude_angle = get_altitude(lat, long, time)
        zenith_angle = 90 - altitude_angle

        fm = ForecastModel('haurwitz', 'haurwitz', 'haurwitz')
        model_location = Location(lat, long, timezone)
        fm.location = model_location
        cloud_series = pd.Series(cloud_cover, index=[time])
        irradiance = fm.cloud_cover_to_irradiance_liujordan(cloud_series)['ghi'][0]

        s = {'t': time, 'temperature': temp, 'solarZenithAngle': zenith_angle, 'ghi': irradiance, 'cloudCover': cloud_cover}
        signals.append(s)

    print('Sending signals: ')
    print(signals)

    return signals
