/* ============================================================
   SpendWise — Service Worker
   Basic offline caching (static assets only)
   ============================================================ */

const CACHE_NAME = 'spendwise-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/manifest.json',
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(STATIC_ASSETS).catch(function () { /* ignore failures */ });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (names) {
      return Promise.all(
        names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function (event) {
  const url = new URL(event.request.url);

  // Only cache same-origin GET requests for static files
  if (event.request.method !== 'GET') return;
  if (url.origin !== location.origin) return;

  // Never cache admin/auth POST-like pages
  if (url.pathname.startsWith('/admin/')) return;
  if (url.pathname.startsWith('/login/')) return;

  event.respondWith(
    caches.match(event.request).then(function (cached) {
      const fetchPromise = fetch(event.request).then(function (response) {
        if (response && response.status === 200 && url.pathname.startsWith('/static/')) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(function () {
        return cached;
      });
      return cached || fetchPromise;
    })
  );
});