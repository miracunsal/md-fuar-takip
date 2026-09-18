const CACHE_NAME = "mdfuar-v1";
const ASSETS = [
  "/",
  "/static/style.css",
  "/static/app.js",
  "/assets/logo.png",
  "/assets/logo_full.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});
