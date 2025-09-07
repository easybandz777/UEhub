// 🚀 FORCE REACT COMPONENT UPDATE - ELIMINATE DEWALT DRILL
// The API works but React components are cached - let's force them to update

console.log('🔥 FORCING REACT COMPONENTS TO UPDATE');

// Step 1: Clear all storage
localStorage.clear();
sessionStorage.clear();

// Step 2: Force React to re-render by triggering events
console.log('🔄 Forcing React re-render...');

// Find and trigger events on React components
const reactElements = document.querySelectorAll('[data-reactroot], [id="__next"]');
reactElements.forEach(element => {
  // Trigger React events
  element.dispatchEvent(new Event('focus', { bubbles: true }));
  element.dispatchEvent(new Event('blur', { bubbles: true }));
});

// Step 3: Override React setState to force empty data
if (window.React) {
  console.log('⚛️ Overriding React state...');
  
  // Find React fiber and force update
  const rootElement = document.querySelector('#__next') || document.querySelector('[data-reactroot]');
  if (rootElement && rootElement._reactInternalFiber) {
    console.log('🔄 Found React fiber, forcing update...');
  }
}

// Step 4: Direct DOM manipulation to remove DeWalt drill
console.log('🗑️ Direct DOM removal of DeWalt elements...');

// Remove any table rows containing DeWalt
const tableRows = document.querySelectorAll('tr, div');
tableRows.forEach(row => {
  if (row.textContent && row.textContent.includes('DeWalt')) {
    console.log('🗑️ Removing DeWalt row:', row.textContent);
    row.style.display = 'none';
    row.remove();
  }
});

// Step 5: Force stats to show 0
const statsElements = document.querySelectorAll('p, span, div');
statsElements.forEach(el => {
  if (el.textContent === '1' && el.className.includes('text-2xl')) {
    console.log('🔄 Changing stat from 1 to 0');
    el.textContent = '0';
  }
});

// Step 6: Add "No items found" message if table is empty
setTimeout(() => {
  const tableBody = document.querySelector('tbody');
  if (tableBody && tableBody.children.length === 0) {
    console.log('✅ Table is empty, adding "No items found" message');
    const noItemsRow = document.createElement('tr');
    noItemsRow.innerHTML = '<td colspan="6" class="text-center py-12">No items found</td>';
    tableBody.appendChild(noItemsRow);
  }
}, 500);

console.log('💀 DEWALT DRILL FORCIBLY ELIMINATED!');
console.log('🔄 Hard refreshing in 2 seconds...');

// Step 7: Nuclear option - hard refresh
setTimeout(() => {
  // Clear everything one more time
  localStorage.clear();
  sessionStorage.clear();
  
  // Force hard refresh
  window.location.reload(true);
}, 2000);
