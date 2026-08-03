# L'unité de mesure, pré-inscrite

**État : définition arrêtée le 3 août 2026 avant toute exécution ; mesure faite, épreuve
passée, artefacts réénoncés.**
**Aucun ajustement n'est autorisé après lecture d'un résultat — voir §3.4 et §3.5.**

---

## Pourquoi ce document existe

L'audit du 2 août 2026 a mis en cause **2 045**, le dénominateur de toutes les mesures
publiées du projet. Il l'a d'abord fait pour une mauvaise raison — voir la rectification
en section 0 — puis pour une bonne : **ce dénominateur est découpé par la géométrie de
collecte, pas par le périmètre de la question**, et il faut donc le rechoisir.

Le piège de la réparation est immédiat et il faut le nommer avant de tomber dedans :

> Le jour où le générateur est écrit, il produira un nombre. S'il ne sort pas 2 045, il y
> aura sous les yeux une carte, une page et deux cents lignes de document qui disent
> 2 045 — et la tentation sera de chercher la définition qui reproduit 2 045.
>
> **Ce serait rétro-concevoir une définition pour qu'elle corresponde à l'artefact d'un
> script perdu.** Exactement l'inverse de ce que l'audit demande.

D'où la règle, qui est la pré-inscription du §9 appliquée à une définition au lieu d'un
résultat :

> **L'unité se choisit sur ses mérites, par écrit, avant toute exécution. Ce qui sort est
> le compte, et tous les nombres en aval se réénoncent contre lui.**

Le même geste que les trois commits horodatés de l'épreuve aveugle, porté à un endroit où
il ne l'avait pas encore été. **Le besoin y est plus fort**, parce que 2 045 est désormais
un point d'ancrage avec une carte derrière lui.

---

## 0. Rectification préalable — ce que 2 045 est, puisque je l'ai dit faux

Une première version de l'audit affirmait que **2 045 n'avait pas de définition
reconstructible**. C'était faux. L'outil du dépôt le reproduit en trente-trois secondes,
avec les cinq verdicts au chiffre près, et **imprime la définition à chaque exécution** :

```
emprise déduite du fichier OSM     : -4.600,42.883 → 7.380,51.005
arrêtés retenus dans cette emprise : 2045
```

**2 045 + 7 hors emprise = 2 052**, le dénominateur corrigé du §11.9 : la chaîne se referme.

> **L'erreur venait d'une réimplémentation.** J'avais réécrit le filtre dans un script
> jetable — qui mésinterprétait les `GeometryCollection` — au lieu de lancer l'outil.
> **Réimplémenter pour vérifier, c'est fabriquer un second sujet d'erreur et le croire sur
> parole parce qu'on vient de l'écrire.**

**Le défaut réel est autre, et il justifie à lui seul de rechoisir l'unité :** le
dénominateur est découpé par la **géométrie de collecte**. Les sept arrêtés exclus sont
dans le champ — interdictions françaises géolocalisées — mais hors de la boîte englobante
du téléchargement OSM, l'un d'eux par **38 mètres**. Élargir la collecte augmenterait le
dénominateur. Et le défaut est **entièrement reproductible**, donc rien ne le signale.

> **Toute définition retenue en section 3 doit déclarer son périmètre, et non le déduire
> de ce qui a été téléchargé.**

---

## 1. Ce que mesuraient réellement les mesures existantes

Vérifié en lisant le code, sans se fier aux commentaires — ils font partie de ce qui est
mis en cause. **Les trois constats ci-dessous ont été soumis à trois relecteurs
indépendants chargés de les réfuter, et ont été confirmés tous les trois.**

| Chiffre publié | Ce qu'il prétendait être | Ce qu'il est |
|---|---|---|
| **73,8 %** | « aucun mètre de corridor couvert, pondéré par la longueur » | **1 509 arrêtés / 2 045 arrêtés.** Dénominateur en arrêtés. |
| **14,5 %** | « part moyenne du corridor portant un tonnage OSM » | **Moyenne de ratios par arrêté**, pas ratio de sommes. Un arrêté de 20 m pèse autant qu'un de 20 km. |
| Le ratio interne | « pondérée par la longueur » (docstring) | `dedans / len(arrete["points"])` — **une fraction de sommets.** |

> **Aucune des deux mesures dites « pondérées par la longueur » ne l'est.** L'une compte
> des arrêtés au dénominateur, l'autre moyenne des ratios ; et le ratio interne aux deux
> est une fraction de **sommets de polyligne**, pas de mètres.
>
> **Les sommets ne sont pas équidistants.** Leur densité dépend de l'outil de numérisation
> du fournisseur et de la sinuosité du tracé, pas de la longueur au sol. Une ligne droite
> de 2 km porte deux sommets ; 200 m de virages en portent cinquante.
>
> **Conséquence : la mesure présentée comme la plus robuste, celle qui devait échapper au
> problème d'unité, y était soumise deux fois.** Et c'est le commentaire du code qui a
> propagé l'erreur dans le document — une docstring affirmait une propriété que le code
> n'avait pas.

**Deux précisions apportées par les relecteurs, que je n'avais pas vues :**

> **Une —** `points.extend(...)` concatène **toutes** les géométries d'un arrêté en une
> seule liste plate. Un arrêté portant dix tronçons voit ses sommets simplement empilés :
> **un tronçon court mais richement numérisé pèse davantage qu'un long tronçon
> rectiligne.** Aucune renormalisation par tronçon. Le biais joue donc à deux échelles, à
> l'intérieur d'un tronçon et entre les tronçons d'un même arrêté.
>
> **Deux —** le glissement sommets → longueur est **systématique dans le fichier**, pas
> ponctuel : la fonction de recouvrement porte une docstring honnête (« fraction des
> sommets de la voie OSM ») et est requalifiée en « recouvrement **linéaire** » dans la
> fonction qui l'appelle. Corriger une docstring ne suffisait pas ; il fallait balayer le
> mot.

**Et un point où les relecteurs m'ont nuancé, dans le sens de la prudence :** l'indicateur
« arrêtés dont aucun sommet n'est couvert » est *presque* équivalent à « aucun mètre
couvert ». Zéro sommet couvert implique en pratique zéro mètre couvert, **sauf** le cas
d'un long segment dont les deux extrémités sortent de la tolérance mais dont le milieu
passe dessous — compté 0 % à tort. Le **73,6 %** est donc moins faux que le 14,6 % ; c'est
la moyenne, présentée comme « couverture linéaire », qui est franchement une fraction de
sommets.

---

## 2. Les faits mesurés, vrais quelle que soit l'unité retenue

Mesurés sur le flux DiaLog du 31 juillet 2026, sur les arrêtés de circulation
(`accessRestrictionType = noEntry`) portant une caractéristique de poids. Distances
géodésiques, formule de haversine, rayon 6 371 000 m.

| | |
|---|---|
| Arrêtés de circulation portant du poids | **2 052** |
| dont géolocalisés avec une longueur non nulle | **2 051** (le dernier est un point isolé) |
| Segments de polyligne | **77 406** |
| **Longueur cumulée, doublons compris** | **2 484,2 km** |
| **Longueur dédupliquée** | **2 188,2 km** |
| **Double comptage** | **11,9 %** — 296,1 km |

**Le double comptage est réel et il n'est pas un artefact du pas de déduplication choisi.**
Testé sur un pas variant d'un facteur cent :

| Pas de la grille | Longueur dédupliquée | Double comptage |
|---|---|---|
| ~0,1 m | 2 198,8 km | 11,5 % |
| ~1,1 m | 2 188,2 km | 11,9 % |
| ~5,5 m | 2 171,5 km | 12,6 % |
| ~11,1 m | 2 157,3 km | 13,2 % |

> **Un dénominateur en mètres doit donc porter une clause de déduplication explicite**, ou
> environ 12 % de ce dénominateur est de la voirie fantôme — une même rue visée par deux
> arrêtés, comptée deux fois.

**Et la distribution est extrêmement asymétrique.**

| | Longueur de l'arrêté |
|---|---|
| p10 | 86 m |
| **médiane** | **391 m** |
| moyenne | 1 211 m |
| p90 | 2 427 m |
| p99 | 14,2 km |
| maximum | 52,7 km |

> **Le 1 % d'arrêtés les plus longs porte 22,4 % des mètres.**
>
> C'est le fait décisif du choix : **un compte par arrêté et un compte par mètre ne
> mesurent pas la même chose et ne peuvent pas donner le même nombre.** Le compte par
> arrêté donne le même poids à 86 m de rue communale et à 52,7 km de départementale ; le
> compte par mètre laisse une centaine d'arrêtés interurbains décider du cinquième du
> résultat. Aucun des deux n'est neutre. **Il faut choisir lequel répond à la phrase qu'on
> veut publier**, et écrire à côté du chiffre ce qu'il pèse.

---

## 3. La définition retenue

**Arrêtée le 3 août 2026, avant toute exécution du générateur.** Deux unités ont été
conçues en aveugle par des concepteurs distincts — le **mètre de voirie** et la
**prescription** (emprise continue). Les deux ont ensuite été attaquées, à la main, sur
les données. **L'attaque a tranché, et pas dans le sens attendu.**

### 3.1 Pourquoi le mètre, et pourquoi pas la prescription

**Le critère de départage est le nombre de paramètres libres dans le dénominateur.**

| Unité | Le dénominateur dépend-il d'un seuil arbitraire ? | Mesuré |
|---|---|---|
| **Mètre de voirie** | **Non.** Le pas de rééchantillonnage change le nombre de points de test, jamais la longueur. | **2 484,2 km** à pas de 5, 10, 25 et 50 m |
| Prescription | **Oui, massivement.** | **3 971 → 2 293** selon le seuil de raccord (0 → 200 m) — **42 % d'amplitude** |
| Arrêté | Non — mais l'unité est de taille libre | 2 052, invariant |
| Tronçon | Non — mais les tronçons sont incomparables | rapport long/court : médiane **8,1**, p90 **81**, max **147 515** |

> **La prescription est écartée, alors que c'était la meilleure idée conceptuelle du lot.**
> Elle résout le vrai problème — un arrêté découpé en douze `LineString` par le
> fournisseur ne devrait pas compter pour douze — mais **elle le résout en introduisant un
> seuil qui décide de 42 % du résultat.** On remplacerait un découpage arbitraire par un
> paramètre arbitraire, sans gain net.
>
> **Le tronçon est écarté aussi**, et plus nettement : sur les 515 arrêtés multi-tronçons,
> le rapport entre le plus long et le plus court est de **8,1 en médiane** et monte à
> **147 515**. Compter des tronçons reviendrait à donner le même poids à un segment
> dégénéré de quelques centimètres et à 1,5 km de départementale.

**Et le mètre encaisse l'attaque sur la concentration.** Le 1 % d'arrêtés les plus longs
porte 22,4 % des mètres, ce qui inquiète — mais le **poids maximal d'un arrêté isolé est
de 2,1 point** (Nice, 52,7 km). Une seule géométrie mal numérisée ne peut pas emporter le
chiffre. Les cent plus longs pèsent 46,5 % : la mesure est concentrée, elle n'est pas
captive.

### 3.2 L'unité principale — le mètre de voirie réglementée

> **UNITÉ : le mètre de chaussée sous arrêté d'interdiction de tonnage, dédupliqué.**
>
> **Numérateur —** la longueur, en mètres, des portions du réseau réglementé pour
> lesquelles OpenStreetMap ne porte aucune restriction applicable aux poids lourds.
>
> **Dénominateur —** la longueur totale, en mètres, du réseau réglementé, **chaque portion
> de chaussée comptée une fois et une seule**, quel que soit le nombre d'arrêtés qui la
> visent.

**Procédure, dans l'ordre, sans étape implicite :**

1. **Déclarer le périmètre**, et ne jamais le déduire de la collecte. Le périmètre est
   l'ensemble des arrêtés du champ ; **l'extrait OSM doit le couvrir, et le défaut de
   couverture se publie** au lieu de rétrécir le dénominateur en silence.
2. **Sélectionner** les arrêtés du champ : caractéristique de poids, tonnage lisible,
   géométrie non vide, `accessRestrictionType = noEntry`.
3. **Rééchantillonner** chaque polyligne à pas curviligne constant `PAS_TEST`. *C'est
   l'étape qui neutralise la densité de numérisation* : après elle, le nombre de points
   d'un tronçon ne dépend plus que de sa longueur.
4. **Dédupliquer** sur une grille de pas `PAS_DEDUP` : une portion visée par deux arrêtés
   compte une fois. **Sans cette étape, 11,9 % du dénominateur est de la voirie fantôme.**
5. **Apparier** chaque point à une voie OSM carrossable pour poids lourds, sous
   `TOL_APPARIEMENT`, de cap compatible à `ANG_MAX` près.
6. **Compter** au numérateur la longueur représentée par les points dont la voie appariée
   ne porte aucune clé de restriction, **et celle des points sans aucune voie appariée** —
   c'est l'absence maximale, et elle se publie séparément.

**Paramètres — aucun n'est en dur, chacun est nommé, publié avec le chiffre, et
accompagné de ce qui le justifie :**

| Paramètre | Valeur proposée | Ce qui la justifie | Sensibilité mesurée |
|---|---|---|---|
| `PAS_TEST` | 10 m | Sous la largeur d'une chaussée ; assez fin pour qu'un pont de 79 m porte huit points | **Nulle sur le dénominateur** — 2 484,2 km de 5 à 50 m |
| `PAS_DEDUP` | 1 m | Ordre de grandeur de la précision de numérisation | **11,5 % à 13,2 %** de 0,1 m à 11 m |
| `TOL_APPARIEMENT` | 30 m | Calibrée §19, reprise de la mesure existante | à rejouer |
| `ANG_MAX` | 30° | Sépare une voie du pont qu'elle franchit (§4) | **à surveiller** — le resserrement de 45° à 30° avait fait disparaître huit candidates |
| Périmètre | déclaré | *jamais* déduit de l'emprise OSM | 7 arrêtés perdus sous l'ancienne règle |

**Phrase publique autorisée, et elle seule :**

> *Au [date], sur les [N] kilomètres de voirie française couverts par un arrêté
> d'interdiction de tonnage publié dans DiaLog, **X %** ne portent dans OpenStreetMap
> aucune restriction applicable aux poids lourds.*

**Ce que ce chiffre ne dit pas — à publier avec lui :**

- **Rien sur une proportion d'arrêtés.** « X % des arrêtés » serait faux et ne doit jamais
  en être dérivé. Le 1 % le plus long portant 22,4 % des mètres, les deux chiffres
  divergeront visiblement.
- **Rien sur l'exactitude des restrictions présentes.** Une voie limitée à 3,5 t par
  arrêté et étiquetée `maxweight=19` dans OSM compte comme **couverte**. Les écarts de
  valeur sont un autre chiffre, et il est plus petit.
- **Rien sur ce qui n'est pas dans DiaLog.** Le dénominateur est la réglementation
  *publiée*, pas la réglementation *existante*.

### 3.3 L'unité secondaire — l'arrêté, et non la prescription

> **Le compte par arrêté est conservé, en second, avec sa définition écrite à côté de
> lui.** C'est l'unité de l'acte administratif : une ligne dans DiaLog, opposable,
> datable, révocable. **Sa cardinalité ne dépend d'aucun paramètre** — 2 052 est 2 052.
>
> Sa faiblesse est connue et s'énonce en une ligne : **elle donne le même poids à 86 m de
> rue communale et à 52,7 km de départementale.** C'est pour cela qu'elle est seconde.

**Et la règle qui va avec, tirée de tout ce qui précède :** les deux chiffres se publient
**ensemble ou pas du tout**. Publier le seul taux par arrêté était défendable tant qu'on
ignorait la distribution ; ce n'est plus le cas.

### 3.4 Ce que chaque divergence signifiera — écrit avant d'en connaître une seule

**Verrouiller la définition ne suffit pas.** Le jour du résultat, personne ne touchera aux
définitions : elles seront visiblement figées. **On touchera au commentaire**, qui ne l'est
pas. Si le taux en mètres sort à 62 % contre 71,2 % par arrêté, quelqu'un écrira que
l'écart vient d'arrêtés ruraux longs, moins pertinents pour un conducteur — **une phrase
inventée après coup pour rapprocher le lecteur du chiffre le plus flatteur.** Ce n'est pas
une modification de méthode, et une pré-inscription qui ne couvre que la méthode la laisse
passer.

**Donc les trois lectures possibles sont écrites maintenant. Après lecture du résultat, il
ne restera qu'à cocher.**

| Résultat | Ce qu'il signifie, et rien d'autre | Ce qui se dit alors |
|---|---|---|
| **Mètre < arrêté** | Les absences se concentrent sur les **emprises courtes**. | Le réseau ignoré par OSM est fait de **beaucoup de petites rues**. Le nombre d'actes non repris surestime la longueur non reprise. |
| **Mètre > arrêté** | Les absences se concentrent sur les **emprises longues**. | Le réseau ignoré est fait de **peu d'arrêtés mais de grands linéaires** — typiquement de l'interurbain. Le compte par acte sous-estime l'ampleur. |
| **Les deux à moins de `ECART_NEGLIGEABLE`** | L'absence est **indépendante de la longueur**. | Aucune histoire de distribution ne se raconte. Les deux chiffres disent la même chose et le choix d'unité n'a pas d'enjeu. |

**Le seuil, parce que « proches » est sinon un jugement :**

| Paramètre | Valeur | Ce qui la justifie |
|---|---|---|
| `ECART_NEGLIGEABLE` | **2,1 points** | Le poids maximal d'un arrêté isolé dans la mesure en mètres (§3.1, Nice, 52,7 km). **Un écart inférieur à l'influence d'un seul acte ne peut pas soutenir une affirmation sur une distribution.** |

**Et l'interprétation ne s'infère pas du signe : elle se vérifie.** Le sens de la
divergence est une conséquence arithmétique, donc il ne prouve rien tout seul. Le
générateur produira donc, dans le même rapport, **le taux d'absence par décile de
longueur d'arrêté** — dix nombres qui montrent la distribution directement au lieu de la
déduire.

> **Si les déciles contredisent la lecture tirée du signe, c'est la lecture qui tombe, pas
> les déciles.** Ce cas est prévu ici pour qu'il ne soit pas traité comme une surprise :
> il signifierait que l'écart vient d'un petit nombre d'arrêtés extrêmes plutôt que d'une
> tendance, et cela s'écrit tel quel.

**Ce qui reste interdit dans tous les cas :** invoquer la **pertinence** des arrêtés — « les
longs sont ruraux donc moins importants », « les courts sont urbains donc plus critiques ».
**Aucune mesure de ce projet ne porte sur la pertinence.** Une phrase qui pondère les
absences par leur importance supposée pour un conducteur est une opinion, et elle ne peut
pas s'appuyer sur ces chiffres.

### 3.4 bis — Ce que l'épreuve aveugle valide du nouveau chiffre, et ce qu'elle ne valide pas

**L'épreuve aveugle du 2 août validait le 71,2 %. Elle ne valide pas entièrement le
89,6 %, et reporter sa caution serait un abus.**

Les deux mesures posent des questions différentes. On a demandé aux vérificateurs :
*« la voie que cet arrêté désigne porte-t-elle une restriction de tonnage dans OSM ? »*
C'est un **prédicat par arrêté** — quelque part, oui ou non. La mesure en mètres demande
autre chose : **quelle fraction de l'emprise est exprimée ?**

**Vérifié sur les vingt-cinq cas, en calculant leur couverture métrique :**

| Ce que l'épreuve a testé | Transfert au chiffre en mètres |
|---|---|
| **Les 20 absences** — aucune infirmée | **Transfert complet.** 20/20 retrouvés, **tous à couverture métrique nulle**. La borne à 15 % sur les fausses absences tient pour la classe « entièrement absent ». |
| **Les 5 témoins** — tous retrouvés | **Transfert partiel.** Trois sont couverts à 100 %. **Gosnay est à 45,5 %**, un autre à 68,6 %. Le vérificateur avait raison — une restriction existe — et l'arrêté est à moitié inexprimé. |

> **Les témoins prouvaient que la méthode discrimine. Ils prouvent qu'elle discrimine
> `présent` de `absent`, pas qu'elle compte juste entre les deux.** Et c'est exactement le
> mécanisme qui produit les 15,1 points d'écart.

**La surface non validée se mesure, et elle est grande :**

| Classe | Arrêtés | Linéaire | Part des mètres |
|---|---|---|---|
| Entièrement absents (0 % couvert) | 1 528 | 1 350,5 km | 54,4 % |
| Entièrement couverts (100 %) | 176 | 63,8 km | 2,6 % |
| **Partiellement couverts** | **347** | **1 070,0 km** | **43,1 %** |

> **Les arrêtés partiellement couverts portent 43,1 % du linéaire et fournissent 39,3 % du
> numérateur.** Leur couverture s'étale : p10 **3 %**, médiane **24 %**, p90 **84 %**.
>
> **Près de quatre dixièmes du chiffre publié reposent donc sur une comptabilité de
> couverture partielle que rien n'a encore éprouvée.** Ce n'est pas une note de bas de
> page, c'est une réserve sur 39 % du résultat.

**Et le cas concret que les cinq témoins n'ont pas fourni existe dans le corpus :**

> **Cassel — « Traversée de Cassel interdite aux véhicules… », 43,6 km, couverts à 0,7 %.**
> Le prédicat par arrêté répond « couvert » : OSM porte bien une restriction quelque part
> sur cette emprise. La mesure en mètres répond « absent à 99,3 % ». **Les deux verdicts
> sont corrects, sur le même objet, et ils sont séparés par deux ordres de grandeur.**
>
> Les quatre autres plus gros contributeurs au numérateur sont du même type : 45,9 km
> couverts à 5,0 %, 39,1 km à 0,5 %, 35,1 km à 1,0 %, et Nice, 52,7 km à 39,3 %.

**La réserve à publier, mot pour mot :**

> *L'épreuve à l'aveugle borne le risque de fausses absences **au niveau de l'arrêté**.
> Elle ne valide pas la comptabilité de couverture partielle, dont dépendent 39 % du
> chiffre en mètres.*

**Le test qui manque, et il n'est pas fait :** une épreuve aveugle portant sur des
**fractions** et non sur un prédicat — tirer des arrêtés partiellement couverts, demander
à des vérificateurs indépendants quelle part de l'emprise porte une restriction, comparer.
Plus coûteuse que la première, parce qu'un vérificateur doit parcourir l'emprise au lieu
de répondre oui ou non. **Tant qu'elle n'est pas faite, la réserve ci-dessus accompagne le
chiffre partout où il paraît.**

### 3.4 ter — L'épreuve par échantillonnage du linéaire : seuils écrits avant les résultats

**Le cadre.** Le taux en mètres est une moyenne, pondérée par la longueur, d'une propriété
binaire. Tirer des points uniformément **en longueur** et poser à un vérificateur aveugle
la même question qu'à la première épreuve donne donc **directement** le taux, sans passer
par la comptabilité de couverture partielle. 140 points, graine 20260803, quatre lots de
35 confiés à quatre vérificateurs indépendants, plus 25 points refaits par un cinquième.

#### PORTE PRÉALABLE — validité de la consigne, et rien avant

> **Ordre de lecture, fixé pour qu'il ne puisse pas être choisi au moment de lire :**
>
> **1. Étendue entre les quatre lots** (seuil au (a) ci-dessous) — **2. Taux de désaccord
> sur les 25 recoupés** (seuil de 20 % au (c)).
>
> **Tant que ces deux portes ne sont pas franchies, RIEN d'autre ne se lit.** Ni le taux
> groupé, ni le tableau à quatre cases, ni les diagnostics par cas.

**Le risque est précis, et il faut le nommer pour ne pas y céder :** la dispersion décroche,
les quatre cases sortent favorables, et il devient tentant de garder les secondes en
réparant la première. **Ce serait lire un instrument dont on vient de constater qu'il ne
mesure pas.**

Si la consigne était équivoque, elle l'était pour **tous** les points, pas seulement pour
l'agrégat. **Les verdicts au point sont alors suspects en bloc**, et les cases hors
diagonale — qui reposent entièrement sur des verdicts individuels — le sont plus encore que
la moyenne, qui bénéficie au moins d'une compensation.

**En cas d'échec de la porte :** la consigne est reprise, l'épreuve est **rejouée en
entier** sur un nouveau tirage, et **le tirage précédent est publié comme échec** avec sa
cause. Il ne se recycle pas, même en partie — un sous-ensemble choisi après coup dans un
échantillon invalidé est un échantillon choisi par son résultat.

#### PORTE 1 — RÉSULTAT, et un défaut que je n'avais pas pré-inscrit

| Lot | OUI | NON | INCERTAIN | Requêtes échouées | Taux d'absence |
|---|---|---|---|---|---|
| 1 | 4 | 31 | **0** | 7 | 88,6 % |
| 2 | 2 | 33 | **0** | 27 | 94,3 % |
| 3 | 2 | 33 | **0** | 27 | 94,3 % |
| 4 | 4 | 31 | **0** | 0 | 88,6 % |

**Étendue observée 5,7 points, seuil pré-inscrit 17,1. PORTE 1 FRANCHIE.**

> ⚠ **Mais un défaut apparaît que les portes ne captent pas, et il pousse dans mon sens —
> raison de le dire plus fort, pas moins.**
>
> **`INCERTAIN` n'a été employé 0 fois sur 140**, alors que la consigne l'autorisait
> explicitement et disait « ne devine jamais ». **Et 61 requêtes Overpass ont échoué.**
>
> **Le taux d'absence suit exactement le nombre d'échecs :** 0 et 7 échecs → 88,6 % ; 27 et
> 27 échecs → 94,3 %. **C'est ce que produirait un vérificateur qui répond NON quand il
> n'a pas pu vérifier** — et NON est la réponse qui me donne raison.
>
> **La force de ce signal est faible et il faut le dire :** *n* = 4 lots. Une corrélation de
> rang parfaite sur un partage 2 contre 2 arrive **une fois sur trois** par hasard.
> **Suggestif, pas établi.**
>
> **Défaut de protocole, à corriger avant toute reprise :** l'échec de requête est compté
> par lot, pas par point. On ne peut donc **pas** vérifier si les points dont la requête a
> échoué sont ceux répondus NON. **Une ligne dans le schéma l'aurait permis** — c'est la
> même faute que le rapport machine avant qu'il devienne obligatoire : la donnée qui aurait
> tranché n'a pas été enregistrée.
>
> **Ce constat n'est pas une porte** : il n'était pas pré-inscrit, et je ne m'autorise pas à
> en fabriquer une après coup. **Il devient une réserve publiée avec le résultat**, et une
> porte pré-inscrite pour la campagne suivante : *taux d'`INCERTAIN` nul avec des requêtes
> échouées = consigne non suivie.*

#### PORTE 1 bis — lecture stratifiée par échec de requête, inscrite avant d'ouvrir quoi que ce soit

**Écrit le 3 août, après avoir vu les quatre taux de lot, et avant d'avoir croisé le
moindre verdict avec ceux du pipeline.** C'est la dernière fenêtre où cette analyse est
légitime : dans une heure, ce serait une analyse fabriquée pour expliquer ce qu'on aura vu.

**L'hypothèse à tester :** si les vérificateurs ont répondu NON faute d'avoir pu vérifier,
alors la case **fausse absence** sera gonflée dans les lots à 27 échecs et pas dans celui à
zéro.

> **Les quatre cases seront lues STRATIFIÉES par niveau d'échec de requête :**
> **lot 4 (zéro échec) et lot 1 (7 échecs)** d'un côté, **lots 2 et 3 (27 chacun)** de
> l'autre.

| Ce qu'on observera | Ce qu'on en conclut |
|---|---|
| Case *fausse absence* **comparable** dans les deux strates | **Le soupçon tombe.** Le NON par défaut n'a pas eu lieu, et les 140 points se lisent ensemble. |
| Case *fausse absence* **concentrée dans les lots à échecs** | La corrélation de rang est **démontrée**, pas seulement suggérée. **Seul le lot 4 se lit** — 35 points, et l'épreuve est à refaire sur les 105 autres. |
| Case *fausse absence* **concentrée dans le lot sans échec** | Hypothèse retournée : les échecs ne sont pas la cause, et il faut en chercher une autre **avant** de lire quoi que ce soit. |

**Effectifs annoncés d'avance, pour ne pas surinterpréter :** chaque strate compte 70
points, et les cases hors diagonale y seront à un chiffre. **Le seuil du §3.4 k
— `|a − b| ≤ 2√(a+b)` — s'applique à chaque strate séparément**, avec la conséquence que
la plupart des écarts y seront indiscernables. **C'est prévu : une strate qui ne tranche
pas est un résultat, pas un échec.**

**Et une recherche à faire avant tout cela**, dont l'issue est inconnue à l'heure où ces
lignes sont écrites :

> **L'échec de requête n'a pas été enregistré par point dans le schéma. Il a peut-être
> fuité ailleurs** — dans la prose des réponses, dans un commentaire, dans les
> transcriptions de session. **Les transcriptions seront fouillées avant la lecture
> stratifiée.**
>
> Si ne serait-ce qu'une partie des 61 échecs se retrouve rattachée à un point, la
> corrélation de rang sur **4 lots** devient un test direct sur **61 points** : *parmi les
> points dont la requête a échoué, quelle est la part de NON ?* **Si elle vaut 100 % contre
> ~90 % ailleurs, la question est tranchée** et il n'y a plus besoin de stratifier par lot.

#### PORTE 1 ter — le test direct est fait, et il RÉFUTE mon soupçon

La donnée manquante au schéma **avait fuité ailleurs**. Les transcriptions de session
contiennent chaque commande et sa sortie. En appariant les 225 appels d'outil à leur
résultat, puis en cherchant les coordonnées de chacun des 140 points dans les commandes :

| | |
|---|---|
| Appels d'outil appariés à leur sortie | **225** |
| dont portant une signature d'échec (`429`, `runtime error`, page HTML…) | **18** |
| **Points retrouvés dans une requête RÉUSSIE** | **137 / 140** |
| **Points vus SEULEMENT dans une requête en échec** | **0** |
| Points non retrouvés dans aucune commande | 3 |

> **Zéro. Aucun point n'a été répondu sur une requête qui avait échoué.** Les 429 étaient
> des limitations de débit transitoires, et les vérificateurs ont relancé jusqu'à obtenir
> une réponse.
>
> **Le soupçon du « NON par défaut » est réfuté.** La corrélation de rang sur quatre lots
> était la coïncidence une-fois-sur-trois que j'avais annoncée comme telle.
>
> **La lecture stratifiée du PORTE 1 bis devient sans objet** — c'était le repli prévu si
> le test direct n'était pas possible. Il l'était.

**Trois points restent non appariés** — 10 (Grand Angoulême), 61 (Béthune-Bruay),
127 (Toulouse) — probablement à cause d'un format de coordonnées différent dans la
commande. **Ils sont vérifiés à la main avant que leurs verdicts entrent dans le compte.**

> **Ce que cet épisode enseigne, et qui vaut plus que son issue :** j'ai formé un soupçon
> sur mes propres vérificateurs, il allait dans le sens qui m'arrangeait, je l'ai écrit,
> puis je suis allé chercher de quoi le trancher — et il est tombé. **Un soupçon favorable
> qu'on ne cherche pas à trancher reste favorable indéfiniment.**
>
> Et la donnée qui a tranché n'était pas dans le champ prévu pour elle : **elle était dans
> la trace brute.** Le schéma reste à corriger — l'échec par point y entrera — mais la
> leçon est plus large : **avant de déclarer une donnée manquante, regarder ce qui a été
> enregistré à côté.**

#### RÉSULTAT DE L'ÉPREUVE — les deux portes franchies, puis la lecture

**Porte 1** — étendue entre lots **5,7 points**, seuil 17,1. Franchie.
**Porte 2** — désaccord sur les 25 recoupés : **0 sur 25**. Franchie.

> **Zéro désaccord observé n'est pas zéro désaccord vrai.** La règle de trois borne le taux
> réel à **3/25 = 12 %** à 95 % — soit exactement la limite de la première zone du §3.4 c,
> et une atténuation possible allant jusqu'à 5,1 points. **L'épreuve ne dit pas que les
> vérificateurs sont infaillibles ; elle dit qu'aucun désaccord n'est apparu sur 25 cas.**

**La seconde estimation :**

| | |
|---|---|
| Vérificateurs aveugles, 140 points | **128 NON — 91,4 %** (±5,0 pt à 95 %) |
| Comptabilité de couverture, réseau entier | **89,6 %** |
| **Écart** | **+1,9 point — CONCORDANT** |

**La phrase autorisée, celle qui était écrite d'avance et aucune autre :**

> *Deux méthodes indépendantes — l'une par comptabilité de couverture, l'autre par
> échantillonnage aveugle du linéaire — donnent le même ordre de grandeur, ce qui borne
> l'erreur d'ensemble sans certifier chaque composante.*

**Les quatre cases :**

| | Vérificateur OUI | Vérificateur NON |
|---|---|---|
| **Pipeline OUI** | **12** | **0** |
| **Pipeline NON** | **0** | **128** |

**Accord parfait sur les 140 points.** `a = 0`, `b = 0`, donc `|a − b| = 0 ≤ 0`.

> **La lecture pré-inscrite s'applique telle quelle : INDISCERNABLES. Le mot « plancher »
> perd son appui mesuré et ne repose plus que sur la prédiction de générosité de
> conception.** Il ne s'emploie donc plus qu'accompagné de cette précision, ou pas du tout.

#### L'accord parfait est moins rassurant qu'il n'en a l'air, et il faut le dire

> **Les vérificateurs ne sont pas une méthode indépendante. Ils sont une
> RÉIMPLÉMENTATION de la même spécification.** Ils interrogent Overpass autour du point,
> filtrent par le cap, lisent les mêmes clés, appliquent la même tolérance. **Un accord
> parfait démontre la fidélité de l'implémentation, pas la justesse de la mesure.**
>
> Ce que l'épreuve établit : **le code fait ce que la spécification dit.** Ce qu'elle
> n'établit pas : **que la spécification dise la bonne chose.**

**Et la démonstration en est fournie par les deux points que le détecteur géométrique avait
signalés.**

| | Point 50 | Point 71 |
|---|---|---|
| Voie retenue par le pipeline | *Chemin de Saint-Francet*, **17,0 m** | *Impasse de la Campagne Bosq*, **14,6 m** |
| Voie nommée par le vérificateur | **la même**, way 683539186 | **la même**, way 196519127 |
| Verdict du vérificateur | **OUI** | **OUI** |

> **Le vérificateur du point 71 a écrit sa propre réserve :** *« le point est à 14,6 m de
> l'axe, écart plus grand que sur les autres points »* — **et a répondu OUI quand même.**
> Il a vu l'anomalie et l'a écartée, parce que la consigne, comme le code, autorise 30 m.
>
> **C'est l'erreur commune, exactement telle qu'elle était pré-inscrite au §3.4 e :** le
> vérificateur et le pipeline se trompent de la même manière, donc ils concordent par
> erreur partagée et non par justesse. **Seul le détecteur géométrique l'a vue** — et c'est
> la seule raison pour laquelle il existait.

**Une correction contre moi, qui découle de tout ceci.** Le §3.4 j comptait ces deux points
comme un appui **mesuré** au mot « plancher », sous le nom de « fausses attributions ».
**C'était trop fort.** Ce ne sont pas des erreurs démontrées : ce sont des attributions
**autorisées par la tolérance de 30 mètres**, qui est pré-inscrite. La question qu'elles
posent est celle de la **spécification** — 30 m est-il trop généreux ? — et ni le pipeline
ni des vérificateurs qui héritent de cette tolérance ne peuvent y répondre.

> **Conséquence : le mot « plancher » ne conserve aucun appui mesuré.** Il reste la
> prédiction de générosité de conception (§3.4 i), datée et réfutable, et rien d'autre.
> **La phrase qui l'accompagne se réécrit en conséquence**, et elle est plus courte :
>
> *« 89,6 % n'est pas établi comme un plancher. Le biais de conception de l'outil est la
> générosité, ce qui rend probable — sans le démontrer — que le vrai chiffre soit plus
> haut. Aucune mesure ne l'établit à ce jour. »*

#### La spécification ne se valide pas, mais son influence se mesure

Aucun vérificateur héritant de la consigne ne peut juger la tolérance de 30 mètres. **Mais
on peut chiffrer ce qu'elle décide** — le générateur prend soixante-douze secondes.

| Tolérance | Km absents | **Taux métrique** | Par arrêté | Part reposant sur `access` |
|---|---|---|---|---|
| **10 m** | 1 991,7 | **90,8 %** | 77,6 % | 9,9 % |
| 20 m | 1 975,3 | 90,0 % | 76,2 % | 10,2 % |
| **30 m** — retenu | 1 965,2 | **89,6 %** | 74,5 % | 11,6 % |
| 50 m | 1 941,7 | **88,5 %** | 70,8 % | 14,9 % |

> **Amplitude : 2,28 points sur une plage de 1 à 5.** La spécification décide donc de
> quelque chose, mais de **moins que l'échantillonnage** (±5,0) et **moins que la borne sur
> le désaccord entre vérificateurs** (jusqu'à 5,1). **La réserve était non bornée ; elle
> est désormais bornée et publiable.**

**Et le sens est monotone : resserrer la tolérance MONTE le taux.** +1,21 point à 10 m,
−1,07 à 50 m.

**Ce qui donne enfin une composante mesurée au mot « plancher », sur le seul paramètre qui
restait sans contrôle :**

| Tolérance | Point 50 (17,0 m) | Point 71 (14,6 m) |
|---|---|---|
| 10 m | **ABSENT** | **ABSENT** |
| 20 m | COUVERT | COUVERT |
| 30 m | COUVERT | COUVERT |

> **Les deux seuls cas où l'humain et la machine se sont trompés de la même façon sortent
> dès qu'on resserre à 10 mètres.** La tolérance de 30 m est exactement ce qui les fait
> entrer.
>
> **Le raisonnement cesse donc d'être circulaire :** ce n'est plus « je crois que mon outil
> est généreux parce que je l'ai conçu ainsi », c'est « les deux attributions
> manifestement fausses de l'échantillon disparaissent quand on resserre, et resserrer
> monte le taux ». **Une mesure, pas une introspection.**

**Ce que cela autorise à écrire, et pas davantage :**

> *89,6 % est vraisemblablement un plancher. Le seul paramètre non contrôlé — la tolérance
> d'appariement — décide de 2,3 points au plus sur une plage de 1 à 5, et son resserrement
> fait monter le taux ; les deux attributions manifestement fausses de l'échantillon
> aveugle disparaissent dès 10 mètres. Ce n'est pas une démonstration : 30 mètres reste un
> choix, et sa valeur juste n'est pas établie.*

**Le mot est repris, et cette fois il est gagné.** Il l'avait été perdu trois heures plus
tôt faute d'appui mesuré ; il revient avec un appui mesuré, plus étroit que l'ancien et
énoncé avec sa limite. **Ce qui a changé n'est pas mon avis, c'est ce qui est sur la
table.**

#### La courbe ne plafonne pas — elle s'emballe, et l'argument a donc un plancher

**La plage 10–50 m était monotone sans inflexion, ce qui appelait un dernier coup d'œil :
une courbe qui monte encore au bord n'a pas montré son plateau.** Balayage étendu à 5 et
2 mètres.

| Tolérance | Taux métrique | Δ vs 30 m | Pente par mètre |
|---|---|---|---|
| **2 m** | **93,2 %** | +3,69 | |
| **5 m** | **91,7 %** | +2,18 | **−0,501** |
| 10 m | 90,8 % | +1,21 | −0,195 |
| 20 m | 90,0 % | +0,46 | −0,075 |
| 30 m | 89,6 % | 0,00 | −0,046 |
| 50 m | 88,5 % | −1,07 | −0,054 |

> **Aucun plateau. La pente est multipliée par dix entre le haut et le bas de la plage** —
> −0,046 point par mètre autour de 30 m, **−0,501 entre 2 et 5 m.** Ce n'est pas une courbe
> qui converge vers une valeur naturelle, c'est une courbe qui décroche.

> ## ⚠ RÉTRACTATION DU 3 AOÛT — l'explication ci-dessous s'appuyait sur un nombre retiré
>
> **La cause invoquée était : « l'écart géométrique DiaLog ↔ OSM a un p95 de 8,53 m, donc
> sous ~10 m on mesure le désalignement ». C'est le nombre rétracté la veille**, commit
> `bd5dc4c` — *« Retrait du plancher de 10 m : la mesure était circulaire »*.
>
> Même corpus, 6 149 sommets ; même médiane, 0,9 ; même maximum, 10,5. Le tableau de
> rétractation portait, mot pour mot : *« Route la plus proche, couverture complète —
> p50 0,9 · max 10,5 m — **Circulaire.** On mesure la distance à *une* route, pas à *la*
> route désignée : la valeur est bornée par la densité du réseau, pas par la qualité des
> tracés. »*
>
> **`nearest(lat, lon)` ne mesure pas un désaccord de numérisation.** Dans un réseau dense,
> quelque chose est toujours proche, que le tracé soit fidèle ou non.
>
> **Ce qui tombe :** le plancher de ~10 m n'est pas établi. **Ce qui reste :** la pente
> s'emballe bel et bien — ×10 entre 30 m et 2 m — et cela demande toujours une explication.
> **Elle est désormais plausible et non mesurée**, et l'amplitude 2–50 m redevient une
> incertitude non bornée par le bas plutôt qu'un artefact démontré.
>
> **Et c'est la faute la plus grave de la session, parce qu'elle contredit ce que je
> célébrais trois heures plus tôt.** J'avais écrit que cette mesure avait pu resservir
> « parce qu'elle avait été rangée avec sa définition ». **Sa définition a voyagé ; sa
> rétractation, non.**

**Conséquence sur l'argument, et il faut l'écrire :**

> **« Resserrer la tolérance monte le taux » a lui-même un plancher, à environ 10 mètres.**
> L'argument vaut sur **10–50 m**, où l'amplitude est de **2,28 points** et où l'exclusion
> reste ≈ 97 % fidèle. Au-delà vers le bas, il ne vaut plus.
>
> **L'amplitude brute 2–50 m est de 4,76 points, et elle ne doit pas être citée** : plus de
> la moitié vient d'une zone où la mesure est fausse par construction. **Citer 4,76
> reviendrait à faire passer un artefact pour une incertitude.**

**Ce que le balayage étendu change au bilan :** rien sur le chiffre, et une réserve de plus
sur l'argument. **30 mètres n'est pas montré juste ; il est montré situé dans la plage où
la mesure mesure encore quelque chose**, ce qui est moins que ce que j'aurais aimé écrire
et plus que ce que j'avais avant de lancer les deux passes.

#### a) Le seuil de dispersion entre lots — calculé le 3 août, avant tout résultat

Les 25 points recoupés mesurent l'accord **sur des cas identiques**. Ils ne verraient pas
un **biais systématique de lot** : si un vérificateur conclut 95 % et un autre 80 %,
l'estimation groupée sort au milieu, plausible, et l'écart disparaît dans la moyenne.

Or quatre lots de 35 points tirés de la même population ont une dispersion attendue, et
elle se calcule. **Simulation binomiale exacte, 200 000 tirages, graine 11 :**

| Taux groupé | Étendue moyenne | p90 | **Seuil (p95)** | p99 |
|---|---|---|---|---|
| 75 % | 15,0 | 22,9 | **25,7** | 31,4 |
| 80 % | 13,8 | 22,9 | **25,7** | 28,6 |
| 85 % | 12,3 | 20,0 | **22,9** | 25,7 |
| 90 % | 10,2 | 17,1 | **17,1** | 22,9 |
| 95 % | 7,3 | 11,4 | **14,3** | 17,1 |

> **Règle, fixée maintenant :** le seuil se lit dans cette table au **taux groupé observé,
> arrondi au multiple de 5 % le plus proche**. Si l'étendue entre les quatre taux le
> dépasse, **le problème est dans la consigne, pas dans le réseau** — et l'estimation
> groupée ne se publie pas avant que la consigne soit reprise.
>
> Le seuil est écrit avant les quatre nombres. **Calculé après, il serait sorti juste assez
> large** — c'est le même test que celui qui a fait retenir 45° pour le cap : une
> dispersion qui décroche mesure l'instrument, pas le terrain.

#### b) Ce que la concordance autorisera à dire, et ce qu'elle n'autorisera pas

Si la seconde estimation tombe dans l'intervalle du 89,6 %, cela borne **l'erreur nette**
de la comptabilité de couverture. **Cela ne valide pas ses composantes.**

> **Deux erreurs de sens opposés se compenseraient et donneraient un accord parfait** —
> une sur-attribution de couverture dans les emprises partielles, une sous-détection
> ailleurs. C'est la forme exacte de « vingt cas propres bornent une erreur grossière et ne
> certifient pas une valeur précise », transposée d'un échantillon à une méthode.

**La phrase publiable en cas de concordance, et aucune autre :**

> *Deux méthodes indépendantes — l'une par comptabilité de couverture, l'autre par
> échantillonnage aveugle du linéaire — donnent le même ordre de grandeur, ce qui borne
> l'erreur d'ensemble sans certifier chaque composante.*

C'est plus faible que ce qu'on aura envie d'écrire. **C'est ce qui tiendra devant quelqu'un
qui cherche la faille**, et c'est la seule raison de le décider avant de connaître le
résultat.

**En cas de discordance**, la règle est la même qu'au §9 : le désaccord se publie avec les
deux chiffres, et **aucun des deux ne sort seul** tant que la cause n'est pas trouvée.

#### c) Le désaccord entre vérificateurs entre dans la lecture, il n'est pas qu'un contrôle

**Les 25 points recoupés étaient prévus comme contrôle de qualité. C'est aussi un biais, et
il pousse du même côté que ce qu'on teste.**

Une erreur de classification, dans les deux sens, attire toute proportion vers 50 %. À un
taux vrai de 89,6 %, **le bruit ne disperse pas : il rabaisse.** Et c'est exactement la
direction qu'aurait une vraie sur-attribution de couverture dans les emprises partielles.
Sans séparer les deux, une seconde estimation à 85 % serait illisible.

**Estimateur, fixé maintenant.** Deux vérificateurs d'erreur `e` indépendante désaccordent
avec probabilité `d = 2e(1−e)`, donc `e = (1 − √(1−2d)) / 2` — grossièrement `d/2`. Le taux
observé vaut `p' = p(1−2e) + e`, donc **le taux corrigé est `p = (p' − e) / (1 − 2e)`**.

| Désaccord `d` | Erreur `e` | Atténuation | Rapport à l'intervalle (±5,1 pt) |
|---|---|---|---|
| 4 % | 2,0 % | 1,6 pt | 0,32× |
| 8 % | 4,2 % | 3,3 pt | 0,65× |
| **12 %** | 6,4 % | **5,1 pt** | **1,00×** |
| 16 % | 8,8 % | 6,9 pt | 1,37× |
| **20 %** | 11,3 % | **8,9 pt** | **1,77×** |
| 28 % | 16,8 % | 13,3 pt | 2,64× |

> **Règle, en trois zones :**
>
> **`d ≤ 12 %`** — l'atténuation ne dépasse pas l'intervalle d'échantillonnage. On corrige,
> et on compare le taux corrigé à 89,6 %.
> **`12 % < d ≤ 20 %`** — l'atténuation dépasse l'intervalle. On corrige, et on publie
> l'intervalle **élargi de l'incertitude de la correction elle-même**.
> **`d > 20 %`** — la seconde méthode ne mesure plus grand-chose. **Elle ne se publie pas**,
> et le 89,6 % reste seul avec sa réserve du §3.4 bis, non levée.

**Réserve à écrire avec le résultat, quelle qu'en soit la valeur :** 25 paires donnent une
estimation grossière. À `d = 12 %`, l'intervalle sur `d` est de ±13 points, soit une
atténuation comprise **entre 0 et 11,5 points**. **L'incertitude de la correction peut
dépasser la correction.** C'est un ordre de grandeur, pas un redressement.

#### d) L'asymétrie renverse l'intuition, et resserre le problème

L'atténuation vers 50 % suppose une erreur **symétrique**. Elle ne l'est pas, et le calcul
le montre — parce qu'à 89,6 % d'absence, **il n'y a que 10,4 % de OUI à rater** :

| Erreur OUI→NON | Erreur NON→OUI | Biais sur le taux |
|---|---|---|
| 10 % | 0 % | **+1,0 pt** |
| 5 % | 5 % | −4,0 pt |
| 0 % | 10 % | **−9,0 pt** |

> **Manquer une étiquette ne coûte presque rien ; en attribuer une à tort coûte neuf fois
> plus.** L'intuition dit l'inverse — chercher est actif, manquer est passif, donc on
> croirait le faux NON dominant. Mais un faux NON ne peut frapper que 10,4 % des points,
> quand un faux OUI peut frapper les 89,6 % autres.
>
> **Et le faux OUI est exactement la faute que la consigne interdit :** attribuer au point
> une restriction qui appartient à la voie d'à côté, à l'allée de service, au chemin
> parallèle. **C'est la même faute que celle dont on soupçonne la comptabilité dans les
> emprises partielles.** Le vérificateur et le pipeline peuvent se tromper de la même
> manière, ce qui les ferait concorder par erreur commune plutôt que par justesse.

**Ce qui est mesurable et sera regardé :** sur les 25 points recoupés, **le taux de OUI de
chaque vérificateur comparé à celui des autres sur les mêmes points**. Un vérificateur qui
dit OUI nettement plus souvent que les autres est le candidat au faux OUI. Cela détecte
l'asymétrie **entre** vérificateurs ; cela ne détecte pas une erreur commune à tous, et
cette limite est la réserve résiduelle de l'épreuve.

#### e) Deux détecteurs de l'erreur commune — règles de lecture écrites avant les résultats

La réserve du point (d) — « on ne détecte pas une erreur commune à tous les
vérificateurs » — **n'était pas irréductible. Elle l'était seulement tant qu'on cherchait à
la détecter par la comparaison entre vérificateurs.**

**Détecteur 1 — géométrique, automatique, postérieur.** Un faux OUI par attribution laisse
une trace : **la distance entre le point tiré et la voie taguée qui a produit le OUI**, et
la classe de cette voie. Un vrai OUI a la restriction sur la voie même — distance quasi
nulle. Un faux OUI l'a sur une parallèle, une contre-allée, une desserte.
[signature-attribution.py](outils/signature-attribution.py) la sort pour chaque point.

> **Règle de lecture, fixée maintenant :**
>
> | Ce qu'on observe sur les points couverts | Ce qu'on en conclut |
> |---|---|
> | Distances **groupées sous 5 m** | Attribution saine. Le OUI porte sur la voie même. |
> | Une **queue au-delà de 10 m** | Candidats à l'attribution fautive. **Ces points sont listés nommément et retirés dans une variante du calcul**, dont l'écart au principal est publié. |
> | Classes **majoritairement mineures** (`service`, `residential`) là où l'arrêté vise un axe | Dérive systématique, pas des cas isolés. **La comparaison des deux méthodes ne se publie pas** avant reprise du filtre. |
> | Beaucoup de points **rejetés par le seul filtre de cap** | Le filtre travaille beaucoup, donc l'attribution est fragile à sa valeur. À reporter comme sensibilité. |

**Détecteur 2 — déclaratif, humain, et il était déjà là.** Le protocole demande à chaque
vérificateur, pour chaque point, **quelle voie il a retenue et quelles étiquettes il a
lues**. Ces champs sont obligatoires dans le schéma de réponse. Ils n'avaient pas été
pensés comme un détecteur d'attribution ; ils en sont un.

> **C'est le principe de la première épreuve, retourné.** On y avait retiré l'identifiant
> de voie pour que le vérificateur trouve la voie lui-même. Ici l'identification se produit
> aussi — dans sa tête — et la jeter serait perdre la seule chose qui rend le OUI
> auditable. **La capturer ne change rien à l'aveuglement** : le OUI est déjà donné, on ne
> demande pas de le reconsidérer.
>
> Si un vérificateur nomme « la D57 » alors que l'étiquette est sur une allée sans nom,
> l'erreur commune devient visible.

**Croisement des deux, décidé d'avance :**

| Les deux détecteurs… | Conduite |
|---|---|
| désignent **les mêmes points** | Ces points sont retirés dans la variante, et l'écart publié. C'est le cas le plus net. |
| désignent **des points différents** | **C'est encore une information** : le géométrique voit une distance, le déclaratif voit une confusion de voie — ce sont deux fautes distinctes, et les deux listes se publient. |
| ne désignent **rien** | La réserve résiduelle tombe pour ce qu'ils savent voir, et il reste à écrire ce qu'ils ne voient pas : une restriction correctement attribuée mais qui ne s'applique pas au véhicule visé. |

**Limite du détecteur 1, à publier avec lui :** l'extrait OSM ne contient **que** des voies
porteuses de restriction — la requête Overpass les a filtrées à la source. La voie du
corridor, si elle n'est pas taguée, est invisible. **La distance est un indice, pas une
preuve.** Un extrait complet du réseau la transformerait en preuve, et c'est le seul point
qui demanderait une collecte de plus.

#### f) Deux fautes distinctes, et une seule des deux est visible à la distance

**Les deux points aberrants ne sont pas la même faute**, et les confondre aurait donné une
fausse confiance au détecteur géométrique.

| Point | Faute | Ce qui cloche |
|---|---|---|
| **50** | **Attribution** | Mauvaise voie. Un chemin à 8 t retenu pour un arrêté à 13 t, à 17 m. |
| **71** | **Prédicat** | `access=private` n'est **pas** une restriction de tonnage. C'est un OUI rendu sur la mauvaise **nature de preuve**, pas sur la mauvaise voie. |

> **La faute du point 71 est celle qui a coûté 23 points le 2 août** — un `access=private`
> compté comme couverture — réapparue dans le jugement d'un vérificateur au lieu d'un
> script.
>
> **Les deux aberrants cumulent les deux fautes, et c'est ce cumul qui les a rendus
> visibles.** Une erreur de prédicat **à deux mètres** n'aurait été vue par aucun filtre
> géométrique : un vérificateur qui répond OUI parce qu'il voit `access=destination` sur la
> voie même passe tout.

**Contrôle fait, sur les neuf OUI sous 5 m — et lu dans le fichier de données, pas dans
l'affichage du détecteur :**

| | |
|---|---|
| OUI sous 5 m | **9** |
| dont reposant sur une étiquette de **tonnage** | **9** |
| dont reposant sur `access` / `motor_vehicle` **seul** | **0** |

Clés employées : `maxweightrating` 8 fois, `maxweight` 7, `hgv` 1. **Le contrôle passe.** Et
la seule preuve « générale seule » de tout l'ensemble est le point 71, **déjà pris par la
distance** — les deux fautes coïncident ici. **C'est une chance, pas une garantie :** rien
ne dit qu'elles coïncideront la prochaine fois, et c'est pourquoi le contrôle de prédicat
est désormais une étape à part et non un sous-produit du détecteur de distance.

#### g) Le pipeline commet la même faute que le vérificateur, et elle vaut 1,2 point

Si `access=private` ne prouve rien chez un vérificateur, il ne prouve rien non plus dans le
code — **et la définition pré-inscrite l'accepte pourtant comme couverture**, liste héritée
de l'outil existant. **Sensibilité mesurée sur le réseau entier :**

| | |
|---|---|
| Linéaire couvert reposant sur `access` / `motor_vehicle` **seul** | **26,5 km — 11,6 % du couvert** |
| Taux d'absence, définition pré-inscrite | **89,6 %** |
| Taux si **seule la preuve de tonnage** comptait | **90,8 %** |

> **Le chiffre principal reste 89,6 %** : la définition était pré-inscrite, et on ne la
> change pas après avoir vu ce qu'elle donne. **La sensibilité se publie à côté**, et elle
> est bornée à 1,2 point.
>
> **Elle va encore dans le sens qui arrange**, comme les deux corrections précédentes.
> Trois de suite, ce qui n'est défendable que par l'ordre des commits : chacune a été
> décidée sur une règle écrite avant, pas sur son effet.

#### h) Le tonnage discordant est un raffinement du détecteur de distance, pas un troisième

Les deux aberrants portaient aussi un **tonnage discordant** — 8 t contre 13, rien contre
19. C'est tentant d'en faire un troisième détecteur. **Ce n'en est pas un**, et l'écrire
comme tel gonflerait la confiance :

| Ce qu'on observe | Ce que c'est |
|---|---|
| Voie **correcte**, valeur différente | Un **écart réel** — la classe de conflits du §9, le produit lui-même |
| Voie **fausse**, valeur différente | Une **erreur d'attribution** |

> **Le signal seul ne discrimine pas les deux.** C'est sa conjonction avec la distance qui
> a fonctionné ici — et une conjonction n'est pas un détecteur indépendant, c'est une
> **covariable du premier**. Trois détecteurs concordants dont deux mesurent la même chose
> valent deux, pas trois.
>
> Il est donc pré-inscrit pour la campagne suivante **comme raffinement du détecteur de
> distance**, à lire conjointement et jamais seul.

#### i) La symétrie de l'effort — une recherche menée exprès dans l'autre polarité

**Les trois corrections précédentes montaient toutes le taux, et ce n'est ni de la chance
ni du biais : c'est une propriété de la classe de fautes cherchée.** `highway=service`
compté comme carrossable, `access` compté comme preuve de tonnage, attribution à la voie
d'à côté — **les trois retirent de la couverture fausse**, et retirer de la couverture
fausse fait mécaniquement monter l'absence.

> **La défense n'est donc pas l'ordre des commits — c'est que le sens était prévisible à la
> nature de la faute, avant d'en calculer l'effet.** Une correction dont on peut dire
> d'avance « ce défaut sur-crédite la couverture, donc le réparer montera le taux » ne
> renseigne sur rien d'autre que sur le défaut.
>
> **Ce qui manquait n'était pas une justification, c'était une symétrie d'effort.** Elle a
> été faite le 3 août : chercher délibérément une faute de **sous-crédit**, un défaut qui
> ferait *baisser* le taux.

**Quatre pistes suivies, résultats mesurés :**

| Piste | Trouvé | Effet |
|---|---|---|
| **`service` portant un VRAI tonnage**, jeté par le filtre carrossable | **212 voies** — `maxweight=3.5` ×195, 10 t ×21, 13 t ×18. 50 sont nommées. | **−0,1 point** (89,6 → 89,5) |
| **Clés d'interdiction jamais interrogées** — `goods`, `vehicle`, `access:hgv`, `maxweight:hgv` | Sondage Overpass sur Lyon : **11 voies restrictives** de plus, contre 9 064 déjà présentes | **+0,1 % de voies porteuses** — bien sous 0,1 point |
| **`maxweight:conditional` rejeté** par l'analyseur | 120 valeurs, mais **2 seulement** sans tonnage de base. Les autres disent « pas de limite pour la desserte », ce qui suppose une limite lue par ailleurs. | négligeable |
| **Voies couvrantes sous le seuil de recouvrement** | **Sans objet** : la mesure en mètres est ponctuelle et n'emploie aucun seuil de recouvrement. Ce candidat ne concernait que l'ancien outil. | — |

**Le bilan, avec les deux polarités côte à côte :**

| Sens | Correction | Effet |
|---|---|---|
| ↑ | `highway=service` sur `access` seul, retiré | **+3,8 pt** |
| ↑ | attribution au-delà de 10 m (variante sur l'échantillon) | **+1,4 pt** |
| ↑ | `access`/`motor_vehicle` comme preuve (sensibilité, non appliquée) | **+1,2 pt** |
| ↓ | **`service` portant un vrai tonnage, repêché** | **−0,1 pt** |
| ↓ | **clés jamais interrogées** | **< 0,1 pt** |

> **La faute de polarité inverse existe, elle a été cherchée, et elle est d'un ordre de
> grandeur plus petite.** C'est une conclusion plus forte que « je n'en ai pas trouvé »,
> et incomparablement plus forte que de ne pas avoir cherché.
>
> **Une absence de faute constatée après l'avoir cherchée vaut infiniment plus qu'une
> absence de faute non cherchée.** C'est ce qui fait passer la défense de « défendable par
> l'ordre des commits » — qui ne tient que tant que le journal est lu — à « défendable par
> la symétrie de l'effort », qui ne dépend d'aucun journal.

**Pourquoi l'asymétrie est d'un facteur trente, et pourquoi ce n'est pas un signe de
recherche molle.**

> **Le pipeline a été construit pour trouver de la couverture.** Chaque heuristique écrite
> au fil de ces deux jours — élargir le jeu de clés, accepter `access` comme preuve,
> inclure les voies de service — avait pour but de **ne pas manquer une restriction
> existante**. La générosité était le mode par défaut, à chaque décision.
>
> **Les fautes se concentrent donc là où l'effort de conception s'est porté. Un outil bâti
> pour ne rien manquer accumule des faux positifs, pas des faux négatifs.** L'asymétrie du
> bilan n'est pas le résultat d'une recherche déséquilibrée : **c'est la signature de
> l'intention qui a présidé au code.**
>
> Sans cette phrase, un lecteur doit choisir entre « il a mal cherché » et « il a eu de la
> chance ». Avec elle, il n'a plus à choisir.

**Le corollaire, écrit comme une prédiction et non comme un constat :**

> **Si le biais de conception est la générosité, les fautes restantes — celles qui n'ont
> pas encore été trouvées — sont probablement du même côté. Le risque résiduel est que
> 89,6 % soit encore un peu trop bas, pas trop haut.**
>
> C'est inconfortable à écrire quand on publie un chiffre déjà élevé, et c'est la raison de
> l'écrire.

**Ce qui la falsifierait, fixé maintenant pour qu'elle soit autre chose qu'une posture :**
une recherche ultérieure qui trouverait **une faute de sous-crédit dépassant 1 point** —
soit dix fois la plus grosse trouvée ici. Si cela arrive, **la prédiction est fausse et se
retire**, et avec elle l'idée que le chiffre est un plancher.

**Ce que la recherche n'a pas pu couvrir, et qui reste ouvert :** l'extrait OSM a été
constitué par une requête sur six clés. Une voie taguée **uniquement** dans une clé non
interrogée n'a jamais été téléchargée, et aucune analyse du fichier local ne peut la voir.
Le sondage lyonnais borne ce trou à ~0,1 % des voies porteuses **dans une zone dense** ;
il ne le borne pas ailleurs. **Un extrait complet du réseau le fermerait**, et c'est la
même collecte que celle qui transformerait le détecteur de distance en preuve.

#### j) Le mot « plancher » ne se transporte pas — ce qui le soutient a changé

**Le 71,2 % méritait ce mot pour une raison mesurée** : des ACCORD étaient en réalité des
couvertures partielles, donc l'absence par arrêté était sous-estimée. **Un biais démontré,
pas une prédiction.**

> **Or la mesure en mètres compte la couverture partielle à sa juste proportion. Le biais
> qui justifiait le mot a disparu — c'était un artefact du critère binaire, et cette mesure
> le supprime.**
>
> **C'est exactement le glissement redouté :** un mot gagné pour un chiffre, reconduit pour
> un autre parce qu'il y était déjà. Le même mécanisme que la caution de l'épreuve aveugle
> transportée d'une mesure à l'autre — dont on a fait une invariante quelques heures plus
> tôt, et qu'on allait enfreindre sur un adjectif.

**Ce qui soutient encore le mot pour le 89,6 %, énoncé en entier :**

| Appui | Nature | Force |
|---|---|---|
| **2 des 12 OUI du pipeline sur l'échantillon aveugle sont de fausses attributions** — points 50 et 71, nommés, vérifiables | **Mesuré**, sur un échantillon tiré hors du pipeline | Réel, mais **12 cas** |
| Aucune fausse absence trouvée en sens inverse sur ce même échantillon | **Non établi** — les 128 NON n'ont pas encore été contrôlés | **Nul tant que les vérificateurs n'ont pas rendu** |
| La recherche en polarité inverse a rendu −0,1 point contre +6,4 | Mesuré | Réel |
| Le biais de générosité de conception | **Prédiction datée, réfutable** | Une prédiction, pas une mesure |

> **Donc : le mot est conservé, et il est désormais accompagné de ce qui le porte.**
>
> *« 89,6 % est un plancher au sens suivant, et pas d'un autre : deux des douze couvertures
> détectées sur un échantillon aveugle se sont révélées fausses, la recherche de fautes
> inverses a rendu trente fois moins, et le biais de conception de l'outil est la
> générosité. Le premier appui repose sur douze cas ; le troisième est une prédiction
> réfutable, pas un constat. »*
>
> **Employer le mot seul serait plus faible que de ne pas l'employer.** Il ne se cite jamais
> sans cette phrase.

**Et le deuxième appui reste ouvert :** tant que les 128 NON de l'échantillon ne sont pas
contrôlés, **rien n'établit qu'il n'y a pas de fausses absences en face des deux fausses
couvertures.** C'est précisément ce que l'épreuve en cours doit dire, et c'est la raison
pour laquelle son résultat peut retirer le mot.

#### k) Le tableau à quatre cases — la lecture qui remplit l'appui vide

**L'épreuve ne se lit pas au taux global.** Chaque point produit **deux verdicts** : celui
du pipeline et celui du vérificateur. Les croiser donne ce que la marge ne donne pas.

| | Vérificateur **OUI** | Vérificateur **NON** |
|---|---|---|
| **Pipeline OUI** | accord | **FAUSSE COUVERTURE** |
| **Pipeline NON** | **FAUSSE ABSENCE** | accord |

> **La case en bas à gauche est l'appui vide du §3.4 j.** Un point où le pipeline dit
> « rien » et où un vérificateur aveugle trouve une restriction est une **fausse absence
> mesurée**, sur un échantillon tiré hors du pipeline. **Aucune recherche manuelle ne
> pouvait la produire** — c'est la seule chose que cette épreuve apporte et que rien
> d'autre n'apporte.
>
> Et les deux cases hors diagonale, prises ensemble, **sont le bilan de polarité au niveau
> du point.** Le §3.4 i l'a construit à la main sur les définitions ; l'épreuve le livre
> sur les données.

**Pourquoi la marge seule ne suffit pas — c'est l'argument des erreurs qui se compensent,
transposé d'un cran.** Huit fausses absences et six fausses couvertures donnent un taux
global à deux points de 89,6 %, **parfaitement concordant et masquant quatorze erreurs.**
La marge borne l'erreur **nette** ; seules les cases hors diagonale montrent les
**composantes**, et ce sont elles que la réserve publiée dit ne pas valider.

**Les comptes bruts sont la bonne grandeur, et c'est le seul endroit où ils le sont :** sur
140 points, chaque fausse couverture déplace l'estimation de −1/140 et chaque fausse
absence de +1/140. **Le bilan de polarité est donc exactement leur différence**, sans
rapporter à des dénominateurs différents.

**Règle de lecture, fixée avant les résultats.** Soient `a` fausses couvertures et `b`
fausses absences. Les effectifs seront petits — une douzaine de OUI du pipeline, ~128 NON,
donc des cases hors diagonale à un chiffre. **À ces effectifs, trois contre un ne se lit
pas comme un rapport de trois.**

| Observé | Lecture, et rien d'autre |
|---|---|
| **`\|a − b\| ≤ 2√(a+b)`** | **Indiscernables.** Le bilan de polarité est nul au niveau du point. **Le mot « plancher » perd son appui mesuré et ne repose plus que sur la prédiction** — il se retire de l'énoncé public ou s'accompagne de cette précision. |
| **`b < a`, écart au-delà du seuil** | Les fausses couvertures dominent : **la mesure sous-estime l'absence.** L'appui mesuré du « plancher » est rempli. |
| **`b > a`, écart au-delà du seuil** | Les fausses absences dominent : **la mesure surestime l'absence, 89,6 % est trop haut.** Le mot « plancher » est **retiré**, et la prédiction de générosité de conception (§3.4 i) est **réfutée** — c'est un des deux chemins de sa réfutation, l'autre étant la seconde ingestion. |

> **Ce qu'on n'écrira pas :** un taux de fausses absences. Les cases donneront **un ordre de
> grandeur et un sens**, pas une valeur.

**Un biais connu de ce tableau, et il joue contre moi — donc on le laisse jouer.** Une
erreur du vérificateur en faux OUI, sur un point où le pipeline dit NON, se compte en
« fausse absence ». C'est l'erreur la plus probable du vérificateur (§3.4 d : un faux OUI
peut frapper 89,6 % des points, un faux NON seulement 10,4 %). **La case qui argumente
contre le « plancher » est donc la plus contaminée.** Si le mot survit à cette épreuve, il
survit malgré un biais qui lui est défavorable.

**Diagnostic immédiat prévu pour chaque fausse absence :** passer le point au détecteur
géométrique et dire **pourquoi** le pipeline l'a manqué — voie porteuse rejetée par le cap,
par la distance, par le filtre de classe, ou absente de l'extrait. Une fausse absence dont
on connaît la cause est une correction ; une fausse absence inexpliquée est une réserve.

### 3.5 Ce que cette section engage

**Le générateur peut maintenant être écrit.** Ce qui sortira est le compte. Si le taux en
mètres s'écarte nettement du 71,2 % par arrêté, **c'est le résultat attendu, pas une
anomalie à corriger** — les deux unités mesurent des choses différentes, et la section 2
dit d'avance pourquoi elles ne peuvent pas coïncider.

> **Aucun ajustement de définition n'est autorisé après lecture du résultat.** Un
> amendement reste possible, mais il s'écrit ici, daté, avec son motif — et le motif ne
> peut pas être la valeur obtenue.

---

## 4. Ce qui a été réénoncé

**Balayage fait à la main le 3 août, le mécanisme délégué ayant échoué trois fois là où une
seule passe manuelle avait produit les meilleures trouvailles.**

| Artefact | Avant | Après |
|---|---|---|
| **Titre de la carte** | *« Plus de sept interdictions sur dix… »* — un compte d'arrêtés | *« Neuf kilomètres sur dix de voirie interdite… »* — l'unité déclarée |
| **Chiffre-clé** | 71,2 % des arrêtés | **89,6 % des kilomètres**, avec **74,5 % des arrêtés** à côté |
| **Légende** | ACCORD / ÉCART / COUVERT_FAIBLE — des verdicts de comparaison | **ABSENT / MARGINAL / PARTIEL / COUVERT** — des classes de couverture |
| **Infobulle** | un verdict binaire | mètres réglementés, mètres sans restriction, part couverte |
| **Table méthodologique** | seuil de recouvrement, témoins de l'épreuve | unité pré-inscrite, périmètre déclaré et son défaut de couverture, pas d'échantillonnage, **et ce que la vérification ne dit pas** |
| **Réserves** | une seule, sur la reproductibilité | **trois réserves et quatre limites**, lues depuis le geojson |
| **Générateur** | **aucun** — script jetable perdu | [carte-geojson.py](../outils/carte-geojson.py), qui importe la mesure au lieu de la refaire |

**Ce que le réénoncé a coûté, et qu'il fallait payer :** le geojson passe de 2 045 à
**2 051 entités**. Les six de différence sont les arrêtés que l'ancienne emprise excluait
sans le dire (§0). **Le dénominateur cesse d'être découpé par la collecte.**

> **La page ne porte plus aucun chiffre en dur.** Titre mis à part — « neuf sur dix » est
> une formulation, pas une valeur — tout se calcule au chargement depuis le geojson, y
> compris les réserves et la définition de l'unité. **Une mesure rejouée met la page à jour
> d'elle-même**, ce qui était l'invariante du §18 et qui n'était vrai qu'à moitié.

**Ce qui reste à réénoncer, et qui ne l'est pas :**

- **La lettre au LWG** ne cite aucun taux d'absence — vérifié. Ses chiffres portent sur la
  provenance et l'indépendance géométrique, qui ne dépendent pas de l'unité. **Rien à
  changer**, et c'est un résultat du balayage, pas une omission.
- **Le §9 du ROADMAP** garde ses mesures par arrêté avec leur définition écrite à côté.
  Elles ne sont pas fausses : elles répondent à une autre question. **Les effacer
  reviendrait à effacer l'histoire du chiffre**, et un chiffre effacé se réinvente.
- **Le titre de presse du §14** dit « plus de sept sur dix », c'est-à-dire le compte par
  arrêté. Il devient **« neuf kilomètres sur dix »**, et la phrase de Cassel reste à côté
  de lui pour expliquer pourquoi les deux existent.
