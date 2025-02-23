# Deployment Guide for Exxas-Planner Sync Application

This guide explains how to deploy the Exxas-Planner Sync application on Ubuntu as a system service.

## Prerequisites

- Ubuntu 20.04 or newer
- A non-root user with sudo privileges
- Python 3 or newer

## 1. System Preparation

First, update your system and install required dependencies:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-dev build-essential libpq-dev nginx
```

## 2. Create Application User and Directory

Create a dedicated system user for the application:

```bash
sudo useradd -r -s /bin/false exxas_sync
sudo mkdir -p /opt/exxas_sync
sudo mkdir -p /var/log/exxas_sync
sudo chown -R exxas_sync:exxas_sync /opt/exxas_sync /var/log/exxas_sync
```

## 3. Prepare Requirements File

Before installing the application, create the requirements.txt file:

```bash
cat > requirements.txt << EOL
flask
flask-sqlalchemy
flask-login
flask-wtf
gunicorn
apscheduler
email-validator
psycopg2-binary
sqlalchemy
werkzeug
EOL
```

## 4. Install Application

Clone or copy your application files to the installation directory:

```bash
# As your regular user, copy application files
sudo cp -r ./* /opt/exxas_sync/
cd /opt/exxas_sync

# Create and activate virtual environment
sudo python3 -m venv venv
sudo chown -R exxas_sync:exxas_sync venv

# Install dependencies
sudo -u exxas_sync ./venv/bin/pip install -r requirements.txt
```

## 5. Create Configuration File

Create a configuration file for the application:

```bash
sudo mkdir -p /etc/exxas_sync
sudo nano /etc/exxas_sync/config.env
```

Add the following content (adjust as needed):

```env
FLASK_APP=main.py
FLASK_ENV=production
DATABASE_URL=sqlite:////opt/exxas_sync/instance/sync_app.db
SESSION_SECRET=your-secure-secret-key-here
```

Set proper permissions:

```bash
sudo chown -R exxas_sync:exxas_sync /etc/exxas_sync
sudo chmod 600 /etc/exxas_sync/config.env
```

## 6. Create Systemd Service

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/exxas_sync.service
```

Add the following content:

```ini
[Unit]
Description=Exxas-Planner Sync Application
After=network.target

[Service]
Type=simple
User=exxas_sync
Group=exxas_sync
WorkingDirectory=/opt/exxas_sync
EnvironmentFile=/etc/exxas_sync/config.env
ExecStart=/opt/exxas_sync/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 7. Configure Nginx as Reverse Proxy

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/exxas_sync
```

Add the following content:

```nginx
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain

    access_log /var/log/nginx/exxas_sync_access.log;
    error_log /var/log/nginx/exxas_sync_error.log;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/exxas_sync /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site if exists
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

## 8. Start and Enable Services

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Start and enable the application service
sudo systemctl start exxas_sync
sudo systemctl enable exxas_sync

# Verify service status
sudo systemctl status exxas_sync
```

## 9. Security Considerations

1. Set up SSL/TLS with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

2. Configure firewall:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 10. Maintenance

### Logging
- Application logs: `/var/log/exxas_sync/sync_app.log`
- Nginx access logs: `/var/log/nginx/exxas_sync_access.log`
- Nginx error logs: `/var/log/nginx/exxas_sync_error.log`
- System service logs: `sudo journalctl -u exxas_sync`

### Service Management
```bash
# Restart application
sudo systemctl restart exxas_sync

# View logs
sudo journalctl -u exxas_sync -f

# Stop application
sudo systemctl stop exxas_sync
```

### Updates
To update the application:
```bash
# Stop the service
sudo systemctl stop exxas_sync

# Update files
sudo cp -r /path/to/new/files/* /opt/exxas_sync/

# Update dependencies if needed
sudo -u exxas_sync /opt/exxas_sync/venv/bin/pip install -r /opt/exxas_sync/requirements.txt

# Restart the service
sudo systemctl restart exxas_sync
```

## Troubleshooting

1. Check service status:
```bash
sudo systemctl status exxas_sync
```

2. View application logs:
```bash
sudo tail -f /var/log/exxas_sync/sync_app.log
```

3. Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/exxas_sync_error.log
```

4. Verify permissions:
```bash
sudo ls -la /opt/exxas_sync
sudo ls -la /var/log/exxas_sync
```

5. Test application directly:
```bash
sudo -u exxas_sync /opt/exxas_sync/venv/bin/python /opt/exxas_sync/main.py