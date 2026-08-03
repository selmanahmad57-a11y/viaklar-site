# Viaklar — la mesure

**[viaklar.com](https://viaklar.com)** — les arrêtés français d'interdiction de tonnage,
confrontés un par un à OpenStreetMap.

## ⚠ Chiffres corrigés le 3 août 2026

**Les valeurs publiées jusqu'ici — 2 194 km, 89,6 %, 74,5 %, 2 051 arrêtés — sont
RÉTRACTÉES.** Un arrêté DiaLog porte de 1 à 8 régulations — circulation,
stationnement, sens unique, vitesse — chacune avec ses propres critères **et sa
propre géométrie**. Le chargeur lisait les tonnages et les géométries à la portée
de l'**arrêté** au lieu de la **régulation**, et attribuait à la circulation ce
qui appartenait au stationnement.

| | avant | après |
|---|---:|---:|
| dénominateur dédupliqué | 2 194,4 km | **2 060,3 km** |
| taux métrique | 89,553 5 % | **89,430 1 %** |
| taux par arrêté | 74,500 2 % | **74,634 1 %** |
| arrêtés mesurés | 2 051 | **2 050** |

*(colonne « avant » : valeurs rétractées — [methode/retractations.json](methode/retractations.json))*

**Deux choses qui se disent ensemble :** la correction est réelle et se publie avec
la même visibilité qu'une hausse ; et elle est **immatérielle au regard des
réserves** — 0,123 point, contre 2,313 pour l'amplitude du balayage de tolérance et
± 5,0 pour l'erreur d'échantillonnage.

**Et le nombre à ne jamais citer :** le calcul bouge de 0,123 point, l'affichage de
0,2, parce que 89,553 5 et 89,430 1 tombent de part et d'autre d'une frontière
d'arrondi. **« La correction vaut 0,2 point » est faux.**

## Le chiffre

> **Au 3 août 2026, sur les 2 060 kilomètres de voirie française couverts par un
> arrêté d'interdiction de tonnage publié dans DiaLog, 89,4 % ne portent dans
> OpenStreetMap aucune restriction applicable aux poids lourds.**

**74,6 % des 2 050 arrêtés n'y sont pas repris du tout.** Deux chiffres différents
parce qu'ils comptent deux choses différentes — un arrêté régit de 10 m à 52,7 km,
et le 1 % le plus long porte 22,6 % du linéaire.

**Ce chiffre s'accompagne de quatre réserves, sans exception.** Elles sont dans
[methode/enonces-autorises.md](methode/enonces-autorises.md), qui dit aussi ce qui
ne se dit jamais.

## Pourquoi ce dépôt existe

Pour qu'un tiers puisse **refaire la mesure et obtenir autre chose.**

| | |
|---|---|
| [methode/unite-preinscrite.md](methode/unite-preinscrite.md) | **L'unité de mesure, arrêtée et commitée AVANT toute exécution.** Avec les erreurs commises en chemin, et pourquoi |
| [methode/verification-terrain.md](methode/verification-terrain.md) | Le protocole terrain, **pré-inscrit avant le tirage** — bornes, règles d'ambiguïté, calendrier |
| [methode/retractations.json](methode/retractations.json) | **Douze chiffres retirés, avec leur motif.** Un nombre rétracté se marque, il ne se supprime pas |
| [outils/](outils/) | Les outils de mesure. **Aucun paramètre n'a de valeur par défaut** : une valeur absente fait échouer la commande |

## Reproduire

```sh
python3 outils/mesure-metrique.py <dialog.xml> <osm.json> <rapport.json> \
        <pas_test> <pas_dedup> <tolerance> <ang_max> <ecart> <couverture_min> <service>
```

Les sources sont publiques : [DiaLog](https://www.data.gouv.fr/datasets/base-de-donnees-nationale-de-la-reglementation-de-circulation)
en Licence Ouverte 2.0, OpenStreetMap en ODbL. Le rapport machine porte les
empreintes SHA-256 des deux fichiers d'entrée : **une divergence est détectable.**

## Ce que la mesure ne dit pas

- Rien sur une **proportion d'arrêtés** — « X % des arrêtés » ne se dérive jamais du taux métrique
- Rien sur l'**exactitude** des restrictions présentes
- Rien sur la réglementation **non publiée** dans DiaLog
- Rien sur OpenStreetMap **ailleurs qu'en France**, ni à une autre date

## Licences

Arrêtés : **DiaLog / DGITM**, Licence Ouverte / Etalab 2.0.
Comparaison et fond de carte : **© les contributeurs OpenStreetMap**, ODbL.
Outils et documents de ce dépôt : à préciser.
