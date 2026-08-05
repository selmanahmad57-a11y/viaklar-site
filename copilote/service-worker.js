// Le copilote fonctionne hors réseau, ou il ne sert à rien.
//
// CONTRAINTE: ce service worker ne sert JAMAIS une tuile d'une version
//   antérieure à celle de l'index servi — un mélange de millésimes ferait dire
//   au copilote des règles retirées.
// CONTRAINTE: une ressource absente du cache ET du réseau remonte l'échec à la
//   page, jamais une réponse vide qui se lirait comme « rien ici ».
//
// POURQUOI. Une zone blanche est précisément l'endroit où le conducteur est
// seul, et c'est là qu'une page qui télécharge ses données se tait. Sans ce
// fichier, le copilote est une application qui marche partout sauf là où elle
// compte.
//
// LE MILLÉSIME VIENT DE LA DONNÉE, PAS D'UNE CONSTANTE. `genere_le` de
// index.json nomme le cache : republier de nouvelles tuiles invalide l'ancien
// cache tout seul, et personne n'a à penser à incrémenter un numéro. Une
// version qu'on oublie de changer sert des règles périmées en silence.

"use strict";

const INDEX = "index.json";

// La coquille : ce qu'il faut pour que l'application démarre sans réseau. Les
// tuiles ne sont PAS ici — elles se mettent en cache au fur et à mesure du
// trajet, parce que pré-charger la France entière coûterait 7 Mo pour un
// conducteur qui roule dans un département.
const COQUILLE = ["./", "index.html", "proximite.js", "evaluateur.js",
                  "manifest.json", INDEX];

async function millesime() {
  // Au réseau d'abord : c'est l'installation, on veut la version courante.
  const r = await fetch(INDEX, { cache: "no-store" });
  const d = await r.json();
  return "viaklar-" + d.genere_le;
}

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const nom = await millesime();
    const cache = await caches.open(nom);
    await cache.addAll(COQUILLE);
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    // TOUT AUTRE MILLÉSIME EST SUPPRIMÉ. Garder l'ancien laisserait une tuile
    // d'hier répondre à un index d'aujourd'hui — des règles retirées qui
    // continuent d'interdire, ou pire, des règles ajoutées qui manquent.
    const nom = await millesime();
    for (const c of await caches.keys()) if (c !== nom) await caches.delete(c);
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== self.location.origin) return;

  e.respondWith((async () => {
    const nom = await millesime().catch(() => null);
    // Hors réseau, `millesime()` échoue : on cherche alors dans le cache le
    // plus récent qu'on ait, plutôt que de rendre une erreur.
    const cache = await caches.open(nom || (await caches.keys())[0] || "viaklar");

    const enCache = await cache.match(e.request, { ignoreSearch: true });
    if (enCache) {
      // Le réseau rafraîchit en arrière-plan, sans faire attendre le conducteur.
      e.waitUntil(fetch(e.request)
        .then((r) => (r.ok ? cache.put(e.request, r.clone()) : null))
        .catch(() => null));
      return enCache;
    }

    try {
      const r = await fetch(e.request);
      if (r.ok) e.waitUntil(cache.put(e.request, r.clone()));
      return r;
    } catch (erreur) {
      // NI CACHE NI RÉSEAU. On remonte l'échec tel quel : la page distingue
      // « zone sans arrêté ingéré » de « zone qu'on n'a pas pu lire », et une
      // réponse vide fabriquée ici détruirait cette distinction.
      return new Response(
        JSON.stringify({
          erreur: "hors_reseau_et_hors_cache",
          pourquoi: "Cette ressource n'est ni en cache ni joignable. Le "
            + "copilote ne sait pas ce qu'il y a ici. Aucune absence "
            + "d'alerte ne vaut autorisation.",
        }),
        { status: 504, headers: { "Content-Type": "application/json" } });
    }
  })());
});
