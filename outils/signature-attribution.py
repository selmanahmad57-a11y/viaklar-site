#!/usr/bin/env python3
"""Signature géométrique des OUI : détecte la dérive d'attribution.

Un faux OUI par attribution — la restriction appartient à la voie d'à côté —
laisse une trace mesurable : **la distance entre le point tiré et la voie taguée
qui a produit le OUI**, et la **classe** de cette voie.

    un VRAI OUI  : la restriction est sur la voie même, distance quasi nulle
    un FAUX OUI  : elle est sur une parallèle, une contre-allée, une desserte —
                   quelques mètres à quelques dizaines

C'est le seul détecteur qui voie une erreur COMMUNE au vérificateur et au
pipeline. La comparaison entre vérificateurs ne peut pas la voir : si tous se
trompent de la même façon, ils s'accordent. Ici on ne compare pas des avis, on
regarde la géométrie de ce qui a produit l'avis.

Limite à écrire avec le résultat : l'extrait OSM ne contient QUE des voies
porteuses de restriction — la requête Overpass les a filtrées à la source. On ne
peut donc pas identifier la voie du corridor lorsqu'elle n'est pas taguée, ni
prouver que la voie porteuse n'est pas la bonne. **La distance est un indice,
pas une preuve.** Un extrait complet du réseau la transformerait en preuve.

Usage :
    python3 outils/signature-attribution.py <corrige.json> <osm.json> \\
            <sortie.json> <tolerance_m> <ang_max_deg>
"""

import importlib.util
import json
import os
import sys

VOISIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesure-metrique.py")
_spec = importlib.util.spec_from_file_location("_mesure", VOISIN)
mesure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mesure)


def porteuse_la_plus_proche(point, cap, voies, tolerance, ang_max, exiger_cap):
    """Voie porteuse la plus proche, avec ou sans le filtre de cap.

    Les deux passes servent : sans le filtre, on voit ce qui aurait été attribué
    si le cap n'avait pas trié — donc l'ampleur du travail que fait ce filtre.
    """
    echelle = mesure.metres_par_degre(point[1])
    meilleur = None
    for voie in voies:
        for debut, fin in zip(voie["points"], voie["points"][1:]):
            distance = mesure.distance_point_segment(point, debut, fin, echelle)
            if distance > tolerance:
                continue
            ecart = mesure.ecart_de_cap(
                mesure.cap_segment(debut, fin, echelle), cap
            )
            if exiger_cap and ecart > ang_max:
                continue
            if meilleur is None or distance < meilleur["distance_m"]:
                meilleur = {
                    "distance_m": distance,
                    "ecart_cap_deg": ecart,
                    "way_id": voie["id"],
                    "classe": voie.get("classe", ""),
                    "nom": voie.get("nom", ""),
                    "etiquettes": voie.get("etiquettes", {}),
                }
    return meilleur


def main():
    mesure.exiger(
        len(sys.argv) >= 6,
        "Usage : python3 outils/signature-attribution.py <corrige.json> "
        "<osm.json> <sortie.json> <tolerance_m> <ang_max_deg>",
    )
    corrige = json.load(open(sys.argv[1], encoding="utf-8"))
    tolerance = mesure.parametre(
        "SIGNATURE_TOLERANCE_M", 4,
        "Tolérance d'appariement, identique à celle de la mesure.",
    )
    ang_max = mesure.parametre(
        "SIGNATURE_ANG_MAX_DEG", 5,
        "Écart de cap maximal, identique à celui de la mesure.",
    )

    # On recharge l'OSM en gardant les étiquettes et la classe : la mesure les
    # jette, et ce sont elles qu'on veut regarder ici.
    donnees = json.load(open(sys.argv[2], encoding="utf-8"))
    voies = []
    for element in donnees.get("elements", []):
        if element.get("type") != "way":
            continue
        etiquettes = element.get("tags", {})
        points = [(n["lon"], n["lat"]) for n in element.get("geometry") or []]
        if len(points) < 2:
            continue
        if etiquettes.get("highway") not in mesure.CLASSES_CARROSSABLES_PL:
            continue
        porte = any(
            mesure.tonnage_osm(etiquettes.get(c, "")) is not None
            for c in mesure.CLES_NUMERIQUES
        ) or any(
            etiquettes.get(c) in mesure.VALEURS_RESTRICTIVES
            for c in mesure.CLES_POIDS_LOURD + mesure.CLES_GENERALES
        )
        if not porte:
            continue
        voies.append(
            {
                "id": element["id"],
                "points": points,
                "classe": etiquettes.get("highway", ""),
                "nom": etiquettes.get("name") or etiquettes.get("ref") or "",
                "etiquettes": {
                    c: etiquettes[c]
                    for c in mesure.CLES_NUMERIQUES
                    + mesure.CLES_POIDS_LOURD
                    + mesure.CLES_GENERALES
                    if c in etiquettes
                },
            }
        )

    resultats = []
    for p in corrige["points"]:
        point = (p["lon"], p["lat"])
        marge = tolerance / mesure.METRES_PAR_DEGRE_LATITUDE
        boite = mesure.boite_de([point], marge)
        proches = [
            v
            for v in voies
            if not mesure.boites_disjointes(
                boite, mesure.boite_de(v["points"], marge)
            )
        ]
        avec = porteuse_la_plus_proche(
            point, p["cap"], proches, tolerance, ang_max, True
        )
        sans = porteuse_la_plus_proche(
            point, p["cap"], proches, tolerance, ang_max, False
        )
        resultats.append(
            {
                "point": p["point"],
                "lat": p["lat"],
                "lon": p["lon"],
                "verdict_pipeline": "COUVERT" if avec else "ABSENT",
                "porteuse_retenue": avec,
                "porteuse_sans_filtre_de_cap": sans,
                "rejete_par_le_cap": bool(sans and not avec),
                "autorite_arrete": p["autorite"],
                "tonnage_arrete_t": p["tonnage_arrete_t"],
            }
        )

    couverts = [r for r in resultats if r["verdict_pipeline"] == "COUVERT"]
    rejetes = [r for r in resultats if r["rejete_par_le_cap"]]
    sortie = {
        "outil": os.path.basename(__file__),
        "parametres": {"tolerance_m": tolerance, "ang_max_deg": ang_max},
        "limite": "l'extrait OSM ne contient que des voies porteuses de "
        "restriction ; la voie du corridor, si elle n'est pas taguée, est "
        "invisible. La distance est un indice d'attribution fautive, pas une "
        "preuve.",
        "points": len(resultats),
        "couverts_par_le_pipeline": len(couverts),
        "rejetes_par_le_filtre_de_cap": len(rejetes),
        "distances_des_couverts_m": sorted(
            round(r["porteuse_retenue"]["distance_m"], 2) for r in couverts
        ),
        "classes_des_porteuses": {
            classe: sum(
                1 for r in couverts if r["porteuse_retenue"]["classe"] == classe
            )
            for classe in sorted(
                {r["porteuse_retenue"]["classe"] for r in couverts}
            )
        },
        "detail": resultats,
    }
    mesure.ecrire_rapport(sys.argv[3], sortie)

    print(f"points examinés                  : {len(resultats)}")
    print(f"couverts par le pipeline         : {len(couverts)}")
    print(f"rejetés par le seul filtre de cap: {len(rejetes)}")
    if couverts:
        d = sortie["distances_des_couverts_m"]
        q = lambda f: d[int(f * (len(d) - 1))]
        print(f"\ndistance point → voie porteuse, en mètres")
        print(f"  min {d[0]:6.2f}   médiane {q(.5):6.2f}   p90 {q(.9):6.2f}   "
              f"max {d[-1]:6.2f}")
        print(f"  sous 5 m  : {sum(1 for x in d if x <= 5):3d} / {len(d)}")
        print(f"  au-delà de 10 m : {sum(1 for x in d if x > 10):3d} / {len(d)}")
        print(f"\nclasses des voies porteuses : {sortie['classes_des_porteuses']}")


if __name__ == "__main__":
    main()
