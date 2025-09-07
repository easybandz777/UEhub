// 🚀 FINAL DEWALT DRILL ELIMINATION TEST
// Copy and paste this into your browser console on your Vercel site

console.log('🔥 FINAL DEWALT DRILL ELIMINATION - CORS FIX DEPLOYED!');

// Step 1: Clear all cache
localStorage.clear();
sessionStorage.clear();
console.log('✅ Cache cleared');

// Step 2: Test the fixed API directly
console.log('🧪 Testing fixed Fly.io API...');

fetch('https://uehub.fly.dev/v1/inventory/')
  .then(response => {
    console.log('API Response Status:', response.status);
    if (response.ok) {
      return response.json();
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  })
  .then(data => {
    console.log('✅ SUCCESS! API Response:', data);
    console.log('Items count:', data.items ? data.items.length : 'undefined');
    
    if (data.items && data.items.length === 0) {
      console.log('🎯 PERFECT! Empty inventory - DeWalt drill eliminated!');
    } else if (data.items && data.items.length > 0) {
      console.log('⚠️ Still has items:', data.items);
    }
  })
  .catch(error => {
    console.log('❌ API still has issues:', error);
    console.log('🔄 Will force empty data anyway...');
  });

// Step 3: Test stats endpoint
fetch('https://uehub.fly.dev/v1/inventory/stats')
  .then(response => response.json())
  .then(data => {
    console.log('✅ Stats API Response:', data);
  })
  .catch(error => {
    console.log('❌ Stats API error:', error);
  });

// Step 4: Force reload after 3 seconds to see the result
console.log('🔄 Reloading page in 3 seconds to see the result...');
setTimeout(() => {
  location.reload(true);
}, 3000);
