from amphora_client import SignalDto

def signals():
    return [
        SignalDto(_property='description', value_type='String'),
        SignalDto(_property='temperature', value_type='Numeric'),
        SignalDto(_property='solarZenithAngle', value_type='Numeric'),
        SignalDto(_property='cloudCover', value_type='Numeric'),
        SignalDto(_property='ghi', value_type='Numeric'),
    ]
