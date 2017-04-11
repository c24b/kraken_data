#/usr/bin/env python3
#coding: utf-8
'''
filename: utils.py
'''
import json
from pymongo import MongoClient

def export(data, outfname):
    '''export in a json format'''
    import json
    json_data = json.dumps(data,  indent=4, sort_keys=True)
    with open(outfname, 'w', encoding="utf-8") as f:
        f.write(json_data)
    return outfname

def store(type_d, data):
    client = MongoClient()
    db = client.kraken
    if type not in ["types", "tags", "score", "analogy", "graph"]:
        raise Exception("Wrong collection type `%s` for data. Failed to store into kraken DB" %type_d)
    if type(data) == dict:
        db.results.insert(data)
    elif type(data) == list:
        db.results.insert_many(data)
    else:
        raise Exception("Wrong data type. Failed to store into kraken DB")
