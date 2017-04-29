#/usr/bin/env python3
#coding: utf-8
'''
filename: intersection.py
Get the intersection concept between two ressources
The main goal is to understand the analogy and discover links
For now using dbpedia: because predicate are verbose
'''

import re
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter, defaultdict
import nltk
import networkx as nx
import matplotlib.pyplot as plt
from pymongo import MongoClient
from itertools import chain


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

def get_tags():

def get_tags_d(resource_dict):
    '''given a single resource_dict of types
    return a dict of tags with tag as key
    and a list of corresponding url and ns and occurence
    e.g: Jacques_Tati
    '''
    # retrieve the list of tags from keys
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    from nltk.corpus import stopwords
    tags = []
    tag_dict = {}
    for k,v in resource_dict.items():
        for n in re.findall('[A-Z][^A-Z]*', k):
            sing = wnl.lemmatize(n.lower())
            # if sing not in stopwords.words('english'):
            if sing not in tag_dict.keys():
                print(sing, k, v)
            # try:
                tag_dict[sing] = {"predicates": [k],
                                  "urls": [n["url"] for n in v],
                                  "ns": [n["ns"] for n in v],
                                  "count":1
                                }
            else:
            # except KeyError:
                tag_dict[sing]["predicates"].append(k)
                tag_dict[sing]["urls"].extend([n["url"] for n in v])
                tag_dict[sing]["ns"].extend([n["ns"] for n in v])
                tag_dict[sing]["count"] += 1
    return tag_dict


def build_graph_cotypes(resources, types):
    '''Show the graph of common types
    predicates are shown as **nodes**
    '''
    co_types = get_common_types(resources, types)
    g = nx.DiGraph()

    nodes = resources
    targets = [n[1] for n  in co_types]

    for nodes, edge in co_types:

        for node in nodes:
            g.add_edge(node, edge)
    pos = nx.spring_layout(g)

    # nx.draw_networkx_nodes(g,pos,
    #                        nodelist=resources,
    #                        node_color='red')
    # #
    # nx.draw_networkx_nodes(g,pos,
    #                        nodelist=targets,
    #                        node_color='blue')
    #
    #

    nx.draw(g,pos, with_labels = True)
    plt.savefig("level0.png") # save as png
    plt.show()
def get_tags():
    pass
# def get_tags_freq(types):
#     '''extract tags from description'''
#     from nltk.stem import WordNetLemmatizer
#     wnl = WordNetLemmatizer()
#     from nltk.corpus import stopwords
#     tags = []
#     for k in types.keys():
#         for n in re.findall('[A-Z][^A-Z]*', k):
#             sing = wnl.lemmatize(n.lower())
#             if sing not in stopwords.words('english'):
#                 tags.append(sing)
#     return Counter(tags)
#
# def filter_frequent_tags(types, offset=5):
#     '''filter the most frequent tags'''
#     return get_tags(types).most_common(offset)
#
# def filter_by_tags(tags, types, offset):
#     '''return all the predicates of the most common type'''
#     predicates = []
#     for n in tags:
#         for k in types.keys():
#             if n[0] in k.lower():
#                 #print(n[0],"=>", types[k])
#                 predicates.append([types[k], n[1],n[0]])
#     return predicates
#
# def get_similar_tags(tagsA, tagsB, offset=3):
#     '''get tags that are shared between 2 lists of tags with offset'''
#     similar_prop = []
#     for n in list(set(tagsA) & set(tagsB)):
#         if tagsA[n] > 1 and tagsB[n] > 1:
#             similar_prop.append([n, tagsA[n], tagsB[n]])
#     return sorted(similar_prop, key=lambda x: int(x[2]), reverse=True)[:offset]
#
# def get_predicate(typesA,tags):
#     ''' get the full predicate'''
#     predicates = defaultdict.fromkeys([t[0] for t in tags], [])
#     for k in typesA.keys():
#         for t, t_nb, t_nb2 in tags:
#             if t in k.lower():
#                 predicates[t].extend(typesA[k])
#     return(predicates)
#
# def build_edges(resource="Louis_de_Funès"):
#     types = get_type_label(resource)
#     tags = get_tags(types)
#     edges = [(resource,t,w) for t,w in tags.items() if w > 1]
#     return edges
#
#
# def get_commons_tags(g, resources):
#     '''get commons tags between the resources'''
#     return [k for k,v in nx.degree(g).items() if v>=len(resources) and k not in resources]
#
# def build_graph(resources,edges):
#     g2 = nx.Graph()
#
#     for e in edges:
#         # print(e[0])
#         g2.add_edge(e[0], e[1])
#     return g2

# def draw_graph(g, resources):
#     node_path = get_commons_tags(g,resources)
#     pos = nx.spring_layout(g)
#     nx.draw_networkx_nodes(g,pos,
#                        nodelist=g.nodes(),
#                        node_color='grey',
#                        node_size=100,
#                    alpha=0.6, with_labels=True)
#     nx.draw_networkx_nodes(g,pos,
#                        nodelist=node_path,
#                        node_color='green',
#                        node_size=300,
#                    alpha=0.7, with_labels=True)
#     nx.draw_networkx_nodes(g,pos,
#                        nodelist=resources,
#                        node_color='r',
#                        node_size=500,
#                    alpha=0.8, with_labels=True)
#     labels = {}
#     for i,n in enumerate(g.nodes()):
#         labels[n] = n
#     nx.draw_networkx_labels(g,pos,labels,font_size=10)
#     nx.draw_networkx_edges(g, pos=pos)
#
#     plt.savefig("digraph.png") # save as png
#     plt.show()
#     return g

def wikicat(resource):
    '''
    given a resource expressed in wikicat
    return entity definition equivalent of a category in wikidata
    and aliases e.g tag synonym
    i.e a dict of label_tag along with their common uris:
    {label_tag: [uri, uri, ...]}
    e.g: Jacques_Tati
    '''

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
    entities = []
    definitions = {}
    translations = {}
    entities_eq = {}
    for r in results["results"]["bindings"]:
        val = r["type"]["value"]
        if "entity" in val:
            #wikidata IDS equivalent of (entities| Notice AUT)
            rq = requests.get(val)
            r_json = rq.json()
            for e in r_json["entities"].values():
                entity_id = e["title"]
                #synonymes dans toutes les langues
                for lang, v in e["aliases"].items():
                    for syn in v:
                        entities.append((entity_id, syn["value"], syn["language"], "translation"))
                        try:
                            if syn["value"] not in translations[syn["language"]]:
                                translations[syn["language"]].append(syn["value"])
                        except KeyError:
                            translations[syn["language"]] = [syn["value"]]
                #definition dans toutes les langues
                for lang, v in e["descriptions"].items():
                    # entities.append((entity_id, v["value"], v["language"], "definition"))
                    try:
                        if v["value"] not in definitions[v["language"]]:
                            definitions[v["language"]].append(v["value"])
                    except KeyError:
                        definitions[v["language"]] = [v["value"]]

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

def export(data, outfname):
    '''export in a json format'''
    import json
    json_data = json.dumps(data)
    with open(outfname, 'w') as f:
        f.write(json_data, encoding="utf-8", indent=4, sort_keys=True)
    return outfname

if __name__ == "__main__":
    from itertools import chain

    resources = ["Jacques_Tati", "Pierre_Richard", "Jean_Dujardin"]
    # unique ressources types
    # types = get_types_d(resources[0])
    # multiple ressources types
    types = get_mtypes_d(resources)
    export(types, "ressources_mtypes_example.json")

    # common predicate: level 0 matching common properties
    co_types = get_common_types(resources, types)
    export(co_types, "co_mtypes_example.json")
    # unique ressource tags

    # common tags levl 0 matching common properties
    co_types = get_common_types(resources, types)
    #build_graph_cotypes(resources, types)
    # tags_d = get_tags_d(types)
    #get the common tags
    # commons_tags = get_commons_tags(g,resources)
