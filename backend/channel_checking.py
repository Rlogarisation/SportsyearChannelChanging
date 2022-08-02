import requests
import pprint
import shelve
from db.storage import persist_schedule,  load_schedule, load_tv_channels, ir_load_blaster_data
from routes.channels import _set_channel 
from routes.IR import _ir_set_channel
from collections import OrderedDict
from datetime import datetime

#returns schedule dictionary for all upcoming fixtures and events
def obtain_schedule():
    #URL = "https://sportsyear.com.au/api/v1/fixtures/search?preset=next_1_hours&inCalendars=f1a639ff7134f1e783b787968e5cf2dfd02880d4075abbb2b55a92c0907652a3&startingAndEnding=1&includeBroadcasting=1&ac=0"
    URL = "https://sportsyear.com.au/api/v1/fixtures/search?preset=next_24_hours&inCalendars=53b2554ac7ded01572467f4cf88128e3771d8c4646f6956a21e8199a6d221359&startingAndEnding=1&includeBroadcasting=1&ac=0"
    r = requests.get(url = URL)
    data = r.json()

    chan_dic = {}
    pprint.pprint(data)
    for fix in data['entities']['fixtures']['byId']:

        # print('hello')
        print(fix)
        if (data['entities']['channels']['broadcastingFixture'][fix] == []): continue
        chan_dic[fix] = {
            'channel_name' : data['entities']['channels']['byId'][str(data['entities']['channels']['broadcastingFixture'][fix][0])]['apiCode'],
            'channel_number' : data['entities']['channels']['broadcastingFixture'][fix][0],
            'end' : data['entities']['fixtures']['byId'][fix]['endDateTimeUTC'],    
            'ranking' : data['entities']['fixtures']['byId'][fix]['ranking'],    
            'start' : data['entities']['fixtures']['byId'][fix]['startDateTimeUTC']    
        }
    print('new fixture')

    # Update below to test a custom schedule
    # chan_dic['123456'] = {
    #     'channel_name': '7mate',
    #     'channel_number': 10,
    #     'end': '2022-08-02T12:50:00Z',
    #     'ranking': 200,
    #     'start': '2022-08-02T11:12:00Z'
    # }

    ordered_channels_info = dict(OrderedDict(sorted(chan_dic.items(), key=lambda kv: kv[1]['ranking'],reverse=True)))
    #print(ordered_channels_info)
    persist_schedule(ordered_channels_info)
    print("schedule obtained on database")
    pprint.pprint(ordered_channels_info)
    return ordered_channels_info

# CHANNEL AUTOMATION FOR SMART TVs CHECKS ON TRIGGER
def channel_automation(): 
    currentDateTimeUTC = datetime.utcnow().replace(second=0,microsecond=0).isoformat() + 'Z'
    channel_data = load_schedule()
    channel_change_flag = False
    #remove any outdated fixtures and update on database
    for channel in list(channel_data):
        if currentDateTimeUTC > channel_data[channel]['end']:
            del channel_data[channel]
            channel_change_flag = True
    persist_schedule(channel_data)

    #filter out any channels that have yet to be shown 
    channel_data = load_schedule()
    for channel in list(channel_data):
        if currentDateTimeUTC == channel_data[channel]['start']:
            channel_change_flag = True
        if currentDateTimeUTC < channel_data[channel]['start']:
            del channel_data[channel]
    print('Running Smart Automation, db schedule checked')

    db = shelve.open('db\storage')
    tvs = list(db['scan'])
    channel_num_list = []
    channel_start_list = []
    channel_end_list = []
    for channel in channel_data:
        channel_num_list.append(channel_data[channel]['channel_number'])
        channel_start_list.append(channel_data[channel]['start'])
        channel_end_list.append(channel_data[channel]['end'])
    print(f'Channel Number: {channel_num_list}')
    print(f'Fixture UTC Start Time: {channel_start_list}')
    print(f'Fixture UTC End Time: {channel_end_list}')
    print(f'Current UTC Time: {currentDateTimeUTC}')
    print('------------------------------------------------------------------------------')
    if (channel_change_flag is True):
        #case 1: if #channels = #tvs -> just set 1 to 1
        if len(channel_num_list) is len(tvs):
            for i in range(len(channel_num_list)):
                 print("case1: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
                 _set_channel(str(channel_num_list[i]),tvs[i])
        #case 2: if #channels < #tvs -> have the channels wrap again 
        elif len(channel_num_list) < len(tvs):
            for i in range(len(tvs)):
                 if (i > len(channel_num_list)):
                    _set_channel(str(channel_num_list[i-len(channel_num_list)]),tvs[i-len(channel_num_list)])
                 else :
                    print("case 2: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
                 _set_channel(str(channel_num_list[i]),tvs[i])
        #case 3: if #channels > #tvs -> have set channels on tvs and exit loop
        elif len(channel_num_list) > len(tvs):
             for i in range(len(tvs)):
                 print("case 3: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
                 _set_channel(str(channel_num_list[i]),tvs[i])
    db.close()
    if not channel_num_list:
        print("no scheduled channels at this moment (Wifi)")
    return channel_data

# INITIAL CHANNEL AUTOMATION FOR SMART TVs
def force_channel_automation(): 
    currentDateTimeUTC = datetime.utcnow().replace(second=0,microsecond=0).isoformat() + 'Z'
    channel_data = load_schedule()
    #remove any outdated fixtures and update on database
    for channel in list(channel_data):
        if currentDateTimeUTC > channel_data[channel]['end']:
            del channel_data[channel]
    persist_schedule(channel_data)

    #filter out any channels that have yet to be shown 
    channel_data = load_schedule()
    for channel in list(channel_data):
        if currentDateTimeUTC < channel_data[channel]['start']:
            del channel_data[channel]
        
    print('db schedule checked for Wifi')

    db = shelve.open('db\storage')
    tvs = list(db['scan'])
    db.close()
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
        for i in range(len(tvs)):
            if (i > len(channel_num_list)):
                _set_channel(str(channel_num_list[i-len(channel_num_list)]),tvs[i-len(channel_num_list)])
            else :
                print("case 2: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
                _set_channel(str(channel_num_list[i]),tvs[i])
    #case 3: if #channels > #tvs -> have set channels on tvs and exit loop
    elif len(channel_num_list) > len(tvs):
        for i in range(len(tvs)):
            print("case 3: setting tv with uuid: ",tvs[i]," with channel number: ",channel_num_list[i])
            _set_channel(str(channel_num_list[i]),tvs[i])
    if not channel_num_list:
        print("no scheduled channels at this moment (Wifi)")
    return channel_data

# CHANNEL AUTOMATION FOR IR CHECKS ON TRIGGER
def channel_automation_IR():
    currentDateTimeUTC = datetime.utcnow().replace(second=0,microsecond=0).isoformat() + 'Z'
    channel_data = load_schedule()
    channel_change_flag = False
    #remove any outdated fixtures and update on database
    for channel in list(channel_data):
        if currentDateTimeUTC > channel_data[channel]['end']:
            del channel_data[channel]
            channel_change_flag = True
    pprint.pprint(channel_data)
    persist_schedule(channel_data)

    #filter out any channels that have yet to be shown 
    channel_data = load_schedule()
    for channel in list(channel_data):
        if currentDateTimeUTC == channel_data[channel]['start']:
            channel_change_flag = True
        if currentDateTimeUTC < channel_data[channel]['start']:
            del channel_data[channel]
    print('Running IR Automation, db schedule checked')

    #db = shelve.open('db\storage')
    #tvs = list(db['scan'])

    channel_num_list = []
    channel_start_list = []
    channel_end_list = []
    for channel in channel_data:
        channel_num_list.append(channel_data[channel]['channel_number'])
        channel_start_list.append(channel_data[channel]['start'])
        channel_end_list.append(channel_data[channel]['end'])
    print(f'Channel Number: {channel_num_list}')
    print(f'Fixture UTC Start Time: {channel_start_list}')
    print(f'Fixture UTC End Time: {channel_end_list}')
    print(f'Current UTC Time: {currentDateTimeUTC}')
    print('------------------------------------------------------------------------------')
    ir_tvs = ir_load_blaster_data()
    ip_list = []
    port_list = []
    type_list = []
    for tv in ir_tvs:
         ip_list.append(ir_tvs[tv]['ip_address'])
         port_list.append(ir_tvs[tv]['port'])   
         type_list.append(ir_tvs[tv]['type'])   

    if (channel_change_flag is True):
        #case 1: if #channels = #tvs -> just set 1 to 1
        if len(channel_num_list) is len(ir_tvs):
            for i in range(len(channel_num_list)):
                 print("case 1: IR signal sent") 
                 _ir_set_channel(ip_list[i], port_list[i], channel_num_list[i], type_list[i])    
        #case 2: if #channels < #tvs -> have the channels wrap again 
        elif len(channel_num_list) < len(ir_tvs):
            for i in range(len(ir_tvs)):
                 if (i > len(channel_num_list)):
                    print("case 2.1: IR signal sent") 
                    _ir_set_channel(ip_list[i-len(channel_num_list)], port_list[i-len(channel_num_list)], str(channel_num_list[i-len(channel_num_list)]), type_list[i-len(channel_num_list)])
                 else :
                    print("case 2.2: IR signal sent") 
                    _ir_set_channel(ip_list[i], port_list[i], channel_num_list[i], type_list[i])  
        #case 3: if channels > tvs -> have set channels on tvs and exit loop
        elif len(channel_num_list) > len(ir_tvs):
             for i in range(len(ir_tvs)):
                print("case 3: IR signal sent") 
                _ir_set_channel(ip_list[i], port_list[i], channel_num_list[i], type_list[i])   
    #db.close()
    if not channel_num_list:
        print("no scheduled channels at this moment (IR)")

    return channel_data

# INITIAL CHANNEL AUTOMATION FOR IR
def force_channel_automation_IR():
    currentDateTimeUTC = datetime.utcnow().replace(second=0,microsecond=0).isoformat() + 'Z'
    channel_data = load_schedule()
    #remove any outdated fixtures and update on database
    for channel in list(channel_data):
        if currentDateTimeUTC > channel_data[channel]['end']:
            del channel_data[channel]
    persist_schedule(channel_data)

    #filter out any channels that have yet to be shown 
    channel_data = load_schedule()
    for channel in list(channel_data):
        if currentDateTimeUTC < channel_data[channel]['start']:
            del channel_data[channel]
        
    print('db schedule checked for IR')

    channel_num_list = []
    for channel in channel_data:
        channel_num_list.append(channel_data[channel]['channel_number'])  

    ir_tvs = ir_load_blaster_data()
    ip_list = []
    port_list = []
    type_list = []
    for tv in ir_tvs:
         ip_list.append(ir_tvs[tv]['ip_address'])
         port_list.append(ir_tvs[tv]['port'])   
         type_list.append(ir_tvs[tv]['type'])   
    print(ip_list)
    print(port_list)
    print(type_list)
    #case 1: if #channels = #tvs -> just set 1 to 1
    if len(channel_num_list) is len(ir_tvs):
        for i in range(len(channel_num_list)):
            print("case 1: IR signal sent") 
            _ir_set_channel(ip_list[i], port_list[i], channel_num_list[i], type_list[i])    
    #case 2: if #channels < #tvs -> have the channels wrap again 
    elif len(channel_num_list) < len(ir_tvs):
        for i in range(len(ir_tvs)):
            if (i > len(channel_num_list)):
                print("case 2.1: IR signal sent") 
                _ir_set_channel(ip_list[i-len(channel_num_list)], port_list[i-len(channel_num_list)], str(channel_num_list[i-len(channel_num_list)]), type_list[i-len(channel_num_list)])
            else :
                print("case 2.2: IR signal sent")
                print(ip_list[i], port_list[i], channel_num_list[i], type_list[i])
                _ir_set_channel(ip_list[i], port_list[i], channel_num_list[i], type_list[i])  
    #case 3: if channels > tvs -> have set channels on tvs and exit loop
    elif len(channel_num_list) > len(ir_tvs):
        for i in range(len(ir_tvs)):
            print("case 3: IR signal sent") 
            _ir_set_channel(ip_list[i], port_list[i], channel_num_list[i], type_list[i])   

    if not channel_num_list:
        print("no scheduled channels at this moment (IR)")
    return {}
