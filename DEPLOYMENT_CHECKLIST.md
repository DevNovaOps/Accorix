# 🚀 **ACCORIX ERP - DEPLOYMENT CHECKLIST**

## 📋 **Pre-Deployment Checklist**

### 🔧 **System Requirements**
- [ ] Python 3.8+ installed
- [ ] MySQL/PostgreSQL database setup
- [ ] Web server (Nginx/Apache) configured
- [ ] SSL certificate installed
- [ ] Domain name configured
- [ ] Backup system in place

### 📦 **Dependencies**
- [ ] All packages from `requirements.txt` installed
- [ ] Virtual environment activated
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Media directory permissions set

### 🔐 **Security Configuration**
- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] Database credentials secured
- [ ] Stripe keys in environment variables
- [ ] HTTPS enforced
- [ ] CSRF protection enabled

### 💳 **Stripe Integration**
- [ ] Stripe account created and verified
- [ ] API keys obtained (test and live)
- [ ] Webhook endpoint configured
- [ ] Webhook secret added to environment
- [ ] Payment flow tested with test cards
- [ ] Production keys ready for go-live

---

## 🏗️ **DEPLOYMENT STEPS**

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx mysql-server -y

# Create application user
sudo useradd -m -s /bin/bash accorix
sudo usermod -aG sudo accorix
```

### Step 2: Application Deployment
```bash
# Switch to application user
sudo su - accorix

# Clone repository
git clone https://github.com/yourusername/accorix-erp.git
cd accorix-erp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Database Setup
```bash
# Create database
sudo mysql -u root -p
CREATE DATABASE accorix_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'accorix_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON accorix_erp.* TO 'accorix_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 4: Environment Configuration
```bash
# Create production .env file
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=accorix_erp
DB_USER=accorix_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=3306

# Stripe (use live keys for production)
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF
```

### Step 5: Django Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test server
python manage.py runserver 0.0.0.0:8000
```

### Step 6: Web Server Configuration
```nginx
# /etc/nginx/sites-available/accorix
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/accorix/accorix-erp/static/;
        expires 30d;
    }

    location /media/ {
        alias /home/accorix/accorix-erp/media/;
        expires 30d;
    }
}
```

### Step 7: Process Management
```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo tee /etc/systemd/system/accorix.service << EOF
[Unit]
Description=Accorix ERP Django Application
After=network.target

[Service]
User=accorix
Group=accorix
WorkingDirectory=/home/accorix/accorix-erp
Environment=PATH=/home/accorix/accorix-erp/venv/bin
ExecStart=/home/accorix/accorix-erp/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 accorix.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable accorix
sudo systemctl start accorix
```

---

## ✅ **POST-DEPLOYMENT VERIFICATION**

### Functional Testing
- [ ] Admin login works
- [ ] User creation and roles function
- [ ] Invoice creation and PDF generation
- [ ] Payment processing with Stripe
- [ ] Analytics dashboard loads
- [ ] Portal access for customers/vendors
- [ ] Webhook endpoint responds correctly

### Performance Testing
- [ ] Page load times acceptable
- [ ] Database queries optimized
- [ ] Static files served efficiently
- [ ] PDF generation performance
- [ ] Chart rendering speed

### Security Testing
- [ ] HTTPS enforced
- [ ] Admin panel secured
- [ ] File upload restrictions
- [ ] SQL injection protection
- [ ] XSS protection enabled
- [ ] CSRF tokens working

---

## 🔄 **MAINTENANCE TASKS**

### Daily
- [ ] Check application logs
- [ ] Monitor payment transactions
- [ ] Verify webhook deliveries
- [ ] Check system resources

### Weekly
- [ ] Database backup
- [ ] Update security patches
- [ ] Review error logs
- [ ] Performance monitoring

### Monthly
- [ ] Full system backup
- [ ] Security audit
- [ ] Dependency updates
- [ ] Stripe reconciliation

---

## 🆘 **EMERGENCY PROCEDURES**

### System Down
1. Check systemd service status
2. Review application logs
3. Verify database connectivity
4. Check disk space and memory
5. Restart services if needed

### Payment Issues
1. Check Stripe dashboard
2. Verify webhook deliveries
3. Review payment logs
4. Contact Stripe support if needed

### Data Recovery
1. Stop application services
2. Restore from latest backup
3. Run database migrations
4. Restart services
5. Verify data integrity

---

## 📞 **SUPPORT CONTACTS**

- **System Admin**: your-admin@company.com
- **Stripe Support**: https://support.stripe.com
- **Database Support**: your-db-admin@company.com
- **Emergency Contact**: +91-XXXXXXXXXX