import requests
import pprint
import shelve
from db.storage import persist_schedule,  load_schedule, load_tv_channels
from routes.channels import _set_channel
from collections import OrderedDict
from datetime import datetime

#returns schedule dictionary for all upcoming fixtures and events
def obtain_schedule():
    #URL = "https://sportsyear.com.au/api/v1/fixtures/search?preset=next_1_hours&inCalendars=f1a639ff7134f1e783b787968e5cf2dfd02880d4075abbb2b55a92c0907652a3&startingAndEnding=1&includeBroadcasting=1&ac=0"
    URL = "https://sportsyear.com.au/api/v1/fixtures/search?preset=next_24_hours&inCalendars=53b2554ac7ded01572467f4cf88128e3771d8c4646f6956a21e8199a6d221359&startingAndEnding=1&includeBroadcasting=1&ac=0"
    r = requests.get(url = URL)
    data = r.json()
    #pprint.pprint(data)
    channels_info = {}

    for fixture in data['entities']['fixtures']['byId']:
        channels_info[fixture] =  {}   
        channel_id = data['entities']['channels']['broadcastingFixture'][fixture][0]
        channel_name = data['entities']['channels']['byId'][str(channel_id)]['apiCode']
        channels_info[fixture].update({'channel_name':channel_name})

        channels_info[fixture].update({'channel_number':channel_id})

        startUTC = data['entities']['fixtures']['byId'][fixture]['startDateTimeUTC']
        channels_info[fixture].update({'start':startUTC})

        endUTC = data['entities']['fixtures']['byId'][fixture]['endDateTimeUTC']
        channels_info[fixture].update({'end':endUTC})
        
        rank = data['entities']['fixtures']['byId'][fixture]['ranking']   
        channels_info[fixture].update({'ranking':rank})

    ordered_channels_info = OrderedDict(sorted(channels_info.items(), key=lambda kv: kv[1]['ranking'],reverse=True))
    #print(ordered_channels_info)
    persist_schedule(ordered_channels_info)
    print("Schedule updated on database")
    return ordered_channels_info

#returns a dictionary of channels to be played at the present instance
def channel_automation():
    #pprint.pprint(channel_data)
    currentDateTimeUTC = datetime.utcnow().replace(second=0,microsecond=0).isoformat() + 'Z'
    channel_data = load_schedule()
    #pprint.pprint(channel_data)

    channel_count = 0
    for channel in channel_data:
        channel_count +=1
        if currentDateTimeUTC > channel_data[channel]['end']:
            del channel_data[channel]
    persist_schedule(channel_data)
    pprint.pprint(channel_data)
    print('successfully removed any finishes fixtures')

    #db = shelve.open('db\storage')
    #data = db['store']['client_key']
    #key= data
    #pprint.pprint(key)

    db = shelve.open('db\storage')
    tvs = db['scan']
    #print("uuid: ",pprint.pprint(tvs))

    for channel in channel_data:
        channel_id = channel_data[channel]['channel_number']
        pprint.pprint(channel_id)
        for tv_id in tvs:
            #print(tv_id)
            _set_channel(channel_id,tv_id)

    #print(channel_data)
    return channel_data

