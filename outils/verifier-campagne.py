#!/usr/bin/env python3
"""Une date qui passe sans rien publier est un souhait.

Ce contrôle donne un coût à la date : si une étape est en retard et que l'état
n'a pas été mis à jour, il échoue — donc l'intégration continue passe au rouge,
donc quelqu'un doit soit consigner l'avancement, soit consigner l'incomplétude.

    L'incomplétude devient publiable, et c'est ce qui fait tenir le calendrier.

C'est la contre-mesure du §4.bis — publier une baisse avec la même visibilité
qu'une hausse — appliquée au temps plutôt qu'au chiffre.

Usage :
    python3 outils/verifier-campagne.py <campagne.json> <aujourdhui AAAA-MM-JJ>

La date du jour est un PARAMÈTRE, pas une lecture d'horloge : un contrôle qui
dépend de l'heure à laquelle on le lance n'est pas rejouable.
"""
import json, sys
from datetime import date

def exiger(c, m):
    if not c: sys.exit(m)

def main():
    exiger(len(sys.argv) >= 3,
           "Usage : python3 outils/verifier-campagne.py <campagne.json> <AAAA-MM-JJ>")
    etat = json.load(open(sys.argv[1], encoding="utf-8"))
    jour = date.fromisoformat(sys.argv[2])

    visites = sum(e["visites"] for e in etat["etapes"])
    defaillances = sum(e["defaillances"] for e in etat["etapes"])
    absents = 0.75 * visites
    borne = 3 / absents if absents else None

    print(f"au {jour} — {visites} site(s) visité(s), {defaillances} défaillance(s)")
    print(f"borne sur p_absent : "
          f"{f'{borne:.1%}' if borne and borne < 1 else 'aucune'}"
          f"   portée : {'NATIONALE' if visites >= 20 else 'conditionnelle à la portion parcourue'}")

    if defaillances >= 2:
        print("\n  ⚠ DEUX DÉFAILLANCES OU PLUS — le protocole impose l'ARRÊT.")
        print("    L'échantillon devient une estimation et il est trop petit pour ça.")

    retard = [e for e in etat["etapes"]
              if not e["fait"] and date.fromisoformat(e["avant_le"]) < jour]
    print()
    for e in etat["etapes"]:
        d = date.fromisoformat(e["avant_le"])
        marque = "fait" if e["fait"] else ("EN RETARD" if d < jour else f"d-{(d-jour).days}")
        print(f"  {e['libelle']:34s} {e['sites']:>2} sites  {e['avant_le']}  {marque}")

    if retard:
        sys.exit(
            f"\n{len(retard)} étape(s) en retard.\n\n"
            "  À PUBLIER, avec la même visibilité que le chiffre :\n"
            "  « Campagne de vérification terrain incomplète au "
            f"{jour} — {visites} site(s) sur 20. La borne est conditionnelle à la\n"
            "    portion parcourue et n'est pas nationale. »\n\n"
            "  Ou mettre l'état à jour dans docs/campagne-terrain.json.\n"
            "  Une date sans conséquence est un souhait ; celle-ci en a une."
        )
    print("\nCalendrier tenu.")

if __name__ == "__main__":
    main()
