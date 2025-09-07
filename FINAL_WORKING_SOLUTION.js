// 🎯 FINAL WORKING SOLUTION - Run this in your browser console
// This will fix the remaining API issues and make the save function work

console.log('🚀 LOADING FINAL WORKING SOLUTION...');

// 1. Complete fetch override with proper error handling
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
  // Convert all API calls to use the working Fly.io backend
  if (typeof url === 'string') {
    if (url.startsWith('/api/')) {
      url = url.replace('/api/', 'https://uehub.fly.dev/v1/');
      console.log('🔄 API call redirected to:', url);
    } else if (url.includes('localhost')) {
      url = url.replace(/http:\/\/localhost:\d+\/v1\//, 'https://uehub.fly.dev/v1/');
      console.log('🔄 Fixed localhost call to:', url);
    } else if (url.includes('u-ehub') && url.includes('vercel.app')) {
      // Fix any internal Vercel calls that might be broken
      if (url.includes('/api/')) {
        url = url.replace(/.*\/api\//, 'https://uehub.fly.dev/v1/');
        console.log('🔄 Fixed Vercel API call to:', url);
      }
    }
  }
  
  // Add proper headers for CORS and content type
  const newOptions = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers
    },
    mode: 'cors'
  };
  
  console.log('📤 Making request to:', url, 'with options:', newOptions);
  
  return originalFetch.call(this, url, newOptions)
    .then(response => {
      console.log('📥 Response received:', response.status, response.statusText);
      return response;
    })
    .catch(error => {
      console.error('❌ Fetch error:', error);
      throw error;
    });
};

// 2. Override form submission with direct API call
function setupFormSubmission() {
  console.log('📝 Setting up enhanced form submission...');
  
  // Find and override all forms
  const forms = document.querySelectorAll('form');
  forms.forEach((form, index) => {
    console.log(`📋 Found form ${index + 1}`);
    
    // Remove existing event listeners
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);
    
    newForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      console.log('📤 Form submission intercepted!');
      
      // Get form data
      const formData = new FormData(newForm);
      const itemData = {
        sku: formData.get('sku') || document.querySelector('input[name="sku"]')?.value || 'TEST-001',
        name: formData.get('name') || document.querySelector('input[name="name"]')?.value || 'Test Item',
        location: formData.get('location') || document.querySelector('input[name="location"]')?.value || 'Warehouse A',
        barcode: formData.get('barcode') || document.querySelector('input[name="barcode"]')?.value || '',
        qty: parseInt(formData.get('qty') || document.querySelector('input[name="qty"]')?.value || '1'),
        min_qty: parseInt(formData.get('min_qty') || document.querySelector('input[name="min_qty"]')?.value || '0')
      };
      
      console.log('📦 Item data to send:', itemData);
      
      // Show loading state
      const submitBtn = newForm.querySelector('button[type="submit"]') || newForm.querySelector('.create-btn');
      const originalText = submitBtn?.textContent;
      if (submitBtn) {
        submitBtn.textContent = 'Creating...';
        submitBtn.disabled = true;
      }
      
      try {
        console.log('📤 Sending POST request to create item...');
        
        const response = await fetch('https://uehub.fly.dev/v1/inventory', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(itemData)
        });
        
        console.log('📥 Response status:', response.status);
        
        if (response.ok) {
          const result = await response.json();
          console.log('✅ SUCCESS! Item created:', result);
          
          // Show success message
          const successDiv = document.createElement('div');
          successDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #10b981;
            color: white;
            padding: 20px;
            border-radius: 12px;
            z-index: 10000;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            text-align: center;
          `;
          successDiv.innerHTML = `
            <div>✅ SUCCESS!</div>
            <div style="margin-top: 10px; font-size: 14px;">Item "${itemData.name}" created successfully!</div>
            <div style="margin-top: 10px; font-size: 12px;">Saved to Neon database via Fly.io</div>
          `;
          document.body.appendChild(successDiv);
          
          // Remove success message and reload after 3 seconds
          setTimeout(() => {
            successDiv.remove();
            console.log('🔄 Reloading page to show new item...');
            window.location.reload();
          }, 3000);
          
        } else {
          const errorText = await response.text();
          console.error('❌ Failed to create item:', response.status, errorText);
          
          // Show error message
          const errorDiv = document.createElement('div');
          errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #ef4444;
            color: white;
            padding: 20px;
            border-radius: 12px;
            z-index: 10000;
            font-weight: bold;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            text-align: center;
          `;
          errorDiv.innerHTML = `
            <div>❌ Error ${response.status}</div>
            <div style="margin-top: 10px; font-size: 14px;">${errorText}</div>
            <button onclick="this.parentElement.remove()" style="margin-top: 10px; padding: 5px 10px; background: white; color: #ef4444; border: none; border-radius: 4px; cursor: pointer;">Close</button>
          `;
          document.body.appendChild(errorDiv);
        }
      } catch (error) {
        console.error('❌ Network error:', error);
        
        // Show network error message
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          background: #ef4444;
          color: white;
          padding: 20px;
          border-radius: 12px;
          z-index: 10000;
          font-weight: bold;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
          text-align: center;
        `;
        errorDiv.innerHTML = `
          <div>❌ Network Error</div>
          <div style="margin-top: 10px; font-size: 14px;">${error.message}</div>
          <button onclick="this.parentElement.remove()" style="margin-top: 10px; padding: 5px 10px; background: white; color: #ef4444; border: none; border-radius: 4px; cursor: pointer;">Close</button>
        `;
        document.body.appendChild(errorDiv);
      } finally {
        // Restore button state
        if (submitBtn) {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
        }
      }
    });
  });
}

// 3. Test API connectivity
async function testAPIConnectivity() {
  console.log('🧪 Testing API connectivity...');
  
  try {
    // Test stats endpoint
    const statsResponse = await fetch('https://uehub.fly.dev/v1/inventory/stats');
    const statsData = await statsResponse.json();
    console.log('✅ Stats API working:', statsData);
    
    // Test inventory list endpoint
    const inventoryResponse = await fetch('https://uehub.fly.dev/v1/inventory');
    const inventoryData = await inventoryResponse.json();
    console.log('✅ Inventory API working:', inventoryData);
    
    return true;
  } catch (error) {
    console.error('❌ API connectivity test failed:', error);
    return false;
  }
}

// 4. Main execution
async function main() {
  console.log('🎯 FINAL WORKING SOLUTION ACTIVATED!');
  
  // Test API connectivity
  const apiWorking = await testAPIConnectivity();
  
  if (apiWorking) {
    console.log('✅ API connectivity confirmed - setting up form handling');
    
    // Setup enhanced form submission
    setupFormSubmission();
    
    // Show ready message
    const readyDiv = document.createElement('div');
    readyDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #3b82f6;
      color: white;
      padding: 15px;
      border-radius: 8px;
      z-index: 9999;
      font-weight: bold;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      cursor: pointer;
    `;
    readyDiv.innerHTML = '🎯 READY! Click Create to save to database!';
    readyDiv.onclick = () => readyDiv.remove();
    document.body.appendChild(readyDiv);
    
    console.log('🎉 SETUP COMPLETE!');
    console.log('📋 Instructions:');
    console.log('  1. Fill out the form (or use the existing data)');
    console.log('  2. Click "Create" button');
    console.log('  3. Item will be saved to your Neon database');
    console.log('  4. Page will reload to show the new item');
    
  } else {
    console.error('❌ API connectivity failed - check backend status');
    
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ef4444;
      color: white;
      padding: 15px;
      border-radius: 8px;
      z-index: 9999;
      font-weight: bold;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    errorDiv.innerHTML = '❌ Backend API not responding';
    document.body.appendChild(errorDiv);
  }
}

// Run the solution
main();

console.log('🎯 FINAL WORKING SOLUTION LOADED!');
console.log('💡 The form is ready - click Create to save your item!');
