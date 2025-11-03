const CACHE_NAME = 'vision-ai-pwa-v2'; // Bumped version to invalidate old cache
const URLS_TO_CACHE = [
  '/',
  '/index.html'
];

// On install, cache the core assets and immediately activate.
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(URLS_TO_CACHE);
      })
      .then(() => self.skipWaiting()) // Force the new service worker to activate
  );
});

// Use a "Network falling back to Cache" strategy.
self.addEventListener('fetch', (event) => {
  // We only handle GET requests.
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // If the network request is successful, clone it, cache it, and return it.
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME)
          .then((cache) => {
            // We don't cache POST requests to the Gemini API
            if(!event.request.url.includes('googleapis.com')) {
              cache.put(event.request, responseToCache);
            }
          });
        return networkResponse;
      })
      .catch(() => {
        // If the network request fails (e.g., offline), return the cached response.
        return caches.match(event.request);
      })
  );
});

// On activation, clean up old caches and take control of the page.
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim()) // Take control of open clients
  );
});