import shelve

def store_is_empty():
    db = shelve.open('db\storage')
    store = db['store']
    return store == {}

def load_store():
    db = shelve.open('db\storage')
    store = db['store']
    return store

def persist_store(new_store):
    db = shelve.open('db\storage')
    db['store'] = new_store
    db.close()

def load_tv_ips():
    db = shelve.open('db\storage')
    tv_ips = db['scan']
    return tv_ips

def persist_tv_ips(new_store):
    db = shelve.open('db\storage')
    db['scan'] = new_store
    db.close()