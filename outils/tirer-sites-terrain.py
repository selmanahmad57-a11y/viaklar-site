#!/usr/bin/env python3
"""Tire les sites de vérification terrain, uniformément EN LONGUEUR.

Applique le protocole de docs/verification-terrain.md, pré-inscrit et commité
avant l'existence de ce fichier.

    Tirage AU MÈTRE, jamais à l'arrêté. Les absences se concentrent sur les longs
    linéaires — Cassel, 43,6 km — et tirer par arrêté surpondérerait les emprises
    courtes, celles qui pèsent le moins dans les 1 965,2 km absents.

Deux populations, mélangées et scellées :
  - les cellules ABSENTES, dont on va vérifier qu'un panneau existe bien ;
  - des cellules COUVERTES, les témoins, qui testent l'observateur et non la
    carte. Quelqu'un qui rapporte « aucun panneau » partout se trahit sur eux.

La feuille de route ne porte QUE des coordonnées : ni verdict, ni tonnage, ni
description d'arrêté, ni le nombre de témoins. Le corrigé est un fichier à part.

Usage :
    python3 outils/tirer-sites-terrain.py <dialog.xml> <osm.json> \\
            <feuille.md> <corrige.json> <n_absents> <n_temoins> <graine> \\
            <pas_test> <pas_dedup> <tolerance> <ang_max> <service_si_tonnage>
"""

import importlib.util
import json
import os
import random
import sys

VOISIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesure-metrique.py")
_spec = importlib.util.spec_from_file_location("_mesure", VOISIN)
mesure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mesure)

ZOOM = 18
ROSE = (("nord-sud", 0), ("nord-est / sud-ouest", 45),
        ("est-ouest", 90), ("nord-ouest / sud-est", 135))


def direction(cap):
    return min(ROSE, key=lambda x: mesure.ecart_de_cap(cap, x[1]))[0]


def main():
    mesure.exiger(
        len(sys.argv) >= 13,
        "Usage : python3 outils/tirer-sites-terrain.py <dialog.xml> <osm.json> "
        "<feuille.md> <corrige.json> <n_absents> <n_temoins> <graine> "
        "<pas_test> <pas_dedup> <tolerance> <ang_max> <service_si_tonnage>",
    )
    flux, osm, chemin_feuille, chemin_corrige = sys.argv[1:5]
    n_absents = int(sys.argv[5])
    n_temoins = int(sys.argv[6])
    graine = int(sys.argv[7])
    par = {
        "pas_test": float(sys.argv[8]),
        "pas_dedup": float(sys.argv[9]),
        "tolerance": float(sys.argv[10]),
        "ang_max": float(sys.argv[11]),
        "service_si_tonnage": bool(int(sys.argv[12])),
    }
    mesure._verifier_listes_partagees()

    arretes, operateurs, _ = mesure.charger_dialog(flux)
    inattendus = {o: n for o, n in operateurs.items() if o != mesure.OPERATEUR_ATTENDU}
    mesure.exiger(not inattendus, f"Invariante rompue : {inattendus}")
    voies, _, instantane = mesure.charger_osm(osm, par["service_si_tonnage"])

    # Même parcours que la mesure : les cellules tirées SONT celles du
    # dénominateur, pas une population voisine.
    marge = par["tolerance"] / mesure.METRES_PAR_DEGRE_LATITUDE
    for voie in voies:
        voie["boite"] = mesure.boite_de(voie["points"], marge)
    pas_degres = par["pas_dedup"] / mesure.METRES_PAR_DEGRE_LATITUDE

    absentes, couvertes = {}, {}
    for arrete in arretes:
        tous = [p for ligne in arrete["lignes"] for p in ligne]
        boite = mesure.boite_de(tous, marge)
        candidates = [v for v in voies
                      if not mesure.boites_disjointes(boite, v["boite"])]
        for ligne in arrete["lignes"]:
            for point, poids, cap in mesure.reechantillonner(ligne, par["pas_test"]):
                preuve = mesure.couvert(point, candidates, par["tolerance"],
                                        par["ang_max"], cap)
                cle = mesure.cellule(point, pas_degres)
                cible = couvertes if preuve else absentes
                autre = absentes if preuve else couvertes
                if cle in autre:
                    # Une cellule vue couverte par un arrêté l'est pour tous :
                    # la couverture l'emporte, comme dans la mesure.
                    if preuve:
                        autre.pop(cle, None)
                    else:
                        continue
                cible.setdefault(cle, (point, poids, cap, arrete))

    mesure.exiger(len(absentes) >= n_absents, f"{len(absentes)} cellules absentes")
    mesure.exiger(len(couvertes) >= n_temoins, f"{len(couvertes)} cellules couvertes")

    alea = random.Random(graine)

    def tirer(population, combien):
        items = list(population.values())
        poids = [p for _, p, _, _ in items]
        pris, vus = [], set()
        while len(pris) < combien:
            (i,) = alea.choices(range(len(items)), weights=poids, k=1)
            if i in vus:
                continue
            vus.add(i)
            pris.append(items[i])
        return pris

    sites = [(x, "absent") for x in tirer(absentes, n_absents)]
    sites += [(x, "temoin") for x in tirer(couvertes, n_temoins)]
    alea.shuffle(sites)

    lignes = [
        "# Vérification terrain — feuille de route",
        "",
        f"**{len(sites)} sites**, tirés au hasard uniformément en longueur le long du",
        "réseau français sous arrêté d'interdiction de tonnage.",
        "",
        "## Ce qu'on vous demande, sur chaque site",
        "",
        "Deux constats **séparés**. Ne les fusionnez pas : un pont bas sans panneau et",
        "un panneau sans obstacle sont deux résultats différents.",
        "",
        "**A — Panneau réglementaire.** Y a-t-il, à cet endroit, un panneau limitant",
        "le tonnage ou interdisant l'accès aux poids lourds ? **Regardez les deux sens.**",
        "Si oui : relevez la valeur et le type de panneau.",
        "",
        "**B — Gabarit physique.** Y a-t-il un ouvrage bas, un passage étroit, une",
        "structure qui limiterait de fait un poids lourd ? Mesurez ou estimez, et dites",
        "**comment** vous avez obtenu la valeur.",
        "",
        "**Site non atteint : consignez-le comme non atteint.** Ne le remplacez jamais",
        "par un autre, même proche, même plus commode — sinon c'est l'itinéraire qui",
        "choisit l'échantillon.",
        "",
        "Rien ici n'indique ce qui est attendu, et le nombre de sites de chaque nature",
        "n'est pas donné.",
        "",
        "---",
        "",
    ]
    corrige = []
    for rang, ((point, poids, cap, arrete), nature) in enumerate(sites, start=1):
        lon, lat = point
        lignes += [
            f"### Site {rang}",
            "",
            f"**Coordonnées** — {lat:.6f}, {lon:.6f}",
            f"**Orientation de la voie** — {direction(cap)}",
            f"**Carte** — https://www.openstreetmap.org/#map={ZOOM}/{lat:.5f}/{lon:.5f}",
            "",
            "A · panneau réglementaire : ______   valeur : ______",
            "",
            "B · gabarit physique : ______   méthode : ______",
            "",
            "atteint : oui / non — si non, pourquoi : ______",
            "",
        ]
        corrige.append({
            "site": rang, "nature": nature, "lat": lat, "lon": lon, "cap": cap,
            "poids_m": poids, "tonnage_arrete_t": arrete["tonnage"],
            "autorite": arrete["autorite"], "description": arrete["description"],
        })

    mesure.ecrire_rapport(chemin_corrige, {
        "protocole": "docs/verification-terrain.md, pré-inscrit et commité avant ce tirage",
        "graine": graine, "parametres": par, "instantane_osm": instantane,
        "entrees": {"dialog": mesure.empreinte_fichier(flux),
                    "osm": mesure.empreinte_fichier(osm)},
        "population_absente_cellules": len(absentes),
        "population_couverte_cellules": len(couvertes),
        "sites_absents": n_absents, "sites_temoins": n_temoins,
        "borne_si_zero_defaillance": 3 / n_absents,
        "sites": corrige,
    })
    with open(chemin_feuille, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))

    print(f"population absente  : {len(absentes)} cellules")
    print(f"population couverte : {len(couvertes)} cellules")
    print(f"sites tirés         : {n_absents} absents + {n_temoins} témoins "
          f"(graine {graine})")
    print(f"borne si zéro défaillance : {300/n_absents:.0f} %")
    print(f"feuille : {chemin_feuille}\ncorrigé : {chemin_corrige}")


if __name__ == "__main__":
    main()
