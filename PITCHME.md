# KRAKEN
#### *un moteur de similarité sémantique*

![./poulpe-small.png](./poulpe-small.png)

---
#### Comment découvrir des connaissances sans connaître le vocabulaire ?
#### Comment faire de l'alignement automatique entre triplestore ?
---

**Ceci est un projet exploratoire**

Explorer un triple-store par analogie sans connaissance préalable du vocabulaire:
1. A partir des prédicats de *n* ressources
2. Détecter les similarités de description
3. Permettre l'alignement entre triplestore: enrichir les relations
4. Permettre l'inférence: des points communs intéressants

---
#### Hypothèse de départ

Une ressource est définie sémantiquement par des prédicats normés et classés dans des vocabulaires spécifiques. Les relations qu'elle entretient avec d'autres ressources sont définies par une ontologie, et son modèle.

---

Un objet du monde est donc représenté par un graphe étiqueté.
![](http://data.bnf.fr/images/exemple_graphe_1.jpg)

<small>Le modèle DATA BNF</small>

---

Il faut donc connaitre le vocabulaire et le modèle **AVANT** de pouvoir faire de la découverte de connaissance.

---
💡

 **Décrire les relations entre deux ressources en se servant des prédicats comme des étiquettes**

---

1. Décrire la ressource a partir de ses prédicats trasformés en étiquettes

![](./examples/testA.png)

---

2. Trouver les prédicats communs entre *n* ressources

![](./examples/digraph.png)

---

3. Pour découvrir des similarités
