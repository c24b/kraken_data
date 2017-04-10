#/usr/bin/env python3
#coding: utf-8
'''
filename: ressources_def.py
Get the definition equivalent of a category or synonyms
in WIKICAT
'''

from SPARQLWrapper import SPARQLWrapper, JSON

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
