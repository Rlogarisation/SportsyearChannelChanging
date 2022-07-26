import shelve
from werkzeug.exceptions import BadRequest

def load_store(uuid):
    db = shelve.open('db\storage')
    data = db['scan']

    try:
        store = data[uuid]['store']

    except:
        print("Store Doesn't Exist Yet")
        store = {}

    return store

def persist_store(new_store, uuid):
    db = shelve.open('db\storage')
    data = db['scan']
    data[uuid]['store'] = new_store
    db['scan'] = data
    db.close()

def load_tv_data():
    db = shelve.open('db\storage')
    tv_data = db['scan']
    return tv_data

def persist_tv_data(new_store):
    db = shelve.open('db\storage')
    db['scan'] = new_store
    db.close()

def persist_tv_channels(list, uuid):
    db = shelve.open('db\storage')
    data = db['scan']
    data[uuid]['tv_channels'] = list
    db['scan'] = data
    db.close()

def load_tv_channels(uuid):
    db = shelve.open('db\storage')
    data = db['scan']

    try:
        tv_channels = data[uuid]['tv_channels']
    except:
        print("No TV Channels")
        raise BadRequest("No TV Channels, please run scan_channels(uuid)")

    return tv_channels


def persist_schedule(channel_data):
    db = shelve.open('db\storage')
    db['schedule'] = channel_data
    db.close()

def load_schedule():
    db = shelve.open('db\storage')  
    try:
        data = db['schedule']
    except:
        raise BadRequest("No schedules in database")
    return data
