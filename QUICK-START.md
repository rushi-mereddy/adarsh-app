# 🚀 Adarsh College App - Quick Deployment Guide

## 🎯 Super Simple Deployment (2 Options)

### Option 1: Automated GitHub Actions (Recommended)

#### Step 1: Setup Your EC2 Instance (One Time)
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Run the automated setup
curl -fsSL https://raw.githubusercontent.com/rushi-mereddy/adarsh-app/main/setup-ec2.sh | bash

# Logout and login again for Docker permissions
exit
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
```

#### Step 2: Configure GitHub Secrets (One Time)
Go to: https://github.com/rushi-mereddy/adarsh-app/settings/secrets/actions

Add these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `EC2_HOST` | Your EC2 Public IP | `54.123.456.789` |
| `EC2_USERNAME` | `ubuntu` | `ubuntu` |
| `EC2_SSH_KEY` | Your private SSH key content | Copy from `~/.ssh/id_rsa` |
| `POSTGRES_PASSWORD` | Strong database password | `AdarshCollege2024!` |
| `SESSION_SECRET` | Random secret key | `adarsh-super-secret-key-2024` |
| `DOMAIN` | Your domain or EC2 IP | `your-domain.com` |

#### Step 3: Deploy (Automatic!)
```bash
# Just push any change to trigger deployment
git add .
git commit -m "Deploy Adarsh College App"
git push origin main
```

**That's it!** GitHub Actions will automatically:
- ✅ Test the code
- ✅ Deploy to your EC2
- ✅ Setup database
- ✅ Create admin user
- ✅ Start all services

---

### Option 2: Manual Deployment (Also Simple)

#### One Command Setup + Deploy:
```bash
# SSH into your EC2
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Setup EC2 (one time only)
curl -fsSL https://raw.githubusercontent.com/rushi-mereddy/adarsh-app/main/setup-ec2.sh | bash

# Logout and login for Docker permissions
exit
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Clone and deploy
git clone https://github.com/rushi-mereddy/adarsh-app.git
cd adarsh-app
chmod +x deploy.sh
./deploy.sh
```

---

## 🎉 After Deployment

### Access Your Application:
- **URL**: `http://YOUR-EC2-IP`
- **Admin Login**: `admin@college.edu` / `admin123`

### Important Security Steps:
1. **Change Admin Password**: Login → Profile → Change Password
2. **Update Security Group**: Allow HTTP (80) and HTTPS (443) in AWS Console

---

## 🔧 Quick Commands

### Check if everything is running:
```bash
cd adarsh-app
docker-compose -f docker-compose.prod.yml ps
```

### View logs:
```bash
docker-compose -f docker-compose.prod.yml logs web
```

### Restart services:
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update application (manual):
```bash
cd adarsh-app
git pull origin main
./deploy.sh
```

---

## 🆘 Troubleshooting

### If deployment fails:
1. Check GitHub Actions logs in the Actions tab
2. SSH into EC2 and check: `docker-compose -f docker-compose.prod.yml logs`
3. Ensure Security Group allows HTTP (port 80)
4. Verify all GitHub secrets are set correctly

### Common Issues:
- **Can't access app**: Check AWS Security Group settings
- **Database errors**: Wait 30 seconds and try again (PostgreSQL startup)
- **Permission denied**: Make sure you logged out/in after Docker installation

---

## 🎯 What You Get

After successful deployment:
- ✅ **Professional College Management System**
- ✅ **Student/Faculty/Admin Dashboards**  
- ✅ **Attendance Management**
- ✅ **Announcements & Notifications**
- ✅ **Banner Management**
- ✅ **Modern UI with Mobile Support**
- ✅ **Production-Ready Setup**
- ✅ **Automatic SSL Support (optional)**

## 📞 Need Help?

- **GitHub Issues**: https://github.com/rushi-mereddy/adarsh-app/issues
- **Check Logs**: `docker-compose -f docker-compose.prod.yml logs`
- **Restart Everything**: `./deploy.sh`

---

## 🚀 Ready to Deploy?

Choose your method:
- **GitHub Actions**: Follow Option 1 above
- **Manual**: Follow Option 2 above

Both methods will have your Adarsh College App running in under 10 minutes! 🎉
