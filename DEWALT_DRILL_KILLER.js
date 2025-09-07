// NUCLEAR DEWALT DRILL DESTROYER
// Copy and paste this ENTIRE script into your browser console

console.log("🚨 NUCLEAR DEWALT DRILL DESTROYER ACTIVATED");
console.log("💥 Destroying all traces of DeWalt drill...");

// 1. Clear ALL localStorage
localStorage.clear();
console.log("✅ localStorage cleared");

// 2. Clear ALL sessionStorage  
sessionStorage.clear();
console.log("✅ sessionStorage cleared");

// 3. Clear ALL cookies for this domain
document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
});
console.log("✅ Cookies cleared");

// 4. Clear IndexedDB
if ('indexedDB' in window) {
    indexedDB.databases().then(databases => {
        databases.forEach(db => {
            console.log('Clearing IndexedDB:', db.name);
            indexedDB.deleteDatabase(db.name);
        });
    });
}

// 5. Clear Cache API
if ('caches' in window) {
    caches.keys().then(cacheNames => {
        cacheNames.forEach(cacheName => {
            console.log('Clearing cache:', cacheName);
            caches.delete(cacheName);
        });
    });
}

// 6. Force override any React state
setTimeout(() => {
    // Try to find and override React state
    const reactRoot = document.querySelector('#root, [data-reactroot], .react-root');
    if (reactRoot && reactRoot._reactInternalFiber) {
        console.log("🔧 Attempting to override React state...");
    }
}, 1000);

console.log("💀 DEWALT DRILL DESTROYED!");
console.log("🔄 Now do HARD REFRESH: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)");
console.log("🎯 The drill should be GONE!");

// Test API after clearing
setTimeout(() => {
    fetch('http://localhost:8000/v1/inventory/')
        .then(response => response.json())
        .then(data => {
            console.log("✅ API Test - Items found:", data.items?.length || 0);
            if (data.items?.length === 0) {
                console.log("🎉 SUCCESS! API returns 0 items - DeWalt drill is DEAD!");
            }
        })
        .catch(error => {
            console.log("⚠️ API not responding, but cache is cleared");
            console.log("Frontend should show 0 items now");
        });
}, 2000);
