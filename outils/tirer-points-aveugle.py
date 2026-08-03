#!/usr/bin/env python3
"""Tire des points uniformément EN LONGUEUR le long du réseau réglementé.

Produit une épreuve à l'aveugle qui estime directement le taux d'absence en
mètres, sans passer par la comptabilité de couverture partielle.

    Le taux en mètres est une moyenne, pondérée par la longueur, d'une propriété
    binaire : en chaque point du réseau réglementé, OSM porte ou ne porte pas une
    restriction. Donc la PROPORTION DE « NON » sur un échantillon uniforme en
    longueur EST le taux d'absence en mètres.

Trois propriétés qui font de ce cadre autre chose qu'un contrôle :

  - le coût par cas est celui de la première épreuve — un point, une question,
    oui ou non. Pas de parcours d'emprise ;
  - ce n'est pas une vérification du calcul, c'est une SECONDE ESTIMATION de la
    même grandeur par une méthode indépendante ;
  - l'échantillon est tiré de la géométrie DiaLog, donc HORS du pipeline testé.
    L'invariante du §18 — « quand la grandeur mesurée est une propriété du
    pipeline, l'échantillon doit être sélectionné par autre chose que le
    pipeline » — est respectée, ce qui n'était pas gagné.

Et l'échantillon tombera de lui-même à ~43 % dans les emprises partiellement
couvertes, puisque c'est leur part du linéaire : la surface non validée est
couverte à proportion de son poids, sans avoir à la cibler.

Aucun témoin n'est ajouté artificiellement. À ~90 % d'absence, environ un point
sur dix doit être couvert : ce sont les témoins, et ils sont tirés par le hasard
plutôt que choisis. Un vérificateur qui répond « non » partout se trahit seul.

Usage :
    python3 outils/tirer-points-aveugle.py <dialog.xml> <sujet.md> <corrige.json> \\
            <nombre_de_points> <graine> <pas_test_m>

Le corrigé ne contient PAS le verdict du pipeline : il ne pourrait pas servir de
corrigé s'il portait ce qu'il est censé mettre à l'épreuve. Il porte l'identité
des points, et le rapprochement se fait après coup contre le rapport machine.
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

# Le zoom du lien cartographique : assez serré pour désigner une voie sans
# ambiguïté, assez large pour voir le carrefour voisin.
ZOOM_CARTE = 18

ROSE = (
    ("nord-sud", 0), ("nord-est / sud-ouest", 45),
    ("est-ouest", 90), ("nord-ouest / sud-est", 135),
)


def direction(cap):
    """Nom lisible de l'orientation, pour que le vérificateur sache QUELLE voie.

    Sans elle, un point posé sur un carrefour est ambigu et le vérificateur
    répond sur la mauvaise rue — ce serait un bruit ajouté par l'énoncé, pas
    une erreur de la carte.
    """
    return min(ROSE, key=lambda x: mesure.ecart_de_cap(cap, x[1]))[0]


def main():
    mesure.exiger(
        len(sys.argv) >= 7,
        "Usage : python3 outils/tirer-points-aveugle.py <dialog.xml> <sujet.md> "
        "<corrige.json> <nombre_de_points> <graine> <pas_test_m>",
    )
    flux, chemin_sujet, chemin_corrige = sys.argv[1], sys.argv[2], sys.argv[3]
    nombre = mesure.parametre(
        "TIRAGE_NOMBRE", 4,
        "Nombre de points à tirer.\n"
        "Autour de 90 %, 40 points donnent ±10 points à 95 %, 140 donnent ±5.",
        int,
    )
    graine = mesure.parametre(
        "TIRAGE_GRAINE", 5,
        "Graine du tirage. Elle est DÉCLARÉE et publiée : un tirage qu'on ne\n"
        "peut pas rejouer n'est pas un tirage, c'est un choix.",
        int,
    )
    pas = mesure.parametre(
        "TIRAGE_PAS_M", 6,
        "Pas de rééchantillonnage, identique à celui de la mesure : les deux\n"
        "estimations doivent porter sur la même population de points.",
    )

    arretes, operateurs, journal = mesure.charger_dialog(flux)
    inattendus = {
        op: n for op, n in operateurs.items() if op != mesure.OPERATEUR_ATTENDU
    }
    mesure.exiger(not inattendus, f"Invariante rompue : {inattendus}")

    # Population de tirage : exactement les cellules du dénominateur, chacune
    # portant son poids en mètres. Tirer proportionnellement au poids, c'est
    # tirer uniformément en longueur.
    pas_degres = mesure.METRES_PAR_DEGRE_LATITUDE and 1.0 / mesure.METRES_PAR_DEGRE_LATITUDE
    cellules = {}
    for arrete in arretes:
        for ligne in arrete["lignes"]:
            for point, poids, cap in mesure.reechantillonner(ligne, pas):
                cle = mesure.cellule(point, pas_degres)
                if cle not in cellules:
                    cellules[cle] = (point, poids, cap, arrete)

    population = list(cellules.values())
    total_m = sum(poids for _, poids, _, _ in population)
    mesure.exiger(
        population, "Aucun point tirable : le flux ne porte aucune emprise."
    )
    mesure.exiger(
        nombre <= len(population),
        f"{nombre} points demandés pour {len(population)} disponibles.",
    )

    alea = random.Random(graine)
    poids = [p for _, p, _, _ in population]
    tirage = []
    vus = set()
    # Tirage sans remise, proportionnel au poids. Les poids étant quasi égaux,
    # c'est à très peu près uniforme en longueur ; le proportionnel corrige le
    # résidu dû aux tronçons dont la longueur n'est pas un multiple du pas.
    while len(tirage) < nombre:
        (indice,) = alea.choices(range(len(population)), weights=poids, k=1)
        if indice in vus:
            continue
        vus.add(indice)
        tirage.append(population[indice])
    alea.shuffle(tirage)

    lignes = [
        "# Épreuve à l'aveugle — le réseau réglementé, point par point",
        "",
        f"**{nombre} points** tirés au hasard le long du réseau français "
        "sous arrêté d'interdiction de tonnage, **uniformément en longueur**.",
        "",
        "## Ce qu'on vous demande",
        "",
        "Pour chaque point, ouvrez le lien, regardez **la voie qui passe par ce "
        "point précis** dans la direction indiquée, et répondez à une seule "
        "question :",
        "",
        "> **Cette voie porte-t-elle, dans OpenStreetMap, une restriction "
        "applicable aux poids lourds à cet endroit ?**",
        "",
        "Compte comme restriction : une limite de tonnage (`maxweight`, "
        "`maxweightrating`, `maxweight:conditional`), une interdiction "
        "poids lourds (`hgv`), ou un `access` / `motor_vehicle` restrictif "
        "(`no`, `destination`, `private`, `delivery`, `agricultural`, "
        "`forestry`) sur une voie carrossable.",
        "",
        "Ne compte pas : une restriction sur un chemin piéton, une piste "
        "cyclable, un escalier ou une allée de service voisine. La question "
        "porte sur **la voie carrossable qui passe par le point**.",
        "",
        "Répondez **OUI**, **NON**, ou **INCERTAIN**. `INCERTAIN` est une "
        "réponse légitime et utile — ne devinez pas.",
        "",
        "**N'utilisez que votre propre consultation d'OpenStreetMap.** Aucun "
        "chiffre de ce projet ne doit entrer dans votre jugement, et rien ici "
        "n'indique la réponse attendue.",
        "",
        "---",
        "",
    ]
    corrige = []
    for rang, (point, poids_m, cap, arrete) in enumerate(tirage, start=1):
        lon, lat = point
        lignes += [
            f"### Point {rang}",
            "",
            f"**Coordonnées** — {lat:.6f}, {lon:.6f}",
            f"**Orientation de la voie visée** — {direction(cap)}",
            f"**Carte** — https://www.openstreetmap.org/#map={ZOOM_CARTE}/"
            f"{lat:.5f}/{lon:.5f}",
            "",
            "Réponse : ______",
            "",
        ]
        corrige.append(
            {
                "point": rang,
                "lat": lat,
                "lon": lon,
                "cap": cap,
                "poids_m": poids_m,
                "tonnage_arrete_t": arrete["tonnage"],
                "autorite": arrete["autorite"],
                "description_arrete": arrete["description"],
            }
        )

    mesure.ecrire_rapport(
        chemin_corrige,
        {
            "protocole": "épreuve aveugle sur points tirés uniformément en "
            "longueur ; la proportion de NON estime le taux d'absence en mètres",
            "graine": graine,
            "pas_test_m": pas,
            "points_tires": nombre,
            "population_cellules": len(population),
            "longueur_totale_m": total_m,
            "sans_verdict_du_pipeline": "délibéré — un corrigé qui porterait le "
            "verdict à éprouver ne serait pas un corrigé. Le rapprochement se "
            "fait après coup contre le rapport de mesure.",
            "points": corrige,
        },
    )
    with open(chemin_sujet, "w", encoding="utf-8") as sortie:
        sortie.write("\n".join(lignes))

    print(f"population de tirage : {len(population)} cellules, {total_m/1000:.1f} km")
    print(f"points tirés         : {nombre}  (graine {graine})")
    print(f"sujet                : {chemin_sujet}")
    print(f"corrigé              : {chemin_corrige}")
    attendu = (nombre * 0.9 * 0.1) ** 0.5 / nombre
    print(f"\nprécision attendue autour de 90 % : ±{196 * attendu:.1f} points à 95 %")


if __name__ == "__main__":
    main()
