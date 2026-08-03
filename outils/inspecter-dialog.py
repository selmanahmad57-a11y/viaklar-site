#!/usr/bin/env python3
"""Inspection du flux DiaLog (DATEX II v3) — outil de mesure, pas code produit.

Répond aux questions du §5 et du §15.4 du ROADMAP :
  - combien d'arrêtés, de quelles collectivités ?
  - portent-ils des géométries, ou seulement des noms de rue ?
  - combien concernent le gabarit, et lequel ?

Le flux vit : rejouer cette mesure plutôt que de citer des chiffres datés.

Usage :
    python3 outils/inspecter-dialog.py <url-ou-fichier>
    DIALOG_URL=... python3 outils/inspecter-dialog.py

Aucune URL par défaut n'est codée en dur : une source absente doit faire
échouer la commande avec un message explicite, jamais être devinée.
"""

import collections
import json
import os
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

NS_TR = "{http://datex2.eu/schema/3/trafficRegulation}"
NS_COM = "{http://datex2.eu/schema/3/common}"
NS_DX = "{https://raw.githubusercontent.com/MTES-MCT/dialog/main/docs/spec/datex2}"

ORDER = NS_TR + "trafficRegulationOrder"
AUTHORITY = NS_TR + "issuingAuthority"
VALUE = NS_COM + "value"
VEHICLE_TYPE = NS_COM + "vehicleType"
GEOMETRY = NS_DX + "geoJsonGeometry"

# Balises DATEX II portant une contrainte de gabarit, par nature.
GABARIT = {
    "poids": "grossWeightCharacteristic",
    "hauteur": "heightCharacteristic",
    "largeur": "widthCharacteristic",
    "longueur": "lengthCharacteristic",
}

TOP = 15


def source_depuis_environnement():
    """URL ou chemin du flux. Échoue bruyamment si rien n'est fourni."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    depuis_env = os.environ.get("DIALOG_URL")
    if depuis_env:
        return depuis_env
    sys.exit(
        "Aucune source fournie.\n"
        "  python3 outils/inspecter-dialog.py <url-ou-fichier>\n"
        "  ou DIALOG_URL=<url> python3 outils/inspecter-dialog.py\n"
        "L'URL du flux DiaLog est publiée sur data.gouv.fr, jeu de données\n"
        "« Base de données nationale de la réglementation de circulation »."
    )


def recuperer(source):
    """Retourne un chemin local, en téléchargeant si la source est distante."""
    if not source.startswith(("http://", "https://")):
        return source, False
    fd, chemin = tempfile.mkstemp(suffix=".xml", prefix="dialog-")
    os.close(fd)
    print(f"Téléchargement de {source} …", file=sys.stderr)
    urllib.request.urlretrieve(source, chemin)
    return chemin, True


def inspecter(chemin):
    total = 0
    avec_geometrie = 0
    avec_roadname = 0
    avec_gabarit = 0
    types_geometrie = collections.Counter()
    par_gabarit = collections.Counter()
    collectivites = collections.Counter()
    collectivites_gabarit = collections.Counter()
    types_vehicule = collections.Counter()

    for _, element in ET.iterparse(chemin, events=("end",)):
        if element.tag != ORDER:
            continue

        total += 1
        brut = ET.tostring(element, encoding="unicode")

        geometries = list(element.iter(GEOMETRY))
        if geometries:
            avec_geometrie += 1
        for geometrie in geometries:
            try:
                types_geometrie[json.loads(geometrie.text).get("type", "?")] += 1
            except (json.JSONDecodeError, TypeError):
                types_geometrie["illisible"] += 1

        if "roadName" in brut:
            avec_roadname += 1

        noms = [
            (valeur.text or "").strip()
            for autorite in element.iter(AUTHORITY)
            for valeur in autorite.iter(VALUE)
        ]
        for nom in noms:
            collectivites[nom] += 1

        touche = False
        for nature, balise in GABARIT.items():
            if balise in brut:
                par_gabarit[nature] += 1
                touche = True
        if touche:
            avec_gabarit += 1
            for nom in noms:
                collectivites_gabarit[nom] += 1

        for vehicule in element.iter(VEHICLE_TYPE):
            types_vehicule[(vehicule.text or "").strip()] += 1

        element.clear()

    return {
        "total": total,
        "avec_geometrie": avec_geometrie,
        "avec_roadname": avec_roadname,
        "avec_gabarit": avec_gabarit,
        "types_geometrie": types_geometrie,
        "par_gabarit": par_gabarit,
        "collectivites": collectivites,
        "collectivites_gabarit": collectivites_gabarit,
        "types_vehicule": types_vehicule,
    }


def pourcentage(part, total):
    return f"{100 * part / total:.1f} %" if total else "n/a"


def restituer(r):
    total = r["total"]
    print(f"\narrêtés (trafficRegulationOrder)  : {total}")
    print(
        f"  avec géométrie GeoJSON          : {r['avec_geometrie']}"
        f"  ({pourcentage(r['avec_geometrie'], total)})"
    )
    print(f"  mentionnant un roadName         : {r['avec_roadname']}")
    print(f"  collectivités distinctes        : {len(r['collectivites'])}")

    print(f"\ntypes de géométrie : {dict(r['types_geometrie'])}")

    print(
        f"\narrêtés portant une restriction de gabarit : {r['avec_gabarit']}"
        f"  ({pourcentage(r['avec_gabarit'], total)})"
    )
    for nature, nombre in r["par_gabarit"].most_common():
        print(f"   {nature:9s} : {nombre}")

    print("\ntypes de véhicule visés :")
    for nom, nombre in r["types_vehicule"].most_common(10):
        print(f"   {nombre:6d}  {nom}")

    print(f"\ncollectivités portant du gabarit : {len(r['collectivites_gabarit'])}")
    for nom, nombre in r["collectivites_gabarit"].most_common(TOP):
        print(f"   {nombre:6d}  {nom}")


def main():
    source = source_depuis_environnement()
    chemin, temporaire = recuperer(source)
    try:
        restituer(inspecter(chemin))
    finally:
        if temporaire:
            os.unlink(chemin)


if __name__ == "__main__":
    main()
