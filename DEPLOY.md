# Movies Project Deployment Guide

## Prerequisites
- VPS server with Ubuntu 20.04 or newer
- Registered domain name
- Minimum 1GB RAM
- SSH access to server

## Deployment Steps

1. Clone the project to server:
```bash
git clone 
cd Movies
```

2. Configure environment variables:
- Open .env file
- Replace all values with your own
- It's especially important to replace DJANGO_SECRET_KEY and passwords

3. Run deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

4. After script execution, verify:
- Website accessibility via domain
- SSL certificate functionality
- Static files serving
- Media files uploading

## Maintenance

### Checking logs:
```bash
# Gunicorn logs
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/gunicorn/access.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restarting services:
```bash
sudo systemctl restart movies
sudo systemctl restart nginx
```

### Project update:
```bash
git pull
poetry install
poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
sudo systemctl restart movies
```

### Database backup:
```bash
pg_dump movies_db > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

1. If the site is not accessible:
- Check services status:
```bash
sudo systemctl status movies
sudo systemctl status nginx
```

2. If static files are not working:
- Check file permissions:
```bash
sudo chown -R www-data:www-data /home/cysco/Movies/staticfiles
sudo chown -R www-data:www-data /home/cysco/Movies/media
```

3. Poetry issues:
- Reinstall Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Support Contacts
If you encounter any issues, please contact:
- Email: your-email@example.com
- GitHub: https://github.com/your-username
