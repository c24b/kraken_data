# KRAKEN

![](./poulpe.png)

---------

Projet exploratoire: Explorer un triple-store par analogie sans connaissance préalable du vocabulaire:
1. A partir des prédicats de *n* ressources
4. Détecter les similarités de description
5. et permettre l'inférence et l'alignement

---------------

## Hypothèses de travail

Les ressources sont reparties dans différents triplestores elles possèdent différentes caractéristiques parfois redondantes parfois semblables dans leur énoncés.

--------------
Décrire les liens qu'entretiennent deux ou + de ressources
à plusieurs niveaux et en déduire leurs caractéristiques majeures.
-------------------
La similarité entre n ressources est définie par
le nombre de prédicats commun
pondérées par le nombre de prédicats qui la définissent
--------------------
Cette mesure de similarité est ensuite affinée par le nombre d'étapes (de pas) dans le parcours du graph
qui s'arrête au moment ou deux objets sont communs ou lorsque la source est identique à l'objet.
---
* Premiers développements
* Outils de visualisations

---

## Premiers dévelopements

Objectif: Cartographier les points communs entre n ressources et parcourir les liens(étiquettes) qu'ils ont en commun

### Décrire une ressource a partir de ces prédicats

En prenant une ressource disponible dans un triplestore
(pour le moment wikidata)
on constitue une typologie (un dictionnaire de types) pour cette ressource à partir des prédicats qui décrivent la ressource comme composé dans le fichier [`types.json`](./types.json).
```json
{
    "20th-centuryActors": {
        "_score": 1,
        "ns": [
            "http://dbpedia.org/class/yago"
        ],
        "resources": [
            "Jean_Dujardin"
        ],
        "urls": [
            "http://dbpedia.org/class/yago/Wikicat20th-centuryActors"
        ]
    },
    "20th-centuryFrenchMaleActors": {
        "_score": 1,
        "ns": [
            "http://dbpedia.org/class/yago"
        ],
        "resources": [
            "Jean_Dujardin"
        ],
        "urls": [
            "http://dbpedia.org/class/yago/Wikicat20th-centuryFrenchMaleActors"
        ]
    },
    "21st-centuryActors": {
        "_score": 1,
        "ns": [
            "http://dbpedia.org/class/yago"
        ],
        "resources": [
            "Jean_Dujardin"
        ],
        "urls": [
            "http://dbpedia.org/class/yago/Wikicat21st-centuryActors"
        ]
    }
  }
```

![](./examples/testA.png)

* Niveau 0:
Les ressources partagent x prédicats

![](./examples/level0.png)

* Niveau 1:
Les ressources partagent des **étiquettes** de prédicats en commun
![](./examples/digraph.png)
* Niveau 2 etc...
