/* Le verdict rendu à un conducteur, sur UNE règle qui le concerne ici.
 *
 *     evaluer(regle, vehicule, entreprise, trajet, instant, config)  -> constat
 *     evaluerToutes(regles, vehicule, entreprise, trajet, instant, config) -> verdict
 *
 * PORT DE outils/evaluateur.py. Même sémantique, même vocabulaire, même
 * configuration — config/registre.json §evaluateur, passée en argument.
 *
 * POURQUOI DANS LE NAVIGATEUR. Colorier la carte exige d'évaluer TOUTES les
 * règles visibles pour CE véhicule à CET instant. Le véhicule et l'instant sont
 * dans la main du conducteur : aucun cache serveur ne peut porter ce produit
 * cartésien, donc l'évaluation doit tourner chez lui. Un service statique — un
 * dossier de fichiers, pas de processus — suffit alors à faire tourner le
 * copilote sur un téléphone.
 *
 * AUTOSUFFISANTE. La règle arrive HYDRATÉE : ses `criteres`, ses `exemptions`,
 * ses `periodes`, ses `etats` et son identité. Cette fonction n'ouvre rien, ne
 * demande rien à personne, et ne fait AUCUNE géométrie : l'appelant a déjà
 * sélectionné spatialement. C'est ce que outils/conformite.py exige et qui
 * échoue tant que la sélection rend des règles creuses.
 *
 * PURE. Aucun état entre deux appels, aucune horloge lue, aucune écriture. Deux
 * appels identiques rendent le même verdict — c'est ce qui rend une trace
 * reproductible le jour où un conducteur conteste ce que l'app lui a dit.
 *
 * CINQ VERDICTS, ET L'INCERTITUDE CHANGE DE SIÈGE À CHAQUE FOIS
 *
 *     interdit                    l'incertitude ne siège nulle part
 *     aucune_restriction_connue   PAS « autorisé » : dire autorisé exigerait de
 *                                 savoir que la couverture existe ici, ce qui
 *                                 n'est jamais établi
 *     indetermine                 elle siège dans NOTRE donnée, ou dans NOTRE
 *                                 logiciel quand une règle a été écartée
 *     autorise_sous_declaration   elle siège dans LE CONDUCTEUR — un fait du
 *                                 monde qu'il affirme, vérifiable par inspection
 *     autorise_sur_titre          elle siège dans un ACTE ADMINISTRATIF qu'il
 *                                 détient, vérifiable par présentation du papier
 *
 * TROIS PORTEURS, ET LES CONFONDRE CASSE LE MODÈLE. Le véhicule se MESURE et ne
 * bouge pas ; l'entreprise porte une habilitation permanente et déclarative ; le
 * trajet change à chaque étape. Le même camion frigorifique est exempté le matin
 * et ne l'est plus l'après-midi à vide. C'est pourquoi la signature les prend
 * SÉPARÉMENT au lieu d'un « profil » : trois arguments ne se confondent pas.
 *
 * Chargement : module ES, aucune dépendance, aucun bundler.
 *     import { evaluer, evaluerToutes } from "./evaluateur.js";
 */

// CONTRAINTE: `evaluer` et `evaluerToutes` sont PURES : aucun état conservé, aucun réseau,
//   aucune écriture, aucune horloge lue. Deux appels identiques rendent le même verdict.
// CONTRAINTE: aucune valeur du domaine n'est écrite ici. Seuils, unités, sens des
//   opérateurs, porteurs, vocabulaires, mots du verdict viennent de `config` §evaluateur,
//   et une clé absente LÈVE EN LA NOMMANT — aucun repli silencieux sur une valeur plausible.
// CONTRAINTE: un axe indéterminé se propage au verdict SI ET SEULEMENT S'IL PORTE ; il ne
//   se comble jamais par une valeur plausible.
// CONTRAINTE: aucun verdict permissif n'est rendu là où une règle a été écartée —
//   `ecartees` non vide impose `indetermine` au verdict d'ensemble.
// CONTRAINTE: MIROIR de la précédente, écrit parce qu'une contrainte à une seule direction
//   abrite son défaut dans l'autre — aucun verdict RESTRICTIF n'est rendu du seul fait
//   d'une incertitude : une sortie définitive « ne vise pas ce véhicule » prime sur tout
//   axe inconnu.
// CONTRAINTE: `autorise_sous_declaration` n'est jamais émis avant que le conducteur ait
//   déclaré. Tant qu'il n'a rien dit, la règle mord ET le verdict porte la liste des
//   déclarations qui la lèveraient.
// CONTRAINTE: ce fichier est un PORT de outils/evaluateur.py. Toute divergence sémantique
//   est un défaut, pas une amélioration. Les écarts assumés sont listés sous « PORTAGE »
//   ci-dessous, et aucun d'eux ne change un verdict.

/* ── PORTAGE : les écarts assumés avec outils/evaluateur.py ───────────────────
 *
 * Ils sont ÉCRITS parce que deux implémentations de la même règle qui divergent
 * sans que rien ne le signale est le défaut que ce projet a payé le plus cher.
 * Un écart tu serait ce défaut ; un écart écrit est un fait vérifiable.
 *
 * 1. L'INSTANT. Python exige un `datetime` porteur d'un fuseau et échoue sur un
 *    instant naïf. Ici : un `Date` (qui EST un instant absolu, donc aware) ou
 *    une chaîne ISO 8601 portant explicitement son décalage. Une chaîne SANS
 *    décalage est exactement le cas naïf — `new Date("2026-08-04T09:30")` la
 *    lirait dans le fuseau de la machine, ce qui est le nombre déguisé en
 *    instant que §validite.instant_naif refuse. Elle échoue.
 *
 * 2. UN ENREGISTREMENT INCOMPLET lève RegistreIncompatible EN NOMMANT le champ,
 *    là où Python lève un KeyError nu. Le comportement — refuser de rendre un
 *    verdict — est le même ; seul le nom de la faute est meilleur.
 *
 * 3. UN VERDICT HORS §ordre_de_gravite lève ConfigurationIncomplete en le
 *    nommant, là où `list.index` de Python lève un ValueError nu. Ce chemin est
 *    ATTEIGNABLE par la configuration du 4 août 2026 : §porteurs.vehicule et
 *    §porteurs.calcul portent `verdict_si_leve = "autorise"`, mot qui n'est PAS
 *    dans §ordre_de_gravite.du_plus_grave_au_moins_grave. Les deux
 *    implémentations refusent donc de rendre un verdict au même endroit, sur la
 *    même donnée — c'est une lacune de la configuration, pas du portage, et
 *    aucune des deux ne la comble.
 *
 * 4. LES NOMS D'AXES. Python écrit `regle["etats"]["spatial"]` et
 *    `regle["etats"]["temporel"]` en clair. Ici ils sont LUS dans
 *    §propagation_des_axes.ordre_d_examen, et une garde échoue si cette liste
 *    cesse d'être celle que ce code implémente — même idiome que la garde de
 *    §combinaison_des_criteres qui existe déjà dans la référence.
 *
 * 5. `null` SE REND « None » dans les gabarits de message, comme `str(None)` en
 *    Python. Un seul gabarit peut l'atteindre — `leve_par_titre`, sur une levée
 *    sans référence ni autorité — et aucune règle de type levée n'existe dans le
 *    registre au 4 août 2026. Rendre `""` à la place serait plus joli et
 *    produirait deux textes différents pour la même donnée.
 *
 * 6. LES PHRASES CONSTRUITES EN CODE. La référence assemble deux phrases hors
 *    §messages — « … au-dessus du maximum de … » et « classe … » — ainsi que le
 *    résumé d'une plage. Elles sont portées MOT POUR MOT, y compris le tiret
 *    demi-cadratin du résumé. Les remettre en configuration est un travail sur
 *    la référence, pas sur le port : le faire ici seul créerait la divergence.
 *
 * ── ce que ce fichier NE FAIT PAS, et c'est délibéré ─────────────────────────
 *
 *   - il ne comble AUCUN axe indéterminé par une valeur plausible : 353 règles
 *     portent `etat_temporel=indetermine`, et il répond « restriction avec plage
 *     horaire non évaluable » ;
 *
 *   - mais il ne propage un axe indéterminé QUE S'IL PORTE. Un utilitaire de 3 t
 *     est hors du champ d'une interdiction aux plus de 7,5 t, que l'heure soit
 *     connue ou non. Sur-restreindre n'est pas prudent, et sur-douter non plus :
 *     c'est la même défaillance par le canal de l'attention ;
 *
 *   - il ÉCARTE les 448 règles à `etat_vehicule=indetermine` — le flux dit
 *     « interdit à tous » là où l'intitulé dit SENS UNIQUE ou Piétonisation. La
 *     mesure les compte, l'évaluateur non : les livrer fermerait des voies
 *     franchissables. Et une règle écartée n'est PAS une règle absente : c'est
 *     une règle que NOTRE logiciel n'a pas su traiter, donc le verdict
 *     d'ensemble devient `indetermine` ;
 *
 *   - il n'applique JAMAIS une levée automatiquement. Une levée retire de la
 *     prudence, donc l'asymétrie de l'arbitre s'applique : tous ses axes doivent
 *     être déterminés et elle doit DÉSIGNER les interdictions qu'elle lève.
 */

/* ── échecs nommés ───────────────────────────────────────────────────────────
 *
 * Ils LÈVENT et ils portent la clé. Une page qui replierait silencieusement sur
 * une valeur plausible peindrait la carte en vert sur une donnée qu'elle n'a
 * pas — c'est précisément ce que les quatre axes d'état existent pour empêcher.
 */

export class ConfigurationIncomplete extends Error {
  constructor(message) {
    super(message);
    this.name = "ConfigurationIncomplete";
  }
}

export class ProfilIncomplet extends Error {
  constructor(message) {
    super(message);
    this.name = "ProfilIncomplet";
  }
}

export class RegistreIncompatible extends Error {
  constructor(message) {
    super(message);
    this.name = "RegistreIncompatible";
  }
}

function _estDict(valeur) {
  return typeof valeur === "object" && valeur !== null && !Array.isArray(valeur);
}

function _possede(objet, nom) {
  // hasOwnProperty et non `in` : une clé de donnée qui s'appellerait
  // « constructor » ou « toString » trouverait sinon une valeur du prototype,
  // et un vocabulaire du registre devient une clé de configuration.
  return _estDict(objet) && Object.prototype.hasOwnProperty.call(objet, nom);
}

/** Lit une clé de configuration, ou échoue EN LA NOMMANT. */
export function cle(config, ...chemin) {
  let courant = config;
  const parcouru = [];
  for (const morceau of chemin) {
    parcouru.push(morceau);
    if (!_possede(courant, morceau)) {
      throw new ConfigurationIncomplete(
        "Configuration incomplète : la clé « " +
          parcouru.join(".") +
          " » est absente.\nAucune valeur par défaut n'est fournie : " +
          "cette valeur est une décision."
      );
    }
    courant = courant[morceau];
  }
  return courant;
}

/** Lit un champ d'un ENREGISTREMENT du registre, ou échoue en le nommant. */
function _champ(regle, nom) {
  if (!_possede(regle, nom)) {
    throw new RegistreIncompatible(
      "Enregistrement que l'évaluateur ne sait pas lire : le champ « " +
        nom +
        " » est absent. Une règle arrive HYDRATÉE ou elle n'est pas évaluable."
    );
  }
  return regle[nom];
}

function _optionnel(regle, nom) {
  return _possede(regle, nom) ? regle[nom] : null;
}

/* ── les deux fonctions publiques ────────────────────────────────────────────*/

/**
 * Ce qu'UNE règle hydratée dit de CE véhicule, pour CETTE entreprise, sur CE
 * trajet, à CET instant.
 *
 * Rend un constat : l'identité de la règle, son `verdict`, et le `pourquoi` qui
 * dit QUI a établi le fait. `verdict === null` signifie « cette règle ne
 * concerne pas ce véhicule ici et maintenant » — ce n'est pas une autorisation,
 * c'est une absence de propos, et `classement` dit laquelle.
 *
 *     classement = "retenue"     elle porte un verdict
 *                  "hors_champ"  elle ne vise pas ce véhicule / pas cette heure
 *                  "ecartee"     NOTRE logiciel n'a pas su la traiter (règle 3)
 *                  "information" elle n'influence pas le verdict
 *                  "levee"       elle ne se lit qu'EN COMPOSITION avec les
 *                                interdictions qu'elle désigne : une règle
 *                                seule ne peut pas se lever elle-même, donc
 *                                seul `evaluerToutes` la compose.
 */
export function evaluer(regle, vehicule, entreprise, trajet, instant, config) {
  const contexte = _contexte(config, vehicule, entreprise, trajet, instant);
  const { classement, constat } = _classer(regle, contexte);
  return {
    ...constat,
    verdict: _possede(constat, "verdict") ? constat.verdict : null,
    classement,
  };
}

/**
 * Le verdict d'ensemble sur les règles que l'appelant a sélectionnées ICI.
 *
 * Le verdict d'ensemble est le plus grave des constats, et chaque constat retenu
 * est rendu tel quel pour que l'écran puisse dire POURQUOI et pas seulement QUOI.
 *
 * Quatre listes distinctes plutôt qu'une seule : ranger « écartée par la règle
 * 3 » et « ne vise pas ce véhicule » au même endroit ferait disparaître la
 * différence entre une décision de produit et un fait du monde — et c'est cette
 * différence que l'on relit en litige.
 */
export function evaluerToutes(regles, vehicule, entreprise, trajet, instant, config) {
  const contexte = _contexte(config, vehicule, entreprise, trajet, instant);
  const { cfg, messages, gravite } = contexte;

  const retenues = [];
  const hors_champ = [];
  const ecartees = [];
  const informations = [];
  const levees = [];

  for (const regle of regles || []) {
    const { classement, constat } = _classer(regle, contexte);
    if (classement === "ecartee") ecartees.push(constat);
    else if (classement === "levee") levees.push(regle);
    else if (classement === "information") informations.push(constat);
    else if (classement === "hors_champ") hors_champ.push(constat);
    else retenues.push(constat);
  }

  _composer_levees(retenues, levees, contexte);

  let verdict = "aucune_restriction_connue";
  for (const constat of retenues) verdict = _plus_grave(verdict, constat.verdict, gravite);

  // UNE RÈGLE ÉCARTÉE N'EST PAS UNE RÈGLE ABSENTE : c'est une règle que NOTRE
  // LOGICIEL n'a pas su traiter. Même siège d'incertitude que « module absent →
  // indetermine → l'incertitude siège dans NOTRE logiciel, pas dans votre
  // véhicule ».
  //
  // Le cas qui l'a imposé : 3.27070, 49.81241 — aucune règle retenue, et un
  // arrêté « INTERDICTION DE CIRCULATION DANS LES DEUX SENS PAR MESURE DE
  // SÉCURITÉ » écarté sur ce point exact. Le verdict rendu était le plus
  // permissif du vocabulaire, et tout client l'aurait peint en vert.
  if (ecartees.length) verdict = _plus_grave(verdict, "indetermine", gravite);

  const tete = _tete(retenues, gravite);
  const declarations = [];
  for (const constat of retenues) {
    for (const attendue of constat.declarations_qui_leveraient || []) {
      if (!declarations.includes(attendue)) declarations.push(attendue);
    }
  }

  // « Aucune règle ne restreint ce véhicule » serait FAUX là où un arrêté existe
  // et que la règle 3 l'a écarté. Le dire autrement n'est pas une politesse :
  // c'est refuser d'affirmer une propriété que le code n'a pas.
  let raison;
  if (tete) raison = tete.pourquoi;
  else if (ecartees.length) {
    raison = _format(cle(messages, "autorise_avec_ecartees"), { nombre: ecartees.length });
  } else raison = cle(messages, "aucune_restriction_connue");

  return {
    verdict,
    pourquoi: raison,
    tete: tete || null,
    regles: retenues,
    hors_champ,
    ecartees,
    informations,
    [cle(cfg, "declaration", "champ_du_verdict")]: declarations,
  };
}

/* ── le contexte, établi une fois ────────────────────────────────────────────*/

function _contexte(config, vehicule, entreprise, trajet, instant) {
  const cfg = cle(config, "evaluateur");
  // Les trois noms de porteur sont ceux de la SIGNATURE — ils ne sont pas
  // devinés, ils sont les paramètres que l'appelant passe. §profil.porteurs_
  // obligatoires reste l'arbitre : un porteur qu'il exige et que la signature
  // n'offre pas échoue en le nommant, au lieu d'être lu comme vide.
  const profil = { vehicule, entreprise, trajet };
  _exiger_profil(profil, cfg);
  return {
    cfg,
    profil,
    messages: cle(cfg, "messages"),
    gravite: cle(cfg, "ordre_de_gravite", "du_plus_grave_au_moins_grave"),
    conduites: cle(cfg, "types_de_regle"),
    axes: _axes(cfg),
    ms: _exiger_instant(instant, cfg),
  };
}

function _classer(regle, contexte) {
  const { cfg, messages, conduites } = contexte;

  if (_est_ecartee(regle, cfg)) {
    return {
      classement: "ecartee",
      constat: { ..._carte(regle), pourquoi: _optionnel(regle, "pourquoi_indetermine") },
    };
  }

  const conduite = _conduite(regle, conduites);
  if (conduite === "compose") return { classement: "levee", constat: _carte(regle) };
  if (conduite === "n_influence_pas_le_verdict") {
    return { classement: "information", constat: _carte(regle) };
  }
  if (conduite === "indeterminer") {
    return {
      classement: "retenue",
      constat: {
        ..._carte(regle),
        verdict: "indetermine",
        pourquoi: cle(messages, "obligation_non_lue"),
      },
    };
  }
  // "restreint"
  const constat = _constater(regle, contexte);
  return { classement: constat.verdict === null ? "hors_champ" : "retenue", constat };
}

/* ── un constat, une règle ───────────────────────────────────────────────────*/

/**
 * LES SORTIES DÉFINITIVES PASSENT AVANT TOUTE INDÉTERMINATION. Un « ne vous vise
 * pas » établi prime sur un axe inconnu : c'est ce qui empêche les 353 règles à
 * plage indéterminée de teindre en gris les véhicules qu'elles ne visaient de
 * toute façon pas.
 */
function _constater(regle, contexte) {
  const { messages, axes } = contexte;
  const carte = _carte(regle);

  const [hors, pourquoiHors] = _hors_validite(regle, contexte);
  if (hors) return { ...carte, verdict: null, pourquoi: pourquoiHors };

  const [vise, causes_vehicule] = _examiner_criteres(regle, contexte);
  if (vise === "hors_champ") {
    return { ...carte, verdict: null, pourquoi: cle(messages, "hors_champ") };
  }

  const plage = _examiner_plages(regle, contexte);
  if (plage.etat === "hors_plage") return { ...carte, verdict: null, pourquoi: plage.pourquoi };

  const derogation = _examiner_exemptions(regle, contexte);
  if (derogation.joue) {
    const [verdict, raison] = derogation.joue;
    return { ...carte, verdict, pourquoi: raison };
  }

  // À partir d'ici la règle mord, ou l'on ne sait pas dire qu'elle ne mord pas.
  // L'ordre des indéterminations est celui de §propagation_des_axes : la cause
  // nommée au conducteur doit être la plus proche de ce qui manque.
  if (vise === "indetermine") {
    return { ...carte, verdict: "indetermine", pourquoi: causes_vehicule.join(" ") };
  }

  if (_etat(regle, axes.spatial) === "indetermine") {
    return {
      ...carte,
      verdict: "indetermine",
      pourquoi: _avec_origine(cle(messages, "emprise_non_etablie"), regle),
    };
  }

  const incertaines = derogation.illisibles.concat(derogation.non_calculees);
  if (incertaines.length) {
    return {
      ...carte,
      verdict: "indetermine",
      pourquoi: _avec_origine(incertaines.join(" "), regle),
    };
  }

  if (plage.etat === "indetermine") {
    return { ...carte, verdict: "indetermine", pourquoi: plage.pourquoi };
  }

  let pourquoi = causes_vehicule.length
    ? _format(cle(messages, "interdit_criteres"), { criteres: causes_vehicule.join("; ") })
    : cle(messages, "interdit_sans_critere");

  // `autorise_sous_declaration` NE S'ÉMET JAMAIS avant que le conducteur ait
  // déclaré : ce serait autoriser un camion vide sur la foi d'une phrase que
  // personne n'a dite. La règle mord, ET le verdict porte ce qui la lèverait —
  // c'est ce qui permet à l'app de POSER la question au lieu de la supposer.
  const attendues = derogation.declarations_possibles.map(([motif]) => motif);
  if (attendues.length) {
    pourquoi +=
      " " +
      _format(cle(messages, "declaration_attendue"), {
        choix: derogation.declarations_possibles.map(([, affirme]) => affirme).join(" · "),
      });
  }
  return {
    ...carte,
    verdict: "interdit",
    pourquoi,
    declarations_qui_leveraient: attendues,
  };
}

/* ── l'axe véhicule ──────────────────────────────────────────────────────────*/

/**
 * La règle vise-t-elle ce véhicule ? -> ["mord"|"hors_champ"|"indetermine", causes]
 *
 * ET entre dimensions, OU dans une dimension — §combinaison_des_criteres.
 *
 * Une dimension DÉFINITIVEMENT hors champ l'emporte sur une dimension inconnue :
 * un 3 t n'est pas concerné par un seuil de 7,5 t, que l'on sache ou non lire sa
 * classe.
 */
function _examiner_criteres(regle, contexte) {
  const { cfg } = contexte;
  const combinaison = cle(cfg, "combinaison_des_criteres");
  if (
    cle(combinaison, "entre_dimensions") !== "et" ||
    cle(combinaison, "dans_une_dimension") !== "ou"
  ) {
    throw new ConfigurationIncomplete(
      "§evaluateur.combinaison_des_criteres a changé de lecture ; ce code " +
        "n'implémente que « et » entre dimensions et « ou » dans une " +
        "dimension. Changer la config sans changer le code produirait un " +
        "commentaire qui affirme une propriété que le code n'a pas."
    );
  }

  const criteres = _optionnel(regle, "criteres") || [];
  if (!criteres.length) {
    // « Interdit à tous sauf desserte locale » est une spécification COMPLÈTE,
    // par complément. Les 448 sans critère NI dérogation sont écartées bien
    // avant d'arriver ici.
    return ["mord", []];
  }

  const par_dimension = new Map();
  for (const critere of criteres) {
    const dimension = _champ(critere, "dimension");
    if (!par_dimension.has(dimension)) par_dimension.set(dimension, []);
    par_dimension.get(dimension).push(critere);
  }

  const causes = [];
  let un_axe_manque = false;
  for (const [dimension, lot] of par_dimension) {
    const etats = lot.map((c) => _examiner_critere(dimension, c, contexte));
    const mordantes = etats.filter(([e]) => e === "mord").map(([, c]) => c);
    if (mordantes.length) {
      causes.push(...mordantes);
      continue;
    }
    const inconnues = etats.filter(([e]) => e === "indetermine").map(([, c]) => c);
    if (inconnues.length) {
      causes.push(...inconnues);
      un_axe_manque = true;
      continue;
    }
    return ["hors_champ", []];
  }

  return [un_axe_manque ? "indetermine" : "mord", causes];
}

/** -> ["mord"|"pas"|"indetermine", phrase]. La phrase se lit au conducteur. */
function _examiner_critere(dimension, critere, contexte) {
  const { cfg } = contexte;
  const mesurees = cle(cfg, "dimensions_mesurees");
  const classes = cle(cfg, "classes_lisibles");

  if (_possede(mesurees, dimension) && _estDict(mesurees[dimension])) {
    return _examiner_dimension(dimension, critere, contexte);
  }
  if (dimension === "classe_vehicule") return _examiner_classe(critere, classes, contexte);
  throw new ConfigurationIncomplete(
    `Dimension « ${dimension} » absente de §evaluateur.dimensions_mesurees ` +
      "et non traitée comme une classe. §combinaison_des_criteres." +
      "regle_dimension_inconnue = " +
      `${cle(cfg, "combinaison_des_criteres", "regle_dimension_inconnue")}.`
  );
}

/**
 * Une grandeur du véhicule. Elle se MESURE, donc elle ne produit jamais « sous
 * déclaration » : la hauteur fait 4,00 m que le conducteur le dise ou non.
 */
function _examiner_dimension(dimension, critere, contexte) {
  const { cfg, messages, profil } = contexte;
  const specification = cle(cfg, "dimensions_mesurees", dimension);
  const attendue = cle(specification, "unite");
  const champ = cle(specification, "champ");
  const unite = _optionnel(critere, "unite") || null;
  if (unite !== attendue) {
    throw new RegistreIncompatible(
      `Critère « ${dimension} » en « ${_optionnel(critere, "unite")} » alors que ` +
        `§evaluateur.dimensions_mesurees.${dimension}.unite vaut ` +
        `« ${attendue} ». Une unité sous-entendue est ce qui produit un ` +
        "facteur 1000 silencieux : la comparaison ne se fait pas."
    );
  }

  const comparaison = cle(cfg, "comparaison");
  const operateur = _champ(critere, "operateur");
  if (!_possede(comparaison, operateur)) {
    throw new ConfigurationIncomplete(
      `Opérateur « ${operateur} » absent de §evaluateur.comparaison. ` +
        "config/socle.json fait déjà échouer la construction sur un " +
        "opérateur inconnu ; l'évaluateur ne peut pas être plus permissif " +
        "que le chargeur."
    );
  }
  const mord_si = cle(comparaison, operateur, "mord_si");

  const mesure = (profil.vehicule || {})[champ];
  if (mesure === null || mesure === undefined) {
    return [
      "indetermine",
      _format(cle(messages, "dimension_absente"), {
        dimension,
        champ,
        valeur: _nombre(_champ(critere, "valeur")),
        unite: attendue || "",
      }),
    ];
  }

  // `lessThanOrEqualTo` DÉNOTE le maximum autorisé : la règle mord STRICTEMENT
  // au-dessus. DATEX II donne l'opérateur, jamais le sens de l'interdiction ;
  // inverser ce sens transformerait chaque interdiction poids lourd en
  // interdiction aux voitures, sans qu'aucun test ne s'en aperçoive.
  let mord;
  if (mord_si === "strictement_superieur") {
    mord = _reel(mesure, `profil du véhicule, champ « ${champ} »`) >
      _reel(_champ(critere, "valeur"), `critère « ${dimension} »`);
  } else {
    throw new ConfigurationIncomplete(
      `§evaluateur.comparaison.${operateur}.mord_si = « ${mord_si} » n'est ` +
        "pas implémenté ici. Le sens d'une interdiction ne se devine pas."
    );
  }
  const phrase = (
    `${dimension} ${_nombre(mesure)} ${attendue || ""}`.trim() +
    ` au-dessus du maximum de ${_nombre(_champ(critere, "valeur"))} ` +
    (attendue || "")
  ).trim();
  return [mord ? "mord" : "pas", phrase];
}

/**
 * Une classe DATEX II lisible, ou une chaîne que personne n'a lue.
 *
 * Sur les 22 critères de classe en texte libre : ni interdire ni autoriser —
 * interdire fermerait une voie sur une chaîne de caractères, autoriser
 * effacerait une interdiction réelle.
 */
function _examiner_classe(critere, classes, contexte) {
  const { messages, profil } = contexte;
  const etiquette = _optionnel(critere, "valeur_texte");
  const definition =
    typeof etiquette === "string" && _possede(classes, etiquette) ? classes[etiquette] : null;
  if (!_estDict(definition)) {
    if (cle(classes, "regle_classe_illisible") !== "indeterminer") {
      throw new ConfigurationIncomplete(
        "§evaluateur.classes_lisibles.regle_classe_illisible ne vaut " +
          "plus « indeterminer » ; ce code n'implémente que cette règle."
      );
    }
    return ["indetermine", _format(cle(messages, "classe_illisible"), { classe: etiquette })];
  }

  const porteur = cle(definition, "porteur");
  const champ = cle(definition, "champ");
  const valeurs = (_porteur(profil, porteur) || {})[champ];
  if (valeurs === null || valeurs === undefined) {
    return [
      "indetermine",
      _format(cle(messages, "dimension_absente"), {
        dimension: etiquette,
        champ: `${porteur}.${champ}`,
        valeur: "",
        unite: "",
      }),
    ];
  }
  return [_contient(valeurs, etiquette) ? "mord" : "pas", `classe ${etiquette}`];
}

/* ── l'axe motif ─────────────────────────────────────────────────────────────*/

/**
 * Quelle dérogation joue, laquelle pourrait jouer, laquelle est illisible.
 *
 * UNE DÉROGATION NE PEUT QU'ÉLARGIR L'AUTORISATION : si une dérogation lisible
 * joue déjà, celle qu'on ne sait pas lire ne change rien ; si aucune ne joue, on
 * ne peut pas pour autant conclure à l'interdiction.
 *
 * UNE EXEMPTION CALCULABLE NE SE DÉCLARE JAMAIS. « Desserte » se déduit de la
 * destination du trajet — un calcul n'a pas d'intérêt au résultat, un conducteur
 * si. Si le calcul n'a pas été fait, ce n'est pas un motif absent : c'est une
 * question que l'appelant n'a pas posée, et elle rend indéterminé.
 */
function _examiner_exemptions(regle, contexte) {
  const { cfg, messages, profil, gravite } = contexte;
  const table = cle(cfg, "exemptions");
  const porteurs = cle(cfg, "porteurs");

  let joue = null;
  const illisibles = [];
  const non_calculees = [];
  const declarations = [];

  for (const exemption of _optionnel(regle, "exemptions") || []) {
    const nature = _champ(exemption, "nature");
    const valeur = _champ(exemption, "valeur");

    if (nature === "vehicule") {
      const catalogue = cle(table, "vehicule");
      if (!_contient(cle(catalogue, "valeurs_lisibles"), valeur)) {
        illisibles.push(
          _format(cle(messages, "derogation_illisible"), {
            libelle: _optionnel(exemption, "libelle_source") || valeur,
          })
        );
        continue;
      }
      const porteur = cle(catalogue, "porteur");
      const champ = cle(catalogue, "champ");
      if (_contient((_porteur(profil, porteur) || {})[champ] || [], valeur)) {
        joue = _retenir(
          joue,
          [
            cle(porteurs, porteur, "verdict_si_leve"),
            _format(cle(messages, "leve_par_vehicule"), { motif: valeur }),
          ],
          gravite
        );
      }
      continue;
    }

    if (nature !== "motif_de_trajet") {
      throw new ConfigurationIncomplete(
        `Nature d'exemption « ${nature} » inconnue de §evaluateur.exemptions.`
      );
    }

    const definition = cle(table, "motif_de_trajet", valeur);
    const porteur = cle(definition, "porteur");
    const champ = cle(definition, "champ");

    if (porteur === "calcul") {
      // « trajet » est écrit ici comme dans la référence : `calcul` n'est pas un
      // porteur du profil — c'est un SIÈGE d'incertitude — et le résultat d'un
      // calcul de desserte est une propriété du trajet du jour.
      const calculs = (profil.trajet || {})[champ];
      if (!_possede(calculs, valeur)) {
        if (cle(table, "regle_calcul_absent") !== "indeterminer") {
          throw new ConfigurationIncomplete(
            "§evaluateur.exemptions.regle_calcul_absent ne vaut " +
              "plus « indeterminer » ; ce code n'implémente que cette règle."
          );
        }
        non_calculees.push(
          _format(cle(messages, "motif_non_calcule"), {
            motif: valeur,
            champ: `trajet.${champ}`,
          })
        );
      } else if (calculs[valeur]) {
        joue = _retenir(
          joue,
          [
            cle(porteurs, porteur, "verdict_si_leve"),
            _format(cle(messages, "leve_par_calcul"), { motif: valeur }),
          ],
          gravite
        );
      }
      continue;
    }

    const affirme = cle(definition, "ce_qui_est_affirme");
    if (_contient((_porteur(profil, porteur) || {})[champ] || [], valeur)) {
      joue = _retenir(
        joue,
        [
          cle(porteurs, porteur, "verdict_si_leve"),
          _format(cle(messages, "leve_par_declaration"), {
            motif: valeur,
            ce_qui_est_affirme: affirme,
          }),
        ],
        gravite
      );
    } else {
      declarations.push([valeur, affirme]);
    }
  }

  return { joue, illisibles, non_calculees, declarations_possibles: declarations };
}

/**
 * Entre deux dérogations qui jouent, la MOINS incertaine gagne.
 *
 * Un vélo exempté par sa nature n'a pas à devenir « sous votre déclaration »
 * parce que la même règle exempte aussi les livraisons.
 */
function _retenir(courant, candidat, gravite) {
  if (courant === null) return candidat;
  return _rang(courant[0], gravite) <= _rang(candidat[0], gravite) ? courant : candidat;
}

/* ── l'axe temporel ──────────────────────────────────────────────────────────*/

/**
 * La fenêtre de vigueur de l'arrêté : un instant ABSOLU, déjà converti. À ne pas
 * confondre avec une plage récurrente, qui est une heure MURALE. Une règle échue
 * ne restreint plus personne.
 */
function _hors_validite(regle, contexte) {
  const { messages, ms } = contexte;
  for (const [champ, message] of [
    ["debut", "hors_validite_avant"],
    ["fin", "hors_validite_apres"],
  ]) {
    const brut = _optionnel(regle, champ);
    if (!brut) continue;
    const borne = _instant_source(brut, regle, champ);
    if ((champ === "debut" && ms < borne) || (champ === "fin" && ms > borne)) {
      return [true, _format(cle(messages, message), { [champ]: brut })];
    }
  }
  return [false, null];
}

/**
 * -> {etat: "sans_objet"|"dans_la_plage"|"hors_plage"|"indetermine"}
 *
 * Le flux DiaLog déclare ses plages en +00:00, mais 303 heures de fin valent
 * 22:59 et aucune 23:59 : quelle heure MURALE l'arrêté disait n'est pas établi.
 * On ne devine pas. La règle reste livrable et l'évaluateur dit qu'il ne sait pas.
 */
function _examiner_plages(regle, contexte) {
  const { messages, axes, ms } = contexte;
  const periodes = _optionnel(regle, "periodes") || [];
  if (!periodes.length) return { etat: "sans_objet", pourquoi: null };

  const resume = periodes.map(_resumer_plage).join(" ; ");
  if (_etat(regle, axes.temporel) === "indetermine") {
    return {
      etat: "indetermine",
      pourquoi: _format(cle(messages, "plage_non_evaluable"), {
        plages: resume,
        origine: _optionnel(regle, "pourquoi_indetermine") || "",
      }).trim(),
    };
  }

  if (periodes.some((p) => _dans_la_plage(p, ms))) {
    return { etat: "dans_la_plage", pourquoi: null };
  }
  return { etat: "hors_plage", pourquoi: _format(cle(messages, "hors_plage"), { plages: resume }) };
}

/**
 * Heure MURALE dans le fuseau de la période, jamais un instant converti.
 *
 * Une plage qui franchit minuit appartient au jour de son DÉBUT : « 21h-6h le
 * vendredi » couvre la nuit de vendredi à samedi, pas celle de jeudi à vendredi.
 */
function _dans_la_plage(periode, ms) {
  const fuseau = _optionnel(periode, "fuseau");
  if (!fuseau) {
    throw new RegistreIncompatible(
      "Période sans identifiant de fuseau : ce n'est pas une heure " +
        "murale, c'est un nombre. Règle 4 du plan d'intégration."
    );
  }
  const local = _champs_locaux(ms, fuseau);
  const jour_local = _numero_de_jour(local.annee, local.mois, local.jour);

  for (const [borne, sens] of [["date_debut", -1], ["date_fin", 1]]) {
    const brut = _optionnel(periode, borne);
    if (brut && (jour_local - _jour_source(brut, borne)) * sens > 0) return false;
  }

  const debut = _heure(_optionnel(periode, "heure_debut")) || 0;
  const brute_fin = _heure(_optionnel(periode, "heure_fin"));
  const fin = brute_fin === null ? 24 * 3600 : brute_fin;
  const courant = local.heure * 3600 + local.minute * 60 + local.seconde;
  const jours = String(_optionnel(periode, "jours") || "")
    .split(",")
    .filter((j) => j);

  let dedans;
  let nom_du_jour_porteur;
  if (debut <= fin) {
    dedans = debut <= courant && courant <= fin;
    nom_du_jour_porteur = local.nom_du_jour;
  } else {
    // franchit minuit : le jour porteur est celui du début
    dedans = courant >= debut || courant <= fin;
    nom_du_jour_porteur =
      courant >= debut
        ? local.nom_du_jour
        : _nom_du_jour_precedent(local.annee, local.mois, local.jour);
  }
  if (!dedans) return false;
  return !jours.length || jours.includes(nom_du_jour_porteur);
}

/* ── les levées ──────────────────────────────────────────────────────────────*/

/**
 * L'évaluateur COMPOSE : interdiction + levée sur le même point -> sur titre.
 *
 * UNE LEVÉE RETIRE DE LA PRUDENCE, donc elle ne s'applique jamais
 * automatiquement. Trois conditions, toutes nécessaires : tous ses axes
 * déterminés, une DÉSIGNATION explicite des interdictions qu'elle lève, et ses
 * propres critères satisfaits à cet instant. Si sa portée est incertaine, elle
 * ne s'applique pas — et c'est le seul endroit du fichier où l'asymétrie joue
 * dans ce sens.
 *
 * Aucune règle de type `levee` n'existe dans le registre au 4 août 2026 : ce
 * chemin est ÉCRIT ET NON EXERCÉ par la donnée réelle, et le dire vaut mieux que
 * le laisser croire.
 */
function _composer_levees(retenues, levees, contexte) {
  if (!levees.length) return;
  const { cfg, messages } = contexte;
  const parametres = cle(cfg, "levee");
  const designation = cle(parametres, "champ_designation");
  const verdict_leve = cle(parametres, "verdict_si_appliquee");
  const levables = cle(parametres, "leve_les_verdicts");

  const portees = new Map();
  for (const levee of levees) {
    if (
      cle(parametres, "exige_tous_les_axes_determines") &&
      _axes_de_la_regle(levee).some((etat) => etat === "indetermine")
    ) {
      continue;
    }
    const vises = _optionnel(levee, designation);
    if (!vises || !vises.length) continue; // portée non désignée : elle ne s'applique pas
    if (_hors_validite(levee, contexte)[0]) continue;
    if (_examiner_criteres(levee, contexte)[0] !== "mord") continue;
    if (_examiner_plages(levee, contexte).etat === "hors_plage") continue;
    for (const identifiant of vises) {
      if (!portees.has(identifiant)) portees.set(identifiant, levee);
    }
  }

  for (const constat of retenues) {
    const levee = portees.get(constat.regle);
    if (levee === undefined || !_contient(levables, constat.verdict)) continue;
    constat.verdict = verdict_leve;
    constat.pourquoi = _format(cle(messages, "leve_par_titre"), {
      reference: _optionnel(levee, "reference"),
      autorite: _optionnel(levee, "autorite"),
    });
    delete constat.declarations_qui_leveraient;
  }
}

/* ── petites choses ──────────────────────────────────────────────────────────*/

function _exiger_profil(profil, cfg) {
  const obligatoires = cle(cfg, "profil", "porteurs_obligatoires");
  for (const porteur of obligatoires) {
    if (!_possede(profil, porteur) || profil[porteur] === undefined) {
      throw new ProfilIncomplet(
        `Porteur « ${porteur} » absent du profil. Attendus : ` +
          `${_liste(obligatoires)}.\n` +
          "Un porteur absent serait lu comme vide, donc comme « aucune " +
          "habilitation, aucun chargement » — l'absence habillée en valeur."
      );
    }
  }
}

function _porteur(profil, nom) {
  if (!_possede(profil, nom)) {
    throw new ProfilIncomplet(
      `Porteur « ${nom} » absent du profil : la configuration le désigne, la ` +
        "signature ne l'offre pas. Le lire comme vide serait l'absence " +
        "habillée en valeur."
    );
  }
  return profil[nom];
}

/**
 * L'instant, en millisecondes depuis l'époque.
 *
 * Un `Date` EST un instant absolu, donc il porte son fuseau au sens où
 * §validite l'entend. Une chaîne doit porter son décalage EXPLICITEMENT : sans
 * lui, `new Date(...)` la lirait dans le fuseau de la machine du conducteur, ce
 * qui est le nombre déguisé en instant que §validite.instant_naif refuse.
 */
function _exiger_instant(instant, cfg) {
  if (cle(cfg, "validite", "instant_naif") !== "echouer") {
    throw new ConfigurationIncomplete(
      "§evaluateur.validite.instant_naif ne vaut plus « echouer » ; ce " +
        "code n'implémente que cette règle."
    );
  }
  const naif =
    "Un instant sans fuseau n'est pas un instant, c'est un nombre — " +
    "même phrase que outils/registre.py pour les heures murales, et " +
    "même raison.";
  if (instant instanceof Date) {
    if (!Number.isFinite(instant.getTime())) throw new RegistreIncompatible(naif);
    return instant.getTime();
  }
  if (typeof instant === "string") {
    const parties = _ISO.exec(instant.trim());
    if (!parties) {
      throw new RegistreIncompatible(`Instant illisible « ${instant} » : ISO 8601 attendu.`);
    }
    if (!parties[8]) throw new RegistreIncompatible(naif);
    return _epoque(parties);
  }
  throw new RegistreIncompatible(naif);
}

/** RÈGLE 3. La mesure les compte, l'évaluateur non. */
function _est_ecartee(regle, cfg) {
  const ecart = cle(cfg, "regles_ecartees");
  return _etat(regle, cle(ecart, "axe")) === cle(ecart, "etat");
}

/** Les quatre axes d'une règle, quelle que soit la forme de son enregistrement. */
function _axes_de_la_regle(regle) {
  const plats = Object.keys(regle).filter((k) => k.startsWith("etat_"));
  if (plats.length) return plats.map((k) => regle[k]);
  return Object.values(_champ(regle, "etats"));
}

function _etat(regle, axe) {
  /* L'ARBITRE DU VOCABULAIRE EST LE REGISTRE. Une règle hydratée porte
     `etat_spatial`, `etat_temporel`, `etat_vehicule`, `etat_motif` — les noms
     de colonnes de la table `regle`. La version Python lit `etats.<axe>`,
     hérité de sa propre construction en mémoire.

     Deux modules également cohérents, deux vocabulaires : c'est exactement le
     désaccord que `outils/conformite.py` a rendu visible, et l'arbitre n'est ni
     l'un ni l'autre — les deux sont en aval du registre, donc ses noms gagnent.

     La forme groupée reste acceptée : elle est celle de l'appelant Python, et
     la refuser casserait la concordance qui prouve que les deux implémentations
     ne divergent pas. */
  const plat = "etat_" + axe;
  if (_possede(regle, plat)) return regle[plat];
  const etats = _champ(regle, "etats");
  if (!_possede(etats, axe)) {
    throw new RegistreIncompatible(
      `Règle ${_optionnel(regle, "id")} : l'axe d'état « ${axe} » est absent de ` +
        "son enregistrement. Un axe absent lu comme déterminé serait " +
        "l'incertitude habillée en certitude."
    );
  }
  return etats[axe];
}

/**
 * Les quatre axes, LUS dans la configuration.
 *
 * §propagation_des_axes.ordre_d_examen ne classe QUE les indéterminations entre
 * elles. Ce code implémente UNE lecture de cet ordre ; si la liste change, il
 * échoue au lieu de porter un commentaire qui affirme une propriété qu'il n'a
 * pas — même garde que §combinaison_des_criteres.
 */
function _axes(cfg) {
  const ordre = cle(cfg, "propagation_des_axes", "ordre_d_examen");
  const implemente = ["vehicule", "spatial", "motif", "temporel"];
  if (
    !Array.isArray(ordre) ||
    ordre.length !== implemente.length ||
    ordre.some((axe, rang) => axe !== implemente[rang])
  ) {
    throw new ConfigurationIncomplete(
      "§evaluateur.propagation_des_axes.ordre_d_examen vaut " +
        `${_liste(ordre)} alors que ce code implémente ${_liste(implemente)}. ` +
        "L'ordre décide QUELLE cause est nommée au conducteur : le changer " +
        "sans changer le code nommerait la mauvaise."
    );
  }
  return { vehicule: ordre[0], spatial: ordre[1], motif: ordre[2], temporel: ordre[3] };
}

function _conduite(regle, conduites) {
  const type = _champ(regle, "type");
  const conduite = _possede(conduites, type) ? conduites[type] : null;
  if (typeof conduite !== "string") {
    throw new ConfigurationIncomplete(
      `Type de règle « ${type} » absent de §evaluateur.types_de_regle. ` +
        "Un type nouveau ne prend pas silencieusement le comportement d'un autre."
    );
  }
  return conduite;
}

/** Ce que l'écran affiche pour identifier la règle. Rien de plus. */
function _carte(regle) {
  return {
    regle: _champ(regle, "id"),
    reference: _optionnel(regle, "reference"),
    intitule: _optionnel(regle, "intitule"),
    autorite: _optionnel(regle, "autorite"),
    voie: _optionnel(regle, "voie"),
    url: _optionnel(regle, "url"),
  };
}

function _rang(verdict, gravite) {
  const rang = gravite.indexOf(verdict);
  if (rang < 0) {
    throw new ConfigurationIncomplete(
      `Verdict « ${verdict} » absent de ` +
        "§evaluateur.ordre_de_gravite.du_plus_grave_au_moins_grave."
    );
  }
  return rang;
}

function _plus_grave(a, b, gravite) {
  return _rang(a, gravite) <= _rang(b, gravite) ? a : b;
}

function _tete(retenues, gravite) {
  let tete = null;
  let meilleur = null;
  for (const constat of retenues) {
    const rang = _rang(constat.verdict, gravite);
    if (meilleur === null || rang < meilleur) {
      meilleur = rang;
      tete = constat;
    }
  }
  return tete;
}

/**
 * La raison du registre est rendue TELLE QUELLE, jamais reformulée. C'est elle
 * qui dit ce qu'il faudrait obtenir pour lever l'indétermination ; la réécrire
 * ferait perdre le seul endroit où la question ouverte est posée.
 */
function _avec_origine(phrase, regle) {
  const origine = _optionnel(regle, "pourquoi_indetermine");
  return origine ? `${phrase} ${origine}`.trim() : phrase;
}

function _contient(collection, valeur) {
  if (Array.isArray(collection)) return collection.includes(valeur);
  if (typeof collection === "string") return collection.includes(valeur);
  throw new RegistreIncompatible(
    `Une collection était attendue pour y chercher « ${valeur} » ; ` +
      `« ${collection} » n'en est pas une.`
  );
}

/* ── mise en forme : gabarits, nombres, plages ───────────────────────────────*/

/**
 * Le gabarit vient de §messages, jamais d'ici. Un nom de trou non fourni ÉCHOUE
 * en le nommant : un message amputé dirait quelque chose de faux au conducteur.
 */
function _format(gabarit, valeurs) {
  if (typeof gabarit !== "string") {
    throw new ConfigurationIncomplete(
      `Un gabarit de message était attendu, « ${gabarit} » n'en est pas un.`
    );
  }
  return gabarit.replace(/\{([^{}]*)\}/g, (_entier, nom) => {
    if (!Object.prototype.hasOwnProperty.call(valeurs, nom)) {
      throw new ConfigurationIncomplete(
        `Le message « ${gabarit} » attend « {${nom}} », que l'évaluateur ne lui ` +
          "fournit pas. Un trou non rempli est une phrase fausse."
      );
    }
    const valeur = valeurs[nom];
    // PORTAGE 5 : `str(None)` vaut « None » en Python. Rendre « » ici
    // produirait deux textes différents pour la même donnée.
    return valeur === null || valeur === undefined ? "None" : String(valeur);
  });
}

function _nombre(valeur) {
  if (valeur === null || valeur === undefined) return "";
  const reel = _reel(valeur, "un nombre du registre");
  return Number.isInteger(reel) ? String(Math.trunc(reel)) : String(reel);
}

function _reel(valeur, ou) {
  const reel = typeof valeur === "number" ? valeur : Number(valeur);
  if (!Number.isFinite(reel)) {
    throw new RegistreIncompatible(
      `Valeur non numérique « ${valeur} » là où un nombre est attendu (${ou}). ` +
        "Comparer une chaîne à un seuil rendrait un verdict sur rien."
    );
  }
  return reel;
}

function _liste(valeurs) {
  // Même rendu que la liste Python de la référence, pour que deux diagnostics
  // du même défaut se lisent pareil.
  if (!Array.isArray(valeurs)) return String(valeurs);
  return "[" + valeurs.map((v) => `'${v}'`).join(", ") + "]";
}

function _resumer_plage(periode) {
  const jours = _optionnel(periode, "jours");
  const tranche =
    `${_optionnel(periode, "heure_debut") || "00:00:00"}` +
    `–${_optionnel(periode, "heure_fin") || "24:00:00"}`;
  return jours ? `${tranche} (${jours})` : tranche;
}

function _heure(brut) {
  if (!brut) return null;
  const morceaux = String(brut).split(":");
  const secondes = morceaux.map((m) => {
    if (!/^\d+$/.test(m)) {
      throw new RegistreIncompatible(
        `Heure murale illisible « ${brut} » : HH:MM:SS attendu. Une heure ` +
          "devinée n'est pas une heure."
      );
    }
    return Number(m);
  });
  while (secondes.length < 3) secondes.push(0);
  return secondes[0] * 3600 + secondes[1] * 60 + secondes[2];
}

/* ── le calendrier, sans dépendance ──────────────────────────────────────────*/

const _ISO =
  /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,9}))?)?)?(Z|[+-]\d{2}:?\d{2})?$/;

function _utc(annee, mois, jour, heure, minute, seconde, milli) {
  // setUTCFullYear et non Date.UTC : ce dernier replie les années 0 à 99 sur
  // 1900+, ce qui ferait d'une date du registre une autre date, en silence.
  const date = new Date(0);
  date.setUTCFullYear(annee, mois - 1, jour);
  date.setUTCHours(heure, minute, seconde, milli);
  return date.getTime();
}

function _epoque(parties) {
  const fraction = parties[7] ? Number(("0." + parties[7]).slice(0, 8)) : 0;
  const base = _utc(
    Number(parties[1]),
    Number(parties[2]),
    Number(parties[3]),
    Number(parties[4] || 0),
    Number(parties[5] || 0),
    Number(parties[6] || 0),
    Math.round(fraction * 1000)
  );
  const decalage = parties[8];
  if (decalage === "Z") return base;
  const signe = decalage[0] === "-" ? -1 : 1;
  const corps = decalage.slice(1).replace(":", "");
  const minutes = Number(corps.slice(0, 2)) * 60 + Number(corps.slice(2, 4));
  return base - signe * minutes * 60000;
}

function _instant_source(brut, regle, champ) {
  const parties = typeof brut === "string" ? _ISO.exec(brut.trim()) : null;
  if (!parties) {
    throw new RegistreIncompatible(
      `Règle ${_optionnel(regle, "id")} : champ « ${champ} » illisible « ${brut} ».`
    );
  }
  if (!parties[8]) {
    throw new RegistreIncompatible(
      `Règle ${_optionnel(regle, "id")} : « ${champ} » = « ${brut} » sans fuseau. Un ` +
        "instant sans fuseau n'est pas comparable à un instant."
    );
  }
  return _epoque(parties);
}

function _jour_source(brut, borne) {
  const parties = typeof brut === "string" ? _ISO.exec(brut.trim()) : null;
  if (!parties) {
    throw new RegistreIncompatible(
      `Borne de période « ${borne} » illisible « ${brut} » : une date ISO est attendue.`
    );
  }
  return _numero_de_jour(Number(parties[1]), Number(parties[2]), Number(parties[3]));
}

function _numero_de_jour(annee, mois, jour) {
  return Math.round(_utc(annee, mois, jour, 0, 0, 0, 0) / 86400000);
}

/**
 * L'heure MURALE dans le fuseau nommé par la période. Intl porte la base de
 * fuseaux du système : c'est ce qui permet de ne pas embarquer de dépendance et
 * de ne jamais deviner un décalage saisonnier.
 */
function _champs_locaux(ms, fuseau) {
  let parties;
  try {
    parties = new Intl.DateTimeFormat("en-US", {
      timeZone: fuseau,
      hourCycle: "h23",
      weekday: "long",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).formatToParts(new Date(ms));
  } catch (erreur) {
    throw new RegistreIncompatible(
      `Fuseau « ${fuseau} » inconnu de cet environnement : l'heure murale de ` +
        "cette période n'est pas calculable ici, et la deviner serait la " +
        "faute que la règle 4 du plan d'intégration nomme."
    );
  }
  const lu = {};
  for (const part of parties) lu[part.type] = part.value;
  const heure = Number(lu.hour) === 24 ? 0 : Number(lu.hour);
  return {
    annee: Number(lu.year),
    mois: Number(lu.month),
    jour: Number(lu.day),
    heure,
    minute: Number(lu.minute),
    seconde: Number(lu.second),
    // Les jours du registre sont écrits en anglais minuscule
    // (« monday,tuesday,… »), comme %A de la référence en locale C.
    nom_du_jour: String(lu.weekday).toLowerCase(),
  };
}

function _nom_du_jour_precedent(annee, mois, jour) {
  const veille = new Date(_utc(annee, mois, jour - 1, 12, 0, 0, 0));
  return new Intl.DateTimeFormat("en-US", { timeZone: "UTC", weekday: "long" })
    .format(veille)
    .toLowerCase();
}
