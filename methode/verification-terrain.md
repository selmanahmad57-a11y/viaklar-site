# Vérification terrain — protocole pré-inscrit

**Écrit le 3 août 2026, AVANT le tirage.** Aucun site n'a été tiré à l'heure où
ces lignes sont écrites. C'est la condition qui rend le reste défendable.

---

## Pourquoi celle-ci, et pas les deux autres chantiers

**C'est la seule des trois qui puisse faire BAISSER le chiffre.**

- **BD TOPO** change le référentiel routier : elle teste le filtre de
  carrossabilité, pas l'arrêté.
- **Les remèdes A et B** sur la table de liaison ne touchent pas au chiffre, et
  leur **latence est nulle** — aucun tiers à attendre. Ils se font la veille du
  jour où ils comptent, c'est-à-dire à l'ouverture de l'accès payant. Les
  commencer maintenant serait refaire l'erreur de la lettre au LWG **dans
  l'autre sens** : agir tôt sur ce qui n'a aucun délai d'acheminement.

## Ce que l'épreuve aveugle n'a pas établi

Les 20 sur 20 ont établi qu'**OpenStreetMap ne porte pas la restriction**. Ils
n'ont pas établi que **la restriction existe sur le terrain**.

> Arrêté abrogé sans retrait du flux · panneau déposé · ouvrage reconstruit ·
> limitation temporaire devenue permanente dans la base et disparue de la route.
>
> **Dans tous ces cas le mètre est compté réglementé alors qu'il ne l'est plus.**

**C'est le seul mode de défaillance qui pousse 89,6 % vers le bas, et l'appareil
ne peut pas le voir seul : les deux sources qu'il compare sont documentaires.**

Et il y a une **date**. La page des énoncés autorisés est écrite ; le chiffre est
donc en position d'être affirmé publiquement **avant que la seule mesure capable
de le contredire ait été tentée.** Ce n'est pas « quand j'aurai le temps ».

---

## Le protocole

### 1. Tirage au mètre, jamais à l'arrêté

Les absences se concentrent sur les longs linéaires — Cassel, 43,6 km. **Tirer
par arrêté surpondérerait les emprises courtes**, c'est-à-dire précisément celles
qui pèsent le moins dans les 1 965,2 km absents.

Le tirage se fait sur les **cellules absentes**, uniformément en longueur, avec la
même machinerie que l'épreuve aveugle du linéaire.

### 2. Témoins mélangés, correspondance scellée

Une part des sites est tirée dans l'ensemble **couvert**. La liste remise à
l'observateur ne porte **que des coordonnées** — ni verdict, ni tonnage, ni
description d'arrêté, ni indication du nombre de témoins. Même dispositif que
pour les 20 de l'épreuve aveugle.

**Les témoins ne testent pas la carte, ils testent l'observateur** : quelqu'un qui
rapporte « aucun panneau » partout se trahit sur eux.

### 3. Table de décision, fixée avant le départ

**Deux colonnes distinctes, à ne jamais fusionner :**

| Constat | Colonne A — panneau réglementaire | Colonne B — gabarit physique |
|---|---|---|
| Panneau de tonnage présent et lisible | **oui**, valeur relevée | sans objet |
| Aucun panneau visible dans les deux sens | **non** | à relever quand même |
| Ouvrage bas, étroit, ou tonnage structurel | — | **mesuré ou estimé, avec la méthode** |

> **Un pont bas sans panneau et un panneau sans obstacle sont deux résultats
> différents, pas deux façons de dire « conforme ».** Les fusionner effacerait
> exactement la distinction que le produit vend.

**Ce qui compte comme défaillance pour la borne :** colonne A négative — aucun
panneau réglementaire, dans aucun sens, sur le site tiré. La colonne B est
relevée pour le corpus de vérité terrain (§10), pas pour cette borne.

### 4. Biais d'accessibilité

> **Tirer d'abord, se déplacer ensuite.** Un site non atteint **se consigne comme
> non atteint**, il ne se remplace pas par le suivant sur la route.

Remplacer un site inaccessible par un site commode, c'est laisser l'itinéraire
choisir l'échantillon — l'invariante du §18 sur l'échantillon sélectionné par
autre chose que le mécanisme évalué, appliquée à une voiture.

### 5. Engagement de publication, écrit avant le tirage

> **Le résultat se publie quel qu'il soit, et une baisse du taux se publie avec la
> même visibilité qu'une hausse.**

C'est la contre-mesure du §4.bis — celle contre l'intérêt que le positionnement
commercial crée — appliquée au seul endroit où elle peut mordre.

---

## Ce que ça achète, chiffré d'avance

| Résultat | Ce qu'il établit |
|---|---|
| **15 sites, 0 défaillance** | Borne haute de **20 %** sur le taux d'arrêtés fantômes (règle de trois, 3/15) |
| Effet d'un tel taux sur le chiffre | **89,6 % → 87,3 %** — même ordre que l'amplitude du balayage de tolérance |
| **1 défaillance** | La borne monte ; l'échantillon reste une borne |
| **2 défaillances ou plus** | **ARRÊT.** L'échantillon devient une estimation, pas une borne, et il est trop petit pour ça. On replanifie avec un effectif calculé |

> **C'est une borne faible, et c'est la première information non nulle sur cet
> axe.** Aucun outil du dépôt ne peut la produire.

**Le calcul, pour qu'il soit vérifiable — et la correction d'une première version.**

L'échantillon est tiré dans les cellules **absentes**. La borne porte donc sur
**cette population**, pas sur le linéaire total :

> 20 % de 1 965,2 km = 393,0 km fantômes
> (1 965,2 − 393,0) / (2 194,4 − 393,0) = **87,3 %**

> ⚠ **Une première version écrivait 86,9 %**, en appliquant les 20 % au linéaire
> **total** — 438,9 km. L'arithmétique était juste, **l'hypothèse ne
> correspondait pas au cadre de tirage.** J'avais vérifié le calcul sans vérifier
> ce qu'il supposait ; c'est la même faute qu'une docstring exacte sur un code qui
> fait autre chose.
>
> **Et l'écart de 0,4 point importe moins que ce qu'il révèle :** cette borne ne
> dit rien des arrêtés fantômes dans l'ensemble **couvert** — un arrêté abrogé
> dont OSM porte encore le tag. L'échantillon ne les touche pas, et **aucune borne
> ne les couvre.**

**Ce que chaque niveau d'effort achète**, puisque les 20 sites s'étalent sur
1 051 km et qu'une campagne partielle reste honnête (§4, un site non atteint se
consigne) :

### ⚠ Estimateur unique — décidé le 3 août, et le motif s'écrit maintenant

**Une première version mélangeait deux estimateurs dans le même tableau** : la
règle de trois pour la colonne favorable, **Clopper-Pearson** pour les lignes
défavorables. Deux estimateurs de la même quantité, côte à côte, sans que rien ne
dise lequel produit quelle cellule.

> **La règle de trois ne s'étend pas à `k > 0`. Clopper-Pearson couvre les cinq
> cellules. Le choix se tranche donc sur la COUVERTURE, pas sur la préférence.**

**Et il faut écrire ce qu'il coûte, parce qu'il relève le chiffre publié partout :**

| Sites visités | Règle de trois | Clopper-Pearson | Écart |
|---|---|---|---|
| 9 | 83,05 % | **84,82 %** | **+1,77** |
| 14 | 85,72 % | **86,40 %** | +0,68 |
| 20 | 87,27 % | **87,53 %** | +0,26 |

> **Trois cellules, trois fois dans le sens qui arrange.** Le motif retenu est
> *« Clopper-Pearson partout parce que c'est le seul estimateur qui couvre les
> cinq cellules »* — écrit **avant** que ce soit « Clopper-Pearson partout » tout
> court, et avant qu'aucun résultat ne soit connu.

### Deux couches, et ne jamais les confondre

| Couche | Règle |
|---|---|
| **Choix de l'estimateur** | sur sa **COUVERTURE** — Clopper-Pearson, défini pour `k > 0` là où la règle de trois ne l'est pas |
| **Publication** | **afficher les DEUX** quand ils diffèrent |

> **Le motif n'est jamais « le plus prudent gagne ».** Une première version de la
> page publique l'avait écrit ainsi, et c'était **une seconde règle capable
> d'annuler la première** : à trois ambigus, le conservateur serait la règle de
> trois, et l'invoquer là ferait rentrer le mélange retiré le matin même.
>
> **Et une politique de toujours prendre le prudent est un biais systématique.**
> C'est la décision du §3.4 j prise dans l'autre sens : le plancher n'est pas
> l'affirmation, parce que **sous-déclarer par règle reste une erreur par
> règle.**
>
> La règle de trois n'était pas fausse : c'est une **approximation conservatrice**
> de Clopper-Pearson à `k = 0`. On perd du conservatisme et on gagne un estimateur
> unique. **C'est un arbitrage, pas une amélioration.**

| **Sites VISITÉS** | Absents (¾, arrondi) | Borne CP | Plancher | Portée |
|---|---|---|---|---|
| **9** — les deux grappes | 7 | 34,82 % | **84,82 %** | **régionale** |
| 14 | 10 | 25,89 % | 86,40 % | régionale |
| **20** | **15** | **18,10 %** | **87,53 %** | **nationale** |

> ⚠ **Trois arrondis d'affilée dans cette table, tous dans le même sens.**
>
> | | Cause | Coût | À qui |
> |---|---|---|---|
> | 82,9 % | 6,8 absents au lieu de 6,75 | +0,25 pt | moi |
> | 82,7 % | **borne arrondie 44,44 → 44 AVANT le calcul** | +0,11 pt | mon interlocuteur |
> | — | calcul sur mes km d'affichage au lieu des mètres exacts du rapport | +0,003 pt | moi |
>
> **La valeur exacte est 82,6466 %.**
>
> **Un arrondi INTERMÉDIAIRE est invisible là où un arrondi final se voit, et il
> hérite d'une direction** — borne rabotée, plancher relevé. Il vaut ici **trente
> fois** l'écart affichage/exact, lequel n'est négligeable que par chance : c'est
> la même faute que les 220 m contre 38 m, sans les conséquences.
>
> **Toutes les bornes de cette table sont désormais écrites non arrondies.**

> **Il n'y a pas de partiel bon marché.** Entre s'arrêter aux grappes et finir, il
> y a **4,6 points ET le passage du conditionnel au national.** L'ancienne table
> faisait croire à un plateau ; **le voyage est presque tout-ou-rien.**

> ⚠ **Correction d'une première version de cette table.** Elle indexait sur les
> *sites absents* tout en étant lue comme des *sites visités* — or seuls trois
> quarts des sites tirés sont du bras absent. **« Cinq sites » donne une borne à
> 80 %, pas à 60 %**, et le « saut rentable à cinq » que j'avais annoncé
> n'existe pas.
>
> **Le premier palier utile est à neuf**, et il n'est atteignable que par les
> grappes.
>
> **Et la planification n'a pas besoin de rompre le sceau :** la borne se calcule
> après, sur les sites absents effectivement atteints. Visiter ce qui est
> joignable, consigner le reste — le sceau tient, la borne suit.

---

## Paramètres

| Paramètre | Valeur | Ce qui la justifie |
|---|---|---|
| `SITES_ABSENTS` | **15** | Donne la borne à 20 %. En deçà, la borne cesse d'être informative |
| `SITES_TEMOINS` | **5** | Même proportion que l'épreuve aveugle (20 + 5). Ils coûtent du déplacement et testent l'observateur, pas la carte |
| `GRAINE` | déclarée au tirage | Un tirage qu'on ne peut pas rejouer n'est pas un tirage, c'est un choix |

---

## Amendement examiné le 3 août — REFUSÉ, et le refus est daté

**L'objection, et elle est juste :** le chiffre est **invariant à un taux de
fantômes uniforme.**

> Si une fraction `p` du linéaire est fantôme des deux côtés,
> `A(1−p) / T(1−p) = A/T`. **Vérifié : 89,56 % à p = 0, 10, 20 et 40 %.**
>
> **L'estimand n'est donc pas le taux de fantômes, c'est l'ÉCART** entre celui de
> l'ensemble absent et celui de l'ensemble couvert.

**Et l'écart ne peut pas être posé à zéro, parce qu'un mécanisme asymétrique
existe :** OpenStreetMap reflète le terrain. **Un arrêté mort ne laisse rien à
taguer**, donc il a une raison de se trouver du côté absent. Aucun mécanisme
symétrique ne pousse dans l'autre sens. **Le biais attendu est adverse.**

**L'amendement proposé :** tirer 8 sites de plus dans la strate couverte, sceller
à 28, pour avoir deux bras au lieu d'un bras et cinq témoins.

**Refusé, sur trois calculs :**

| | |
|---|---|
| **Un** | **Le pire cas est toujours à `p_couvert = 0`.** Borner le bras couvert **n'améliore jamais le plancher publiable** — le plancher est ce qui est publié, et il est insensible à cette borne |
| **Deux** | **À budget de déplacement égal, l'amendement dégrade le plancher.** 15 sites atteints : **86,3 % sans, 84,3 % avec.** L'amendement coûte deux points de plancher |
| **Trois** | **Sept sites ne font pas un bras.** Ils bornent `p_couvert` à 43 % — inutilisable pour un différentiel de quelques points. Il en faudrait **une trentaine**, et c'est une autre campagne |

> **À ce budget, aucun des deux bras ne peut estimer le différentiel. Un seul peut
> borner le plancher.** Le tirage reste **15 absents + 5 témoins**.

**Et le refus ne tient pas que sur le pire cas — il tient sur toutes les
branches.** Un bras à zéro fantôme produit une borne **supérieure** sur
`p_couvert`, quand relever le plancher exigerait une borne **inférieure**. **Le
bras couvert ne peut aider qu'en TROUVANT des fantômes : c'est un pari, pas une
mesure.**

Et le pari perd même quand il gagne :

| Branche | `p_absent` | `p_couvert` | Plancher |
|---|---|---|---|
| Sans amendement, 15 visités | ≤ 26,8 % | ≥ 0 | **86,3 %** |
| Avec amendement, **2 fantômes trouvés sur 7** — branche favorable | ≤ 37,5 % | ≥ 5,3 % | **85,0 %** |

> **La branche chanceuse coûte encore 1,3 point.**

**Ce que le refus concède, et qu'il faut écrire :** le plancher borné est le
**pire cas**, pas la correction attendue. La correction réelle peut être positive
— si les fantômes sont plus nombreux du côté couvert, le taux **monte**. **Cette
quantité-là n'est pas mesurée et ne le sera pas par cette campagne.**

**Et une correction de chiffre au passage :** le « 0,64 n » annoncé dans
l'amendement donnait une borne à 31 %. Recalculé, la proportion est 15/28 = 0,54,
donc **37 %**. L'amendement coûtait plus qu'annoncé.

## Ce que 20 sites achètent réellement : une détection, pas une estimation

| Sites du bras absent | Détecte `p = 50 %` | Détecte `p = 20 %` |
|---|---|---|
| 5 | 97 % | 67 % |
| 10 | 99,9 % | 89 % |
| 15 | 100 % | 96 % |

> **Un problème grossier ne survit pas à cinq sites. Un écart de quelques points
> reste invisible à vingt-huit, et le restera.** C'est tout ce que 1 051 km
> peuvent acheter — **et c'est une raison de partir, pas une raison de gonfler ce
> qu'on en rapportera.**

## Ordre de visite — tranché le 3 août, avant le départ

**Le problème :** cinq sites parcourus dans l'ordre routier ne sont pas un
sous-échantillon des vingt, **ce sont les cinq premiers d'une ligne.** La règle
de trois ne vaut que sur l'ensemble tiré. Un arrêt à cinq **ne donne pas une
borne nationale** — il borne la région traversée.

Et la masse est à **Lyon (6 sites)** et **Aix-Marseille (3)**. Un préfixe partant
de Brest les manque tous les deux.

> **DÉCISION : commencer par les grappes.** Lyon, puis Aix-Marseille. **Neuf
> sites, deux déplacements**, là où sont les mètres.
>
> **Toute complétion partielle produit une borne CONDITIONNELLE à la portion
> parcourue, jamais présentée comme nationale.** La borne devient nationale au
> vingtième site, pas avant.

**Pourquoi trancher maintenant plutôt qu'au retour :** le choix se ferait alors au
moment où l'on est fatigué et où cinq sites ressemblent à un résultat.

*(Le regroupement se lit sur les coordonnées de la feuille de route, qui sont
publiques. **Il ne rompt pas le sceau** : les natures restent scellées.)*

### Le défaut de l'ordre par grappes, et son remède

**L'ordre par grappes optimise le repli.** Il place les neuf sites faciles en tête
et **laisse les onze plus dispersés pour la fin** — c'est-à-dire au moment où
l'envie de s'arrêter sera la plus forte, et où **82,7 % ressemblera à un
résultat.**

C'est le même mécanisme que la règle d'arrêt sans prénom : un engagement qui
repose sur une décision à prendre quand on est fatigué.

> **REMÈDE, posé avant le départ et non au retour de Lyon : les onze derniers
> sites portent des dates.**
>
> | Étape | Sites | Avant le |
> |---|---|---|
> | Grappe 1 — Lyon | 6 | **vendredi 14 août** |
> | Grappe 2 — Aix-Marseille | 3 | **vendredi 21 août** |
> | Dispersés, première moitié | 5 | **dimanche 13 septembre** |
> | Dispersés, derniers | 6 | **mercredi 30 septembre** |
> | ***Publication du résultat terrain*** | — | ***15 octobre*** |
>
> **La dernière ligne est celle qui fait tenir les autres.** Sans publication
> datée, les quatre premières sont des intentions.

**Et une date ne tient que si son dépassement publie quelque chose.**
[campagne-terrain.json](campagne-terrain.json) porte l'état ;
[verifier-campagne.py](../outils/verifier-campagne.py) **échoue** quand une étape
est en retard sans mise à jour, et il tourne en intégration continue. **L'échec
impose de consigner l'avancement ou de consigner l'incomplétude :**

> *« Campagne de vérification terrain incomplète au [date] — N sites sur 20. La
> borne est conditionnelle à la portion parcourue et n'est pas nationale. »*

**Publié avec la même visibilité que le chiffre.** C'est la contre-mesure du
§4.bis appliquée au temps plutôt qu'au résultat.

#### Les six derniers sites ne sont pas achetés pour de la précision

| De → à | Gain |
|---|---|
| 9 → 14 sites | **+3,3 points** |
| 14 → 20 sites | **+1,3 point** — *et la totalité de la portée nationale* |

> **Ils sont achetés pour le droit d'écrire « France ».** C'est le profil exact de
> ce qu'on abandonne : le plus coûteux, le moins rentable numériquement, et le
> seul dont dépend l'énoncé.

#### Un changement d'ordre examiné et décliné

**L'objection :** l'ordre par grappes maximise la valeur d'un voyage interrompu ;
placer quelques dispersés *sur la route* de Lyon maximiserait la probabilité
qu'il ne le soit pas — et le second l'emporte maintenant que le partiel vaut
4,6 points de moins et reste régional.

**Décliné**, pour une raison et une seule : **le mécanisme des dates traite le même
risque plus directement.** Un voyage interrompu ne l'est plus en silence — il
publie son incomplétude. Rouvrir un protocole commité a un coût propre, et il
n'est pas payé par un gain que le calendrier obtient déjà.

## Les sites inclassables — écrit le 3 août, avant d'en connaître un seul

**L'épreuve aveugle a eu zéro ambigu. Le terrain en aura :** panneau illisible,
ouvrage en travaux, site atteint mais inclassable. **Ce n'est pas un site non
atteint** — celui-là est déjà traité au §4.

> **Et un inclassable a une disposition favorable disponible, qui est aussi la
> plus défendable sur le fond :** le compter comme restriction présente resserre
> la borne et relève le plancher. **Un panneau illisible reste un panneau.**
>
> **C'est précisément ce qui la rend dangereuse.** Le geste favorable est le plus
> naturel au bord de la route, après trois heures de conduite, devant un panneau à
> moitié effacé qui « veut clairement dire 3,5 ».

### Règle 1 — on ne classe jamais au bord de la route

> **Un inclassable ne se tranche pas sur place. Il se DOCUMENTE :** photographie,
> ce qui est visible, ce qui ne l'est pas, l'obstacle à la lecture.
>
> **La classification se fait hors site, sur le dossier.**

**« Par quelqu'un qui n'a pas conduit » attend une personne qui n'existe pas.**
L'équipe est d'une personne. Si c'est le même trois semaines plus tard, la
séparation est **temporelle et non personnelle** — plus faible, mais réelle.

> **Le remède est celui appliqué partout ailleurs ici : retirer l'identité.**
>
> Le dossier de classification ne porte **ni coordonnées, ni grappe, ni rang de
> visite, ni date de passage** — la photographie, ce qui est lisible, ce qui ne
> l'est pas, et rien d'autre. **En lot mélangé.**
>
> **Le classificateur, même si c'est le conducteur, ne peut alors pas savoir ce
> que chaque verdict fait au chiffre.** C'est le dispositif de l'épreuve aveugle,
> appliqué à sa propre main.

**Et le dépouillement a une porte de derrière : l'EXIF.** Les photographies
portent leurs **coordonnées GPS et leur horodatage**. Un dossier dépouillé les
réintroduirait sans qu'on le voie.

**Quatre canaux, tous traités par [constituer-dossier.py](../outils/constituer-dossier.py) :**

| Canal | Traitement |
|---|---|
| **EXIF** | Segments `APPn` et `COM` du JPEG, morceaux auxiliaires du PNG — **retirés** |
| **Nom de fichier** | `IMG_20260814_143022.jpg` dit la date et l'heure → `piece-001.jpg` |
| **Date du fichier** | `mtime` et `atime` figés à une date unique |
| **Ordre du lot** | L'ordre de visite est l'ordre géographique → mélangé, graine déclarée |

> **Une instruction écrite — « penser à retirer l'EXIF » — est la classe de
> garde-fou qui échoue :** elle dépend qu'on y pense, le jour où l'on est pressé.
> L'outil **retire puis VÉRIFIE**, et **refuse de produire le dossier** si une
> seule pièce porte encore un témoin (`Exif`, `GPS`, XMP, ICC).
>
> **Éprouvé par la panne pour laquelle il existe :** sur une pièce portant
> `GPSLatitude 47.66806` et `DateTime 2026:08:14`, tout disparaît ; et avec le
> dépouilleur neutralisé exprès, **le dossier n'est pas produit du tout.**
>
> Aucune dépendance externe — ni `exiftool`, ni ImageMagick, ni Pillow. **Aucun
> n'est présent sur cette machine, et un outil qui ne tourne pas est un outil
> absent.**

### Le résidu, qui ne se ferme pas

> **La photographie montre l'endroit.** Un numéro de route, un panneau
> d'agglomération, un relief reconnaissable.

**Et ce n'est pas un canal à boucher : c'est du contenu, et le contenu est la
preuve.** Recadrer retirerait souvent ce qui rend la pièce inclassable — le
panneau à moitié effacé est indissociable du carrefour où il se trouve.

> **Le dépouillement porte sur ce qui ACCOMPAGNE l'image, jamais sur ce qu'elle
> MONTRE.** Un classificateur attentif peut donc, sur certaines pièces,
> reconnaître le site.

**Consigné comme résidu, pas comme oubli.** Il ne se ferme pas : l'aveuglement du
classificateur est **partiel par construction**, et le prétendre complet serait
exactement l'écart entre ce qu'un dispositif garantit et ce qu'il donne
l'impression de garantir — celui que ce dépôt passe son temps à traquer.

**Ce qui reste vrai malgré lui :** le classificateur ne connaît ni le rang de
visite, ni la grappe, ni la date, ni **la nature du site — absent ou témoin**. Or
c'est cette dernière, et elle seule, qui dit ce qu'un verdict fait au chiffre.
**Reconnaître un carrefour ne la donne pas.**

### Règle 2 — le résultat se publie en INTERVALLE, et le primaire est le défavorable

**Coût chiffré d'avance, sur 20 sites visités et un bras absent de 15 :**

| Ambigus | Borne CP | Défavorable — comptés échecs | Favorable — comptés présents | Intervalle |
|---|---|---|---|---|
| 0 | 18,10 % | **87,53 %** | 87,53 % | — |
| **1** | 27,94 % | **86,07 %** | 87,53 % | **1,46 pt** |
| 2 | 36,34 % | 84,51 % | 87,53 % | 3,02 pt |
| **3** | 43,98 % | **82,77 %** | 87,53 % | **4,77 pt** |
| 4 | 51,08 % | 80,75 % | 87,53 % | 6,78 pt |

> **Le chiffre publié est la borne DÉFAVORABLE. L'intervalle se publie avec lui.**
>
> Non parce que le défavorable est plus juste — il ne l'est pas, un panneau
> illisible est un panneau — mais parce que **c'est la seule disposition qu'on ne
> peut pas atteindre en souhaitant un meilleur résultat.** L'écart entre les deux
> est l'information, et il se publie plutôt que de se résoudre.

### Règle 3 — l'ambiguïté ne déclenche pas la règle d'arrêt

La règle du §« ce que ça achète » — **arrêt à deux défaillances** — vise les
**fantômes confirmés**, pas les inclassables. Sans cette précision, deux panneaux
illisibles arrêteraient une campagne que rien ne contredit.

### Règle 4 — le seuil au-delà duquel c'est la feuille qui a échoué

> **Si plus de 4 sites visités sur 20 sont inclassables, le problème n'est pas le
> réseau, c'est la feuille de route.** Les questions posées ne se répondent pas sur
> le terrain, et il faut les reprendre avant de continuer — comme la consigne des
> vérificateurs aveugles se serait reprise au-delà de 20 % de désaccord.

À 4 ambigus l'intervalle atteint 6,8 points, soit plus que tout ce que la
campagne entière achète. **Au-delà, elle ne mesure plus rien.**

---

**Aucun ajustement de ce protocole après le tirage.** Un amendement reste
possible, il s'écrit ici, daté, avec son motif — et le motif ne peut pas être ce
qu'on a vu sur le terrain.
