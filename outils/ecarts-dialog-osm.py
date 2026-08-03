#!/usr/bin/env python3
"""Écarts de tonnage entre les arrêtés DiaLog et OpenStreetMap.

Prototype de la règle de détection qui tourne **sans aucun utilisateur** :
chaque désaccord entre un acte administratif et la carte est une faille
détectée, sourcée par un document opposable.

POURQUOI PLUSIEURS CLÉS OSM
---------------------------
Une interdiction aux plus de 3,5 t s'exprime rarement par la seule clé
`maxweight`. Elle se tague aussi `hgv=no`, `maxweightrating`,
`maxweight:conditional`, voire `access=destination`. Or DiaLog est concentré
à 76 % sur 3,5 t — précisément le seuil que les contributeurs OSM expriment
par `hgv=no` plutôt que par un nombre.

Ne comparer qu'à `maxweight` surévalue donc massivement le taux d'absence.
Une première version de cet outil faisait cette erreur.

VERDICTS
--------
  ACCORD        tonnage OSM numérique identique
  ECART         tonnage OSM numérique différent  <- la vraie sortie produit
  COUVERT_HGV   pas de nombre, mais une restriction poids lourd explicite
  COUVERT_FAIBLE  seulement access/motor_vehicle : indice ambigu, pas une preuve
  ABSENT        aucune expression de restriction

Seul ABSENT est une lacune franche. COUVERT_FAIBLE ne prouve rien : un chemin
privé porte `access=private` sans qu'aucune interdiction de tonnage existe.

SÉMANTIQUE DU TONNAGE
---------------------
Établie sur le flux du 2 août 2026 : le comparisonOperator des 2 835
caractéristiques de poids vaut *toujours* lessThanOrEqualTo. La valeur DiaLog
exprime donc le tonnage autorisé, exactement comme OSM maxweight.
Le script refuse de tourner si cette invariante tombe.

Usage :
    python3 outils/ecarts-dialog-osm.py <dialog.xml> <osm.json> \
            <tolerance_m> <recouvrement> <rapport.json>

    <rapport.json> : OBLIGATOIRE. L'enregistrement machine, à pleine précision.
                 La sortie texte en est une projection arrondie et n'est jamais
                 une source de calcul — l'emprise affichée à trois décimales a
                 déjà produit « 220 m » là où la valeur exacte donne 37,9 m.

    <osm.json> : sortie Overpass `out tags geom;` couvrant TOUTES les clés
                 ci-dessous sur un territoire, par exemple :
                 [out:json][timeout:240];
                 way(<bbox>)["highway"]["maxweight"]->.a;
                 way(<bbox>)["highway"]["maxweight:conditional"]->.b;
                 way(<bbox>)["highway"]["maxweightrating"]->.c;
                 way(<bbox>)["highway"]["hgv"]->.d;
                 way(<bbox>)["highway"]["access"~"^(no|destination|private|delivery|agricultural|forestry)$"]->.e;
                 way(<bbox>)["highway"]["motor_vehicle"~"^(no|destination|private|delivery|agricultural|forestry)$"]->.f;
                 (.a;.b;.c;.d;.e;.f;);out tags geom;

Aucune valeur n'est codée en dur : la tolérance vient de la ligne de commande
ou de ECARTS_TOLERANCE_M, et son absence est une erreur, pas un défaut.

Et aucune valeur destinée à l'affichage ne sert à calculer. Un affichage
arrondit, tronque, formate, résume — c'est son travail ; à la seconde où une
valeur imprimée rentre dans un calcul, le formatage devient une partie du
résultat. D'où le rapport machine obligatoire : on ne répare pas ça par une
consigne de vigilance, on le répare en rendant la valeur exacte plus accessible
que l'affichage.
Les noms de clés et de valeurs ci-dessous sont du vocabulaire OSM, pas des
réglages : ils décrivent le schéma de la source, ils ne s'ajustent pas.
"""

import hashlib
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

NS_TR = "{http://datex2.eu/schema/3/trafficRegulation}"
NS_COM = "{http://datex2.eu/schema/3/common}"
NS_DX = "{https://raw.githubusercontent.com/MTES-MCT/dialog/main/docs/spec/datex2}"

ORDER = NS_TR + "trafficRegulationOrder"
GEOMETRY = NS_DX + "geoJsonGeometry"
WEIGHT = NS_COM + "grossWeightCharacteristic"
OPERATOR = NS_COM + "comparisonOperator"
TONNAGE = NS_COM + "grossVehicleWeight"
ACCESS_TYPE = NS_TR + "accessRestrictionType"
AUTHORITY = NS_TR + "issuingAuthority"

# Plage observée sur les 2 835 caractéristiques de poids du flux : 1,5 à 75 t,
# 32 valeurs distinctes, toutes multiples de 0,5. Au-delà, on signale — le 75 t
# est possible et surprenant, pas impossible.
TONNAGE_PLAUSIBLE = (1.0, 44.0)

OPERATEUR_ATTENDU = "lessThanOrEqualTo"
RAYON_TERRE_M = 6_371_000.0

# Un degré de latitude en mètres, pour convertir une tolérance métrique en marge
# décimale avant le pré-filtre par boîte. Approximation volontaire et majorante :
# elle élargit la boîte, donc ne peut pas écarter un candidat valide. Elle était
# recopiée en trois endroits ; trois copies d'une même valeur, c'est deux
# occasions d'en corriger une seule.
METRES_PAR_DEGRE_LATITUDE = 111_000.0

# Un tonnage DATEX II est un multiple de 0,5 : cette tolérance n'absorbe que le
# bruit de la représentation flottante, jamais un écart réel.
EPSILON_PAS_TONNAGE = 1e-9

# Deux tonnages séparés de moins d'un gramme sont le même tonnage. Sépare un
# désaccord réel d'une différence d'arrondi entre les deux sources.
EPSILON_EGALITE_TONNAGE = 1e-6

NS_LOC = "{http://datex2.eu/schema/3/locationReferencing}"
ROAD_NUMBER = NS_LOC + "roadNumber"
LOCATION_DESC = NS_LOC + "locationDescription"

# Une voie candidate doit CHEVAUCHER l'arrêté, pas seulement le frôler.
# Le cas qui a imposé cette règle : l'arrêté « 1 - Interdiction 7,5t - La Flèche »
# vise la D10 ; l'appariement au plus proche a retenu la C 2, une route qui
# débouche en T sur la D10 et s'en éloigne jusqu'à 660 m. 3 sommets sur 13 sous
# tolérance, distance médiane 268 m — et un faux écart annoncé de 7,5 contre 10 t.
# La D10, elle, portait déjà le bon tonnage.
MOTIF_NUMERO = re.compile(r"([A-Z])\s*0*(\d+)")

# Vocabulaire OSM. Trois niveaux de preuve, du plus fort au plus faible.
CLES_NUMERIQUES = ("maxweight", "maxweightrating", "maxweight:conditional")
CLES_POIDS_LOURD = ("hgv",)
CLES_GENERALES = ("access", "motor_vehicle")
VALEURS_RESTRICTIVES = frozenset(
    {"no", "destination", "private", "delivery", "agricultural", "forestry"}
)

ORDRE_VERDICTS = ("ACCORD", "ECART", "COUVERT_HGV", "COUVERT_FAIBLE", "ABSENT")
ECARTS_MONTRES = 20

# Un poids lourd ne roule pas sur un escalier. Une restriction posée sur un
# chemin, une piste cyclable ou un trottoir ne « couvre » pas une interdiction
# de tonnage sur la départementale voisine.
# Ce qui a imposé ce filtre : sur 31 arrêtés classés « couverts » par un tag
# access ou motor_vehicle, 31 l'étaient par une voie non carrossable — dont un
# arrêté portant sur 6,4 km de départementale « couvert » par un access=private
# sur un chemin sans nom à 4,4 m, et un escalier à 26 m d'un autre.
CLASSES_CARROSSABLES_PL = frozenset(
    {
        "motorway", "motorway_link", "trunk", "trunk_link",
        "primary", "primary_link", "secondary", "secondary_link",
        "tertiary", "tertiary_link", "unclassified", "residential",
        "living_street", "road", "busway",
    }
)


def exiger(condition, message):
    if not condition:
        sys.exit(message)


def tolerance_metres():
    brut = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("ECARTS_TOLERANCE_M")
    exiger(
        brut,
        "Tolérance de rapprochement non fournie.\n"
        "  python3 outils/ecarts-dialog-osm.py <dialog.xml> <osm.json> <tolerance_m> <recouvrement>\n"
        "  ou ECARTS_TOLERANCE_M=<mètres>\n"
        "Cette valeur décide ce qui compte comme « le même endroit ». Elle se\n"
        "calibre sur des cas connus (§19 du ROADMAP), elle ne se devine pas.",
    )
    return float(brut)


def recouvrement_minimal():
    brut = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("ECARTS_RECOUVREMENT_MIN")
    exiger(
        brut,
        "Recouvrement minimal non fourni.\n"
        "  python3 outils/ecarts-dialog-osm.py <dialog.xml> <osm.json> <tolerance_m> <recouvrement>\n"
        "  ou ECARTS_RECOUVREMENT_MIN=<fraction entre 0 et 1>\n"
        "Fraction des sommets de la voie OSM devant tomber sous la tolérance.\n"
        "Sans elle, une route qui ne fait que croiser l'arrêté est retenue —\n"
        "c'est le faux positif de La Flèche. Se calibre, ne se devine pas.",
    )
    valeur = float(brut)
    exiger(0.0 < valeur <= 1.0, "Le recouvrement doit être une fraction dans ]0, 1].")
    return valeur


def chemin_rapport():
    """Où écrire l'enregistrement machine. Obligatoire, comme les autres paramètres.

    Il n'est pas optionnel, et c'est délibéré. Un affichage arrondit, tronque et
    formate — c'est son travail. À la seconde où une valeur imprimée rentre dans
    un calcul, le formatage devient une partie du résultat : l'emprise affichée
    à trois décimales a produit « 220 m » là où la valeur exacte donne 38 m, une
    erreur d'un facteur six.

    On ne répare pas ça par une consigne de vigilance — la vigilance a perdu
    trois fois en deux jours. On le répare en rendant la valeur exacte PLUS
    ACCESSIBLE que l'affichage. Rendre le rapport obligatoire, c'est faire du
    chemin correct le seul chemin.
    """
    brut = sys.argv[5] if len(sys.argv) > 5 else os.environ.get("ECARTS_RAPPORT")
    exiger(
        brut,
        "Chemin du rapport machine non fourni.\n"
        "  python3 outils/ecarts-dialog-osm.py <dialog.xml> <osm.json> "
        "<tolerance_m> <recouvrement> <rapport.json>\n"
        "  ou ECARTS_RAPPORT=<chemin>\n"
        "Ce fichier porte les valeurs à PLEINE PRÉCISION — emprise, seuils,\n"
        "compteurs, empreintes. L'affichage texte en est une projection lisible,\n"
        "jamais une source de calcul.",
    )
    return brut


def ecrire_rapport(chemin, rapport):
    """Écriture atomique : temporaire puis renommage.

    Une écriture en place laisse un JSON tronqué si le processus meurt pendant
    le vidage du tampon — et le fichier est illisible pendant une fraction de
    CHAQUE écriture, pas seulement de la dernière. Une collecte a déjà été
    perdue comme ça.
    """
    temporaire = chemin + ".tmp"
    with open(temporaire, "w", encoding="utf-8") as sortie:
        json.dump(rapport, sortie, ensure_ascii=False, indent=1, sort_keys=True)
        sortie.flush()
        os.fsync(sortie.fileno())
    os.replace(temporaire, chemin)


def empreinte_fichier(chemin):
    """Identité du fichier d'entrée : sans elle, un rapport ne dit pas sur quoi il porte."""
    haché = hashlib.sha256()
    with open(chemin, "rb") as entree:
        for bloc in iter(lambda: entree.read(1 << 20), b""):
            haché.update(bloc)
    return {
        "chemin": os.path.abspath(chemin),
        "octets": os.path.getsize(chemin),
        "sha256": haché.hexdigest(),
    }


def numero_normalise(texte):
    """« 72_D0010 », « D 10 », « D10 » -> « D10 ». None si aucun numéro lisible."""
    if not texte:
        return None
    trouve = MOTIF_NUMERO.search(texte.upper())
    return f"{trouve.group(1)}{trouve.group(2)}" if trouve else None


def metres_par_degre(latitude):
    lat_m = math.pi * RAYON_TERRE_M / 180.0
    return lat_m, lat_m * math.cos(math.radians(latitude))


def distance_point_segment(point, debut, fin, echelle):
    """Distance en mètres d'un point à un segment, en projection locale plane."""
    m_lat, m_lon = echelle
    px, py = point[0] * m_lon, point[1] * m_lat
    ax, ay = debut[0] * m_lon, debut[1] * m_lat
    bx, by = fin[0] * m_lon, fin[1] * m_lat
    dx, dy = bx - ax, by - ay
    longueur2 = dx * dx + dy * dy
    if longueur2 == 0.0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / longueur2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def parcourir_coordonnees(geometrie):
    """Aplatit n'importe quel type GeoJSON en une liste de (lon, lat)."""
    if not isinstance(geometrie, dict):
        return []
    if geometrie.get("type") == "GeometryCollection":
        points = []
        for sous in geometrie.get("geometries", []):
            points.extend(parcourir_coordonnees(sous))
        return points

    points = []

    def descendre(noeud):
        if (
            isinstance(noeud, list)
            and len(noeud) == 2
            and all(isinstance(v, (int, float)) for v in noeud)
        ):
            points.append((float(noeud[0]), float(noeud[1])))
        elif isinstance(noeud, list):
            for enfant in noeud:
                descendre(enfant)

    descendre(geometrie.get("coordinates", []))
    return points


def tonnage_osm(brut):
    """OSM autorise « 3.5 », « 3.5 t », « 7500 kg »… Retourne des tonnes ou None."""
    texte = str(brut).strip().lower().replace(",", ".")
    if ";" in texte or "@" in texte:  # maxweight:conditional composite
        texte = texte.split(";")[0].split("@")[0].strip()
    facteur = 1.0
    for suffixe, coefficient in (("kg", 0.001), ("t", 1.0)):
        if texte.endswith(suffixe):
            texte = texte[: -len(suffixe)].strip()
            facteur = coefficient
            break
    try:
        return float(texte) * facteur
    except ValueError:
        return None


def qualifier(tags):
    """Niveau de preuve porté par une voie OSM, et tonnage si exprimé."""
    for cle in CLES_NUMERIQUES:
        if cle in tags:
            valeur = tonnage_osm(tags[cle])
            if valeur is not None:
                return "numerique", valeur, cle
    for cle in CLES_POIDS_LOURD:
        if tags.get(cle) in VALEURS_RESTRICTIVES:
            return "poids_lourd", None, cle
    # Les clés générales ne valent comme indice que sur une voie où un poids
    # lourd peut effectivement passer. Ailleurs, ce n'est pas une preuve faible :
    # ce n'est pas une preuve.
    if tags.get("highway") in CLASSES_CARROSSABLES_PL:
        for cle in CLES_GENERALES:
            if tags.get(cle) in VALEURS_RESTRICTIVES:
                return "general", None, cle
    return None, None, None


def charger_osm(chemin):
    with open(chemin, encoding="utf-8") as flux:
        donnees = json.load(flux)
    voies = []
    for element in donnees.get("elements", []):
        geometrie = element.get("geometry") or []
        tags = element.get("tags") or {}
        niveau, tonnage, cle = qualifier(tags)
        if not geometrie or niveau is None:
            continue
        voies.append(
            {
                "id": element.get("id"),
                "niveau": niveau,
                "tonnage": tonnage,
                "cle": cle,
                "nom": tags.get("name") or tags.get("ref") or "",
                "numero": numero_normalise(tags.get("ref")),
                "points": [(p["lon"], p["lat"]) for p in geometrie],
            }
        )
    instantane = (donnees.get("osm3s") or {}).get("timestamp_osm_base", "inconnu")
    return voies, instantane


def charger_dialog(chemin):
    """Retourne les arrêtés retenus, les opérateurs vus, et le journal des écarts.

    Aucun enregistrement n'est écarté en silence : chaque rejet est compté et
    restitué. Une assertion sans compteur est une perte de données silencieuse,
    et une donnée qui disparaît sans que personne ne décide est un contournement
    au sens de la règle 4 du §18.
    """
    arretes = []
    operateurs = Counter()
    journal = Counter()
    for _, element in ET.iterparse(chemin, events=("end",)):
        if element.tag != ORDER:
            continue
        journal["ordres_lus"] += 1
        tonnages = []
        for caracteristique in element.iter(WEIGHT):
            operateurs[caracteristique.findtext(OPERATOR)] += 1
            valeur = caracteristique.findtext(TONNAGE)
            if valeur is None:
                journal["rejet_tonnage_illisible"] += 1
                continue
            tonnage = float(valeur)
            # Rejeter l'impossible, signaler l'improbable. Les 32 valeurs
            # observées dans le flux sont toutes multiples de 0,5 ; 7,3 t est
            # impossible, 75 t est possible et surprenant.
            if abs(tonnage * 2 - round(tonnage * 2)) > EPSILON_PAS_TONNAGE:
                journal["rejet_tonnage_hors_pas"] += 1
                continue
            if not TONNAGE_PLAUSIBLE[0] <= tonnage <= TONNAGE_PLAUSIBLE[1]:
                journal["signale_tonnage_rare"] += 1
            tonnages.append(tonnage)
        if tonnages:
            journal["ordres_avec_tonnage"] += 1
            # Un tonnage qui qualifie une règle de stationnement ou de vitesse
            # n'est pas une interdiction de circuler. Si OSM ne porte rien en
            # face, c'est le comportement correct, pas une lacune.
            # Exclu de la MESURE, jamais du corpus : « interdiction de
            # stationner aux plus de 7,5 t » est une donnée directement utile,
            # d'origine officielle et en Licence Ouverte. Un arrêté hors
            # périmètre de mesure change de catégorie, il ne disparaît pas —
            # même logique que la localisation qui échoue et conserve (§11.2).
            restrictions = {(a.text or "").strip() for a in element.iter(ACCESS_TYPE)}
            categorie = "circulation" if "noEntry" in restrictions else "stationnement_ou_vitesse"
            if categorie != "circulation":
                journal["hors_mesure_conserve"] += 1
            points = []
            for geometrie in element.iter(GEOMETRY):
                try:
                    points.extend(parcourir_coordonnees(json.loads(geometrie.text)))
                except (json.JSONDecodeError, TypeError):
                    journal["rejet_geometrie_illisible"] += 1
            if not points:
                journal["rejet_sans_geometrie"] += 1
            if points:
                description = ""
                bloc = element.find(NS_TR + "description")
                if bloc is not None:
                    valeur = bloc.find(".//" + NS_COM + "value")
                    if valeur is not None:
                        description = (valeur.text or "").strip()
                # loc:roadNumber porte son texte directement ; loc:locationDescription
                # enveloppe un com:value. Lire .text sur le second ne renvoie que du
                # blanc — le garde-fou échouait alors sans rien signaler.
                numero = None
                for noeud in element.iter(ROAD_NUMBER):
                    numero = numero or numero_normalise(noeud.text)
                for noeud in element.iter(LOCATION_DESC):
                    for valeur in noeud.iter(NS_COM + "value"):
                        numero = numero or numero_normalise(valeur.text)
                # La collectivité émettrice : sans elle, un arrêté exclu de la
                # mesure n'est qu'une paire de coordonnées, et la liste des
                # exclus n'est pas vérifiable par un lecteur.
                autorite = ""
                for bloc_autorite in element.iter(AUTHORITY):
                    for valeur in bloc_autorite.iter(NS_COM + "value"):
                        autorite = autorite or (valeur.text or "").strip()
                arretes.append(
                    {
                        "tonnage": min(tonnages),
                        "points": points,
                        "description": description,
                        "numero": numero,
                        "categorie": categorie,
                        "autorite": autorite,
                    }
                )
        element.clear()
    return arretes, operateurs, journal


def emprise(voies, marge_degres):
    """Boîte englobante des voies OSM : c'est elle qui définit le territoire.

    Sans ce filtre, on confronterait les arrêtés de toute la France aux voies
    d'un seul département, et le taux d'absence ne mesurerait que l'écart de
    périmètre.
    """
    lons = [p[0] for voie in voies for p in voie["points"]]
    lats = [p[1] for voie in voies for p in voie["points"]]
    exiger(lons and lats, "Le fichier OSM ne contient aucune géométrie exploitable.")
    return (
        min(lons) - marge_degres,
        min(lats) - marge_degres,
        max(lons) + marge_degres,
        max(lats) + marge_degres,
    )


def dans_emprise(points, boite):
    lon_min, lat_min, lon_max, lat_max = boite
    return any(
        lon_min <= lon <= lon_max and lat_min <= lat <= lat_max for lon, lat in points
    )


def bord_franchi(points, boite):
    """Par quel bord de l'emprise un arrêté sort, et de combien.

    Un arrêté qui sort de 220 m et un autre qui sort de 200 km sont deux
    limitations différentes : la première est un bord de boîte mal placé, la
    seconde est un territoire non collecté. Le nombre seul ne les distingue pas.
    """
    lon_min, lat_min, lon_max, lat_max = boite
    par_point = []
    for lon, lat in points:
        # Pour un point donné, le dépassement est le PLUS GRAND des quatre :
        # une valeur négative veut dire « à l'intérieur de ce bord-là », et un
        # point dehors viole au moins une contrainte. Prendre le minimum
        # renverrait la direction où le point est le plus profondément dedans.
        par_point.append(
            max(
                (
                    ("ouest", (lon_min - lon) * METRES_PAR_DEGRE_LATITUDE),
                    ("est", (lon - lon_max) * METRES_PAR_DEGRE_LATITUDE),
                    ("sud", (lat_min - lat) * METRES_PAR_DEGRE_LATITUDE),
                    ("nord", (lat - lat_max) * METRES_PAR_DEGRE_LATITUDE),
                ),
                key=lambda d: d[1],
            )
        )
    # Entre les points de l'arrêté, celui qui est le moins loin dehors décide :
    # c'est de cette marge-là que l'emprise aurait eu besoin pour l'inclure.
    return min(par_point, key=lambda d: d[1])


def boite_de(points, marge=0.0):
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return (
        min(lons) - marge,
        min(lats) - marge,
        max(lons) + marge,
        max(lats) + marge,
    )


def boites_disjointes(a, b):
    return a[0] > b[2] or a[2] < b[0] or a[1] > b[3] or a[3] < b[1]


def distance_a_polyligne(point, polyligne, echelle, plafond):
    """Distance minimale d'un point à une polyligne, arrêtée dès qu'on passe sous le plafond."""
    meilleure = float("inf")
    for debut, fin in zip(polyligne, polyligne[1:]):
        d = distance_point_segment(point, debut, fin, echelle)
        if d < meilleure:
            meilleure = d
            if meilleure <= plafond:
                return meilleure
    return meilleure


def recouvrement(voie, corridor, tolerance):
    """Fraction des sommets de la voie OSM tombant sous la tolérance du corridor.

    C'est ce qui distingue « la même route » de « une route qui la croise ».
    """
    dedans = 0
    for point in voie["points"]:
        echelle = metres_par_degre(point[1])
        if distance_a_polyligne(point, corridor, echelle, tolerance) <= tolerance:
            dedans += 1
    return dedans / len(voie["points"])


def couverture_corridor(arrete, voies_numeriques, tolerance):
    """Part des sommets du corridor à portée d'une voie portant un tonnage.

    Le verdict par arrêté est binaire et il ment par omission : l'arrêté
    « 1 - Interdiction 7,5t - La Flèche » régit 3 448 m de D10, dont seuls 79 m
    — un pont — portent un tonnage dans OSM. Compter cet arrêté « ACCORD » est
    exact et trompeur à la fois.

    ATTENTION À L'UNITÉ. Cette fonction retourne une fraction de SOMMETS, pas
    de mètres : `dedans` est incrémenté de 1 par sommet, et la distance métrique
    ne sert que de prédicat booléen. Les sommets ne sont pas équidistants — leur
    densité suit l'outil de numérisation du fournisseur et la sinuosité du tracé.
    Une ligne droite de 2 km en porte deux, 200 m de virages en portent cinquante.

    Cette docstring a affirmé « pondérée par la longueur » pendant une journée, et
    c'est par elle que l'erreur est entrée dans le ROADMAP puis dans la carte
    publique. Une vraie mesure métrique reste à écrire (docs/unite-preinscrite.md).
    """
    if not voies_numeriques:
        return 0.0
    dedans = 0
    for point in arrete["points"]:
        echelle = metres_par_degre(point[1])
        for voie in voies_numeriques:
            if distance_a_polyligne(point, voie["points"], echelle, tolerance) <= tolerance:
                dedans += 1
                break
    return dedans / len(arrete["points"])


def confronter(arretes, voies, tolerance, recouvrement_min):
    """Pré-filtre par boîte englobante, puis exigence de recouvrement en sommets.

    Le pré-filtre est indispensable : sans lui, le coût est arrêtés x voies x
    segments, soit dix minutes pour un seul département.
    """
    marge = tolerance / METRES_PAR_DEGRE_LATITUDE
    for voie in voies:
        voie["boite"] = boite_de(voie["points"], marge)

    resultats = []
    rejets_numero = 0
    rejets_recouvrement = 0
    for arrete in arretes:
        # Aucun sous-échantillonnage du corridor : à 20 points, la D10 de
        # La Flèche — 92 sommets, la bonne route, en accord exact à 0,1 m —
        # était manquée, et un faux écart prenait sa place.
        corridor = arrete["points"]
        boite_arrete = boite_de(corridor, marge)
        meilleurs = {"numerique": None, "poids_lourd": None, "general": None}
        for voie in voies:
            if boites_disjointes(boite_arrete, voie["boite"]):
                continue

            # Garde-fou gratuit : deux numéros de route différents, deux routes.
            # « D 10 » contre « C 2 » suffisait à écarter le faux positif de
            # La Flèche, sans le moindre calcul de distance.
            if arrete["numero"] and voie["numero"] and arrete["numero"] != voie["numero"]:
                rejets_numero += 1
                continue

            part = recouvrement(voie, corridor, tolerance)
            if part < recouvrement_min:
                if part > 0.0:
                    rejets_recouvrement += 1
                continue

            courant = meilleurs[voie["niveau"]]
            if courant is None or part > courant[0]:
                meilleurs[voie["niveau"]] = (part, voie)

        if meilleurs["numerique"] is not None:
            part, voie = meilleurs["numerique"]
            ecart = abs(voie["tonnage"] - arrete["tonnage"]) > EPSILON_EGALITE_TONNAGE
            resultats.append(("ECART" if ecart else "ACCORD", arrete, part, voie))
        elif meilleurs["poids_lourd"] is not None:
            part, voie = meilleurs["poids_lourd"]
            resultats.append(("COUVERT_HGV", arrete, part, voie))
        elif meilleurs["general"] is not None:
            part, voie = meilleurs["general"]
            resultats.append(("COUVERT_FAIBLE", arrete, part, voie))
        else:
            resultats.append(("ABSENT", arrete, None, None))
    return resultats, rejets_numero, rejets_recouvrement


def main():
    exiger(
        len(sys.argv) >= 3,
        "Usage : python3 outils/ecarts-dialog-osm.py <dialog.xml> <osm.json> [tolerance_m]",
    )
    tolerance = tolerance_metres()
    recouvrement_min = recouvrement_minimal()
    rapport_chemin = chemin_rapport()

    arretes, operateurs, journal = charger_dialog(sys.argv[1])
    inattendus = {op: n for op, n in operateurs.items() if op != OPERATEUR_ATTENDU}
    exiger(
        not inattendus,
        f"Invariante rompue : comparisonOperator attendu « {OPERATEUR_ATTENDU} », "
        f"trouvé aussi {inattendus}.\nLa sémantique du tonnage a changé — "
        "relire le flux avant de comparer quoi que ce soit.",
    )

    voies, instantane = charger_osm(sys.argv[2])
    exiger(
        voies,
        "Aucune voie OSM porteuse de restriction dans ce fichier.\n"
        "La requête Overpass couvre-t-elle bien toutes les clés "
        f"{CLES_NUMERIQUES + CLES_POIDS_LOURD + CLES_GENERALES} ?",
    )
    boite = emprise(voies, marge_degres=tolerance / METRES_PAR_DEGRE_LATITUDE)
    dans = [a for a in arretes if dans_emprise(a["points"], boite)]
    retenus = [a for a in dans if a["categorie"] == "circulation"]
    conserves = len(dans) - len(retenus)

    # POPULATION DANS LE CHAMP vs POPULATION MESURÉE.
    #
    # L'emprise est déduite du fichier OSM, c'est-à-dire de ce qui a été
    # TÉLÉCHARGÉ — jamais du périmètre de la question. Tout ce que produit cet
    # outil en hérite : le dénominateur, mais aussi le numérateur, les écarts,
    # R9, R10, la couverture. Chaque mesure est découpée par une frontière
    # choisie par la collecte.
    #
    # On ne corrige pas ça en élargissant la boîte — la boîte suivante aura la
    # même propriété. On le corrige en DÉCLARANT les deux populations et en
    # publiant l'écart, ce qui transforme un artefact invisible en limitation
    # énoncée.
    #
    # C'est la règle 12 du §18 — aucune assertion sans compteur — appliquée aux
    # rejets GÉOGRAPHIQUES, les seuls auxquels elle ne l'avait jamais été.
    dans_le_champ = [a for a in arretes if a["categorie"] == "circulation"]
    exclus_emprise = [a for a in dans_le_champ if not dans_emprise(a["points"], boite)]

    par_niveau = Counter(voie["niveau"] for voie in voies)

    exiger(
        retenus,
        "Aucun arrêté DiaLog dans l'emprise du fichier OSM : "
        "les deux jeux ne portent pas sur le même territoire.",
    )
    resultats, rejets_numero, rejets_recouvrement = confronter(
        retenus, voies, tolerance, recouvrement_min
    )
    verdicts = Counter(verdict for verdict, _, _, _ in resultats)

    # Fraction de SOMMETS du corridor à portée d'un tonnage : indépendante du
    # seuil de recouvrement, mais PAS pondérée par la longueur — cf. la
    # docstring de couverture_corridor().
    numeriques = [v for v in voies if v["niveau"] == "numerique"]
    marge = tolerance / METRES_PAR_DEGRE_LATITUDE
    for voie in numeriques:
        voie["boite"] = boite_de(voie["points"], marge)
    couvertures = []
    for arrete in retenus:
        boite_arrete = boite_de(arrete["points"], marge)
        candidates = [
            v for v in numeriques if not boites_disjointes(boite_arrete, v["boite"])
        ]
        couvertures.append(couverture_corridor(arrete, candidates, tolerance))
    couvertures.sort()

    # L'ENREGISTREMENT EST CONSTRUIT AVANT L'AFFICHAGE, ET L'AFFICHAGE EN EST
    # UNE PROJECTION.
    #
    # C'est le point de tout ce bloc. Imprimer d'un côté et sérialiser de
    # l'autre recréerait exactement le défaut de la docstring : deux
    # descriptions du même calcul, entretenues séparément, dont l'une finira
    # par mentir. Ici il n'y a qu'une source, et restituer() ne fait que la
    # mettre en forme.
    rapport = {
        "outil": os.path.basename(__file__),
        "instantane_osm": instantane,
        "entrees": {
            "dialog": empreinte_fichier(sys.argv[1]),
            "osm": empreinte_fichier(sys.argv[2]),
        },
        "parametres": {
            "tolerance_m": tolerance,
            "recouvrement_min": recouvrement_min,
            "metres_par_degre_latitude": METRES_PAR_DEGRE_LATITUDE,
            "epsilon_pas_tonnage": EPSILON_PAS_TONNAGE,
            "epsilon_egalite_tonnage": EPSILON_EGALITE_TONNAGE,
            "tonnage_plausible_t": list(TONNAGE_PLAUSIBLE),
            "operateur_attendu": OPERATEUR_ATTENDU,
        },
        "journal_rejets": dict(journal),
        "osm": {
            "voies_porteuses": len(voies),
            "par_niveau": dict(par_niveau),
            # Pleine précision, sans arrondi : c'est cette valeur-ci qui sert à
            # calculer une distance au bord, jamais celle qui est affichée.
            "emprise": {
                "lon_min": boite[0], "lat_min": boite[1],
                "lon_max": boite[2], "lat_max": boite[3],
                "marge_degres": tolerance / METRES_PAR_DEGRE_LATITUDE,
                "origine": "boîte englobante du fichier OSM fourni, "
                           "élargie de la tolérance",
            },
        },
        "populations": {
            "flux_avec_tonnage_et_geometrie": len(arretes),
            "dans_le_champ": len(dans_le_champ),
            "mesuree": len(retenus),
            "hors_emprise": len(exclus_emprise),
            "hors_mesure_conserves": conserves,
            "definition_dans_le_champ":
                "arrêtés portant une caractéristique de poids, un tonnage lisible, "
                "une géométrie, et accessRestrictionType = noEntry",
            "definition_mesuree":
                "les précédents dont au moins un point tombe dans l'emprise OSM — "
                "ce périmètre est HÉRITÉ DE LA COLLECTE et non déclaré",
        },
        "exclus_emprise": [
            {
                "autorite": arrete["autorite"],
                "description": arrete["description"],
                "tonnage_t": arrete["tonnage"],
                "premier_point": {"lon": arrete["points"][0][0],
                                  "lat": arrete["points"][0][1]},
                "bord_franchi": bord_franchi(arrete["points"], boite)[0],
                "marge_manquante_m": bord_franchi(arrete["points"], boite)[1],
            }
            for arrete in exclus_emprise
        ],
        "verdicts": {v: verdicts.get(v, 0) for v in ORDRE_VERDICTS},
        "rejets_appariement": {
            "sur_numero_de_route": rejets_numero,
            "sur_recouvrement": rejets_recouvrement,
        },
        "couverture_en_sommets": {
            "unite": "fraction de sommets de polyligne, PAS de mètres",
            "moyenne": sum(couvertures) / len(couvertures),
            "mediane": couvertures[len(couvertures) // 2],
            "arretes_a_zero_sommet": sum(1 for c in couvertures if c == 0.0),
            "effectif": len(couvertures),
        },
        "ecarts": [
            {
                "tonnage_dialog_t": arrete["tonnage"],
                "tonnage_osm_t": voie["tonnage"],
                "cle_osm": voie["cle"],
                "way_id": voie["id"],
                "nom_osm": voie["nom"],
                "recouvrement": part,
                "description": arrete["description"],
            }
            for verdict, arrete, part, voie in resultats
            if verdict == "ECART"
        ],
    }
    ecrire_rapport(rapport_chemin, rapport)
    restituer(rapport, rapport_chemin)

def restituer(r, chemin):
    """Vue lisible de l'enregistrement. NE CALCULE RIEN.

    Tout ce qui est imprimé ici est arrondi, tronqué ou reformaté : c'est le
    travail d'un affichage. Aucune de ces valeurs ne doit ressortir d'ici pour
    entrer dans un calcul — la version exacte est dans le fichier de rapport,
    dont le chemin est rappelé en tête pour qu'il soit le premier réflexe.
    """
    print(f"rapport machine (valeurs exactes)        : {chemin}")
    print("  l'affichage ci-dessous en est une projection arrondie\n")

    print("journal des écarts — aucun rejet n'est silencieux :")
    for cle in sorted(r["journal_rejets"]):
        print(f"   {cle:32s} : {r['journal_rejets'][cle]}")
    print()
    pop, osm = r["populations"], r["osm"]
    e = osm["emprise"]
    print(f"instantané OSM                           : {r['instantane_osm']}")
    print(f"arrêtés DiaLog avec tonnage et géométrie : "
          f"{pop['flux_avec_tonnage_et_geometrie']} (France entière)")
    print(f"voies OSM porteuses d'une restriction    : "
          f"{osm['voies_porteuses']}  {osm['par_niveau']}")
    print(f"emprise déduite du fichier OSM           : "
          f"{e['lon_min']:.3f},{e['lat_min']:.3f} → {e['lon_max']:.3f},{e['lat_max']:.3f}"
          f"   (arrondie — exacte dans le rapport)")
    print(f"population DANS LE CHAMP                 : {pop['dans_le_champ']}"
          f"  (interdictions de circuler géolocalisées)")
    print(f"population MESURÉE                       : {pop['mesuree']}"
          f"  (celles couvertes par l'extrait OSM)")
    print(f"  écart, non mesuré faute de couverture  : {pop['hors_emprise']}")
    for x in r["exclus_emprise"]:
        print(
            f"     {x['autorite'][:24]:24s} "
            f"{x['premier_point']['lon']:8.3f},{x['premier_point']['lat']:7.3f}"
            f"  {x['bord_franchi']:9s} +{x['marge_manquante_m']:7.0f} m"
            f"   {x['description'][:44]}"
        )
    print(f"  hors mesure mais conservés au corpus   : {pop['hors_mesure_conserves']}"
          f"  (stationnement ou vitesse)")
    par = r["parametres"]
    print(f"tolérance de rapprochement               : {par['tolerance_m']:.0f} m")
    print(f"recouvrement minimal exigé               : {par['recouvrement_min']:.0%}\n")

    total = sum(r["verdicts"].values())
    for verdict in ORDRE_VERDICTS:
        n = r["verdicts"][verdict]
        print(f"   {verdict:15s} : {n:5d}  ({100 * n / total:.1f} %)")
    print(f"\nlacune franche (ABSENT seul)             : "
          f"{100 * r['verdicts']['ABSENT'] / total:.1f} %")
    rej = r["rejets_appariement"]
    print(f"candidats écartés sur numéro de route    : {rej['sur_numero_de_route']}")
    print(f"candidats écartés sur recouvrement       : {rej['sur_recouvrement']}")

    c = r["couverture_en_sommets"]
    print(
        f"\ncouverture en SOMMETS du réseau réglementé — indépendante du recouvrement :"
        f"\n   ({c['unite']})"
        f"\n   part moyenne des sommets du corridor à portée : {c['moyenne']:.1%}"
        f"\n   médiane                                       : {c['mediane']:.1%}"
        f"\n   arrêtés dont AUCUN sommet n'est couvert       : "
        f"{c['arretes_a_zero_sommet']} / {c['effectif']}"
        f"  ({100 * c['arretes_a_zero_sommet'] / c['effectif']:.1f} %)"
    )

    print(f"\nécarts de valeur — les vraies sorties produit "
          f"({len(r['ecarts'])} au total, {ECARTS_MONTRES} montrés) :")
    for x in r["ecarts"][:ECARTS_MONTRES]:
        nom = f" « {x['nom_osm']} »" if x["nom_osm"] else ""
        print(
            f"   DiaLog {x['tonnage_dialog_t']:>5} t  vs  OSM {x['tonnage_osm_t']:>5} t "
            f"[{x['cle_osm']}]  way {x['way_id']}{nom}, "
            f"recouvrement {x['recouvrement']:.0%}"
        )
        print(f"      {x['description'][:95]}")
        print(f"      https://www.openstreetmap.org/way/{x['way_id']}")


if __name__ == "__main__":
    main()
