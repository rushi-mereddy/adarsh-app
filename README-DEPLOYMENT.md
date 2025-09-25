# 🚀 College Application Manager - Deployment Guide

## Quick Deployment Options

### Option 1: Manual Deployment (Simple)
```bash
# On your EC2 instance
git clone https://github.com/rushi-mereddy/adarsh-app.git
cd adarsh-app
chmod +x deploy.sh
./deploy.sh
```

### Option 2: GitHub Actions (Automated)
Set up automated deployment that triggers on every push to main branch.

## 📋 Prerequisites

### EC2 Instance Requirements
- **Instance Type**: t3.small or larger (minimum 2GB RAM)
- **OS**: Ubuntu 20.04 LTS or newer
- **Storage**: At least 20GB
- **Security Group**: Allow HTTP (80), HTTPS (443), SSH (22)

### Required Software on EC2
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Install Git
sudo apt install git -y

# Logout and login again for Docker permissions
```

## 🔧 GitHub Actions Setup (Recommended)

### Step 1: Fork/Clone Repository
1. Fork this repository to your GitHub account
2. Clone it to your local machine

### Step 2: Configure GitHub Secrets
Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `EC2_HOST` | Your EC2 public IP | `54.123.456.789` |
| `EC2_USERNAME` | EC2 username | `ubuntu` |
| `EC2_SSH_KEY` | Your private SSH key | Contents of `~/.ssh/id_rsa` |
| `POSTGRES_PASSWORD` | Database password | `SecureDBPassword123!` |
| `SESSION_SECRET` | Flask session secret | `your-super-secret-key-here` |
| `DOMAIN` | Your domain (optional) | `your-domain.com` |
| `REPO_URL` | Your repository URL | `https://github.com/rushi-mereddy/adarsh-app.git` |

### Step 3: Generate SSH Key (if you don't have one)
```bash
# On your local machine
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Copy public key to EC2
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@YOUR-EC2-IP

# Copy private key content for GitHub secret
cat ~/.ssh/id_rsa
```

### Step 4: Test Deployment
1. Push any change to your main branch
2. Go to Actions tab in GitHub
3. Watch the deployment process
4. Access your application at `http://YOUR-EC2-IP`

## 🛠 Manual Deployment

### Step 1: Connect to EC2
```bash
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
```

### Step 2: Clone and Deploy
```bash
# Clone repository
git clone https://github.com/rushi-mereddy/adarsh-app.git
cd adarsh-app

# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 3: Access Application
- **URL**: `http://YOUR-EC2-IP`
- **Admin Login**: `admin@college.edu` / `admin123`

## 🔒 Security Configuration

### Update Security Group
1. Go to EC2 Console → Security Groups
2. Select your instance's security group
3. Add inbound rules:
   - HTTP (80): Source `0.0.0.0/0`
   - HTTPS (443): Source `0.0.0.0/0`
   - SSH (22): Source `Your-IP/32`

### Change Default Passwords
1. Login as admin: `admin@college.edu` / `admin123`
2. Go to Profile → Change Password
3. Update to a strong password

## 🔍 Troubleshooting

### Check Service Status
```bash
cd /path/to/adarsh-app
docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs

# Specific service
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml logs nginx
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Complete Rebuild
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 Domain & SSL Setup (Optional)

### Configure Domain
1. Point your domain's A record to your EC2 IP
2. Update `.env` file:
   ```bash
   DOMAIN=your-domain.com
   ```

### Setup SSL with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Stop nginx temporarily
docker-compose -f docker-compose.prod.yml stop nginx

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/
sudo chown $USER:$USER ./ssl/*.pem

# Restart nginx
docker-compose -f docker-compose.prod.yml start nginx
```

## 📊 Monitoring

### Check Application Health
```bash
curl http://YOUR-EC2-IP/health
```

### Monitor Resource Usage
```bash
# Docker stats
docker stats

# System resources
htop
df -h
free -h
```

## 🔄 Updates

### Automatic Updates (GitHub Actions)
- Push changes to main branch
- GitHub Actions will automatically deploy

### Manual Updates
```bash
cd adarsh-app
git pull origin main
./deploy.sh
```

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify all secrets are set correctly
3. Ensure EC2 security group allows traffic
4. Check if services are running: `docker-compose ps`

## 🎯 Default Credentials

After deployment, use these credentials to login:
- **Admin**: `admin@college.edu` / `admin123`

**⚠️ Important**: Change the default admin password immediately after first login!
