import nltk
from nltk.stem import WordNetLemmatizer
import networkx as nx
from collections import Counter, defaultdict
import re
from nltk.corpus import stopwords

def get_tags_d(resource_dict):
    '''given a single resource_dict of types
    return a dict of tags with tag as key
    and a list of corresponding url and ns and occurence
    e.g: Jacques_Tati
    '''
    # retrieve the list of tags from keys

    wnl = WordNetLemmatizer()

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

def get_tags_freq(types):
    '''extract tags from types_d return Counter'''
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
    '''filter the most frequent tags from types_d'''
    return get_tags(types).most_common(offset)

def filter_by_tags(tags, types, offset):
    '''by giving tags, types and offset return list
    of the most common tags
    '''
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

def get_commons_tags(g, resources):
    '''get commons tags of a graph between the resources'''
    return [k for k,v in nx.degree(g).items() if v>=len(resources) and k not in resources]
