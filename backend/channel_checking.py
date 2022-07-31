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

    chan_dic = {}
    for fix in data['entities']['fixtures']['byId']:
        print('hello')
        chan_dic[fix] = {
            'channel_name' : data['entities']['channels']['byId'][str(data['entities']['channels']['broadcastingFixture'][fix][0])]['apiCode'],
            'channel_number' : data['entities']['channels']['broadcastingFixture'][fix][0],
            'end' : data['entities']['fixtures']['byId'][fix]['endDateTimeUTC'],    
            'ranking' : data['entities']['fixtures']['byId'][fix]['ranking'],    
            'start' : data['entities']['fixtures']['byId'][fix]['startDateTimeUTC']    
        }
    print('new fixture')
   
    ordered_channels_info = dict(OrderedDict(sorted(chan_dic.items(), key=lambda kv: kv[1]['ranking'],reverse=True)))
    #print(ordered_channels_info)
    persist_schedule(ordered_channels_info)
    print("schedule obtained on database")
    pprint.pprint(ordered_channels_info)
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

    print('db schedule checked')

    db = shelve.open('db\storage')
    tvs = list(db['scan'])
    print("uuid: ")

    channel_num_list = []
    for channel in channel_data:
        channel_num_list.append(channel_data[channel]['channel_number'])    
    print(channel_num_list)
    print('------------------------------------------------------------------------------')

    #case 1: if #channels = #tvs -> just set 1 to 1
    if len(channel_num_list) is len(tvs):
        for i in range(len(channel_num_list)):
             print("case1: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
             _set_channel(str(channel_num_list[i]),tvs[i])    
    #case 2: if #channels < #tvs -> have the channels wrap again 
    elif len(channel_num_list) < len(tvs):
        for i in range(len(channel_num_list)):
             print("case 2: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
             _set_channel(str(channel_num_list[i]),tvs[i])    
    #case 3: if channels > tvs -> have set channels on tvs and exit loop
    elif len(channel_num_list) > len(tvs):
         for i in range(len(tvs)):
             print("case 3: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
             _set_channel(str(channel_num_list[i]),tvs[i])     

    return channel_data
