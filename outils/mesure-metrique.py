#!/usr/bin/env python3
"""Mesure en MÈTRES de l'absence des arrêtés de tonnage dans OpenStreetMap.

Implémente exactement la définition pré-inscrite dans docs/unite-preinscrite.md
§3.2, arrêtée le 3 août 2026 AVANT toute exécution de ce fichier.

    numérateur   longueur, en mètres, du réseau réglementé pour lequel OSM ne
                 porte aucune restriction applicable aux poids lourds
    dénominateur longueur totale du réseau réglementé, chaque portion de
                 chaussée comptée UNE FOIS, quel que soit le nombre d'arrêtés
                 qui la visent

Ce que ce fichier NE FAIT PAS, et c'est délibéré :

  - il ne compte pas d'arrêtés au dénominateur. « X % des arrêtés » ne se dérive
    jamais de sa sortie (§3.2) ;
  - il ne déduit pas son périmètre de l'extrait OSM. Le périmètre est le champ,
    et le défaut de couverture se publie au lieu de rétrécir le dénominateur
    (§0 — sept arrêtés avaient disparu ainsi, l'un par 37,9 m) ;
  - il ne compte pas de sommets. Le rééchantillonnage à pas constant est ce qui
    neutralise la densité de numérisation (§1 — la mesure dite « pondérée par la
    longueur » était une fraction de sommets).

Usage :
    python3 outils/mesure-metrique.py <dialog.xml> <osm.json> <rapport.json> \\
            <pas_test> <pas_dedup> <tolerance> <ang_max> <ecart> <couverture_min>

Paramètres, tous obligatoires, aucun en dur (§3.2) :
    MESURE_PAS_TEST_M           pas de rééchantillonnage
    MESURE_PAS_DEDUP_M          pas de la grille de déduplication
    MESURE_TOL_APPARIEMENT_M    distance maximale point ↔ voie OSM
    MESURE_ANG_MAX_DEG          écart de cap maximal
    MESURE_ECART_NEGLIGEABLE_PT seuil de divergence mètre/arrêté (§3.4)
    MESURE_COUVERTURE_MIN       part minimale du périmètre que l'extrait couvre

Le rapport machine porte les valeurs à pleine précision ; la sortie texte en est
une projection qui ne calcule rien.
"""

import hashlib
import json
import math
import os
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

OPERATEUR_ATTENDU = "lessThanOrEqualTo"
RAYON_TERRE_M = 6_371_000.0
METRES_PAR_DEGRE_LATITUDE = 111_000.0
EPSILON_PAS_TONNAGE = 1e-9

# Clés OSM valant restriction pour un poids lourd. Reprises telles quelles de
# ecarts-dialog-osm.py : deux listes divergentes donneraient deux mesures
# incomparables sans que rien ne le signale.
CLES_NUMERIQUES = ("maxweight", "maxweightrating", "maxweight:conditional")
CLES_POIDS_LOURD = ("hgv",)
CLES_GENERALES = ("access", "motor_vehicle")
VALEURS_RESTRICTIVES = frozenset(
    {"no", "destination", "private", "delivery", "agricultural", "forestry"}
)

# Une restriction ne couvre une interdiction routière que si elle porte sur une
# voie carrossable pour le véhicule concerné. Un access=private sur un escalier
# avait fait sous-estimer l'absence de 23 points (§18).
#
# LISTE IDENTIQUE À CELLE DE ecarts-dialog-osm.py, ET L'ÉGALITÉ EST VÉRIFIÉE
# À L'IMPORT, pas affirmée en commentaire. La première version de ce fichier
# portait « reprises telles quelles » au-dessus d'une liste qui contenait
# highway=service en plus — un commentaire affirmant une propriété que le code
# n'avait pas, exactement le défaut que ce projet passe son temps à corriger.
# L'écart valait 23 145 voies, soit 82 % du jeu retenu.
#
# highway=service exclu : ce sont très majoritairement des allées privées et
# des voies de desserte. Un access=private sur une allée n'exprime pas la
# restriction de tonnage de la rue voisine, il exprime que l'allée est privée.
# Faut-il en réintégrer une partie ? C'est une question ouverte, qui se tranche
# sur ses mérites et pas après lecture d'un résultat.
CLASSES_CARROSSABLES_PL = frozenset(
    {
        "motorway", "trunk", "primary", "secondary", "tertiary",
        "unclassified", "residential", "living_street",
        "motorway_link", "trunk_link", "primary_link", "secondary_link",
        "tertiary_link", "road", "busway",
    }
)

DECILES = 10


def _verifier_listes_partagees():
    """Les listes communes aux deux outils sont ÉGALES, et on le vérifie.

    Une divergence rendrait les deux mesures incomparables sans que rien ne le
    signale. Un commentaire qui l'affirme ne suffit pas : c'est précisément
    ainsi que 23 145 voies étaient entrées dans le jeu retenu.
    """
    import importlib.util

    voisin = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "ecarts-dialog-osm.py")
    if not os.path.exists(voisin):
        return
    spec = importlib.util.spec_from_file_location("_ecarts", voisin)
    autre = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(autre)
    for nom in ("CLASSES_CARROSSABLES_PL", "VALEURS_RESTRICTIVES",
                "CLES_NUMERIQUES", "CLES_POIDS_LOURD", "CLES_GENERALES"):
        ici, la = globals()[nom], getattr(autre, nom, None)
        exiger(
            la is None or set(ici) == set(la),
            f"Invariante rompue : {nom} diffère entre les deux outils.\n"
            f"  ici       : {sorted(set(ici) - set(la or ()))} en plus\n"
            f"  ecarts-…  : {sorted(set(la or ()) - set(ici))} en plus\n"
            "Deux listes divergentes produisent deux mesures incomparables.",
        )



def exiger(condition, message):
    if not condition:
        sys.exit(message)


def parametre(nom_env, position, explication, conversion=float):
    """Un paramètre absent fait échouer, il ne prend pas de valeur par défaut."""
    brut = (
        sys.argv[position]
        if len(sys.argv) > position
        else os.environ.get(nom_env)
    )
    exiger(brut, f"Paramètre {nom_env} non fourni.\n{explication}")
    return conversion(brut)


# ── géométrie ────────────────────────────────────────────────────────────────

def haversine(a, b):
    lat1, lon1 = math.radians(a[1]), math.radians(a[0])
    lat2, lon2 = math.radians(b[1]), math.radians(b[0])
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * RAYON_TERRE_M * math.asin(min(1.0, math.sqrt(h)))


def metres_par_degre(latitude):
    lat_m = math.pi * RAYON_TERRE_M / 180.0
    return lat_m, lat_m * math.cos(math.radians(latitude))


def longueur(ligne):
    return sum(haversine(p, q) for p, q in zip(ligne, ligne[1:]))


def polylignes(geometrie):
    """Toutes les polylignes d'une géométrie GeoJSON, quel que soit son type.

    Le Point est absent volontairement : il n'a pas de longueur, donc il n'entre
    pas dans une mesure en mètres. Il est compté à part.
    """
    forme = geometrie.get("type")
    coordonnees = geometrie.get("coordinates")
    if forme == "LineString":
        return [coordonnees]
    if forme in ("MultiLineString", "Polygon"):
        return list(coordonnees)
    if forme == "MultiPolygon":
        return [anneau for poly in coordonnees for anneau in poly]
    if forme == "GeometryCollection":
        return [
            ligne
            for sous in geometrie.get("geometries", [])
            for ligne in polylignes(sous)
        ]
    return []


def reechantillonner(ligne, pas):
    """Points à intervalle curviligne constant, avec le poids en mètres de chacun.

    C'EST L'ÉTAPE QUI NEUTRALISE LA DENSITÉ DE NUMÉRISATION. Après elle, le
    nombre de points d'un tronçon ne dépend plus que de sa longueur : une ligne
    droite de 2 km et 200 m de virages ne pèsent plus pareil parce que le
    fournisseur a posé deux sommets d'un côté et cinquante de l'autre.

    Retourne [(point, poids_m, cap)] où la somme des poids vaut la longueur
    exacte et où `cap` est l'azimut du segment PORTEUR de l'échantillon. Le cap
    est produit ici et non recherché ensuite : le point vient d'un segment
    connu, donc son orientation est exacte et gratuite. La chercher après coup
    serait à la fois approché et quadratique.
    """
    totale = longueur(ligne)
    if totale <= 0.0:
        return []
    nombre = max(2, int(totale / pas) + 1)
    intervalle = totale / nombre
    # Un point au MILIEU de chaque intervalle : il représente son intervalle
    # entier. Échantillonner aux extrémités compterait deux fois les jonctions
    # et donnerait à chaque tronçon un poids supérieur à sa longueur.
    cibles = [(i + 0.5) * intervalle for i in range(nombre)]

    echantillons = []
    parcourue = 0.0
    curseur = 0
    for debut, fin in zip(ligne, ligne[1:]):
        segment = haversine(debut, fin)
        while curseur < len(cibles) and parcourue <= cibles[curseur] <= parcourue + segment:
            t = 0.0 if segment == 0.0 else (cibles[curseur] - parcourue) / segment
            point = (
                debut[0] + t * (fin[0] - debut[0]),
                debut[1] + t * (fin[1] - debut[1]),
            )
            echantillons.append(
                (point, intervalle, cap_segment(debut, fin, metres_par_degre(point[1])))
            )
            curseur += 1
        parcourue += segment
    while len(echantillons) < nombre:  # bord d'arrondi flottant en fin de ligne
        dernier = tuple(ligne[-1][:2])
        echantillons.append(
            (
                dernier,
                intervalle,
                cap_segment(ligne[-2], ligne[-1], metres_par_degre(dernier[1])),
            )
        )
    return echantillons


def distance_point_segment(point, debut, fin, echelle):
    lat_m, lon_m = echelle
    px = (point[0] - debut[0]) * lon_m
    py = (point[1] - debut[1]) * lat_m
    sx = (fin[0] - debut[0]) * lon_m
    sy = (fin[1] - debut[1]) * lat_m
    carre = sx * sx + sy * sy
    if carre == 0.0:
        return math.hypot(px, py)
    t = max(0.0, min(1.0, (px * sx + py * sy) / carre))
    return math.hypot(px - t * sx, py - t * sy)


def cap_segment(debut, fin, echelle):
    lat_m, lon_m = echelle
    return math.degrees(
        math.atan2((fin[0] - debut[0]) * lon_m, (fin[1] - debut[1]) * lat_m)
    ) % 180.0


def ecart_de_cap(a, b):
    brut = abs(a - b) % 180.0
    return min(brut, 180.0 - brut)


def boite_de(points, marge=0.0):
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return (min(lons) - marge, min(lats) - marge, max(lons) + marge, max(lats) + marge)


def boites_disjointes(a, b):
    return a[0] > b[2] or b[0] > a[2] or a[1] > b[3] or b[1] > a[3]


# ── chargement ───────────────────────────────────────────────────────────────

def charger_dialog(chemin):
    """Arrêtés du CHAMP : poids, tonnage lisible, géométrie, noEntry.

    Aucun rejet n'est silencieux — règle 12 du §18.
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
            brut = caracteristique.findtext(TONNAGE)
            if brut is None:
                journal["rejet_tonnage_illisible"] += 1
                continue
            valeur = float(brut)
            if abs(valeur * 2 - round(valeur * 2)) > EPSILON_PAS_TONNAGE:
                journal["rejet_tonnage_hors_pas"] += 1
                continue
            tonnages.append(valeur)
        if not tonnages:
            continue
        journal["ordres_avec_tonnage"] += 1

        restrictions = {(a.text or "").strip() for a in element.iter(ACCESS_TYPE)}
        if "noEntry" not in restrictions:
            journal["hors_champ_stationnement_ou_vitesse"] += 1
            element.clear()
            continue

        lignes = []
        points_seuls = 0
        for geometrie in element.iter(GEOMETRY):
            try:
                objet = json.loads(geometrie.text)
            except (json.JSONDecodeError, TypeError):
                journal["rejet_geometrie_illisible"] += 1
                continue
            if objet.get("type") == "Point":
                points_seuls += 1
            for ligne in polylignes(objet):
                propres = [
                    (float(p[0]), float(p[1]))
                    for p in ligne
                    if isinstance(p, list) and len(p) >= 2
                ]
                if len(propres) >= 2:
                    lignes.append(propres)
        if points_seuls:
            journal["geometries_ponctuelles_sans_longueur"] += points_seuls
        if not lignes:
            journal["rejet_sans_longueur"] += 1
            element.clear()
            continue

        description = ""
        bloc = element.find(NS_TR + "description")
        if bloc is not None:
            valeur = bloc.find(".//" + NS_COM + "value")
            if valeur is not None:
                description = (valeur.text or "").strip()
        autorite = ""
        for source in element.iter(AUTHORITY):
            for valeur in source.iter(NS_COM + "value"):
                autorite = autorite or (valeur.text or "").strip()

        arretes.append(
            {
                "tonnage": min(tonnages),
                "lignes": lignes,
                "description": description,
                "autorite": autorite,
            }
        )
        element.clear()
    return arretes, operateurs, journal


def tonnage_osm(brut):
    texte = str(brut).strip().lower().replace(",", ".")
    if ";" in texte or "@" in texte:
        return None
    for suffixe, facteur in (("kg", 0.001), ("t", 1.0), ("", 1.0)):
        if suffixe and texte.endswith(suffixe):
            try:
                return float(texte[: -len(suffixe)].strip()) * facteur
            except ValueError:
                return None
    try:
        return float(texte)
    except ValueError:
        return None


def charger_osm(chemin, service_si_tonnage):
    """Voies OSM CARROSSABLES portant une restriction poids lourds."""
    donnees = json.load(open(chemin, encoding="utf-8"))
    voies = []
    journal = Counter()
    for element in donnees.get("elements", []):
        if element.get("type") != "way":
            continue
        etiquettes = element.get("tags", {})
        points = [(n["lon"], n["lat"]) for n in element.get("geometry") or []]
        if len(points) < 2:
            journal["rejet_voie_sans_geometrie"] += 1
            continue
        # CLASSE CARROSSABLE, avec une exception paramétrée.
        #
        # highway=service est exclu de la liste parce que 22 316 allées privées
        # y portent un access=private qui n'exprime aucune restriction de
        # tonnage. Mais 212 voies de cette classe portent un VRAI maxweight —
        # une allée nommée à 3,5 t est presque sûrement une vraie rue mal
        # classée dans OSM, et la jeter est de la couverture perdue.
        #
        # Recherche menée exprès dans la polarité inverse des trois corrections
        # précédentes, qui retiraient toutes de la couverture fausse et
        # faisaient donc monter le taux. Celle-ci le fait baisser.
        classe = etiquettes.get("highway")
        exception = (
            service_si_tonnage
            and classe == "service"
            and (
                any(
                    tonnage_osm(etiquettes.get(cle, "")) is not None
                    for cle in CLES_NUMERIQUES
                )
                or etiquettes.get("hgv") in VALEURS_RESTRICTIVES
            )
        )
        if classe not in CLASSES_CARROSSABLES_PL and not exception:
            journal["rejet_voie_non_carrossable_pl"] += 1
            continue
        if exception:
            journal["service_repeche_sur_tonnage"] += 1

        # Nature de la preuve, et non simple booléen. Une limite de tonnage
        # dit « les plus de 3,5 t ne passent pas » ; un access=private dit
        # « cette voie est privée » — ce n'est pas la même affirmation, et
        # confondre les deux avait déjà coûté 23 points (§18).
        tonnage = any(
            tonnage_osm(etiquettes.get(cle, "")) is not None
            for cle in CLES_NUMERIQUES
        ) or etiquettes.get("hgv") in VALEURS_RESTRICTIVES
        generale = any(
            etiquettes.get(cle) in VALEURS_RESTRICTIVES for cle in CLES_GENERALES
        )
        if not (tonnage or generale):
            journal["rejet_voie_sans_restriction"] += 1
            continue
        journal["voie_preuve_tonnage" if tonnage else "voie_preuve_generale_seule"] += 1

        voies.append(
            {
                "id": element["id"],
                "points": points,
                "preuve": "tonnage" if tonnage else "generale",
            }
        )
    return voies, journal, donnees.get("osm3s", {}).get("timestamp_osm_base", "")


# ── mesure ───────────────────────────────────────────────────────────────────

def couverture_du_perimetre(arretes, voies, tolerance):
    """Quelle part du périmètre DÉCLARÉ l'extrait OSM couvre-t-il réellement ?

    Sans ce contrôle, l'outil reproduit le défaut qu'il corrige, retourné.
    L'ancien filtrait les arrêtés hors emprise et rétrécissait le dénominateur
    en silence ; celui-ci les garde et, faute de voie OSM en face, les compte
    comme absents — il GONFLE LE NUMÉRATEUR en silence. Le premier sous-estimait
    l'absence, le second la surestime. Les deux se taisent.

    Déclarer le périmètre n'a de sens que si le défaut de couverture est mesuré
    et publié (§3.2, étape 1).
    """
    boite = boite_de(
        [p for v in voies for p in v["points"]],
        marge=tolerance / METRES_PAR_DEGRE_LATITUDE,
    )
    dedans = 0.0
    dehors = 0.0
    hors_couverture = []
    for arrete in arretes:
        metres = sum(longueur(ligne) for ligne in arrete["lignes"])
        touche = any(
            boite[0] <= p[0] <= boite[2] and boite[1] <= p[1] <= boite[3]
            for ligne in arrete["lignes"]
            for p in ligne
        )
        if touche:
            dedans += metres
        else:
            dehors += metres
            hors_couverture.append(
                {
                    "autorite": arrete["autorite"],
                    "description": arrete["description"],
                    "metres": metres,
                    "premier_point": {
                        "lon": arrete["lignes"][0][0][0],
                        "lat": arrete["lignes"][0][0][1],
                    },
                }
            )
    total = dedans + dehors
    return {
        "emprise_osm": {
            "lon_min": boite[0], "lat_min": boite[1],
            "lon_max": boite[2], "lat_max": boite[3],
        },
        "metres_perimetre_declare": total,
        "metres_couverts_par_extrait": dedans,
        "metres_hors_extrait": dehors,
        "part_couverte": dedans / total if total else 0.0,
        "arretes_hors_extrait": sorted(hors_couverture, key=lambda x: -x["metres"]),
    }


def cellule(point, pas_degres):
    return (round(point[0] / pas_degres), round(point[1] / pas_degres))


def couvert(point, voies_proches, tolerance, ang_max, cap_local):
    """Nature de la meilleure preuve à portée : "tonnage", "generale", ou None.

    Retourne la preuve la PLUS FORTE trouvée, pas la première : une voie
    tonnée et une voie simplement privée peuvent toutes deux être à portée, et
    c'est la tonnée qui décide.
    """
    echelle = metres_par_degre(point[1])
    meilleure = None
    for voie in voies_proches:
        if meilleure == "tonnage":
            break
        for debut, fin in zip(voie["points"], voie["points"][1:]):
            if distance_point_segment(point, debut, fin, echelle) > tolerance:
                continue
            if cap_local is not None and (
                ecart_de_cap(cap_segment(debut, fin, echelle), cap_local) > ang_max
            ):
                continue
            if voie["preuve"] == "tonnage":
                meilleure = "tonnage"
                break
            meilleure = meilleure or "generale"
    return meilleure


def mesurer(arretes, voies, par):
    """Retourne la mesure métrique, la mesure par arrêté, et les déciles.

    Les deux mesures sortent du MÊME parcours : les publier séparément
    laisserait deux chemins de calcul diverger sans que rien ne le signale.
    """
    marge = par["tolerance"] / METRES_PAR_DEGRE_LATITUDE
    for voie in voies:
        voie["boite"] = boite_de(voie["points"], marge)
    pas_degres = par["pas_dedup"] / METRES_PAR_DEGRE_LATITUDE

    # La déduplication est globale : une cellule vue par un second arrêté ne
    # rentre pas deux fois au dénominateur. Sans elle, 11,9 % de voirie fantôme.
    cellules_vues = {}
    par_arrete = []

    for arrete in arretes:
        tous = [p for ligne in arrete["lignes"] for p in ligne]
        boite_arrete = boite_de(tous, marge)
        candidates = [
            v for v in voies if not boites_disjointes(boite_arrete, v["boite"])
        ]

        metres_arrete = 0.0
        metres_absents = 0.0
        for ligne in arrete["lignes"]:
            for point, poids, cap_local in reechantillonner(ligne, par["pas_test"]):
                preuve = couvert(
                    point, candidates, par["tolerance"], par["ang_max"], cap_local
                )
                est_couvert = preuve is not None
                metres_arrete += poids
                if not est_couvert:
                    metres_absents += poids

                cle = cellule(point, pas_degres)
                if cle not in cellules_vues:
                    cellules_vues[cle] = (poids, est_couvert, preuve)
                elif est_couvert and not cellules_vues[cle][1]:
                    # Une cellule couverte par un arrêté l'est pour tous : le
                    # tag OSM existe ou n'existe pas, il ne dépend pas de qui
                    # regarde. En cas de désaccord, la couverture l'emporte —
                    # erreur en sens prudent, elle abaisse le taux d'absence.
                    cellules_vues[cle] = (cellules_vues[cle][0], True, preuve)
                elif preuve == "tonnage" and cellules_vues[cle][2] == "generale":
                    # Une preuve forte remplace une preuve faible sur la même
                    # cellule : la question est « qu'est-ce qui existe ici »,
                    # pas « qui l'a vu en premier ».
                    cellules_vues[cle] = (cellules_vues[cle][0], True, "tonnage")

        par_arrete.append(
            {
                "metres": metres_arrete,
                "metres_absents": metres_absents,
                "absent": metres_absents >= metres_arrete,
                "autorite": arrete["autorite"],
                "description": arrete["description"],
                "tonnage": arrete["tonnage"],
            }
        )

    metres_total = sum(poids for poids, _, _ in cellules_vues.values())
    metres_absents = sum(
        poids for poids, couverte, _ in cellules_vues.values() if not couverte
    )
    # SENSIBILITÉ DÉCLARÉE, pas un changement de définition. La définition
    # pré-inscrite retient les deux natures de preuve ; ce second chiffre dit
    # ce qu'elle vaudrait si seule la preuve de tonnage comptait.
    metres_preuve_generale = sum(
        poids for poids, _, preuve in cellules_vues.values() if preuve == "generale"
    )

    # Déciles de LONGUEUR D'ARRÊTÉ : ils montrent la distribution au lieu de la
    # déduire du signe de la divergence (§3.4). Si les déciles contredisent la
    # lecture tirée du signe, c'est la lecture qui tombe.
    tries = sorted(par_arrete, key=lambda a: a["metres"])
    taille = len(tries) / DECILES
    deciles = []
    for i in range(DECILES):
        tranche = tries[int(i * taille) : int((i + 1) * taille)]
        if not tranche:
            continue
        m = sum(a["metres"] for a in tranche)
        deciles.append(
            {
                "decile": i + 1,
                "arretes": len(tranche),
                "longueur_min_m": tranche[0]["metres"],
                "longueur_max_m": tranche[-1]["metres"],
                "metres": m,
                "taux_absence_metrique": (
                    sum(a["metres_absents"] for a in tranche) / m if m else 0.0
                ),
                "taux_absence_par_arrete": (
                    sum(1 for a in tranche if a["absent"]) / len(tranche)
                ),
            }
        )

    return {
        "metrique": {
            "metres_absents": metres_absents,
            "metres_total": metres_total,
            "taux": metres_absents / metres_total if metres_total else 0.0,
            "cellules": len(cellules_vues),
        },
        "sensibilite_nature_de_preuve": {
            "note": "la définition pré-inscrite compte les deux natures ; ce "
            "chiffre dit ce qu'elle vaudrait si access et motor_vehicle ne "
            "valaient pas couverture",
            "metres_couverts_preuve_generale_seule": metres_preuve_generale,
            "part_des_metres_couverts": (
                metres_preuve_generale / (metres_total - metres_absents)
                if metres_total > metres_absents
                else 0.0
            ),
            "taux_si_seule_la_preuve_de_tonnage_compte": (
                (metres_absents + metres_preuve_generale) / metres_total
                if metres_total
                else 0.0
            ),
        },
        "par_arrete": {
            "absents": sum(1 for a in par_arrete if a["absent"]),
            "total": len(par_arrete),
            "taux": (
                sum(1 for a in par_arrete if a["absent"]) / len(par_arrete)
                if par_arrete
                else 0.0
            ),
        },
        "deciles": deciles,
        "detail": par_arrete,
    }


def lire_divergence(mesure, seuil_points):
    """Coche l'une des trois lectures pré-inscrites au §3.4. N'en invente aucune."""
    ecart = 100 * (mesure["metrique"]["taux"] - mesure["par_arrete"]["taux"])
    if abs(ecart) < seuil_points:
        cle, sens = "independante", (
            "L'absence est indépendante de la longueur. Aucune histoire de "
            "distribution ne se raconte."
        )
    elif ecart < 0:
        cle, sens = "courtes", (
            "Les absences se concentrent sur les emprises COURTES : beaucoup de "
            "petites rues. Le nombre d'actes non repris surestime la longueur "
            "non reprise."
        )
    else:
        cle, sens = "longues", (
            "Les absences se concentrent sur les emprises LONGUES : peu "
            "d'arrêtés, de grands linéaires. Le compte par acte sous-estime "
            "l'ampleur."
        )

    # Contrôle par les déciles, qui montrent la distribution directement.
    deciles = mesure["deciles"]
    moitie = len(deciles) // 2
    courts = [d["taux_absence_metrique"] for d in deciles[:moitie]]
    longs = [d["taux_absence_metrique"] for d in deciles[moitie:]]
    penche_court = sum(courts) / len(courts) > sum(longs) / len(longs)
    attendu = {"courtes": True, "longues": False}.get(cle)
    return {
        "ecart_points": ecart,
        "seuil_points": seuil_points,
        "lecture": cle,
        "signification": sens,
        "deciles_penchent_vers_les_courtes": penche_court,
        "deciles_confirment": None if attendu is None else (penche_court == attendu),
        "si_contredit": (
            "Les déciles contredisent la lecture tirée du signe : l'écart vient "
            "d'un petit nombre d'arrêtés extrêmes plutôt que d'une tendance. "
            "C'est la lecture qui tombe, pas les déciles (§3.4)."
        ),
    }


# ── rapport ──────────────────────────────────────────────────────────────────

def empreinte_fichier(chemin):
    haché = hashlib.sha256()
    with open(chemin, "rb") as entree:
        for bloc in iter(lambda: entree.read(1 << 20), b""):
            haché.update(bloc)
    return {
        "chemin": os.path.abspath(chemin),
        "octets": os.path.getsize(chemin),
        "sha256": haché.hexdigest(),
    }


def ecrire_rapport(chemin, rapport):
    """Temporaire puis renommage : une écriture en place laisse un JSON tronqué."""
    temporaire = chemin + ".tmp"
    with open(temporaire, "w", encoding="utf-8") as sortie:
        json.dump(rapport, sortie, ensure_ascii=False, indent=1, sort_keys=True)
        sortie.flush()
        os.fsync(sortie.fileno())
    os.replace(temporaire, chemin)


def restituer(r, chemin):
    """Projection lisible du rapport. NE CALCULE RIEN."""
    print(f"rapport machine (valeurs exactes)   : {chemin}")
    print("  l'affichage ci-dessous en est une projection arrondie\n")

    for cle in sorted(r["journal_rejets"]):
        print(f"   {cle:38s} : {r['journal_rejets'][cle]}")
    print()
    p = r["populations"]
    print(f"instantané OSM                      : {r['instantane_osm']}")
    print(f"population DANS LE CHAMP            : {p['dans_le_champ']}  arrêtés")
    print(f"  sans longueur exploitable         : {p['sans_longueur']}")
    print(f"voies OSM carrossables restrictives : {r['osm']['voies_retenues']}")
    c = r["couverture_du_perimetre"]
    print(f"périmètre déclaré                   : "
          f"{c['metres_perimetre_declare']/1000:9.1f} km")
    print(f"  couvert par l'extrait OSM         : {c['part_couverte']:9.1%}"
          f"   ({c['metres_hors_extrait']/1000:.1f} km hors extrait)")
    for x in c["arretes_hors_extrait"][:5]:
        print(f"     {x['autorite'][:22]:22s} {x['metres']:7.0f} m"
              f"   {x['description'][:44]}")

    m, a = r["mesure_metrique"], r["mesure_par_arrete"]
    print(f"\n{'':4s}MESURE PRINCIPALE — le mètre de voirie réglementée")
    print(f"    réseau réglementé, dédupliqué   : {m['metres_total']/1000:9.1f} km")
    print(f"    sans restriction dans OSM       : {m['metres_absents']/1000:9.1f} km")
    print(f"    TAUX D'ABSENCE                  : {m['taux']:9.1%}")
    sp = r["sensibilite_nature_de_preuve"]
    print(f"    dont couvert par access/motor_vehicle SEUL : "
          f"{sp['metres_couverts_preuve_generale_seule']/1000:.1f} km"
          f"  ({sp['part_des_metres_couverts']:.1%} du couvert)")
    print(f"    taux si seule la preuve de tonnage compte  : "
          f"{sp['taux_si_seule_la_preuve_de_tonnage_compte']:.1%}")

    print(f"\n{'':4s}MESURE SECONDAIRE — l'arrêté")
    print(f"    arrêtés mesurés                 : {a['total']:9d}")
    print(f"    entièrement absents d'OSM       : {a['absents']:9d}")
    print(f"    TAUX D'ABSENCE                  : {a['taux']:9.1%}")

    d = r["divergence"]
    print(f"\n{'':4s}DIVERGENCE  {d['ecart_points']:+.1f} point(s)"
          f"   (seuil pré-inscrit {d['seuil_points']:.1f})")
    print(f"    lecture cochée : {d['signification']}")
    if d["deciles_confirment"] is False:
        print(f"    ⚠ {d['si_contredit']}")
    elif d["deciles_confirment"] is True:
        print("    déciles : cohérents avec cette lecture")

    print(f"\n{'':4s}taux d'absence par décile de longueur d'arrêté")
    print(f"{'':6s}{'décile':>7s} {'arrêtés':>8s} {'longueur':>18s} "
          f"{'km':>8s} {'absence m':>10s} {'absence n':>10s}")
    for x in r["deciles"]:
        print(
            f"{'':6s}{x['decile']:7d} {x['arretes']:8d} "
            f"{x['longueur_min_m']:7.0f}–{x['longueur_max_m']:<10.0f} "
            f"{x['metres']/1000:8.1f} {x['taux_absence_metrique']:10.1%} "
            f"{x['taux_absence_par_arrete']:10.1%}"
        )


def main():
    # Vérifié à chaque exécution, jamais supposé.
    _verifier_listes_partagees()
    exiger(
        len(sys.argv) >= 4,
        "Usage : python3 outils/mesure-metrique.py <dialog.xml> <osm.json> "
        "<rapport.json> <pas_test> <pas_dedup> <tolerance> <ang_max> "
        "<ecart_negligeable> <couverture_min>",
    )
    par = {
        "pas_test": parametre(
            "MESURE_PAS_TEST_M", 4,
            "Pas de rééchantillonnage, en mètres. C'est lui qui neutralise la\n"
            "densité de numérisation. Il ne change pas le dénominateur (§3.1).",
        ),
        "pas_dedup": parametre(
            "MESURE_PAS_DEDUP_M", 5,
            "Pas de la grille de déduplication, en mètres. Sans déduplication,\n"
            "11,9 % du dénominateur est de la voirie comptée deux fois (§2).",
        ),
        "tolerance": parametre(
            "MESURE_TOL_APPARIEMENT_M", 6,
            "Distance maximale entre un point du corridor et une voie OSM.\n"
            "Se calibre sur des cas connus (§19), ne se devine pas.",
        ),
        "ang_max": parametre(
            "MESURE_ANG_MAX_DEG", 7,
            "Écart de cap maximal. Sépare une voie du pont qu'elle franchit.\n"
            "Attention : le resserrement de 45° à 30° avait fait disparaître\n"
            "trois faux positifs ET huit candidates (§18).",
        ),
        "service_si_tonnage": parametre(
            "MESURE_SERVICE_SI_TONNAGE", 10,
            "1 pour repêcher les highway=service portant un VRAI tonnage, 0 sinon.\n"
            "La définition pré-inscrite vaut 0 — la liste des classes vient de\n"
            "l'outil existant. Le 1 est une sensibilité déclarée, cherchée dans\n"
            "la polarité inverse des corrections qui montaient le taux.",
            lambda x: bool(int(x)),
        ),
        "couverture_min": parametre(
            "MESURE_COUVERTURE_MIN", 9,
            "Part minimale du périmètre déclaré que l'extrait OSM doit couvrir,\n"
            "entre 0 et 1. En deçà, l'outil refuse de produire un taux : il\n"
            "gonflerait le numérateur avec de la voirie qu'aucune donnée OSM ne\n"
            "peut couvrir. Mesurer sur un territoire partiel est légitime — il\n"
            "faut alors DÉCLARER ce territoire, pas laisser l'extrait le choisir.",
        ),
        "ecart_negligeable": parametre(
            "MESURE_ECART_NEGLIGEABLE_PT", 8,
            "Seuil de divergence mètre/arrêté, en points. En deçà, aucune\n"
            "affirmation sur la distribution n'est autorisée (§3.4).",
        ),
    }
    chemin_rapport = sys.argv[3]

    arretes, operateurs, journal = charger_dialog(sys.argv[1])
    inattendus = {op: n for op, n in operateurs.items() if op != OPERATEUR_ATTENDU}
    exiger(
        not inattendus,
        f"Invariante rompue : comparisonOperator attendu « {OPERATEUR_ATTENDU} », "
        f"trouvé aussi {inattendus}.",
    )
    voies, journal_osm, instantane = charger_osm(sys.argv[2], par["service_si_tonnage"])
    journal.update(journal_osm)
    exiger(arretes, "Aucun arrêté du champ dans ce flux.")
    exiger(voies, "Aucune voie OSM carrossable porteuse de restriction.")

    couverture = couverture_du_perimetre(arretes, voies, par["tolerance"])
    exiger(
        couverture["part_couverte"] >= par["couverture_min"],
        "L'extrait OSM ne couvre que "
        f"{couverture['part_couverte']:.1%} du périmètre déclaré "
        f"({couverture['metres_hors_extrait']/1000:.0f} km hors extrait), "
        f"seuil exigé {par['couverture_min']:.0%}.\n"
        "Poursuivre compterait comme « absente » de la voirie qu'aucune donnée\n"
        "OSM ne peut couvrir : le taux serait faux vers le haut, et rien dans le\n"
        "rapport ne le signalerait.\n"
        "Élargir l'extrait, ou restreindre le flux au territoire réellement\n"
        "couvert — mais alors DÉCLARER ce territoire.",
    )

    mesure = mesurer(arretes, voies, par)
    divergence = lire_divergence(mesure, par["ecart_negligeable"])

    rapport = {
        "outil": os.path.basename(__file__),
        "definition": "docs/unite-preinscrite.md §3.2, pré-inscrite le 2026-08-03",
        "instantane_osm": instantane,
        "entrees": {
            "dialog": empreinte_fichier(sys.argv[1]),
            "osm": empreinte_fichier(sys.argv[2]),
        },
        "parametres": par,
        "journal_rejets": dict(journal),
        "populations": {
            "dans_le_champ": len(arretes),
            "sans_longueur": journal.get("rejet_sans_longueur", 0),
            "definition":
                "arrêtés portant une caractéristique de poids, un tonnage "
                "multiple de 0,5, accessRestrictionType = noEntry, et au moins "
                "une polyligne de longueur non nulle. Le périmètre est DÉCLARÉ : "
                "il n'est jamais restreint à l'emprise de l'extrait OSM.",
        },
        "osm": {"voies_retenues": len(voies)},
        "couverture_du_perimetre": couverture,
        "mesure_metrique": mesure["metrique"],
        "sensibilite_nature_de_preuve": mesure["sensibilite_nature_de_preuve"],
        "mesure_par_arrete": mesure["par_arrete"],
        "deciles": mesure["deciles"],
        "divergence": divergence,
        # Le détail par arrêté fait partie de l'enregistrement, pas des
        # variables locales : sans lui, toute vérification portant sur un
        # arrêté nommé — un témoin de l'épreuve aveugle, par exemple —
        # obligerait à relancer la mesure entière pour poser une question.
        "par_arrete_detail": sorted(
            mesure["detail"], key=lambda a: -a["metres"]
        ),
        "ce_que_le_chiffre_ne_dit_pas": [
            "Rien sur une proportion d'arrêtés : « X % des arrêtés » ne se dérive "
            "jamais du taux métrique (§3.2).",
            "Rien sur l'exactitude des restrictions présentes : une voie limitée "
            "à 3,5 t par arrêté et étiquetée maxweight=19 compte comme couverte.",
            "Rien sur ce qui n'est pas dans DiaLog : le dénominateur est la "
            "réglementation publiée, pas la réglementation existante.",
            "Rien sur la pertinence des arrêtés. Aucune mesure de ce projet n'en "
            "porte, et aucune phrase ne peut s'en réclamer (§3.4).",
        ],
    }
    ecrire_rapport(chemin_rapport, rapport)
    restituer(rapport, chemin_rapport)


if __name__ == "__main__":
    main()
