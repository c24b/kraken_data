#coding: utf-8
import re
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter, defaultdict
import nltk

def get_type(resource):
    '''describe the type of resource by its type'''
    is_type_of = {}
    q = '''
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

def get_similar_prop(tagsA, tagsB):
    similar_prop = []
    for n in list(set(tagsA) & set(tagsB)):
        if tagsA[n] > 1 and tagsB[n] > 1:
            similar_prop.append([n, tagsA[n], tagsB[n]])
    return sorted(similar_prop, key=lambda x: int(x[2]), reverse=True)[:3]

if __name__ == "__main__":
    resourceA = "Marie_Antoinette"
    typesA = get_type(resourceA)
    tagsA = get_tags(typesA)
    #tags = filter_tags(types, 5)
    #print(tags)
    resourceB = "Louis_de_Funès"
    typesB = get_type(resourceB)
    tagsB = get_tags(typesB)
    similar_prop = get_similar_prop(tagsA, tagsB)
    print(similar_prop)
