import requests
import pprint
from datetime import datetime

#URL = "https://sportsyear.com.au/api/v1/fixtures/search?preset=next_1_hours&inCalendars=f1a639ff7134f1e783b787968e5cf2dfd02880d4075abbb2b55a92c0907652a3&startingAndEnding=1&includeBroadcasting=1&ac=0"
URL = "https://sportsyear.com.au/api/v1/fixtures/search?preset=next_30_hours&inCalendars=53b2554ac7ded01572467f4cf88128e3771d8c4646f6956a21e8199a6d221359&startingAndEnding=1&includeBroadcasting=1&ac=0"
r = requests.get(url = URL)
data = r.json()
#pprint.pprint(data)
data_copy = data
if data['entities']['fixtures']['byId']:
    currentDateTimeUTC = datetime.utcnow().isoformat()
    same_time_fixture = {}
    for fixture in data['entities']['fixtures']['byId']:
        if (data['entities']['fixtures']['byId'][fixture]['startDateTimeUTC'] >= currentDateTimeUTC):
            same_time_fixture[fixture] = data['entities']['fixtures']['byId'][fixture]['ranking']     
    same_time_fixture = dict(sorted(same_time_fixture.items(), key=lambda x: x[1], reverse=True))
    
    for fixture in same_time_fixture:
        same_time_fixture[fixture] = data['entities']['channels']['broadcastingFixture'][fixture]
        for channel_id in same_time_fixture[fixture]:     
            same_time_fixture[fixture] = data['entities']['channels']['byId'][str(channel_id)]['apiCode']
    print(same_time_fixture)

    
