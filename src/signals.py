from amphora_client import Signal

def signals():
    return [
        Signal(_property='description', value_type='String'),
        Signal(_property='temperature', value_type='Numeric'),
        Signal(_property='solarZenithAngle', value_type='Numeric'),
        Signal(_property='cloudCover', value_type='Numeric'),
        Signal(_property='ghi', value_type='Numeric'),
    ]
