# Viaklar — la mesure

**[viaklar.com](https://viaklar.com)** — les arrêtés français d'interdiction de tonnage,
confrontés un par un à OpenStreetMap.

## Le chiffre

> **Au 3 août 2026, sur les 2 194 kilomètres de voirie française couverts par un
> arrêté d'interdiction de tonnage publié dans DiaLog, 89,6 % ne portent dans
> OpenStreetMap aucune restriction applicable aux poids lourds.**

**74,5 % des 2 051 arrêtés n'y sont pas repris du tout.** Deux chiffres différents
parce qu'ils comptent deux choses différentes — un arrêté régit de 10 m à 52,7 km,
et le 1 % le plus long porte 22,4 % du linéaire.

**Ce chiffre s'accompagne de trois réserves, sans exception.** Elles sont dans
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
