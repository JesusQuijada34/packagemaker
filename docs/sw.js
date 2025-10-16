const CACHE_NAME = "ipm-cache-v1";
const ASSETS = ["/","/index.html","/style.css","/main.js","/manifest.json"];

self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(self.clients.claim()); });

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/.netlify/functions/")) {
    e.respondWith(fetch(e.request).catch(()=>caches.match("/index.html")));
    return;
  }
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
