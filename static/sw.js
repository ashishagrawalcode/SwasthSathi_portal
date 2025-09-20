self.addEventListener('install', (event) => {
    console.log('Service Worker installing.');
    // Cache your static assets here if you want to enable offline use
    event.waitUntil(
        caches.open('swasth-sathi-cache-v1')
            .then((cache) => {
                return cache.addAll([
                    '/',
                    '/static/css/style.css',
                    '/static/js/script.js',
                    '/static/manifest.json',
                    // Add other crucial files here
                ]);
            })
    );
});

self.addEventListener('fetch', (event) => {
    // This is optional and enables offline support
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
});