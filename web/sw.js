// Minimal service worker: lets the phone install Kagzi and show it in the Share menu. Network always wins (verdicts are never cached).
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});
