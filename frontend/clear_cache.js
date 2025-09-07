// Run this in browser console to completely clear cache
console.log("🗑️ Clearing all localStorage data...");

// Clear specific inventory keys
localStorage.removeItem('inventory-items');
localStorage.removeItem('inventory-stats');

// Clear all localStorage
localStorage.clear();

// Clear sessionStorage too
sessionStorage.clear();

// Clear IndexedDB if it exists
if ('indexedDB' in window) {
    indexedDB.databases().then(databases => {
        databases.forEach(db => {
            indexedDB.deleteDatabase(db.name);
        });
    });
}

console.log("✅ All cache cleared!");
console.log("🔄 Now refresh the page (Ctrl+F5 or Cmd+Shift+R)");

// Test API connection
fetch('http://localhost:8000/health')
    .then(response => response.json())
    .then(data => {
        console.log("✅ Backend is responding:", data);
    })
    .catch(error => {
        console.log("❌ Backend not responding:", error);
        console.log("🔧 Make sure backend is running on port 8000");
    });
