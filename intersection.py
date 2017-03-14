#/usr/bin/env python3
#coding: utf-8
'''
filename: intersection.py
Get the intersection concept between two ressources
The main goal is to understand the analogy and discover links
For now using dbpedia
'''

import re
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter, defaultdict
import nltk
import networkx as nx
import matplotlib.pyplot as plt
from pymongo import MongoClient

def index_type( resource, is_type_of):
    ''''index list and filter e.g
    {u'Musician:[
                {   'url': u'http://dbpedia.org/class/yago/Musician110339966',
                    'ns': u'http://dbpedia.org/class/yago'},
                {   'url': u'http://dbpedia.org/class/yago/Musician110340312',
                    'ns': u'http://dbpedia.org/class/yago'}
                ],
    u'FrenchSingers':[
                {'url': u'http://dbpedia.org/class/yago/WikicatFrenchSingers', 'ns': u'http://dbpedia.org/class/yago'}]
    }
    '''
    for n in resource:
        type_v, ns, url = n
        # if type_v == "Thing":
        #     pass
        if type_v in is_type_of.keys():
            is_type_of[type_v].append({"ns":ns, "url": url})
        else:
            is_type_of[type_v] = [{"ns":ns, "url": url}]
    return is_type_of

def get_type(resource):
    '''
    given a single resource
    return every predicate 
    e.g: Jacques_Tati
    '''
    ns = "http://dbpedia.org"
    dtype = "resource"
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
            # types_labels.append((type_v, ns ,val))
            is_type_of[type_v].append({"url":val,"ns": ns})
        else:
            ns = "/".join(val.split("/")[:-1])

            if "entity" in val:
                #wikidata IDS
                r = requests.get(val)
                r_json =r.json()
                type_v = [e["labels"]["en"]["value"] for e in r_json["entities"].values()][0].lower()
                if type_v in is_type_of.keys():
                    is_type_of[type_v].append({"url":val,"ns": ns})
                else:
                    is_type_of[type_v] =[{"url":val,"ns": ns}]
            else:
                m = re.match('(?P<name>.*?)(?P<id>\d+)$', val)
                if m is not None:
                    type_v = m.group("name").split("/")[-1]

                    if type_v in is_type_of.keys():
                        is_type_of[type_v].append({"url":val,"ns": ns})
                    else:
                        is_type_of[type_v] =[{"url":val,"ns": ns}]

                else:
                    if "Yago" in val or "Wikicat" in val:
                        type_v = re.split("/(Yago|Wikicat)", val)[-1]

                        if type_v in is_type_of.keys():
                            is_type_of[type_v].append({"url":val,"ns": ns})
                        else:
                            is_type_of[type_v] =[{"url":val,"ns": ns}]
                    else:
                        type_v = val.split("/")[-1]
                        # print(type_v)
                        # types_labels.append((type_v, ns ,val))
                        if type_v in is_type_of.keys():
                            is_type_of[type_v].append({"url":val,"ns": ns})
                        else:
                            is_type_of[type_v] =[{"url":val,"ns": ns}]
    return is_type_of

def get_tags_d(types):
    '''build inverse ref tag:[uri, uri,...]'''
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    from nltk.corpus import stopwords
    tags = get_tags(types)
    print(tags)
    tags_d = defaultdict.fromkeys(tags, [])
    for k,v in types.items():
        for n in re.findall('[A-Z][^A-Z]*', k):
            sing = wnl.lemmatize(n.lower())
            if sing not in stopwords.words('english'):
                tags_d[sing].append(v)
    return tags_d


def get_tags(types):
    '''extract tags from description'''
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    from nltk.corpus import stopwords
    tags = []
    for k in types.keys():
        for n in re.findall('[A-Z][^A-Z]*', k):
            sing = wnl.lemmatize(n.lower())
            if sing not in stopwords.words('english'):
                tags.append(sing)
    return Counter(tags)

def filter_frequent_tags(types, offset=5):
    '''filter the most frequent tags'''
    return get_tags(types).most_common(offset)

def filter_by_tags(tags, types, offset):
    '''return all the predicates of the most common type'''
    predicates = []
    for n in tags:
        for k in types.keys():
            if n[0] in k.lower():
                #print(n[0],"=>", types[k])
                predicates.append([types[k], n[1],n[0]])
    return predicates

def get_similar_tags(tagsA, tagsB, offset=3):
    '''get tags that are shared between 2 lists of tags with offset'''
    similar_prop = []
    for n in list(set(tagsA) & set(tagsB)):
        if tagsA[n] > 1 and tagsB[n] > 1:
            similar_prop.append([n, tagsA[n], tagsB[n]])
    return sorted(similar_prop, key=lambda x: int(x[2]), reverse=True)[:offset]

def get_predicate(typesA,tags):
    ''' get the full predicate'''
    predicates = defaultdict.fromkeys([t[0] for t in tags], [])
    for k in typesA.keys():
        for t, t_nb, t_nb2 in tags:
            if t in k.lower():
                predicates[t].extend(typesA[k])
    return(predicates)

def build_edges(resource="Louis_de_Funès"):
    types = get_type_label(resource)
    tags = get_tags(types)
    edges = [(resource,t,w) for t,w in tags.items() if w > 1]
    return edges


def get_commons_tags(g, resources):
    '''get commons tags between the resources'''
    return [k for k,v in nx.degree(g).items() if v>=len(resources) and k not in resources]

def build_graph(resources,edges):
    g2 = nx.Graph()

    for e in edges:
        # print(e[0])
        g2.add_edge(e[0], e[1])
    return g2
def draw_graph(g, resources):
    node_path = get_commons_tags(g,resources)
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g,pos,
                       nodelist=g.nodes(),
                       node_color='grey',
                       node_size=100,
                   alpha=0.6, with_labels=True)
    nx.draw_networkx_nodes(g,pos,
                       nodelist=node_path,
                       node_color='green',
                       node_size=300,
                   alpha=0.7, with_labels=True)
    nx.draw_networkx_nodes(g,pos,
                       nodelist=resources,
                       node_color='r',
                       node_size=500,
                   alpha=0.8, with_labels=True)
    labels = {}
    for i,n in enumerate(g.nodes()):
        labels[n] = n
    nx.draw_networkx_labels(g,pos,labels,font_size=10)
    nx.draw_networkx_edges(g, pos=pos)

    plt.savefig("digraph.png") # save as png
    plt.show()
    return g


def get_category(resource, lang="en"):
    '''
    given a resource expressed in dbpedia
    return the set of entity label along
    with its definition in targeted language
    e.g: Jacques_Tati, "fr"

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
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    tags = []
    definitions = []
    results = sparql.query().convert()
    nb_results = len(results["results"]["bindings"])
    if nb_results == 0:
        raise Exception("No results found for %s" %resource)
    for r in results["results"]["bindings"]:
        val = r["type"]["value"]
        if not "entity" in val:
            pass
        else:
            #wikidata IDS equivalent of (entities| Notice AUT| categories in WIKIDATA)
            rq = requests.get(val)
            r_json = rq.json()

            for e in r_json["entities"].values():
                for l, v in e["aliases"].items():
                    if l.startswith(lang):

                        tags.extend([n["value"] for n in v])
    return tags

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

def get_types_d(resources):
    '''concatenate dict of label for n resources'''
    #chain.from_iterable(get_type_label(n) for n in resources)
    #gave me a list I want a dict
    types = {}
    for r in resources:
        for k, v in get_type_label(r).items():
            try:
                types[k].extend(v)
            except KeyError:
                types[k] = [v]
        types.update(get_type_label(r))

    return types

def get_edges(resources):
    return list(chain.from_iterable(build_edges(n) for n in resources))
def stamp_store(dict_items):
    client = MongoClient()
    db = client.kraken
    db.predicates.insert(dict_items)

if __name__ == "__main__":
    from itertools import chain
    resources = ["Jacques_Tati", "Pierre_Richard", "Molière"]
    print get_type(resource[0])
    #types = get_types_d(resources)
    stamp_store(types)
    #print(types.items())
    tags_d = get_tags_d(types)
    for k, v in tags_d.items():
        print(k,v)

    # print(tags_d.items())

    #edges = get_edges(resources)

    #print(types)
    # types = list(chain.from_iterable(get_type_label(n) for n in resources))

    # edges = list(chain.from_iterable(build_edges(n) for n in resources))

    # g = build_graph(resources, edges)
    # draw_graph(g, resources)
    #next step: backtrack
    #get the common tags
    # commons_tags = get_commons_tags(g,resources)
    #for each tag find out where tag is linked to label
    # for tag in commons_tags:
    #     for t in tags_d[tag]:
    #         print(t)
    #
    #     break
    # note pour plus tard: dictionnaire de tags urls
    # est mal créé:
    # - liste au lieu de set
    # - recuperer uniquement le namespace ns
    #     get_types(tag)
