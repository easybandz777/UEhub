// Create admin user with proper password validation
const API_BASE = 'https://uehub.fly.dev/v1';

async function createAdminUser() {
    console.log('👤 Creating Admin User...\n');
    
    try {
        // Test with stronger password
        console.log('1. Creating admin user with strong password...');
        const adminResponse = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: 'admin@uehub.com',
                name: 'Admin User',
                password: 'Admin123!@#',  // Strong password with uppercase, lowercase, numbers, symbols
                role: 'superadmin'
            })
        });
        
        console.log(`   - Status: ${adminResponse.status}`);
        
        if (adminResponse.ok) {
            const adminData = await adminResponse.json();
            console.log('✅ Admin user created successfully!');
            console.log(`   - ID: ${adminData.id}`);
            console.log(`   - Email: ${adminData.email}`);
            console.log(`   - Role: ${adminData.role}`);
            
            // Test login immediately
            console.log('\n2. Testing admin login...');
            const loginResponse = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: 'admin@uehub.com',
                    password: 'Admin123!@#'
                })
            });
            
            if (loginResponse.ok) {
                const loginData = await loginResponse.json();
                console.log('✅ Admin login successful!');
                console.log(`   - Access token: ${loginData.access_token.substring(0, 30)}...`);
                console.log(`   - User: ${loginData.user.email} (${loginData.user.role})`);
                console.log(`   - Expires in: ${loginData.expires_in} seconds`);
                
                // Save credentials for testing
                console.log('\n🔑 Admin Credentials Created:');
                console.log('   Email: admin@uehub.com');
                console.log('   Password: Admin123!@#');
                console.log('   Role: superadmin');
                
                return {
                    success: true,
                    credentials: {
                        email: 'admin@uehub.com',
                        password: 'Admin123!@#'
                    },
                    token: loginData.access_token,
                    user: loginData.user
                };
                
            } else {
                const loginError = await loginResponse.json();
                console.log(`❌ Admin login failed: ${loginResponse.status}`);
                console.log(`   - Error: ${loginError.detail}`);
                return { success: false, error: 'Login failed after creation' };
            }
            
        } else if (adminResponse.status === 400) {
            const errorData = await adminResponse.json();
            if (errorData.detail === 'Email already registered') {
                console.log('ℹ️  Admin user already exists, testing login...');
                
                // Try to login with existing admin
                const loginResponse = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: 'admin@uehub.com',
                        password: 'Admin123!@#'
                    })
                });
                
                if (loginResponse.ok) {
                    const loginData = await loginResponse.json();
                    console.log('✅ Existing admin login successful!');
                    console.log(`   - User: ${loginData.user.email} (${loginData.user.role})`);
                    
                    return {
                        success: true,
                        credentials: {
                            email: 'admin@uehub.com',
                            password: 'Admin123!@#'
                        },
                        token: loginData.access_token,
                        user: loginData.user
                    };
                } else {
                    console.log('❌ Existing admin login failed - password might be different');
                    
                    // Try with the old password
                    const oldLoginResponse = await fetch(`${API_BASE}/auth/login`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: 'admin@uehub.com',
                            password: 'admin123'
                        })
                    });
                    
                    if (oldLoginResponse.ok) {
                        const loginData = await oldLoginResponse.json();
                        console.log('✅ Login successful with old password!');
                        console.log('🔑 Use these credentials:');
                        console.log('   Email: admin@uehub.com');
                        console.log('   Password: admin123');
                        
                        return {
                            success: true,
                            credentials: {
                                email: 'admin@uehub.com',
                                password: 'admin123'
                            },
                            token: loginData.access_token,
                            user: loginData.user
                        };
                    } else {
                        return { success: false, error: 'Cannot login with any known password' };
                    }
                }
            } else {
                console.log(`❌ Admin creation failed: ${errorData.detail}`);
                return { success: false, error: errorData.detail };
            }
        } else {
            const errorText = await adminResponse.text();
            console.log(`❌ Admin creation failed: ${adminResponse.status}`);
            console.log(`   - Error: ${errorText}`);
            return { success: false, error: errorText };
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        return { success: false, error: error.message };
    }
}

// Run the function
createAdminUser().then(result => {
    if (result.success) {
        console.log('\n🎉 SUCCESS! You can now login to the website with:');
        console.log(`   Email: ${result.credentials.email}`);
        console.log(`   Password: ${result.credentials.password}`);
    } else {
        console.log(`\n❌ FAILED: ${result.error}`);
        console.log('The database connection issues need to be fixed on the server side.');
    }
});
