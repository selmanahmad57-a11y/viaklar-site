#!/usr/bin/env python3
"""Constitue le dossier de classification, dépouillé de toute identité.

Le §« sites inclassables » exige que la classification se fasse sur la
documentation seule, **sans coordonnées, sans grappe, sans rang de visite, sans
date** — pour que le classificateur, même s'il est le conducteur, ne puisse pas
savoir ce que chaque verdict fait au chiffre.

    Mais les photographies portent leurs coordonnées GPS et leur horodatage en
    EXIF. Un dossier dépouillé les réintroduirait par la porte de derrière.

Et une instruction écrite — « penser à retirer l'EXIF » — est la classe de
garde-fou qui échoue : elle dépend qu'on y pense, le jour où l'on est pressé.
D'où cet outil, qui **retire puis VÉRIFIE**, et refuse de produire un dossier
dont une pièce porte encore des métadonnées.

Quatre canaux de réidentification, tous traités :

  EXIF          segments APPn et COM du JPEG, morceaux auxiliaires du PNG
  nom de fichier  IMG_20260814_143022.jpg dit la date et l'heure
  date du fichier  mtime et atime
  ordre du lot    l'ordre de visite est l'ordre géographique

Aucune dépendance externe : ni exiftool, ni ImageMagick, ni Pillow — aucun n'est
présent sur cette machine, et un outil qui ne tourne pas est un outil absent.

Usage :
    python3 outils/constituer-dossier.py <source> <dossier> <sceau.json> <graine>
"""

import hashlib
import json
import os
import random
import shutil
import sys

# Segments JPEG à retirer : APP0 à APP15 (0xFFE0–0xFFEF) et COM (0xFFFE).
# EXIF vit dans APP1, mais APP13 porte de l'IPTC et APP2 de l'ICC qui peut
# contenir un nom d'appareil. On retire toute la famille : rien de ce qu'elle
# contient n'est nécessaire à l'affichage.
APP_MIN, APP_MAX, COM = 0xE0, 0xEF, 0xFE
SANS_LONGUEUR = {0xD8, 0xD9} | set(range(0xD0, 0xD8))  # SOI, EOI, RSTn
DATE_FIGEE = 946_684_800  # 2000-01-01T00:00:00Z — une date, la même pour tous


def exiger(condition, message):
    if not condition:
        sys.exit(message)


def depouiller_jpeg(brut):
    """Retire tous les segments APPn et COM. Conserve l'image."""
    exiger(brut[:2] == b"\xff\xd8", "Ce n'est pas un JPEG (pas de SOI).")
    sortie = bytearray(b"\xff\xd8")
    i, retires = 2, 0
    while i < len(brut):
        if brut[i] != 0xFF:
            sortie.extend(brut[i:])          # données brutes après SOS
            break
        marqueur = brut[i + 1]
        if marqueur == 0xDA:                  # SOS : le reste est l'image
            sortie.extend(brut[i:])
            break
        if marqueur in SANS_LONGUEUR:
            sortie.extend(brut[i : i + 2])
            i += 2
            continue
        longueur = int.from_bytes(brut[i + 2 : i + 4], "big")
        if APP_MIN <= marqueur <= APP_MAX or marqueur == COM:
            retires += 1
        else:
            sortie.extend(brut[i : i + 2 + longueur])
        i += 2 + longueur
    return bytes(sortie), retires


def depouiller_png(brut):
    """Ne conserve que les morceaux critiques et la transparence."""
    exiger(brut[:8] == b"\x89PNG\r\n\x1a\n", "Ce n'est pas un PNG.")
    garder = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS"}
    sortie, i, retires = bytearray(brut[:8]), 8, 0
    while i < len(brut):
        longueur = int.from_bytes(brut[i : i + 4], "big")
        type_ = brut[i + 4 : i + 8]
        bloc = brut[i : i + 12 + longueur]
        if type_ in garder:
            sortie.extend(bloc)
        else:
            retires += 1
        i += 12 + longueur
    return bytes(sortie), retires


# Motifs dont la présence dans le fichier dépouillé signale un échec. Le
# contrôle est fait APRÈS, sur l'octet : une fonction qui prétend avoir retiré
# n'est pas une preuve qu'elle a retiré.
TEMOINS = (b"Exif", b"GPS", b"http://ns.adobe.com/xap", b"<x:xmpmeta", b"ICC_PROFILE")


def verifier(donnees):
    return [t.decode("latin-1") for t in TEMOINS if t in donnees]


def main():
    exiger(
        len(sys.argv) >= 5,
        "Usage : python3 outils/constituer-dossier.py <source> <dossier> "
        "<sceau.json> <graine>",
    )
    source, cible, sceau, graine = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    exiger(os.path.isdir(source), f"Source introuvable : {source}")
    os.makedirs(cible, exist_ok=True)

    pieces = sorted(
        f for f in os.listdir(source)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    exiger(pieces, f"Aucune photographie dans {source}")

    # L'ordre du lot est un canal : l'ordre de visite est l'ordre géographique.
    alea = random.Random(graine)
    alea.shuffle(pieces)

    correspondance, echecs = [], []
    for rang, nom in enumerate(pieces, start=1):
        brut = open(os.path.join(source, nom), "rb").read()
        if nom.lower().endswith(".png"):
            propre, retires = depouiller_png(brut)
            ext = ".png"
        else:
            propre, retires = depouiller_jpeg(brut)
            ext = ".jpg"

        restants = verifier(propre)
        if restants:
            echecs.append((nom, restants))
            continue

        # Nom opaque : IMG_20260814_143022.jpg dit la date et l'heure.
        opaque = f"piece-{rang:03d}{ext}"
        chemin = os.path.join(cible, opaque)
        open(chemin, "wb").write(propre)
        os.utime(chemin, (DATE_FIGEE, DATE_FIGEE))  # mtime et atime aussi

        correspondance.append({
            "piece": opaque,
            "origine": nom,
            "octets_avant": len(brut),
            "octets_apres": len(propre),
            "segments_retires": retires,
            "sha256": hashlib.sha256(propre).hexdigest(),
        })

    if echecs:
        for nom, restants in echecs:
            print(f"  ÉCHEC  {nom} : {', '.join(restants)} subsiste(nt)")
        sys.exit(
            f"\n{len(echecs)} pièce(s) portent encore des métadonnées après "
            "dépouillement.\nLe dossier n'est PAS constitué : une seule pièce "
            "identifiante suffit à rompre l'aveuglement du classificateur."
        )

    with open(sceau, "w", encoding="utf-8") as f:
        json.dump(
            {
                "pourquoi": "Correspondance piece -> photographie d'origine. SCELLÉ : "
                "à n'ouvrir qu'APRÈS classification. L'ouvrir avant rend le "
                "dépouillement inutile.",
                "graine_du_melange": graine,
                "date_figee": DATE_FIGEE,
                "canaux_traites": ["EXIF et segments APPn/COM", "nom de fichier",
                                   "date du fichier", "ordre du lot"],
                "correspondance": correspondance,
            },
            f, ensure_ascii=False, indent=1,
        )

    total = sum(c["segments_retires"] for c in correspondance)
    print(f"pièces dépouillées : {len(correspondance)}")
    print(f"segments retirés   : {total}")
    print(f"contrôle après coup: aucun témoin ({', '.join(t.decode() for t in TEMOINS[:3])}…)")
    print(f"dossier            : {cible}")
    print(f"sceau              : {sceau}  — à n'ouvrir qu'après classification")


if __name__ == "__main__":
    main()
