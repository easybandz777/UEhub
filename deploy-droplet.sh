#!/bin/bash

# Deploy UE Hub to DigitalOcean Droplet
echo "🚀 Deploying UE Hub to DigitalOcean Droplet..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "📦 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install -y git

# Clone repository
echo "📥 Cloning repository..."
cd /opt
sudo git clone https://github.com/easybandz777/UEhub.git
sudo chown -R $USER:$USER UEhub
cd UEhub

# Create environment file
echo "🔧 Creating environment file..."
cat > backend/.env << EOF
DATABASE_URL=postgresql://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
ENVIRONMENT=production
LOG_LEVEL=INFO
API_PREFIX=/v1
ENABLE_DOCS=true
SECRET_KEY=RZdB5TRTPTGavzgPwT3pm4Q7ho-GtwMgZlEE9ydhvHw
NEXT_PUBLIC_STACK_PROJECT_ID=479dce56-2f32-47db-9d59-06ea9cc13e91
NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY=pck_3p4pvs6k8mc3j7efyg6x28v5csv3knc1sreme2cd93b58
STACK_SECRET_SERVER_KEY=ssk_m7fad91vv13axqqnmepga0zvgq5m7r3q1pqk8bjx2bw20
PORT=8080
EOF

# Build and run with Docker
echo "🐳 Building and starting application..."
cd backend
sudo docker build -t uehub-backend .
sudo docker run -d \
  --name uehub-backend \
  --restart unless-stopped \
  -p 80:8080 \
  --env-file .env \
  uehub-backend

# Install Nginx for reverse proxy
echo "🌐 Setting up Nginx..."
sudo apt install -y nginx

# Create Nginx config
sudo cat > /etc/nginx/sites-available/uehub << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/uehub /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "✅ Deployment complete!"
echo "🌐 Your API is available at: http://$(curl -s ifconfig.me)"
echo "🧪 Test endpoint: http://$(curl -s ifconfig.me)/v1/inventory/health"
echo ""
echo "📋 Next steps:"
echo "1. Point your domain to this droplet's IP"
echo "2. Setup SSL with Let's Encrypt (optional)"
echo "3. Update Vercel to use this backend URL"
