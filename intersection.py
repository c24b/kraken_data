#/usr/bin/env python3
#coding: utf-8
'''
filename: intersection.py
Get the intersection concept between two ressources
The main goal is to understand the analogy and discover links
'''

import re
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter, defaultdict
import nltk
import networkx as nx
import matplotlib.pyplot as plt

def get_type(resource):
    '''describe the type of resource by its type'''
    is_type_of = {}
    q = '''
    prefix db-owl: <http://dbpedia.org/ontology/>
    SELECT ?type WHERE {
    <http://dbpedia.org/resource/%s> rdf:type ?type .
    }
    ''' %(resource)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    nb_results = len(results["results"]["bindings"])
    if nb_results == 0:
        raise Exception("No results found for %s" %resource)
    for r in results["results"]["bindings"]:
        val = r["type"]["value"]
        if "entity" in val:
            #print(val)
            pass
        elif "#" in val:
            type_v = val.split("#")[-1]
            type_v = re.sub('s$', '', type_v)
            if type_v in is_type_of.keys():
                is_type_of[type_v].append(val)
            else:
                is_type_of[type_v] = [val]
        else:
            m = re.match('(?P<name>.*?)(?P<id>\d+)$', val)
            if m is not None:
                type_v = m.group("name").split("/")[-1]
                if type_v in is_type_of.keys():
                    is_type_of[type_v].append(val)
                else:
                    is_type_of[type_v] = [val]

            else:
                if "Yago" in val or "Wikicat" in val:
                    type_v = re.split("/(Yago|Wikicat)", val)[-1]

                    if type_v in is_type_of.keys():
                        is_type_of[type_v].append(val)
                    else:
                        is_type_of[type_v] = [val]
                else:
                    type_v = val.split("/")[-1]

                    if type_v in is_type_of.keys():
                        is_type_of[type_v].append(val)
                    else:
                        is_type_of[type_v] = [val]
    return is_type_of

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

def draw_graph(edges):
    '''graph it'''
    g = nx.Graph()
    for n in edges:
        g.add_edge(n[0],n[1], weight=n[2])
    nx.draw(g, with_labels=True)
    plt.savefig("testA.png") # save as png
    plt.show()

def draw_n_intersect(edges):
    g = nx.Graph()
    for e in edges:
        g.add_edge(e[0],e[1], weight=e[2])
    nx.draw(g, with_labels=True)
    plt.show()

def draw_intersect(edgesA, edgesB):
    g = nx.Graph()
    for n in edgesA:
        g.add_edge(n[0],n[1], weight=n[2])
    for n in edgesB:
        g.add_edge(n[0],n[1], weight=n[2])
    nx.draw(g, with_labels=True)
    plt.savefig("insersection.png") # save as png
    plt.show()

if __name__ == "__main__":
    resourceA = "Louis_de_Funès"
    typesA = get_type(resourceA)
    tagsA = get_tags(typesA)
    edgesA = [(resourceA,t,w) for t,w in tagsA.items() if w > 1]
    #draw_graph(edges)

    #tags = filter_tags(types, 5)
    #print(tags)
    resourceB = "Jacques_Tati"
    typesB = get_type(resourceB)
    tagsB = get_tags(typesB)
    edgesB = [(resourceB,t,w) for t,w in tagsB.items() if w > 1]
    resourceC = "Louis_Malle"
    typesC = get_type(resourceC)
    tagsC = get_tags(typesC)
    edgesC = [(resourceC,t,w) for t,w in tagsB.items() if w > 1]
    draw_n_intersect(edgesA + edgesB + edgesC)
    # similar_prop = get_similar_tags(tagsA, tagsB, offset=5)
    # print(similar_prop)
    # predicatesA =(get_predicate(typesA,similar_prop))
    # predicatesB =(get_predicate(typesB,similar_prop))
