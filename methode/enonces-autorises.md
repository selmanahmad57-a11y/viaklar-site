# Les énoncés autorisés

<!-- HORODATAGE DE FRAÎCHEUR. Écrit par outils/tamponner-enonces.py, appelé en
     intégration continue. C'est un TÉMOIN EXTERNE : le contrôle du dépôt est
     administré par la partie qu'il contraint, et un workflow désactivé
     n'émet aucun signal. Cette date, elle, est visible par un lecteur qui
     n'a accès ni à la CI ni au dépôt. Elle ne rend pas le contrôle
     inviolable — elle rend son silence audible depuis l'extérieur. -->

> **Vérifié le 2026-08-03.**
>
> **Si cette date a plus de quelques semaines, les contrôles automatiques ne
> tournent plus** — nombres rétractés, calendrier de la campagne terrain,
> concordance des listes partagées. **Tenez alors tout ce qui suit pour non
> vérifié**, y compris les réserves.

---

**À relire avant d'envoyer un courriel, de faire une diapositive, de répondre à
un journaliste.** Sa seule propriété qui compte est d'être assez courte pour
être relue. Le registre protège les fichiers ; cette page protège les phrases —
imparfaitement, et c'est plus que rien.

---

## ⚠ Correction du 3 août 2026 — les trois nombres ont bougé

**Les chiffres publiés jusqu'au 3 août reposaient sur une attribution fausse et
sont rétractés** : `2 194 km`, `89,6 %`, `74,5 %`, `2 051 arrêtés`. Voir
[retractations.json](retractations.json), entrée `attribution-portee`.

Un arrêté DiaLog est un **conteneur** : il porte de 1 à 8 régulations —
circulation, stationnement, sens unique, vitesse — chacune avec ses propres
critères **et sa propre géométrie**. Le chargeur lisait les tonnages et les
géométries à la portée de l'**arrêté** au lieu de la **régulation**, et
attribuait donc à la circulation ce qui appartenait au stationnement.

**Toutes les valeurs de la colonne « avant » sont RÉTRACTÉES.**

| | avant | après |
|---|---:|---:|
| dénominateur dédupliqué | 2 194,4 km | **2 060,3 km** |
| taux métrique | 89,553 5 % | **89,430 1 %** |
| taux par arrêté | 74,500 2 % | **74,634 1 %** |
| arrêtés mesurés | 2 051 | **2 050** |

*(colonne « avant » : valeurs rétractées)*

**Deux choses se disent ensemble, sous peine de mentir dans un sens ou dans
l'autre :**

> **La correction est réelle et se publie avec la même visibilité qu'une
> hausse.** Elle retire 134,1 km du dénominateur, soit 6,11 %, et **93 arrêtés
> dont le tonnage n'était pas dans une régulation de circulation** — dont
> « Limitation Vitesse – KERUZANVAL », un arrêté de vitesse dans une mesure de
> tonnage.
>
> **Et elle est immatérielle au regard des réserves.** 0,123 point, très en
> dessous de l'amplitude du balayage de tolérance (2,313 points) et de l'erreur
> d'échantillonnage de l'épreuve à l'aveugle (± 5,0 points). Ne dire que la
> première surestimerait ; ne dire que la seconde serait un prétexte pour ne pas
> publier.

### ⚠ Le piège d'arrondi, et le nombre à ne jamais citer

**Le calcul bouge de 0,123 point. L'affichage bouge de 0,2.** 89,553 5 et
89,430 1 tombent de part et d'autre d'une frontière d'arrondi, donc `89,6 %`
devient `89,4 %`.

> **« La correction vaut 0,2 point » est FAUX.** C'est une différence
> d'affichages arrondis, pas une différence de mesures. **L'écart est
> 0,123 point**, et c'est le seul chiffre qui se cite.

### Ce que la correction NE remet pas en cause

- **Le balayage de tolérance a été rejoué** sous l'attribution corrigée :
  amplitude 2,313 points sur 10–50 m, contre 2,3 avant. La réserve tient.
- **L'épreuve à l'aveugle n'a pas été rejouée** — 140 vérifications humaines ne
  se refont pas, et les redessiner détruirait l'aveuglement. **138 de ses
  140 points sont encore dans le champ corrigé** ; les 2 sortants sont à Brest.
  Elle garde 98,6 % de son échantillon, et cela s'énonce plutôt que de la
  présenter comme intacte.

---

## Le chiffre

> **Au 3 août 2026, sur les 2 060 kilomètres de voirie française couverts par un
> arrêté d'interdiction de tonnage publié dans DiaLog, 89,4 % ne portent dans
> OpenStreetMap aucune restriction applicable aux poids lourds.**

**Et son second, qui ne se publie jamais sans lui :**

> **74,6 % des 2 050 arrêtés n'y sont pas repris du tout.** Deux chiffres
> différents parce qu'ils comptent deux choses différentes : un arrêté régit de
> 10 m à 52,7 km, et le 1 % le plus long porte 22,6 % du linéaire.

## Le cas qui explique l'écart

> **Cassel — « Traversée de Cassel interdite aux véhicules… », 43,6 km, couverts
> à 0,7 %.** Le verdict par arrêté dit « couvert » : une restriction existe. La
> mesure en mètres dit « absent à 99,3 % ». **Aucun des deux n'est faux.**

## Sur la vérification

> **Deux méthodes indépendantes — l'une par comptabilité de couverture, l'autre
> par échantillonnage aveugle du linéaire — donnent le même ordre de grandeur, ce
> qui borne l'erreur d'ensemble sans certifier chaque composante.**

## Sur le mot « plancher »

Il ne se cite **jamais seul** :

> **89,4 % est vraisemblablement un plancher.** Le seul paramètre non contrôlé —
> la tolérance d'appariement — décide de 2,313 points au plus sur la plage
> 10–50 m, et son resserrement fait monter le taux : à 10 mètres il vaut
> 90,7 %. **Ce n'est pas une démonstration : 30 mètres reste un choix, et sa
> valeur juste n'est pas établie.**

## Lequel des deux nombres est l'affirmation — décidé le 3 août, **avant** de connaître le plancher

Au retour de la vérification terrain il y aura **deux nombres** : le **89,4 %
mesuré** et un **plancher**. Lequel entre dans l'affirmation se décide maintenant,
pendant qu'on ignore ce que vaut le second. Après, ce ne serait plus un choix de
méthode.

> **L'affirmation est le chiffre MESURÉ. Le plancher est une réserve, et il se
> cite avec lui.**

**Pourquoi celui-là :** le mesuré est ce que produit la méthode sous la définition
pré-inscrite. Le plancher est un **pire cas sous une hypothèse défavorable**
(`p_couvert = 0`) dont on sait qu'elle n'est pas l'attendu. En faire l'affirmation
serait sous-déclarer systématiquement — l'erreur inverse, et une erreur quand
même.

> **Mais le sens attendu de la correction se dit dans la même phrase :** un arrêté
> mort ne laisse rien à taguer, donc il a une raison de se trouver du côté absent.
> **La correction attendue est vers le bas.** Le mesuré est donc un chiffre dont
> on sait qu'il est plutôt haut que bas, et cela s'énonce.
>
> **Le 3 août l'a vérifié une fois :** la correction d'attribution est allée vers
> le bas, comme annoncé. Un cas n'est pas une loi, et il vaut mieux que rien.

## Les quatre réserves, qui accompagnent le chiffre partout

1. **L'épreuve à l'aveugle borne le risque de fausses absences *au niveau de
   l'arrêté*. Elle ne valide pas la comptabilité de couverture partielle, dont
   dépendent 39 % du chiffre en mètres.**
2. **Les vérificateurs ne sont pas une méthode indépendante mais une
   réimplémentation de la même spécification : leur accord démontre la fidélité
   de l'implémentation, pas la justesse de la mesure.**
3. **Le désaccord géométrique entre DiaLog et OpenStreetMap n'est pas mesuré.**
   Le seul chiffre qui avait circulé était circulaire et a été retiré.
4. **La complétude de DiaLog n'est pas établie, et le manque pousse le chiffre
   VERS LE HAUT.** Hors du périmètre du décret du 24 mars 2026, le dépôt dans
   DiaLog est **volontaire**. Un arrêté vivant absent du flux n'entre pas au
   dénominateur — et il est très probablement absent d'OpenStreetMap aussi.
   **L'inclure ferait donc monter le taux d'absence.**

---

## Ce qu'on ne dit jamais

| Interdit | Pourquoi |
|---|---|
| **« X % des arrêtés »** dérivé du taux métrique | Les deux unités divergent de 14,8 points. C'est faux, et visiblement |
| Toute phrase sur la **pertinence** des arrêtés — « les longs sont ruraux donc moins importants » | Aucune mesure de ce projet ne porte sur la pertinence |
| **Vendre les écarts** — « OSM porte 9 t sur la voie X » | Contient du contenu OpenStreetMap. Interne et journalistique seulement |
| Un **décompte** dans un titre | Trois rétractations de la même phrase de presse. Le titre porte un taux |
| **« La correction vaut 0,2 point »** | Différence d'affichages arrondis. La correction vaut **0,123 point** |
| **« Les trois quarts »**, **« 51,1 % »**, **« une cinquantaine de conflits »**, **« huit contradictions »**, **« p95 8,53 m »**, **« 89,6 % »**, **« 2 194 km »**, **« 74,5 % »**, **« 2 051 arrêtés »** | Rétractés. Voir [retractations.json](retractations.json) |

## Ce que le chiffre ne dit pas, et qu'on ajoute si on est interrogé

- Rien sur l'**exactitude** des restrictions présentes : une voie limitée à 3,5 t
  et étiquetée `maxweight=19` compte comme couverte.
- Rien sur la réglementation **non publiée** dans DiaLog — et c'est la réserve 4,
  pas une nuance de plus.
- Rien sur OpenStreetMap **ailleurs qu'en France**, ni à une autre date.
- Rien sur les **arrêtés sans tonnage** : les interdictions exprimées seulement
  par dérogation — « interdit à tous sauf desserte locale » — ne sont pas dans ce
  dénominateur. Les y faire entrer serait une **extension de définition**, pas une
  correction, et elle relèverait le chiffre. Elle n'a pas été faite.

---

**Toute modification de cette page se date et se justifie.** Un énoncé qui
change sans que la mesure ait changé est un glissement, pas une reformulation.
