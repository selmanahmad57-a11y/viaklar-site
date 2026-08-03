#!/usr/bin/env python3
"""Produit le geojson de la carte publique, avec LES DEUX mesures.

Ferme la trouvaille de l'audit du 2 août : le fichier publié venait d'un script
jetable qui n'existait plus, donc l'unité qu'il comptait n'était pas
reconstructible. **Les nombres étaient reproductibles, l'artefact ne l'était
pas.** On peut refaire une mesure sans pouvoir refaire une carte.

Ce fichier ne recalcule rien : il importe mesure-metrique.py et appelle ses
fonctions. Deux implémentations de la même mesure divergeraient sans que rien ne
le signale — c'est exactement l'écart de 23 145 voies trouvé par test
différentiel entre les deux premiers outils.

Il émet UNE ENTITÉ PAR ARRÊTÉ, unité déclarée au §3.3 de
docs/unite-preinscrite.md, et porte sur chacune :

  metres, metres_absents, couverture   la mesure métrique, par arrêté
  etat                                 le verdict binaire, conservé en second

Les deux se publient ensemble ou pas du tout (§3.3) : publier le seul taux par
arrêté était défendable tant qu'on ignorait la distribution des longueurs, et ce
n'est plus le cas — le centile le plus long porte une part du linéaire hors de
proportion avec son effectif.

**Cette part se CALCULE ici, elle ne se récite pas.** Elle valait 22,4 % et vaut
22,6 % depuis la correction d'attribution du 3 août ; la phrase qui la portait
était en dur et a survécu intacte au déplacement. Un générateur dont une part de
la sortie n'est pas reconstructible est exactement le défaut que ce fichier
existe pour empêcher — et il vivait dedans.

Usage :
    python3 outils/carte-geojson.py <dialog.xml> <osm.json> <sortie.geojson> \\
            <pas_test> <pas_dedup> <tolerance> <ang_max> <ecart> \\
            <couverture_min> <service_si_tonnage>
"""

import importlib.util
import json
import os
import sys

VOISIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesure-metrique.py")
_spec = importlib.util.spec_from_file_location("_mesure", VOISIN)
mesure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mesure)

# Part de tête servant à dire la faiblesse de l'unité « arrêté ». Nommée parce
# qu'elle décide du nombre publié : « le 1 % le plus long » et « le 5 % le plus
# long » ne disent pas la même chose de la même donnée.
CENTILE = 0.01

# Seuils de qualification de l'état, en fraction de couverture. Ce ne sont pas
# des seuils de mesure — la mesure est continue — mais des classes d'affichage,
# et elles sont nommées pour que la légende de la carte les lise au lieu de les
# redéfinir.
CLASSES = (
    ("ABSENT", 0.0, "Aucune restriction trouvée dans OSM"),
    ("MARGINAL", 0.10, "Moins d'un dixième de l'emprise couvert"),
    ("PARTIEL", 0.90, "Emprise partiellement couverte"),
    ("COUVERT", 1.01, "Emprise entièrement couverte"),
)


def classer(couverture):
    for nom, plafond, libelle in CLASSES:
        if couverture <= plafond or nom == "COUVERT":
            return nom, libelle
    return CLASSES[-1][0], CLASSES[-1][2]


def main():
    mesure.exiger(
        len(sys.argv) >= 4,
        "Usage : python3 outils/carte-geojson.py <dialog.xml> <osm.json> "
        "<sortie.geojson> <pas_test> <pas_dedup> <tolerance> <ang_max> "
        "<ecart> <couverture_min> <service_si_tonnage>",
    )
    mesure._verifier_listes_partagees()
    par = {
        "pas_test": mesure.parametre("MESURE_PAS_TEST_M", 4, "pas de rééchantillonnage"),
        "pas_dedup": mesure.parametre("MESURE_PAS_DEDUP_M", 5, "pas de déduplication"),
        "tolerance": mesure.parametre("MESURE_TOL_APPARIEMENT_M", 6, "tolérance"),
        "ang_max": mesure.parametre("MESURE_ANG_MAX_DEG", 7, "écart de cap maximal"),
        "ecart_negligeable": mesure.parametre("MESURE_ECART_NEGLIGEABLE_PT", 8, "seuil"),
        "couverture_min": mesure.parametre("MESURE_COUVERTURE_MIN", 9, "couverture min"),
        "service_si_tonnage": mesure.parametre(
            "MESURE_SERVICE_SI_TONNAGE", 10, "repêchage service", lambda x: bool(int(x))
        ),
    }
    arretes, operateurs, journal = mesure.charger_dialog(sys.argv[1])
    inattendus = {
        op: n for op, n in operateurs.items() if op != mesure.OPERATEUR_ATTENDU
    }
    mesure.exiger(not inattendus, f"Invariante rompue : {inattendus}")
    voies, journal_osm, instantane = mesure.charger_osm(
        sys.argv[2], par["service_si_tonnage"]
    )
    journal.update(journal_osm)
    couverture = mesure.couverture_du_perimetre(arretes, voies, par["tolerance"])
    mesure.exiger(
        couverture["part_couverte"] >= par["couverture_min"],
        f"L'extrait OSM ne couvre que {couverture['part_couverte']:.1%} du "
        "périmètre déclaré. Une carte publiée sur une couverture partielle "
        "montrerait comme absente de la voirie qu'aucune donnée ne peut couvrir.",
    )

    resultat = mesure.mesurer(arretes, voies, par)
    detail = resultat["detail"]
    mesure.exiger(
        len(detail) == len(arretes),
        "Le détail par arrêté n'est pas aligné sur les arrêtés — "
        "l'appariement par indice ne tient plus.",
    )

    entites = []
    for arrete, d in zip(arretes, detail):
        c = 0.0 if d["metres"] <= 0 else (d["metres"] - d["metres_absents"]) / d["metres"]
        etat, libelle = classer(c)
        lignes = [[[round(x, 6), round(y, 6)] for x, y in ligne] for ligne in arrete["lignes"]]
        entites.append(
            {
                "type": "Feature",
                "geometry": (
                    {"type": "LineString", "coordinates": lignes[0]}
                    if len(lignes) == 1
                    else {"type": "MultiLineString", "coordinates": lignes}
                ),
                "properties": {
                    "description": arrete["description"],
                    "autorite": arrete["autorite"],
                    "tonnage_t": arrete["tonnage"],
                    "metres": round(d["metres"], 1),
                    "metres_absents": round(d["metres_absents"], 1),
                    "couverture": round(c, 4),
                    "etat": etat,
                    "etat_libelle": libelle,
                },
            }
        )

    # La faiblesse de l'unité « arrêté » se CALCULE, elle ne se récite pas.
    longueurs = sorted((d["metres"] for d in detail), reverse=True)
    mesure.exiger(longueurs, "Aucun arrêté : la faiblesse de l'unité n'a pas de sens.")
    centile = max(1, round(len(longueurs) * CENTILE))
    total_metres = sum(longueurs)
    part_du_centile = 100.0 * sum(longueurs[:centile]) / total_metres

    m, a = resultat["metrique"], resultat["par_arrete"]
    sortie = {
        "type": "FeatureCollection",
        "metadata": {
            "titre": "Arrêtés d'interdiction de tonnage et leur expression dans "
            "OpenStreetMap",
            "genere_par": os.path.basename(__file__),
            "definition": "docs/unite-preinscrite.md §3.2 et §3.3, pré-inscrites "
            "le 2026-08-03 avant toute exécution",
            "source_arretes": "DiaLog / DGITM — Licence Ouverte 2.0",
            "source_comparaison": "OpenStreetMap contributors — ODbL",
            "instantane_osm": instantane,
            "entrees": {
                "dialog": mesure.empreinte_fichier(sys.argv[1]),
                "osm": mesure.empreinte_fichier(sys.argv[2]),
            },
            "parametres": par,
            "mesure_principale": {
                "unite": "mètre de chaussée sous arrêté, dédupliqué",
                "metres_total": m["metres_total"],
                "metres_absents": m["metres_absents"],
                "taux": m["taux"],
            },
            "mesure_secondaire": {
                "unite": "arrêté entièrement absent d'OSM",
                "total": a["total"],
                "absents": a["absents"],
                "taux": a["taux"],
                # Cette phrase portait « 86 m », « 52,7 km » et « 22,4 % » EN
                # DUR. Trois nombres écrits dans une prose que le générateur
                # réémet sans les recalculer : le 3 août, l'attribution de
                # portée a déplacé le 22,4 en 22,6 et la phrase a survécu
                # intacte. C'est le défaut que ce fichier existe pour empêcher —
                # un artefact publié dont une part n'est pas reconstructible —
                # et il vivait dans le fichier lui-même.
                "faiblesse": (
                    f"donne le même poids à {min(longueurs):.0f} m de rue "
                    f"communale et à {max(longueurs)/1000:.1f} km de "
                    f"départementale ; le 1 % le plus long porte "
                    f"{part_du_centile:.1f} % des mètres"
                ).replace(".", ","),
            },
            "couverture_du_perimetre": couverture,
            "reserves": [
                "L'épreuve à l'aveugle borne le risque de fausses absences AU "
                "NIVEAU DE L'ARRÊTÉ. Elle ne valide pas la comptabilité de "
                "couverture partielle, dont dépendent 39 % du chiffre en mètres.",
                "Les vérificateurs aveugles ne sont pas une méthode indépendante "
                "mais une réimplémentation de la même spécification : leur accord "
                "démontre la fidélité de l'implémentation, pas la justesse de la "
                "mesure.",
                "La completude de DiaLog n'est PAS etablie, et le manque pousse "
                "le chiffre VERS LE HAUT : hors du perimetre du decret du 24 mars "
                "2026 le depot est volontaire, et un arrete vivant absent du flux "
                "n'entre pas au denominateur alors qu'il est tres probablement "
                "absent d'OSM aussi.",
                "La tolérance d'appariement décide de 2,3 points sur la plage "
                "10-50 m. En dessous, la pente s'emballe d'un facteur dix, ce qui "
                "reste inexpliqué : le desaccord geometrique entre DiaLog et OSM "
                "N'EST PAS MESURE — le seul chiffre disponible etait circulaire et "
                "a ete retracte (docs/retractations.json, plancher-deplacement).",
            ],
            "ce_que_le_chiffre_ne_dit_pas": [
                "Rien sur une proportion d'arrêtés : « X % des arrêtés » ne se "
                "dérive jamais du taux métrique.",
                "Rien sur l'exactitude des restrictions présentes : une voie "
                "limitée à 3,5 t et étiquetée maxweight=19 compte comme couverte.",
                "Rien sur la réglementation non publiée dans DiaLog.",
                "Rien sur la pertinence des arrêtés.",
            ],
            "classes_affichage": [
                {"etat": n, "plafond_couverture": p, "libelle": l} for n, p, l in CLASSES
            ],
        },
        "features": entites,
    }
    mesure.ecrire_rapport(sys.argv[3], sortie)

    print(f"entités écrites   : {len(entites)}")
    print(f"mesure principale : {m['taux']:.1%} de {m['metres_total']/1000:.1f} km")
    print(f"mesure secondaire : {a['taux']:.1%} de {a['total']} arrêtés")
    par_etat = {}
    for e in entites:
        par_etat[e["properties"]["etat"]] = par_etat.get(e["properties"]["etat"], 0) + 1
    print(f"états             : {par_etat}")
    print(f"sortie            : {sys.argv[3]}")


if __name__ == "__main__":
    main()
