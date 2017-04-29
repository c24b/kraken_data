#/usr/bin/env python3
#coding: utf-8
'''
filename: analogy.py
'''
class Resource(obj):
    def __init__(self, label):
        self.label = label
        self.triplestore = 'http://dbpedia.org/resource/'
        self.resource_uri = "%s/%s"%(self.triplestore, self.label)
        self.endpoint = "http://dbpedia.org/sparql"

    def search(self, target=""):
        '''search the resource on triplestore'''
        pass
    def get_score(self):
        ''' get the score of a resource:
        score is made by the number of predicates
        used to describe the resource
        '''
        query = ''' SELECT ?type WHERE {

            <%s> rdf:type ?type .
        }'''%self.resource_uri
        sparql = SPARQLWrapper(self.endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        self.results = sparql.query().convert()
        self.score = len(results["results"]["bindings"])
