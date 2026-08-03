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

## Le chiffre

> **Au 3 août 2026, sur les 2 194 kilomètres de voirie française couverts par un
> arrêté d'interdiction de tonnage publié dans DiaLog, 89,6 % ne portent dans
> OpenStreetMap aucune restriction applicable aux poids lourds.**

**Et son second, qui ne se publie jamais sans lui :**

> **74,5 % des 2 051 arrêtés n'y sont pas repris du tout.** Deux chiffres
> différents parce qu'ils comptent deux choses différentes : un arrêté régit de
> 10 m à 52,7 km, et le 1 % le plus long porte 22,4 % du linéaire.

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

> **89,6 % est vraisemblablement un plancher.** Le seul paramètre non contrôlé —
> la tolérance d'appariement — décide de 2,3 points au plus sur la plage
> 10–50 m, et son resserrement fait monter le taux ; les deux attributions
> manifestement fausses de l'échantillon aveugle disparaissent dès 10 mètres.
> **Ce n'est pas une démonstration : 30 mètres reste un choix, et sa valeur juste
> n'est pas établie.**

## Lequel des deux nombres est l'affirmation — décidé le 3 août, **avant** de connaître le plancher

Au retour de la vérification terrain il y aura **deux nombres** : le **89,6 %
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

## Les trois réserves, qui accompagnent le chiffre partout

1. **L'épreuve à l'aveugle borne le risque de fausses absences *au niveau de
   l'arrêté*. Elle ne valide pas la comptabilité de couverture partielle, dont
   dépendent 39 % du chiffre en mètres.**
2. **Les vérificateurs ne sont pas une méthode indépendante mais une
   réimplémentation de la même spécification : leur accord démontre la fidélité
   de l'implémentation, pas la justesse de la mesure.**
3. **Le désaccord géométrique entre DiaLog et OpenStreetMap n'est pas mesuré.**
   Le seul chiffre qui avait circulé était circulaire et a été retiré.

---

## Ce qu'on ne dit jamais

| Interdit | Pourquoi |
|---|---|
| **« X % des arrêtés »** dérivé du taux métrique | Les deux unités divergent de 15 points. C'est faux, et visiblement |
| Toute phrase sur la **pertinence** des arrêtés — « les longs sont ruraux donc moins importants » | Aucune mesure de ce projet ne porte sur la pertinence |
| **Vendre les écarts** — « OSM porte 9 t sur la voie X » | Contient du contenu OpenStreetMap. Interne et journalistique seulement |
| Un **décompte** dans un titre | Trois rétractations de la même phrase de presse. Le titre porte un taux |
| **« Les trois quarts »**, **« 51,1 % »**, **« une cinquantaine de conflits »**, **« huit contradictions »**, **« p95 8,53 m »** | Rétractés. Voir [retractations.json](retractations.json) |

## Ce que le chiffre ne dit pas, et qu'on ajoute si on est interrogé

- Rien sur l'**exactitude** des restrictions présentes : une voie limitée à 3,5 t
  et étiquetée `maxweight=19` compte comme couverte.
- Rien sur la réglementation **non publiée** dans DiaLog.
- Rien sur OpenStreetMap **ailleurs qu'en France**, ni à une autre date.

---

**Toute modification de cette page se date et se justifie.** Un énoncé qui
change sans que la mesure ait changé est un glissement, pas une reformulation.
