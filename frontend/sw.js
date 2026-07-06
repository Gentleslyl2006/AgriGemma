// AgriGemma service worker
// Caches the app shell so the interface loads instantly with no connection.
// Note: this does NOT cache backend responses — those come fresh from the
// local Gemma 4 service running on the same device/network.

const CACHE_NAME = "agrigemma-shell-v1";
const APP_SHELL = ["./index.html", "./manifest.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Never cache/intercept calls to the local backend — those must always
  // hit the live AgriGemma/Gemma service for a fresh answer.
  if (url.pathname === "/ask") return;

  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
