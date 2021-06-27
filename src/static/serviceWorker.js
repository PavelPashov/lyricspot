const lyricSpot = "lyricspot-site-v1"
const assets = [
    "/",
    "../templates/index.html",
    "../templates/layout.html",
    "../templates/login.html",
    "../templates/songs.html",
    "style.css",
    "synthwave.css",
    "lightstyles.css",
    "darkstyles.css",
    "scripts.js",
]

self.addEventListener("install", installEvent => {
    installEvent.waitUntil(
        caches.open(lyricSpot).then(cache => {
            cache.addAll(assets)
        })
    )
})

self.addEventListener("fetch", fetchEvent => {
    fetchEvent.respondWith(
        caches.match(fetchEvent.request).then(res => {
            return res || fetch(fetchEvent.request)
        })
    )
})