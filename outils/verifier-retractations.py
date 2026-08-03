#!/usr/bin/env python3
"""Balaye le dépôt à la recherche de nombres rétractés qui respirent encore.

    Un nombre rétracté ne se supprime pas, il se MARQUE.

La suppression est silencieuse — c'est la règle 12 du §18, celle des rejets qui
doivent être journalisés, appliquée aux chiffres au lieu des enregistrements. Un
chiffre effacé d'un document, et dont la raison ne vit que dans un message de
commit, garantit exactement ce qui s'est produit le 3 août : **le nombre survit
dans la tête de qui l'a écrit, la rétractation non.**

Le cas qui l'a imposé : le p95 de 8,53 m, rétracté comme circulaire le 2 août,
reparu le 3 comme plancher de tolérance, inscrit au registre des invariantes, et
invoqué pour disqualifier une amplitude de 4,76 points. Il est revenu **avec ses
papiers en règle** : sa définition avait voyagé avec lui, sa rétractation non.

Ce que cet outil fait : pour chaque valeur du registre, chercher ses occurrences
et signaler celles qui ne sont PAS accompagnées d'une marque de rétractation
dans leur voisinage. Une occurrence marquée est saine — c'est même le but : le
chiffre reste lisible, avec son retrait attaché.

Usage :
    python3 outils/verifier-retractations.py <registre.json> <racine> <fenetre>

    <fenetre> : nombre de lignes de part et d'autre où chercher la marque.
                Ce n'est pas un défaut silencieux : une fenêtre trop large
                blanchit tout, une trop étroite crie sur des cas sains.
"""

import json
import os
import re
import sys

# LA LISTE DE MARQUEURS N'EST PAS DANS CE FICHIER. Elle vit dans le registre,
# versionnée, parce que le compte « N occurrences nues » n'est interprétable
# qu'avec la liste qui l'a produit.
#
# C'est l'invariante 15 du §18 appliquée à un détecteur : un critère assoupli
# jusqu'à ce que les fausses alertes cessent laisse aussi passer les vraies. La
# liste a déjà été élargie une fois — version 2, pour cesser de crier sur des
# tableaux de rétractation qui disaient « erreur » sans dire « rétracté ». Le
# prix est réel et il est écrit dans le registre.

# Fichiers où un nombre rétracté est ATTENDU : le registre lui-même, et le
# journal de session. Les exclure évite un contrôle qui se signale lui-même.
IGNORE = re.compile(r"(^|/)(\.git|traces|__pycache__|node_modules)/|retractations\.json$")

EXTENSIONS = (".md", ".html", ".py", ".json", ".txt", ".js")


def exiger(condition, message):
    if not condition:
        sys.exit(message)


def fichiers(racine):
    for dossier, sous, noms in os.walk(racine):
        sous[:] = [d for d in sous if not IGNORE.search(os.path.join(dossier, d) + "/")]
        for nom in sorted(noms):
            chemin = os.path.join(dossier, nom)
            if nom.endswith(EXTENSIONS) and not IGNORE.search(chemin):
                yield chemin


def main():
    exiger(
        len(sys.argv) >= 4,
        "Usage : python3 outils/verifier-retractations.py <registre.json> "
        "<racine> <fenetre_lignes>",
    )
    registre = json.load(open(sys.argv[1], encoding="utf-8"))
    racine = sys.argv[2]
    fenetre = int(sys.argv[3])
    marqueurs = registre.get("marqueurs")
    exiger(
        marqueurs and marqueurs.get("termes"),
        "Le registre ne porte pas de liste de marqueurs versionnée.\n"
        "Sans elle, le compte produit n'est pas interprétable : « 0 nue » ne "
        "distingue pas un dépôt propre d'une liste élargie.",
    )
    MARQUES = re.compile("|".join(marqueurs["termes"]), re.IGNORECASE)

    trouvailles = []
    saines = 0
    for chemin in fichiers(racine):
        try:
            lignes = open(chemin, encoding="utf-8", errors="replace").read().split("\n")
        except OSError:
            continue
        for entree in registre["retractations"]:
            for valeur in entree["valeurs"]:
                for i, ligne in enumerate(lignes):
                    if valeur not in ligne:
                        continue
                    voisinage = "\n".join(
                        lignes[max(0, i - fenetre) : i + fenetre + 1]
                    )
                    if MARQUES.search(voisinage):
                        saines += 1
                    else:
                        trouvailles.append(
                            {
                                "fichier": os.path.relpath(chemin, racine),
                                "ligne": i + 1,
                                "valeur": valeur,
                                "id": entree["id"],
                                "motif": entree["motif"][:110],
                                "extrait": " ".join(ligne.split())[:130],
                            }
                        )

    # Le compte ne se cite jamais seul : la version de la liste l'accompagne.
    print(f"marqueurs : version {marqueurs['version']}, "
          f"{len(marqueurs['termes'])} termes, modifiée le {marqueurs['modifie_le']}")
    print(f"valeurs rétractées au registre : "
          f"{sum(len(e['valeurs']) for e in registre['retractations'])}"
          f"  ({len(registre['retractations'])} rétractations)")
    print(f"occurrences accompagnées de leur marque : {saines}")
    print(f"occurrences NUES : {len(trouvailles)}\n")

    for t in trouvailles:
        print(f"  {t['fichier']}:{t['ligne']}  « {t['valeur']} »  [{t['id']}]")
        print(f"      {t['extrait']}")
        print(f"      motif : {t['motif']}\n")

    if trouvailles:
        sys.exit(
            f"{len(trouvailles)} occurrence(s) d'un nombre rétracté sans sa marque.\n"
            "Chacune est un nombre mort qui respire encore : il reviendra avec ses "
            "papiers en règle."
        )
    print(f"Aucun nombre mort ne respire — sous la liste de marqueurs "
          f"version {marqueurs['version']}.")


if __name__ == "__main__":
    main()
