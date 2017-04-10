#/usr/bin/env python3
#coding: utf-8
'''
filename: ressources_types.py
Get the intersection between one or multiples ressources
by similarity between predicates
'''

import re
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter, defaultdict

from pymongo import MongoClient



def get_types_d(resource):
    '''
    given a single resource
    return every predicate
    in a common dict with the predicate name as key
    and the corresponding url and ns
    e.g: Jacques_Tati
    '''
    ns = "http://dbpedia.org"
    dtype = "resource"
    #prefix db-owl: <http://dbpedia.org/ontology/>
    q = '''
    prefix db-owl: <http://dbpedia.org/ontology/>
    SELECT ?type WHERE {

        <http://dbpedia.org/resource/%s> rdf:type ?type .
    }

    ''' %(resource)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    is_type_of = {}
    results = sparql.query().convert()
    nb_results = len(results["results"]["bindings"])
    if nb_results == 0:
        raise Exception("No results found for %s" %resource)
    type_urls = [r["type"]["value"] for r in results["results"]["bindings"]]

    for val in type_urls:
    # for r in results["results"]["bindings"]:
        if "#" in val:
            ns = val.split("#")[0]
            type_v = val.split("#")[-1]
            type_v = re.sub('s$', '', type_v)

        else:
            ns = "/".join(val.split("/")[:-1])

            if "entity" in val:
                #wikidata IDS
                r = requests.get(val)
                r_json =r.json()
                type_v = [e["labels"]["en"]["value"] for e in r_json["entities"].values()][0].lower()
            else:
                m = re.match('(?P<name>.*?)(?P<id>\d+)$', val)
                if m is not None:
                    type_v = m.group("name").split("/")[-1]
                else:
                    if "Yago" in val or "Wikicat" in val:
                        type_v = re.split("/(Yago|Wikicat)", val)[-1]
                    else:
                        type_v = val.split("/")[-1]
        #finally mapping
        if type_v in is_type_of.keys():
            is_type_of[type_v]["urls"].append(val)
            is_type_of[type_v]["ns"].append(ns)
        else:
            is_type_of[type_v] = {"urls": [val], "ns":[ns]}
        is_type_of[type_v]["resource"] = resource

    return is_type_of

def get_mtypes_d(resources):
    ''''given multiple resources
    join existing dict_types
    and map
    '''
    data = [get_types_d(r) for r in resources]

    # list_types = map(lambda x:get_types_d(x), resources)
    types = {}
    for d in data:
        for k, v in d.items():

            if k not in types.keys():
                types[k] = {"urls":v["urls"], "ns":v["ns"], "resources": [v["resource"]]}
            else:
                types[k]["urls"].extend(v["urls"])
                types[k]["ns"].extend(v["ns"])
                types[k]["resources"].append(v["resource"])
    #score
    for k, v in types.items():
        types[k]["_score"] = len(types[k]["resources"])
    return types

def get_common_types(resources, types):
    '''Level 0 of similarity
    2 resources are common when they simply share the same type
    '''
    # verbose mode
    # for k,v in types.items():
    #     if v["_score"] > 1:
    #         print("%s have %s in common"%(" & ".join(v["resources"]),k))
    return [(v["resources"], k) for k,v in types.items() if v["_score"] > 1]



def describe(resource):
    r_uri = "http://dbpedia.org/resource/%s" %(resource)
    q = ''' DESCRIBE <%s>''' %(r_uri)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    predicates_d = {}
    for r in results["results"]["bindings"]:
        subj, predicate, obj = r["s"]["value"], r["p"]["value"], r["o"]["value"]
        p_uri = urllib.parse.urlparse(predicate)
        p = {}
        p["dt_store"] = p_uri.netloc
        if "#" in predicate:
            p["label"]= p_uri.fragment
            p["uri"] = predicate
            p["type"] = p_uri.path.split("/")[-1]
            p["tags"] = [n.lower() for n in  re.sub( r"([A-Z]|-)", r" \1", p["label"]).split()]
            p["count"] = 0
        else:
            # print(predicate)
            p["dt_store"] = p_uri.netloc
            p["label"]= p_uri.path.split("/")[-1]
            p["type"] = p_uri.path.split("/")[-2]
            p["tags"] = [n.lower() for n in  re.sub( r"([A-Z]|-)", r" \1", p["label"]).split()]
            p["count"] = 0
        try:
            predicates_d[predicate]["count"] += 1
        except:
            predicates_d[predicate] = p
    return predicates_d

# def get_types_d(resources):
#     '''concatenate dict of label for n resources'''
#     #chain.from_iterable(get_type_label(n) for n in resources)
#     #gave me a list I want a dict
#     types = {}
#     for r in resources:
#         for k, v in get_type_label(r).items():
#             try:
#                 types[k].extend(v)
#             except KeyError:
#                 types[k] = [v]
#         types.update(get_type_label(r))
#
#     return types
#
# def get_edges(resources):
#     return list(chain.from_iterable(build_edges(n) for n in resources))
# def stamp_store(dict_items):
#     client = MongoClient()
#     db = client.kraken
#     db.predicates.insert(dict_items)
