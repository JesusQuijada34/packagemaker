const CACHE_NAME = "ipm-cache-v1";
const ASSETS = [
  "/",
  "/index.html",
  "/style.css",
  "/main.js",
  "/manifest.json"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  // always try network first for API calls, cache others
  if (url.pathname.startsWith("/.netlify/functions/")) {
    event.respondWith(fetch(event.request).catch(()=>caches.match("/index.html")));
    return;
  }
  event.respondWith(caches.match(event.request).then(r => r || fetch(event.request)));
});
