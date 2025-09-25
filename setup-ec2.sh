#!/bin/bash

# EC2 Setup Script for College Application Manager
# Run this script on a fresh Ubuntu EC2 instance

set -e

echo "🚀 Setting up EC2 instance for College Application Manager..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as ubuntu user."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_status "Docker is already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo apt install docker-compose -y
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose is already installed"
fi

# Install Git
print_status "Installing Git..."
if ! command -v git &> /dev/null; then
    sudo apt install git curl htop -y
    print_status "Git and utilities installed successfully"
else
    print_status "Git is already installed"
fi

# Install nginx for SSL setup (optional)
print_status "Installing Nginx (for SSL setup)..."
sudo apt install nginx certbot python3-certbot-nginx -y

# Create application directory
print_status "Creating application directory..."
mkdir -p /home/$USER/adarsh-app
cd /home/$USER/adarsh-app

# Set up firewall (optional but recommended)
print_status "Configuring UFW firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

print_status "✅ EC2 setup completed successfully!"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Clone your repository:"
echo "   git clone https://github.com/rushi-mereddy/adarsh-app.git /home/$USER/adarsh-app"
echo ""
echo "2. Run the deployment script:"
echo "   cd /home/$USER/adarsh-app"
echo "   chmod +x deploy.sh"
echo "   ./deploy.sh"
echo ""
echo "3. Configure your security group to allow HTTP (80) and HTTPS (443)"
echo ""
echo -e "${YELLOW}⚠️ Important:${NC} Please logout and login again for Docker permissions to take effect"
echo ""
echo -e "${GREEN}🎉 Setup completed! You can now deploy your application.${NC}"
