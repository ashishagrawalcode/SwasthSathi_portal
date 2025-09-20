// A basic service worker to enable PWA features.

// The name of the cache. Change this version number to force a new cache refresh.
const CACHE_NAME = 'aroghub-cache-v1';

// A list of assets to pre-cache. These files will be downloaded and
// stored in the cache when the service worker is installed.
const urlsToCache = [
    '/',
    '/login',
    '/register',
    '/static/css/styles.css',
    '/static/js/script.js',
    '/static/images/icon-192x192.png',
    '/static/images/icon-512x512.png',
    '/static/images/logo-dark.svg',
    '/static/images/logo-light.svg',
    // Add any other essential static assets like fonts, other images, etc.
];

// --- INSTALL EVENT ---
// This event is fired when the browser installs the service worker.
self.addEventListener('install', event => {
    console.log('[Service Worker] Install event triggered.');
    // Pre-cache all of the essential assets.
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[Service Worker] Caching essential assets.');
                return cache.addAll(urlsToCache);
            })
            .catch(err => {
                console.error('[Service Worker] Cache pre-caching failed:', err);
            })
    );
});

// --- FETCH EVENT ---
// This event is fired every time the browser requests a resource.
self.addEventListener('fetch', event => {
    // Respond with the cached asset if available, otherwise fetch from the network.
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // If the resource is found in the cache, return it.
                if (response) {
                    return response;
                }
                // Otherwise, fetch the resource from the network.
                return fetch(event.request);
            })
            .catch(err => {
                console.error('[Service Worker] Fetch event failed:', err);
            })
    );
});

// --- ACTIVATE EVENT ---
// This event is fired when the service worker is activated.
// This is a good time to clean up old caches.
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activate event triggered.');
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    // Delete old caches that are not in the whitelist.
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        console.log(`[Service Worker] Deleting old cache: ${cacheName}`);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});