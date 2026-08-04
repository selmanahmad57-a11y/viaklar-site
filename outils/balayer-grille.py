#!/usr/bin/env python3
"""Sonde la sensibilite du taux a la GRILLE DE DEDUPLICATION — taille ET phase.

    Un invariant verifie sur la grandeur mesuree ne protege pas une grandeur
    derivee qui l'atteint par un autre chemin.

Le 4 aout 2026, une transformation qui PRESERVE la longueur — rechainer des
polylignes contigues — a deplace le denominateur de 10,3 km. La longueur etait
intacte ; le reechantillonnage a pas constant placait ses points ailleurs, donc
la deduplication ne touchait plus les memes cellules.

L'invariant de longueur ne protegeait donc rien, et le chiffre publie porte une
sensibilite a la grille que rien n'avait sondee. Le balayage de tolerance
existait, celui-ci n'existait pas.

DEUX AXES, et le second est le plus revelateur :

    TAILLE  pas_dedup de 0,1 a 11 m. Une grille grossiere fusionne des portions
            distinctes ; une grille fine cesse de dedupliquer.
    PHASE   a taille CONSTANTE, on decale l'origine de la grille d'une fraction
            de cellule. La taille ne change pas, la resolution ne change pas —
            SEULE l'appartenance des points aux cellules change. Toute variation
            du taux sur cet axe est du bruit pur : il n'existe aucune raison de
            preferer une origine a une autre.

    L'amplitude sur l'axe PHASE est donc un plancher de bruit du chiffre publie.

Methode : le MEME outil, avec la seule fonction `cellule` remplacee. C'est le
motif du test differentiel qui a attrape highway=service puis l'attribution de
portee.

Usage :
    python3 outils/balayer-grille.py <dialog.xml> <osm.json> <rapport.json> \\
            <pas_test> <tolerance> <ang_max> <perimetre> <perimetres.json> \\
            <pas_dedup_reference> <tailles> <nombre_de_phases>

    <tailles>            liste separee par des virgules, en metres
    <nombre_de_phases>   decalages equirepartis sur [0, pas_dedup_reference[
"""

import importlib.util
import json
import os
import sys

_ICI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_mesure", os.path.join(_ICI, "mesure-metrique.py")
)
mesure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mesure)

CELLULE_ORIGINE = mesure.cellule
REECHANTILLONNER_ORIGINE = mesure.reechantillonner


def cellule_decalee(decalage_lon, decalage_lat):
    """`cellule` avec l'origine de la grille deplacee. Rien d'autre ne change."""

    def cellule(point, pas_degres):
        return (
            round((point[0] + decalage_lon) / pas_degres),
            round((point[1] + decalage_lat) / pas_degres),
        )

    return cellule


def reechantillonner_decale(fraction):
    """`reechantillonner` avec les points deplaces DANS leur intervalle.

    C'est l'axe qui a REELLEMENT produit les 10,3 km du 4 aout : rechainer des
    polylignes change la longueur totale de chaque ligne, donc le nombre
    d'intervalles ET la position de chaque point. La grille, elle, n'avait pas
    bouge. Sonder la grille sans sonder l'echantillonnage aurait laisse croire
    que la sensibilite etait mesuree.

    L'original place un point au MILIEU de chaque intervalle — fraction 0,5.
    Toute autre fraction est aussi arbitraire, donc l'amplitude sur cet axe est
    du bruit au meme titre que la phase de la grille.
    """

    def reechantillonner(ligne, pas):
        totale = mesure.longueur(ligne)
        if totale <= 0.0:
            return []
        nombre = max(2, int(totale / pas) + 1)
        intervalle = totale / nombre
        cibles = [(i + fraction) * intervalle for i in range(nombre)]

        # Corps repris a l'identique de mesure.reechantillonner : SEULE la
        # fraction ci-dessus change. Le poids reste `intervalle`, donc la somme
        # des poids vaut toujours la longueur exacte — l'invariant de longueur
        # tient sur tout l'axe, et c'est precisement ce qui rend l'axe
        # interessant : il ne le rompt pas et deplace quand meme le resultat.
        echantillons = []
        parcourue = 0.0
        curseur = 0
        for debut, fin in zip(ligne, ligne[1:]):
            segment = mesure.haversine(debut, fin)
            while (curseur < len(cibles)
                   and parcourue <= cibles[curseur] <= parcourue + segment):
                t = 0.0 if segment == 0.0 else (cibles[curseur] - parcourue) / segment
                point = (debut[0] + t * (fin[0] - debut[0]),
                         debut[1] + t * (fin[1] - debut[1]))
                echantillons.append((
                    point, intervalle,
                    mesure.cap_segment(debut, fin,
                                       mesure.metres_par_degre(point[1])),
                ))
                curseur += 1
            parcourue += segment
        while len(echantillons) < nombre:
            dernier = tuple(ligne[-1][:2])
            echantillons.append((
                dernier, intervalle,
                mesure.cap_segment(ligne[-2], ligne[-1],
                                   mesure.metres_par_degre(dernier[1])),
            ))
        return echantillons

    return reechantillonner


def main():
    mesure.exiger(
        len(sys.argv) >= 12,
        "Usage : python3 outils/balayer-grille.py <dialog.xml> <osm.json> "
        "<rapport.json> <pas_test> <tolerance> <ang_max> <perimetre> "
        "<perimetres.json> <pas_dedup_reference> <tailles> <nombre_de_phases>",
    )
    flux, osm, sortie = sys.argv[1], sys.argv[2], sys.argv[3]
    pas_test = float(sys.argv[4])
    tolerance = float(sys.argv[5])
    ang_max = float(sys.argv[6])
    nom_perimetre, chemin_perimetres = sys.argv[7], sys.argv[8]
    pas_reference = float(sys.argv[9])
    tailles = [float(x) for x in sys.argv[10].split(",") if x.strip()]
    phases = int(sys.argv[11])
    mesure.exiger(tailles, "Aucune taille de grille a sonder.")
    mesure.exiger(phases >= 2, "Au moins deux phases, sinon rien n'est compare.")

    collectivites, libelle = mesure.charger_perimetre(chemin_perimetres,
                                                      nom_perimetre)
    arretes, _, _ = mesure.charger_dialog(flux, collectivites)
    voies, _, instantane = mesure.charger_osm(osm, False)
    print(f"perimetre {nom_perimetre} — {libelle}")
    print(f"{len(arretes)} arretes, {len(voies)} voies OSM, "
          f"instantane {instantane}\n")

    def jouer(pas_dedup, decalage_lon=0.0, decalage_lat=0.0):
        mesure.cellule = (
            CELLULE_ORIGINE if not (decalage_lon or decalage_lat)
            else cellule_decalee(decalage_lon, decalage_lat)
        )
        resultat = mesure.mesurer(arretes, voies, {
            "pas_test": pas_test, "pas_dedup": pas_dedup,
            "tolerance": tolerance, "ang_max": ang_max,
        })
        mesure.cellule = CELLULE_ORIGINE
        return resultat["metrique"]

    print("=== AXE TAILLE — pas_dedup ===")
    print(f"  {'pas (m)':>8} {'denominateur (km)':>19} {'taux (%)':>11} "
          f"{'cellules':>10}")
    par_taille = []
    for pas in tailles:
        m = jouer(pas)
        par_taille.append({"pas_dedup_m": pas, "taux": m["taux"],
                           "metres_total": m["metres_total"],
                           "cellules": m["cellules"]})
        print(f"  {pas:>8g} {m['metres_total']/1000:>19.1f} "
              f"{m['taux']*100:>11.4f} {m['cellules']:>10}")

    # PHASE : a taille constante, seule l'origine bouge. Le decalage est en
    # degres, exprime en fraction de cellule — la cellule vaut pas/111000 deg.
    pas_degres = pas_reference / mesure.METRES_PAR_DEGRE_LATITUDE
    print(f"\n=== AXE PHASE — pas_dedup = {pas_reference:g} m, origine deplacee ===")
    print("  la taille et la resolution sont CONSTANTES : toute variation ici")
    print("  est du bruit, car aucune origine n'est preferable a une autre.")
    print(f"\n  {'fraction':>9} {'denominateur (km)':>19} {'taux (%)':>11} "
          f"{'cellules':>10}")
    par_phase = []
    for i in range(phases):
        fraction = i / phases
        decalage = fraction * pas_degres
        m = jouer(pas_reference, decalage, decalage)
        par_phase.append({"fraction_de_cellule": fraction, "taux": m["taux"],
                          "metres_total": m["metres_total"],
                          "cellules": m["cellules"]})
        print(f"  {fraction:>9.3f} {m['metres_total']/1000:>19.1f} "
              f"{m['taux']*100:>11.4f} {m['cellules']:>10}")

    # AXE ECHANTILLONNAGE — la position du point DANS son intervalle.
    print(f"\n=== AXE ECHANTILLONNAGE — position du point dans son intervalle ===")
    print("  l'original place le point au MILIEU (fraction 0,5). Toute autre")
    print("  fraction est aussi arbitraire : l'amplitude ici est du bruit.")
    print(f"\n  {'fraction':>9} {'denominateur (km)':>19} {'taux (%)':>11} "
          f"{'cellules':>10}")
    par_echantillon = []
    for i in range(phases):
        fraction = (i + 0.5) / phases
        mesure.reechantillonner = reechantillonner_decale(fraction)
        m = jouer(pas_reference)
        mesure.reechantillonner = REECHANTILLONNER_ORIGINE
        par_echantillon.append({"fraction_d_intervalle": fraction,
                                "taux": m["taux"],
                                "metres_total": m["metres_total"],
                                "cellules": m["cellules"]})
        print(f"  {fraction:>9.3f} {m['metres_total']/1000:>19.1f} "
              f"{m['taux']*100:>11.4f} {m['cellules']:>10}")
    taux_ech = [p["taux"] * 100 for p in par_echantillon]
    metres_ech = [p["metres_total"] for p in par_echantillon]
    cellules_ech = [p["cellules"] for p in par_echantillon]
    print(f"\n  amplitude du taux sur l'ECHANTILLONNAGE : "
          f"{max(taux_ech) - min(taux_ech):.4f} point")
    print(f"  amplitude du denominateur               : "
          f"{(max(metres_ech) - min(metres_ech))/1000:.2f} km  "
          f"({(max(metres_ech)-min(metres_ech))/min(metres_ech)*100:.3f} %)")
    print(f"  amplitude du COMPTE DE CELLULES         : "
          f"{max(cellules_ech) - min(cellules_ech)} "
          f"({(max(cellules_ech)-min(cellules_ech))/min(cellules_ech)*100:.3f} %)")
    print("  -> les TROIS se publient. C'est l'invariance de la LONGUEUR qui")
    print("     avait aveugle le controle precedent ; un balayage qui ne publie")
    print("     que le taux reproduirait le meme angle mort, a son echelle.")

    taux_phase = [p["taux"] * 100 for p in par_phase]
    metres_phase = [p["metres_total"] for p in par_phase]
    amplitude_taux = max(taux_phase) - min(taux_phase)
    amplitude_metres = max(metres_phase) - min(metres_phase)
    taux_taille = [t["taux"] * 100 for t in par_taille]

    cellules_phase = [p["cellules"] for p in par_phase]
    print(f"\n  amplitude du taux sur la PHASE   : {amplitude_taux:.4f} point")
    print(f"  amplitude du denominateur        : {amplitude_metres/1000:.2f} km "
          f"({amplitude_metres/min(metres_phase)*100:.3f} %)")
    print(f"  amplitude du compte de cellules  : "
          f"{max(cellules_phase) - min(cellules_phase)} "
          f"({(max(cellules_phase)-min(cellules_phase))/min(cellules_phase)*100:.3f} %)")
    print(f"  amplitude du taux sur la TAILLE  : "
          f"{max(taux_taille) - min(taux_taille):.4f} point")

    rapport = {
        "pourquoi": "Sensibilite du taux a la grille de deduplication. L'axe "
                    "PHASE est un plancher de BRUIT : la taille et la resolution "
                    "y sont constantes, et aucune origine de grille n'est "
                    "preferable a une autre.",
        "declencheur": "Le 4 aout 2026, rechainer des polylignes contigues — "
                       "transformation qui PRESERVE la longueur — a deplace le "
                       "denominateur de 10,3 km. L'invariant de longueur ne "
                       "protegeait pas le denominateur, qui l'atteint par un "
                       "autre chemin.",
        "perimetre": {"nom": nom_perimetre, "libelle": libelle},
        "instantane_osm": instantane,
        "parametres_fixes": {"pas_test_m": pas_test, "tolerance_m": tolerance,
                             "ang_max_deg": ang_max},
        "entrees": {"dialog": mesure.empreinte_fichier(flux),
                    "osm": mesure.empreinte_fichier(osm)},
        "axe_taille": par_taille,
        "axe_echantillonnage": {
            "pourquoi": "L'axe qui a REELLEMENT produit les 10,3 km du 4 aout. "
                        "Sonder la grille sans lui aurait laisse croire que la "
                        "sensibilite etait mesuree.",
            "mesures": par_echantillon,
            "amplitude_taux_points": max(taux_ech) - min(taux_ech),
            "amplitude_metres": max(metres_ech) - min(metres_ech),
            "amplitude_cellules": max(cellules_ech) - min(cellules_ech),
            "pourquoi_les_trois": "L'invariance de la LONGUEUR avait aveugle le "
                "controle precedent. Un balayage qui ne publie que le taux "
                "reproduirait le meme angle mort, a l'echelle du balayage.",
        },
        "axe_phase": {"pas_dedup_m": pas_reference, "mesures": par_phase,
                      "amplitude_taux_points": amplitude_taux,
                      "amplitude_metres": amplitude_metres},
    }
    mesure.ecrire_rapport(sortie, rapport)


if __name__ == "__main__":
    main()
