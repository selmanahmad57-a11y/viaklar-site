#!/usr/bin/env python3
"""Archive la trace brute d'une campagne, et en commet le manifeste.

    Le schéma enregistre ce qu'on savait vouloir.
    La trace enregistre ce qu'on ne savait pas encore devoir demander.

Ce sont deux besoins opposés, et le second ne se satisfait pas en élargissant le
premier : on ne peut pas prévoir dans un champ la question qu'on se posera dans
trois jours. Un schéma exhaustif reste un schéma — il ne contient que les
colonnes que quelqu'un a imaginées.

D'où la décision, symétrique de celle du rapport machine mais pour la raison
INVERSE. Le rapport est obligatoire parce qu'il est structuré et qu'un
enregistrement facultatif manque le jour où il compte. **La trace est conservée
précisément parce qu'elle n'est PAS structurée**, donc qu'elle survit à
l'évolution des questions.

Deux fois en deux jours, la trace brute a tranché une question que le schéma ne
pouvait pas trancher :

  - le 2 août, une sortie de tâche vide et un journal d'exécution ont dit ce
    qu'un rapport absent ne disait pas : les agents avaient été interrompus, et
    ce qu'ils avaient rendu avant de mourir ;
  - le 3 août, l'appariement des 225 appels d'outil à leurs sorties a réfuté le
    soupçon que des vérificateurs aient répondu sans avoir pu interroger OSM.
    Le champ prévu comptait les échecs PAR LOT ; la trace les rattachait aux
    points.

Une fois est une chance. Deux fois est une propriété.

Usage :
    python3 outils/archiver-trace.py <repertoire_source> <nom_campagne> \\
            <repertoire_archives> <manifeste.json>

Le volume compressé reste modeste — 2,4 Mo pour toutes les campagnes du 3 août —
et le manifeste, lui, est versionné : si l'archive disparaît, son absence se
voit au lieu de passer inaperçue.
"""

import gzip
import hashlib
import json
import os
import shutil
import sys


def exiger(condition, message):
    if not condition:
        sys.exit(message)


def empreinte(chemin):
    haché = hashlib.sha256()
    with open(chemin, "rb") as entree:
        for bloc in iter(lambda: entree.read(1 << 20), b""):
            haché.update(bloc)
    return haché.hexdigest()


def ecrire_atomique(chemin, contenu):
    temporaire = chemin + ".tmp"
    with open(temporaire, "w", encoding="utf-8") as sortie:
        json.dump(contenu, sortie, ensure_ascii=False, indent=1, sort_keys=True)
        sortie.flush()
        os.fsync(sortie.fileno())
    os.replace(temporaire, chemin)


def main():
    exiger(
        len(sys.argv) >= 5,
        "Usage : python3 outils/archiver-trace.py <repertoire_source> "
        "<nom_campagne> <repertoire_archives> <manifeste.json>\n"
        "Le répertoire source est celui des transcriptions brutes ; il n'est "
        "pas deviné, parce qu'il dépend de l'outillage et non du projet.",
    )
    source, campagne, archives, manifeste = sys.argv[1:5]
    exiger(os.path.isdir(source), f"Répertoire source introuvable : {source}")
    os.makedirs(archives, exist_ok=True)

    fichiers = []
    for racine, _, noms in os.walk(source):
        for nom in sorted(noms):
            chemin = os.path.join(racine, nom)
            fichiers.append((os.path.relpath(chemin, source), chemin))
    exiger(fichiers, f"Aucun fichier à archiver dans {source}")

    entrees = []
    octets_bruts = 0
    for relatif, chemin in sorted(fichiers):
        destination = os.path.join(archives, campagne, relatif + ".gz")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        # Compression vers un temporaire puis renommage : une archive tronquée
        # est pire qu'une archive absente, parce qu'elle a l'air d'exister.
        temporaire = destination + ".tmp"
        with open(chemin, "rb") as entree, gzip.open(temporaire, "wb", 9) as sortie:
            shutil.copyfileobj(entree, sortie)
        os.replace(temporaire, destination)
        taille = os.path.getsize(chemin)
        octets_bruts += taille
        entrees.append(
            {
                "fichier": relatif,
                "octets": taille,
                "octets_compresses": os.path.getsize(destination),
                "sha256_source": empreinte(chemin),
                "sha256_archive": empreinte(destination),
            }
        )

    contenu = {
        "campagne": campagne,
        "source": os.path.abspath(source),
        "archives": os.path.abspath(os.path.join(archives, campagne)),
        "fichiers": len(entrees),
        "octets_bruts": octets_bruts,
        "octets_compresses": sum(e["octets_compresses"] for e in entrees),
        "pourquoi": "la trace brute enregistre ce qu'on ne savait pas encore "
        "devoir demander ; le schéma n'enregistre que ce qu'on savait vouloir",
        "entrees": entrees,
    }
    ecrire_atomique(manifeste, contenu)

    print(f"campagne            : {campagne}")
    print(f"fichiers archivés   : {len(entrees)}")
    print(f"volume brut         : {octets_bruts/1048576:.1f} Mo")
    print(f"volume compressé    : {contenu['octets_compresses']/1048576:.1f} Mo")
    print(f"archives            : {contenu['archives']}")
    print(f"manifeste           : {manifeste}")
    print("\nle manifeste est versionné, l'archive non : si elle disparaît,")
    print("son absence se voit au lieu de passer inaperçue.")


if __name__ == "__main__":
    main()
