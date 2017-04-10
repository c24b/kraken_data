def export(data, outfname):
    '''export in a json format'''
    import json
    json_data = json.dumps(data,  indent=4, sort_keys=True)
    with open(outfname, 'w', encoding="utf-8") as f:
        f.write(json_data)
    return outfname
