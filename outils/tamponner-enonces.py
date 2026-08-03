#!/usr/bin/env python3
"""Pose la date de dernière vérification sur la page des énoncés.

    Le contrôle du dépôt est administré par la partie qu'il contraint.

Un échec en intégration continue se fait taire en désactivant le workflow, et
une absence de contrôle n'émet aucun signal — c'est le mode de défaillance que
tout ce dépôt traque, appliqué à l'outil qui le traque.

Le remède est celui des empreintes d'entrée : **déplacer le témoin hors du
dépôt.** Cette date est visible par un lecteur qui n'a accès ni à la CI ni au
dépôt. Si elle est ancienne, il le voit sans avoir à savoir qu'un workflow
existe.

**Elle ne rend pas le contrôle inviolable. Elle rend son silence audible.** Et
c'est tout ce qu'un dispositif auto-administré peut offrir ; au-delà, ce n'est
plus une question de mécanisme.

Usage :
    python3 outils/tamponner-enonces.py <page.md> <AAAA-MM-JJ>

La date est un paramètre, jamais une lecture d'horloge : un tampon qui dépend de
l'heure à laquelle on le pose n'est pas rejouable.
"""
import re, sys
from datetime import date

def main():
    if len(sys.argv) < 3:
        sys.exit("Usage : python3 outils/tamponner-enonces.py <page.md> <AAAA-MM-JJ>")
    chemin, jour = sys.argv[1], sys.argv[2]
    date.fromisoformat(jour)          # échoue bruyamment sur une date malformée
    s = open(chemin, encoding="utf-8").read()
    neuf, n = re.subn(r"> \*\*Vérifié le \d{4}-\d{2}-\d{2}\.\*\*",
                      f"> **Vérifié le {jour}.**", s)
    if n != 1:
        sys.exit(f"Horodatage introuvable ou multiple ({n}) dans {chemin}.\n"
                 "Le témoin externe doit exister et être unique.")
    if neuf != s:
        open(chemin, "w", encoding="utf-8").write(neuf)
        print(f"{chemin} : tamponné au {jour}")
    else:
        print(f"{chemin} : déjà au {jour}")

if __name__ == "__main__":
    main()
