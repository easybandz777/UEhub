// Test production database issues and create admin user
const API_BASE = 'https://uehub.fly.dev/v1';

async function testProductionDatabase() {
    console.log('🔍 Testing Production Database Issues...\n');
    
    try {
        // Test 1: Check if we can access any database endpoint
        console.log('1. Testing database-dependent endpoints...');
        
        const endpoints = [
            '/auth/register',
            '/inventory/',
            '/safety/checklists'
        ];
        
        for (const endpoint of endpoints) {
            try {
                console.log(`   Testing ${endpoint}...`);
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    method: endpoint === '/auth/register' ? 'POST' : 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: endpoint === '/auth/register' ? JSON.stringify({
                        email: 'test@example.com',
                        name: 'Test User',
                        password: 'TestPassword123!'
                    }) : undefined
                });
                
                console.log(`   - Status: ${response.status}`);
                
                if (response.status === 500) {
                    const errorText = await response.text();
                    console.log(`   - Error: ${errorText.substring(0, 200)}...`);
                } else if (response.ok) {
                    const data = await response.json();
                    console.log(`   - Success: ${JSON.stringify(data).substring(0, 100)}...`);
                } else {
                    const errorData = await response.json();
                    console.log(`   - Expected error: ${errorData.detail}`);
                }
            } catch (error) {
                console.log(`   - Network error: ${error.message}`);
            }
        }
        
        // Test 2: Try to create admin user via API
        console.log('\n2. Attempting to create admin user...');
        try {
            const adminResponse = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: 'admin@uehub.com',
                    name: 'Admin User',
                    password: 'admin123',
                    role: 'superadmin'
                })
            });
            
            console.log(`   - Admin creation status: ${adminResponse.status}`);
            
            if (adminResponse.ok) {
                const adminData = await adminResponse.json();
                console.log('   ✅ Admin user created successfully');
                
                // Test 3: Try to login with admin
                console.log('\n3. Testing admin login...');
                const loginResponse = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: 'admin@uehub.com',
                        password: 'admin123'
                    })
                });
                
                if (loginResponse.ok) {
                    const loginData = await loginResponse.json();
                    console.log('   ✅ Admin login successful!');
                    console.log(`   - Token: ${loginData.access_token.substring(0, 20)}...`);
                    console.log(`   - User: ${loginData.user.email} (${loginData.user.role})`);
                    
                    // Test 4: Test authenticated endpoints
                    console.log('\n4. Testing authenticated endpoints...');
                    const authHeaders = {
                        'Authorization': `Bearer ${loginData.access_token}`,
                        'Content-Type': 'application/json'
                    };
                    
                    // Test inventory
                    const inventoryResponse = await fetch(`${API_BASE}/inventory/`, {
                        headers: authHeaders
                    });
                    
                    console.log(`   - Inventory status: ${inventoryResponse.status}`);
                    if (inventoryResponse.ok) {
                        const inventoryData = await inventoryResponse.json();
                        console.log('   ✅ Inventory endpoint works!');
                        console.log(`   - Items: ${inventoryData.items?.length || 0}`);
                    }
                    
                    // Test user profile
                    const meResponse = await fetch(`${API_BASE}/auth/me`, {
                        headers: authHeaders
                    });
                    
                    console.log(`   - Profile status: ${meResponse.status}`);
                    if (meResponse.ok) {
                        const meData = await meResponse.json();
                        console.log('   ✅ User profile endpoint works!');
                        console.log(`   - User: ${meData.email}`);
                    }
                    
                } else {
                    const loginError = await loginResponse.text();
                    console.log(`   ❌ Admin login failed: ${loginResponse.status}`);
                    console.log(`   - Error: ${loginError}`);
                }
                
            } else {
                const adminError = await adminResponse.text();
                console.log(`   ❌ Admin creation failed: ${adminResponse.status}`);
                console.log(`   - Error: ${adminError.substring(0, 200)}...`);
            }
            
        } catch (error) {
            console.log(`   ❌ Admin creation error: ${error.message}`);
        }
        
        console.log('\n📊 Production Database Test Complete');
        
    } catch (error) {
        console.error('❌ Test failed with error:', error.message);
    }
}

// Run the test
testProductionDatabase();
