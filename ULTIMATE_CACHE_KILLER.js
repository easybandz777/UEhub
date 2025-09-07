// 🚀 ULTIMATE CACHE KILLER - Run this in your browser console
// This will COMPLETELY eliminate any cached DeWalt drill data

console.log('🔥 ULTIMATE CACHE KILLER ACTIVATED');

// 1. Clear ALL localStorage
localStorage.clear();
console.log('✅ localStorage cleared');

// 2. Clear ALL sessionStorage  
sessionStorage.clear();
console.log('✅ sessionStorage cleared');

// 3. Clear specific inventory keys (just in case)
const keysToKill = [
  'inventory-items',
  'inventory-stats', 
  'inventory-data',
  'cached-inventory',
  'tools',
  'dewalt',
  'drill'
];

keysToKill.forEach(key => {
  localStorage.removeItem(key);
  sessionStorage.removeItem(key);
});
console.log('✅ Specific inventory keys destroyed');

// 4. Clear IndexedDB (if any)
if ('indexedDB' in window) {
  indexedDB.databases().then(databases => {
    databases.forEach(db => {
      indexedDB.deleteDatabase(db.name);
    });
  });
  console.log('✅ IndexedDB cleared');
}

// 5. Clear Cache API (if supported)
if ('caches' in window) {
  caches.keys().then(names => {
    names.forEach(name => {
      caches.delete(name);
    });
  });
  console.log('✅ Cache API cleared');
}

// 6. Force reload without cache
console.log('🔄 FORCING HARD RELOAD...');
setTimeout(() => {
  location.reload(true);
}, 1000);

console.log('💀 DEWALT DRILL HAS BEEN ELIMINATED!');
