#!/usr/bin/env python3
"""Balaye TOUS les attributs du flux DiaLog par PORTEE, en une passe.

    « Un attribut lu a la portee de l'arrete alors qu'il appartient a la
      regulation. »

Deux defauts de cette forme ont ete trouves un par un — WEIGHT et GEOMETRY dans
charger_dialog(). Les retrouver un par un coute plus cher que de balayer une
fois : ce fichier est ce balayage.

Le test est empirique, pas structurel. Un attribut lu trop haut n'est un defaut
que s'il PEUT differer entre les regulations d'un meme arrete. On compte donc,
pour chaque attribut :

    arretes multi        arretes portant >= 2 regulations ou l'attribut apparait
    arretes divergents   ceux ou les regulations n'ont PAS le meme ensemble de
                         valeurs — une lecture a la portee de l'arrete y melange
                         ce qui appartient a des regulations differentes

`arretes divergents` est le nombre qui compte. A zero, une lecture haute est
inoffensive sur ce flux — et cela reste vrai jusqu'au prochain flux, ce que dit
la sortie.

Un second volet couvre la portee INTERNE a la regulation : la feuille. `negate`
distingue le vehicule VISE de la DEROGATION ; tout critere lu au niveau du
groupe au lieu de la feuille les confond. On compte les groupes qui melangent.

Usage :
    python3 outils/balayer-portees.py <dialog.xml> <rapport.json>
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

NS_TR = "{http://datex2.eu/schema/3/trafficRegulation}"
ORDER = NS_TR + "trafficRegulationOrder"
REGULATION = NS_TR + "trafficRegulation"


def exiger(condition, message):
    if not condition:
        sys.exit(message)


def nom(element):
    return element.tag.split("}")[-1]


# Attributs porteurs de sens, tous niveaux confondus. La liste est celle des
# balises a VALEUR du flux ; les balises de structure (conditions, values,
# validityTimeSpecification) n'y sont pas : elles ne portent rien a attribuer.
ATTRIBUTS = (
    "accessRestrictionType", "standingOrParkingRestrictionType",
    "roadOrCarriagewayOrLaneManagementType", "generalInstructionToRoadUsersType",
    "status", "negate",
    "vehicleType", "vehicleUsage", "otherVehicleType", "loadType",
    "nonVehicularRoadUser", "driverCharacteristicsType", "accessConditionType",
    "vehicleEquipment", "fuelType",
    "grossVehicleWeight", "vehicleHeight", "vehicleLength", "vehicleWidth",
    "comparisonOperator", "typeOfWeight",
    "roadName", "roadNumber", "locationDescription", "geoJsonGeometry",
    "overallStartTime", "overallEndTime",
    "startTimeOfPeriod", "endTimeOfPeriod", "applicableDay",
    "numericValue", "unitOfMeasure", "maxValue",
    "validityStatus", "operator",
)

# Attributs qui vivent LEGITIMEMENT au niveau de l'arrete : les lire la-haut
# n'est pas un defaut, c'est leur place.
DE_L_ARRETE = frozenset((
    "regulationId", "description", "issuingAuthority", "publicUrl", "source",
))


def empreinte(element, attribut):
    """Ensemble des valeurs de `attribut` sous `element`.

    Les geometries sont resumees par leur longueur de texte : comparer des
    MultiLineString entiers coute cher et ne dit rien de plus que « ce ne sont
    pas les memes ».
    """
    valeurs = set()
    for enfant in element.iter():
        if nom(enfant) != attribut:
            continue
        texte = (enfant.text or "").strip()
        if not texte:
            continue
        valeurs.add(f"<{len(texte)}>" if attribut == "geoJsonGeometry" else texte)
    return frozenset(valeurs)


def main():
    exiger(
        len(sys.argv) >= 3,
        "Usage : python3 outils/balayer-portees.py <dialog.xml> <rapport.json>",
    )
    flux, sortie = sys.argv[1], sys.argv[2]
    exiger(os.path.exists(flux), f"Flux introuvable : {flux}")

    # volet 1 — portee ARRETE contre portee REGULATION
    presents = Counter()          # arretes ou l'attribut apparait
    multi = Counter()             # ... et qui portent >= 2 regulations
    divergents = Counter()        # ... ou les regulations different
    exemple = {}

    # volet 2 — portee REGULATION contre portee FEUILLE
    groupes_mixtes = Counter()    # groupes melant negate=false et negate=true
    groupes_vus = Counter()
    attribut_des_deux_cotes = Counter()

    ordres = 0
    for _, ordre in ET.iterparse(flux, events=("end",)):
        if ordre.tag != ORDER:
            continue
        ordres += 1
        regulations = ordre.findall(REGULATION)

        for attribut in ATTRIBUTS:
            empreintes = [empreinte(r, attribut) for r in regulations]
            non_vides = [e for e in empreintes if e]
            if not non_vides:
                continue
            presents[attribut] += 1
            if len(non_vides) < 2:
                continue
            multi[attribut] += 1
            if len({e for e in non_vides}) > 1:
                divergents[attribut] += 1
                if attribut not in exemple:
                    exemple[attribut] = {
                        "regulation_id": (ordre.findtext(NS_TR + "regulationId") or "").strip(),
                        "valeurs_par_regulation": [sorted(e)[:4] for e in non_vides][:4],
                    }

        # volet 2 : a l'interieur d'une regulation, la feuille
        for regulation in regulations:
            for groupe in regulation.iter():
                if nom(groupe) != "conditions":
                    continue
                feuilles = [f for f in groupe if nom(f) == "conditions"]
                marques = {
                    (f.findtext(NS_TR + "negate") or "").strip()
                    for f in feuilles
                    if f.find(NS_TR + "negate") is not None
                }
                if not marques:
                    continue
                groupes_vus["groupes_a_negate"] += 1
                if len(marques) > 1:
                    groupes_mixtes["groupes_melangeant_vise_et_derogation"] += 1
                    for attribut in ATTRIBUTS:
                        cotes = defaultdict(set)
                        for feuille in feuilles:
                            marque = (feuille.findtext(NS_TR + "negate") or "").strip()
                            if not marque:
                                continue
                            valeurs = empreinte(feuille, attribut)
                            if valeurs:
                                cotes[marque] |= valeurs
                        if len(cotes) > 1:
                            attribut_des_deux_cotes[attribut] += 1
        ordre.clear()

    rapport = {
        "pourquoi": "Balayage de portee. Un attribut lu a la portee de l'arrete "
                    "n'est un defaut que s'il PEUT differer entre les regulations "
                    "de cet arrete. `arretes_divergents` est ce nombre.",
        "flux": os.path.basename(flux),
        "ordres_lus": ordres,
        "portee_arrete_contre_regulation": {
            attribut: {
                "arretes_ou_present": presents[attribut],
                "arretes_multi_regulations": multi[attribut],
                "arretes_divergents": divergents[attribut],
                "exemple": exemple.get(attribut),
            }
            for attribut in ATTRIBUTS
            if presents[attribut]
        },
        "portee_groupe_contre_feuille": {
            "groupes_a_negate": groupes_vus["groupes_a_negate"],
            "groupes_melangeant_vise_et_derogation":
                groupes_mixtes["groupes_melangeant_vise_et_derogation"],
            "attributs_presents_des_deux_cotes": dict(
                attribut_des_deux_cotes.most_common()
            ),
        },
        "attributs_de_l_arrete_par_nature": sorted(DE_L_ARRETE),
    }
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=1)

    print(f"ordres lus : {ordres}\n")
    print("VOLET 1 — portee ARRETE contre portee REGULATION")
    print(f"  {'divergents':>10} {'multi':>7} {'present':>8}  attribut")
    lignes = sorted(
        ((divergents[a], multi[a], presents[a], a) for a in ATTRIBUTS if presents[a]),
        reverse=True,
    )
    for d, m, p, a in lignes:
        marque = "  <-- DEFAUT SI LU PLUS HAUT" if d else ""
        print(f"  {d:>10} {m:>7} {p:>8}  {a}{marque}")
    print()
    print("VOLET 2 — portee GROUPE contre portee FEUILLE")
    print(f"  groupes portant un negate            : {groupes_vus['groupes_a_negate']}")
    print("  groupes melangeant vise et derogation : "
          f"{groupes_mixtes['groupes_melangeant_vise_et_derogation']}")
    if attribut_des_deux_cotes:
        print("  attributs presents DES DEUX COTES dans un meme groupe :")
        for attribut, nombre in attribut_des_deux_cotes.most_common():
            print(f"      {nombre:>6}  {attribut}   <-- lu au groupe, "
                  "il confondrait vise et derogation")
    print(f"\nrapport : {sortie}")


if __name__ == "__main__":
    main()
