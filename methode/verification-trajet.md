# Vérification sur trajet — table de décision, pré-inscrite

**Écrite le 5 août 2026, avant tout trajet.** C'est la seule chose qui la rend
valable : une catégorie ajoutée au retour est une catégorie choisie après avoir
vu ce qu'elle classe.

> Le trajet est la première mesure de ces deux jours **sans table de décision
> écrite d'avance**. Toutes les autres en ont eu une — l'unité pré-inscrite du
> §3.2, le protocole terrain, le tirage aveugle. Celle-ci comble ce trou avant
> qu'il produise quelque chose.

---

## Ce qu'un trajet peut établir, et ce qu'il ne peut pas

**Un seul trajet, conduit par l'auteur, ne peut que TROUVER DES DÉFAUTS.**

Il ne délivre aucun certificat : `n = 1`, et le conducteur est la partie qui veut
que ça marche. C'est la même asymétrie que l'épreuve à l'aveugle du 2 août, et
elle se dit avant, pas après.

> **Le compte rendu utile n'est donc pas « ça a bien marché ».** C'est une liste,
> éventuellement vide, avec le **kilométrage parcouru à côté** — pour qu'on sache
> ce que le vide couvre.

Une liste vide sur 12 km ne dit rien. Sur 180 km, elle dit quelque chose de
faible. Ni l'une ni l'autre ne dit « le copilote fonctionne ».

---

## Les cinq catégories, et ce qui n'en est pas

| Catégorie | Ce qui la remplit | Ce qui NE la remplit PAS |
|---|---|---|
| **Fausse alerte** | Une alerte s'affiche, et la règle ne s'applique pas ici | Une alerte sur un verdict **`indéterminé`** n'est pas fausse — elle dit qu'on ne sait pas, et c'est vrai |
| **Manquée** | Un panneau est vu, aucune alerte ne l'a précédé | Si l'arrêté n'est pas dans DiaLog, c'est la **réserve 4**, pas un défaut du copilote. Se vérifie au retour, pas au bord de la route |
| **Mal ancrée** | L'alerte arrive **après** la dernière sortie qui permettait de l'éviter | Une alerte tardive mais encore évitable est mal ancrée « faible » — la noter comme telle |
| **Ambiguïté matérielle** | Deux candidates de raccrochage, et **des verdicts différents** | Deux candidates qui disent la même chose : l'ambiguïté existe et elle est **immatérielle**. Ne pas la consigner |
| **Défaut de l'application** | L'écran rouge « Défaut de l'application », un 4xx | **Ne devrait jamais apparaître.** S'il apparaît, noter le message exact : c'est notre faute, pas le réseau |

**Une observation qui n'entre dans aucune des cinq se consigne quand même, en
texte libre, sous « inclassable ».** Les inclassables sont le signal que la table
était trop étroite — et ce signal se perd si on les force dans une case.

---

## La règle Un : on ne classe JAMAIS au bord de la route

Reprise telle quelle de [verification-terrain.md](verification-terrain.md).

**Au moment du fait, on relève trois choses et rien d'autre :**

| | |
|---|---|
| **la position** | coordonnées, lues sur l'écran ou sur le téléphone |
| **l'heure** | à la minute |
| **une photographie** | du panneau, ou de l'écran, ou des deux |

**La classification se fait à l'arrêt**, sur les catégories ci-dessus, fixées
avant le départ.

**Pourquoi.** Classer en conduisant, c'est classer sous l'effet de ce qu'on vient
de voir — et la catégorie choisie sur le moment justifie ce qu'on ressent plutôt
qu'elle ne décrit ce qui s'est produit. C'est la même raison qui a fait
dépouiller les photographies de leur EXIF : le classificateur ne doit pas savoir
ce que son verdict fait au chiffre.

---

## Ce qu'il faut noter en plus, et qui ne coûte rien

| | pourquoi |
|---|---|
| **kilométrage parcouru** | sans lui, une liste vide ne se lit pas |
| **le gabarit déclaré** | le verdict en dépend entièrement |
| **les motifs déclarés** | « livraison » change 1 262 règles |
| **la voix activée ou non** | une manquée n'a pas le même sens si la voix était coupée |
| **le réseau** | une zone blanche explique une tuile manquante, pas une manquée |

---

## Le trajet à faire, et pourquoi celui-là

**Vers Le Mans.** 61 règles dans la tuile, contre 5 à Laval et **aucune à
Angers, Saumur et Cholet**.

> **Le copilote sera muet à Angers, et c'est correct** : aucun arrêté n'y est
> ingéré. Un trajet dans une zone sans données ne teste rien du copilote — il
> teste seulement qu'il sait se taire honnêtement, ce qui se vérifie en une
> minute sans rouler.

C'est là que cette table servira.

---

## Ce qui se décide au retour, et pas avant

**Rien.** Les catégories sont fixées ici. Si le trajet en réclame une sixième,
elle s'ajoute **datée**, et le compte rendu dit clairement lesquelles ont été
appliquées rétroactivement — parce qu'une catégorie ajoutée après coup ne classe
pas la même chose qu'une catégorie prévue.
