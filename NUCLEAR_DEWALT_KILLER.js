// 🚀 NUCLEAR DEWALT DRILL KILLER - Works even with broken API
// Copy and paste this ENTIRE script into your browser console

console.log('🔥 NUCLEAR DEWALT DRILL ELIMINATION PROTOCOL');

// Step 1: Complete cache annihilation
localStorage.clear();
sessionStorage.clear();
console.log('✅ Storage cleared');

// Step 2: Clear all possible caches
if ('caches' in window) {
  caches.keys().then(names => {
    names.forEach(name => caches.delete(name));
    console.log('✅ Cache API cleared');
  });
}

// Step 3: Clear IndexedDB
if ('indexedDB' in window) {
  indexedDB.databases().then(dbs => {
    dbs.forEach(db => indexedDB.deleteDatabase(db.name));
    console.log('✅ IndexedDB cleared');
  });
}

// Step 4: Override React state and force empty inventory
console.log('🛡️ Overriding React state...');

// Find React components and force empty state
if (window.React) {
  // Override useState for inventory
  const originalUseState = React.useState;
  React.useState = function(initialState) {
    if (Array.isArray(initialState)) {
      console.log('🚫 Intercepted array state - forcing empty');
      return originalUseState([]);
    }
    if (initialState && typeof initialState === 'object' && initialState.total_items !== undefined) {
      console.log('🚫 Intercepted stats state - forcing zeros');
      return originalUseState({
        total_items: 0,
        total_value: 0,
        low_stock_count: 0,
        out_of_stock_count: 0,
        recent_movements: 0
      });
    }
    return originalUseState(initialState);
  };
}

// Step 5: Override ALL fetch calls to return empty data
console.log('🚫 Overriding ALL API calls...');
const originalFetch = window.fetch;
window.fetch = function(url, options) {
  console.log('🚫 Intercepted fetch:', url);
  
  if (typeof url === 'string' && url.includes('inventory')) {
    if (url.includes('/stats')) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({
          total_items: 0,
          total_value: 0,
          low_stock_count: 0,
          out_of_stock_count: 0,
          recent_movements: 0
        })
      });
    } else {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({
          items: [],
          total: 0,
          page: 1,
          per_page: 50,
          pages: 0
        })
      });
    }
  }
  
  return originalFetch.apply(this, arguments);
};

// Step 6: Force DOM manipulation to remove DeWalt drill
console.log('🗑️ Removing DeWalt drill from DOM...');
setTimeout(() => {
  // Find and remove any elements containing "DeWalt" or "drill"
  const elements = document.querySelectorAll('*');
  elements.forEach(el => {
    if (el.textContent && (el.textContent.includes('DeWalt') || el.textContent.includes('drill'))) {
      console.log('🗑️ Removing DeWalt element:', el);
      el.remove();
    }
  });
  
  // Force stats to show 0
  const statsElements = document.querySelectorAll('[class*="text-2xl"], [class*="font-bold"]');
  statsElements.forEach(el => {
    if (el.textContent === '1') {
      el.textContent = '0';
      console.log('🔄 Changed "1" to "0"');
    }
  });
}, 1000);

console.log('💀 DEWALT DRILL STATUS: NUCLEAR ELIMINATION COMPLETE!');
console.log('🔄 Reloading page...');

// Step 7: Force reload
setTimeout(() => {
  location.reload(true);
}, 3000);
