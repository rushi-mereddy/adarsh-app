#!/bin/bash

# Minimal EC2 Setup Script for GitHub Actions Deployment
# Run this ONCE on your EC2 instance before using GitHub Actions

echo "🚀 Setting up EC2 instance for GitHub Actions deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Install Git
print_status "Installing Git..."
if ! command -v git &> /dev/null; then
    sudo apt install git -y
    print_status "Git installed successfully"
else
    print_status "Git is already installed"
fi

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

# Start and enable Docker
print_status "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group (requires logout/login to take effect)
sudo usermod -aG docker $USER

# Install curl (needed for health checks)
print_status "Installing curl..."
sudo apt install curl -y

# Create application directory
print_status "Creating application directory..."
mkdir -p /home/$USER/adarsh-app

print_status "✅ EC2 setup completed successfully!"
echo ""
echo -e "${YELLOW}⚠️ IMPORTANT:${NC} Please logout and login again for Docker permissions to take effect"
echo ""
echo -e "${GREEN}🎉 Your EC2 instance is now ready for GitHub Actions deployment!${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Logout and login again: exit, then ssh back in"
echo "2. Configure GitHub secrets in your repository"
echo "3. Push code to trigger automatic deployment"
echo ""
echo -e "${GREEN}GitHub Secrets needed:${NC}"
echo "- EC2_HOST: $(curl -s http://checkip.amazonaws.com)"
echo "- EC2_USERNAME: $USER"
echo "- EC2_SSH_KEY: (your private SSH key content)"
echo "- POSTGRES_PASSWORD: (choose a strong password)"
echo "- SESSION_SECRET: (choose a random secret)"
echo "- DOMAIN: $(curl -s http://checkip.amazonaws.com)"
