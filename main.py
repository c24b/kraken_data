#/usr/bin/env python3
#coding: utf-8
'''
filename: main.py
Store the predicates
'''
import urllib
import re
from ressources_types import *
from ressources_def import *
from ressources_tags import *
from utils import export

if __name__ == "__main__":
    resources = ["Jacques_Tati", "Pierre_Richard", "Jean_Dujardin"]
    # unique ressources types
    # types = get_types_d(resources[0])
    # multiple ressources types
    types = get_mtypes_d(resources)
    export(types, "types.json")

    # common predicate: level 0 matching common properties
    co_types = get_common_types(resources, types)
    export(co_types, "co_types.json")
    # unique ressource tags

    # common tags level 0 matching common properties
    tags_d = get_tags_d(types)
    # export(tags_d, "tags_d.json")
    #get the common tags
    # commons_tags = get_commons_tags(g,resources)
