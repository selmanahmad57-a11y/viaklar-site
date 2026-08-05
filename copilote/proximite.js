// La proximité, dans le navigateur, sur des tuiles statiques.
//
// CONTRAINTE: ce module ne rend AUCUN jugement réglementaire — il rend des
//   règles candidates avec leur distance, jamais un verdict.
// CONTRAINTE: aucune tuile n'est retéléchargée tant qu'elle est en mémoire, et
//   aucune règle n'est rendue deux fois quand elle chevauche deux tuiles.
// CONTRAINTE: une tuile absente est un TROU DÉCLARÉ, jamais un silence : elle
//   remonte dans `manquantes`, et l'absence de règle ne vaut pas autorisation.
//
// POURQUOI DANS LE NAVIGATEUR. Colorier la route exige d'évaluer toutes les
// règles visibles pour CE véhicule à CET instant : aucun cache serveur n'est
// possible. Et un copilote qui dépend d'un serveur est un copilote qui se tait
// dans une zone blanche — c'est-à-dire précisément là où le conducteur est seul.
//
// LES TUILES SONT L'INDEX. Pas de R*Tree ici : le découpage géographique fait le
// même travail, et il fait en plus le travail que le R*Tree ne fait pas — il
// évite de télécharger Marseille quand on roule en Sarthe.

"use strict";

const RAYON_TERRE_M = 6371000.0;
const METRES_PAR_DEGRE_LATITUDE = 111000.0;

/* La géométrie, portée depuis outils/geometrie.py. Elle y est définie une seule
   fois pour le mesureur et le produit ; ici c'est la troisième écriture, et
   c'est le prix du navigateur — donc elle est ÉPROUVÉE contre l'originale par
   pwa/concordance.js plutôt qu'affirmée conforme. */

export function metresParDegre(latitude) {
  const lat = (Math.PI * RAYON_TERRE_M) / 180.0;
  return [lat, lat * Math.cos((latitude * Math.PI) / 180.0)];
}

export function haversine(a, b) {
  const lat1 = (a[1] * Math.PI) / 180, lon1 = (a[0] * Math.PI) / 180;
  const lat2 = (b[1] * Math.PI) / 180, lon2 = (b[0] * Math.PI) / 180;
  const h = Math.sin((lat2 - lat1) / 2) ** 2
    + Math.cos(lat1) * Math.cos(lat2) * Math.sin((lon2 - lon1) / 2) ** 2;
  return 2 * RAYON_TERRE_M * Math.asin(Math.min(1, Math.sqrt(h)));
}

export function capSegment(debut, fin, echelle) {
  const [latM, lonM] = echelle;
  const dx = (fin[0] - debut[0]) * lonM;
  const dy = (fin[1] - debut[1]) * latM;
  if (dx === 0 && dy === 0) return 0;
  const azimut = (Math.atan2(dx, dy) * 180) / Math.PI;
  return ((azimut % 180) + 180) % 180;
}

export function ecartDeCap(a, b) {
  const d = Math.abs(a - b) % 180;
  return Math.min(d, 180 - d);
}

/* Distance d'un point à un segment, dans le plan local. Le repère est mis à
   l'échelle avant projection : à 48° de latitude, un degré de longitude vaut
   deux tiers d'un degré de latitude, et l'ignorer fausserait toute distance
   est-ouest de 33 %. */
export function distancePointSegment(point, debut, fin, echelle) {
  const [latM, lonM] = echelle;
  const px = (point[0] - debut[0]) * lonM, py = (point[1] - debut[1]) * latM;
  const sx = (fin[0] - debut[0]) * lonM, sy = (fin[1] - debut[1]) * latM;
  const carre = sx * sx + sy * sy;
  if (carre === 0) return Math.hypot(px, py);
  const t = Math.max(0, Math.min(1, (px * sx + py * sy) / carre));
  return Math.hypot(px - t * sx, py - t * sy);
}

// ── les tuiles ──────────────────────────────────────────────────────────────

export class Tuiles {
  /* `index` est le contenu de copilote/index.json : il porte le niveau de
     découpage, la liste des tuiles réellement produites, et l'attribution.
     Rien n'est deviné — une tuile qui n'est pas dans la liste n'existe pas, et
     c'est différent d'une tuile qui existe et qu'on n'a pas pu charger. */
  constructor(base, index) {
    this.base = base.replace(/\/$/, "");
    this.index = index;
    this.pas = index.pas_de_tuile_deg;
    this.existantes = new Set(index.tuiles || []);
    this.enMemoire = new Map();
    this.manquantes = new Set();   // demandées, pas obtenues
  }

  cle(lon, lat) {
    return `${Math.floor(lon / this.pas)}_${Math.floor(lat / this.pas)}`;
  }

  /* Les clés qui couvrent un disque : le carré englobant suffit, la distance
     exacte est vérifiée plus tard sur chaque segment. */
  clesAutour(lon, lat, rayonM) {
    const [latM, lonM] = metresParDegre(lat);
    const dLat = rayonM / latM, dLon = rayonM / lonM;
    const cles = new Set();
    for (let x = lon - dLon; x <= lon + dLon + this.pas; x += this.pas)
      for (let y = lat - dLat; y <= lat + dLat + this.pas; y += this.pas)
        cles.add(this.cle(x, y));
    cles.add(this.cle(lon, lat));
    return [...cles];
  }

  async charger(cles) {
    const attentes = [];
    for (const cle of cles) {
      if (this.enMemoire.has(cle)) continue;
      if (!this.existantes.has(cle)) {
        // Une tuile absente de l'index n'a AUCUNE règle : ce n'est pas un trou,
        // c'est une zone sans arrêté ingéré. La distinction compte, et elle est
        // rendue à l'appelant.
        this.enMemoire.set(cle, []);
        continue;
      }
      attentes.push(
        fetch(`${this.base}/tuiles/${cle}.json`)
          .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
          .then((t) => { this.enMemoire.set(cle, t.regles || []); })
          .catch(() => { this.manquantes.add(cle); })
      );
    }
    await Promise.all(attentes);
  }

  reglesDe(cles) {
    // Une règle chevauchant deux tuiles y figure deux fois : on déduplique sur
    // son identifiant de registre, pas sur son objet.
    const vues = new Map();
    for (const cle of cles)
      for (const r of this.enMemoire.get(cle) || [])
        if (!vues.has(r.id)) vues.set(r.id, r);
    return [...vues.values()];
  }
}

// ── ce qui est autour, et ce qui est devant ─────────────────────────────────

function segmentsDe(regle) {
  const sortie = [];
  for (const emprise of regle.emprises || [])
    for (const ligne of emprise.lignes || [])
      for (let i = 0; i + 1 < ligne.length; i++)
        sortie.push([ligne[i], ligne[i + 1], emprise]);
  return sortie;
}

/** Règles dont l'emprise passe à moins de `rayonM`. Sans jugement. */
export async function reglesAutour(tuiles, position, cap, rayonM, config) {
  const [lon, lat] = position;
  const cles = tuiles.clesAutour(lon, lat, rayonM);
  await tuiles.charger(cles);
  const echelle = metresParDegre(lat);
  const ecartMax = config.ecart_de_cap_max_deg;

  const trouvees = [];
  for (const regle of tuiles.reglesDe(cles)) {
    let plusProche = null, capRetenu = null, voie = null;
    for (const [a, b, emprise] of segmentsDe(regle)) {
      const d = distancePointSegment(position, a, b, echelle);
      if (d > rayonM) continue;
      if (cap != null) {
        const capSeg = capSegment(a, b, echelle);
        if (ecartDeCap(cap, capSeg) > ecartMax) continue;
        if (plusProche === null || d < plusProche) capRetenu = capSeg;
      }
      if (plusProche === null || d < plusProche) {
        plusProche = d;
        voie = emprise.libelle || emprise.reference_voie || null;
      }
    }
    if (plusProche !== null)
      trouvees.push({ ...regle, distance_m: plusProche, cap_de_la_voie: capRetenu, voie });
  }
  return trouvees.sort((a, b) => a.distance_m - b.distance_m);
}

/** Règles sur la trajectoire, avec la distance À PARCOURIR avant de les atteindre.
 *
 *  C'est celle qui compte pour un copilote : « une règle à 300 m à vol d'oiseau »
 *  ne dit pas si elle est devant, derrière, ou sur la rue parallèle.
 *
 *  SANS CAP, cette fonction NE MENT PAS : elle rend `distance_a_parcourir_m`
 *  nul et signale que la sélection est un disque. La page l'affiche alors « à
 *  vol d'oiseau », jamais « dans N mètres ».
 */
export async function reglesDevant(tuiles, position, cap, distanceM, config) {
  if (cap == null || !Number.isFinite(cap)) {
    const autour = await reglesAutour(tuiles, position, null, distanceM, config);
    return {
      regles: autour.map((r) => ({ ...r, distance_a_parcourir_m: null })),
      oriente: false,
      pourquoi: "Sans cap, « devant » n’est pas distinguable de « autour » : la "
        + "sélection est un disque, et une règle DERRIÈRE le véhicule peut y "
        + "figurer.",
      manquantes: [...tuiles.manquantes],
    };
  }

  const [lon, lat] = position;
  const cles = tuiles.clesAutour(lon, lat, distanceM);
  await tuiles.charger(cles);
  const echelle = metresParDegre(lat);
  const [latM, lonM] = echelle;
  const ecartMax = config.ecart_de_cap_max_deg;
  const base = config.couloir_base_m;
  const evasement = Math.tan((config.couloir_evasement_deg * Math.PI) / 180);

  // Repère local orienté par le cap : abscisse devant, ordonnée à droite.
  const rad = (cap * Math.PI) / 180;
  const avX = Math.sin(rad), avY = Math.cos(rad);

  const trouvees = [];
  for (const regle of tuiles.reglesDe(cles)) {
    let meilleure = null;
    for (const [a, b, emprise] of segmentsDe(regle)) {
      const capSeg = capSegment(a, b, echelle);
      if (ecartDeCap(cap, capSeg) > ecartMax) continue;
      for (const p of [a, b]) {
        const dx = (p[0] - lon) * lonM, dy = (p[1] - lat) * latM;
        const devant = dx * avX + dy * avY;        // abscisse
        const cote = dx * avY - dy * avX;          // ordonnée, positif à droite
        if (devant < 0 || devant > distanceM) continue;
        // Le couloir s'évase : un couloir droit perd toute règle en courbe.
        if (Math.abs(cote) > base + devant * evasement) continue;
        if (meilleure === null || devant < meilleure.d)
          meilleure = {
            d: devant, cote,
            voie: emprise.libelle || emprise.reference_voie || null,
          };
      }
    }
    if (meilleure)
      trouvees.push({
        ...regle,
        distance_m: meilleure.d,
        distance_a_parcourir_m: meilleure.d,
        ecart_lateral_m: meilleure.cote,
        voie: meilleure.voie,
      });
  }
  return {
    regles: trouvees.sort((a, b) => a.distance_m - b.distance_m),
    oriente: true,
    pourquoi: null,
    manquantes: [...tuiles.manquantes],
  };
}
