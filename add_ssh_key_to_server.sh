# UE Hub SSH Key Addition Script
# Run this in your DigitalOcean Console

echo ' Adding SSH key for honestroofingcompany@gmail.com...'

# Create .ssh directory
mkdir -p ~/.ssh

# Add the SSH public key
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG4kqcy+/bUEsff7IbKDKzPb6WOGhA0PAY8bY5rw7Mf2 honestroofingcompany@gmail.com' >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Remove duplicates
sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp
mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys

echo ' SSH key added successfully!'
echo ' Test connection with: ssh -i ~/.ssh/id_ed25519_uehub root@echelonx.tech'
