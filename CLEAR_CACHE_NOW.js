// COPY THIS ENTIRE CODE INTO YOUR BROWSER CONSOLE RIGHT NOW!

console.log("🚨 EMERGENCY CACHE CLEAR - FIXING DEWALT DRILL ISSUE");

// Nuclear localStorage clear
localStorage.removeItem('inventory-items');
localStorage.removeItem('inventory-stats');
localStorage.clear();

// Clear sessionStorage
sessionStorage.clear();

// Clear any IndexedDB
if ('indexedDB' in window) {
    indexedDB.databases().then(databases => {
        databases.forEach(db => {
            console.log('Clearing IndexedDB:', db.name);
            indexedDB.deleteDatabase(db.name);
        });
    });
}

// Clear service worker cache
if ('caches' in window) {
    caches.keys().then(cacheNames => {
        cacheNames.forEach(cacheName => {
            console.log('Clearing cache:', cacheName);
            caches.delete(cacheName);
        });
    });
}

console.log("✅ ALL CACHE CLEARED!");
console.log("🔄 NOW DO HARD REFRESH: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)");

// Test if backend is working
setTimeout(() => {
    fetch('http://localhost:8000/v1/inventory/')
        .then(response => response.json())
        .then(data => {
            console.log("✅ Backend working! Items:", data.items?.length || 0);
        })
        .catch(error => {
            console.log("❌ Backend not ready yet:", error.message);
            console.log("Wait a moment and refresh again");
        });
}, 2000);
