#!/bin/bash

# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3.12 python3.12-venv python3-pip nginx postgresql postgresql-contrib

# Установка Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Настройка переменных окружения
export PATH="/root/.local/bin:$PATH"

# Создание и настройка виртуального окружения с Poetry
cd /home/cysco/Movies
poetry install --no-dev

# Настройка Django
poetry run python manage.py collectstatic --noinput
poetry run python manage.py migrate

# Настройка Gunicorn
sudo mkdir -p /var/log/gunicorn
sudo chown -R www-data:www-data /var/log/gunicorn

# Создание systemd сервиса
sudo tee /etc/systemd/system/movies.service << EOF
[Unit]
Description=Movies Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/cysco/Movies
ExecStart=/root/.local/bin/poetry run gunicorn --workers 3 --bind unix:/run/movies.sock movies.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Настройка Nginx
sudo tee /etc/nginx/sites-available/movies << EOF
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    location /static/ {
        root /home/cysco/Movies;
    }

    location /media/ {
        root /home/cysco/Movies;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/movies.sock;
    }
}
EOF

# Активация Nginx конфигурации
sudo ln -s /etc/nginx/sites-available/movies /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Запуск Django приложения
sudo systemctl start movies
sudo systemctl enable movies

# Настройка SSL с Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

echo "Деплой завершен!"
