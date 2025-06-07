# Production Deployment Guide

## Quick Deploy (Recommended)

### Step 1: Server Setup
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose git -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### Step 2: Deploy Application
```bash
# Clone repository
git clone <your-repo-url>
cd college-management-system

# Configure environment
cp .env.example .env
nano .env  # Edit with your values

# Deploy with one command
./deploy.sh
```

## Manual Production Setup

### 1. Environment Configuration

Create `.env` file:
```env
DATABASE_URL=postgresql://college_user:SECURE_PASSWORD_HERE@db:5432/college_db
SESSION_SECRET=VERY_SECURE_SECRET_KEY_CHANGE_THIS
POSTGRES_PASSWORD=SECURE_PASSWORD_HERE
FLASK_ENV=production
```

### 2. SSL Certificate (Optional)

For HTTPS, place SSL certificates in `ssl/` directory:
```bash
mkdir ssl
# Copy your certificate files:
# ssl/cert.pem
# ssl/key.pem
```

### 3. Production Deployment

```bash
# Production with Nginx
docker-compose -f docker-compose.prod.yml up -d

# Development/Testing
docker-compose up -d
```

## Cloud Platform Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Security Group: Allow ports 22, 80, 443

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose git -y
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Deploy Application**
   ```bash
   git clone <repository>
   cd college-management-system
   cp .env.example .env
   # Edit .env with production values
   ./deploy.sh
   ```

### DigitalOcean Droplet

1. **Create Droplet**
   - Ubuntu 22.04
   - 2GB RAM minimum
   - Enable monitoring

2. **Deploy**
   ```bash
   ssh root@your-droplet-ip
   apt update && apt upgrade -y
   apt install docker.io docker-compose git -y
   
   git clone <repository>
   cd college-management-system
   ./deploy.sh
   ```

### Google Cloud Platform

1. **Create Compute Engine Instance**
   ```bash
   gcloud compute instances create college-app \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud \
     --machine-type=e2-medium \
     --tags=http-server,https-server
   ```

2. **Setup Firewall**
   ```bash
   gcloud compute firewall-rules create allow-college-app \
     --allow tcp:80,tcp:443 \
     --source-ranges 0.0.0.0/0 \
     --tags http-server,https-server
   ```

## Domain and SSL Setup

### 1. Domain Configuration

Point your domain to server IP:
```
A record: @ -> YOUR_SERVER_IP
A record: www -> YOUR_SERVER_IP
```

### 2. Let's Encrypt SSL (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check application status
curl -f http://localhost:5000/health

# View logs
docker-compose logs -f web
docker-compose logs -f db
```

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U college_user college_db > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20241207.sql | docker-compose exec -T db psql -U college_user college_db
```

### Log Management

```bash
# Rotate logs (add to crontab)
0 2 * * * docker system prune -f

# Monitor disk usage
df -h
docker system df
```

## Performance Optimization

### 1. Database Optimization

Add to `init.sql`:
```sql
-- Performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attendance_composite 
ON attendance(date, student_id, status);

-- Vacuum and analyze
VACUUM ANALYZE;
```

### 2. Application Optimization

Update `docker-compose.prod.yml`:
```yaml
web:
  environment:
    - WORKERS=4  # CPU cores * 2
    - TIMEOUT=120
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '1.0'
```

### 3. Nginx Caching

Add to `nginx.conf`:
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Security Hardening

### 1. Firewall Setup

```bash
# UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Fail2Ban (Optional)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### 3. Regular Updates

```bash
# System updates
sudo apt update && sudo apt upgrade -y

# Container updates
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Database Connection Issues**
   ```bash
   docker-compose logs db
   docker-compose exec db psql -U college_user college_db
   ```

3. **Memory Issues**
   ```bash
   free -h
   docker system prune -f
   ```

### Performance Issues

1. **High CPU Usage**
   ```bash
   docker stats
   htop
   ```

2. **Database Slow Queries**
   ```bash
   docker-compose exec db psql -U college_user college_db
   \x on
   SELECT * FROM pg_stat_activity;
   ```

## Scaling

### Horizontal Scaling

Update `docker-compose.prod.yml`:
```yaml
web:
  scale: 3
  deploy:
    replicas: 3
```

### Load Balancer

Add to `nginx.conf`:
```nginx
upstream app {
    server web_1:5000;
    server web_2:5000;
    server web_3:5000;
}
```

## Backup Strategy

### Automated Backups

Create backup script:
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U college_user college_db > backups/db_$DATE.sql
tar -czf backups/uploads_$DATE.tar.gz static/uploads/
# Upload to cloud storage
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

This deployment guide ensures your college management system can be easily deployed and maintained in production environments.