# Инструкция по деплою проекта Movies

## Предварительные требования
- VPS сервер с Ubuntu 20.04 или новее
- Зарегистрированное доменное имя
- Минимум 1GB RAM
- SSH доступ к серверу

## Шаги по деплою

1. Скопируйте проект на сервер:
```bash
git clone 
cd Movies
```

2. Настройте переменные окружения:
- Откройте файл .env
- Замените все значения на свои
- Особенно важно заменить DJANGO_SECRET_KEY и пароли

3. Запустите скрипт деплоя:
```bash
chmod +x deploy.sh
./deploy.sh
```

4. После выполнения скрипта проверьте:
- Работу сайта по домену
- Работу SSL сертификата
- Статические файлы
- Загрузку медиа файлов

## Обслуживание

### Проверка логов:
```bash
# Логи Gunicorn
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/gunicorn/access.log

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Перезапуск сервисов:
```bash
sudo systemctl restart movies
sudo systemctl restart nginx
```

### Обновление проекта:
```bash
git pull
poetry install
poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
sudo systemctl restart movies
```

### Бэкап базы данных:
```bash
pg_dump movies_db > backup_$(date +%Y%m%d).sql
```

## Устранение неполадок

1. Если сайт не открывается:
- Проверьте статус сервисов:
```bash
sudo systemctl status movies
sudo systemctl status nginx
```

2. Если не работают статические файлы:
- Проверьте права доступа:
```bash
sudo chown -R www-data:www-data /home/cysco/Movies/staticfiles
sudo chown -R www-data:www-data /home/cysco/Movies/media
```

3. Проблемы с Poetry:
- Переустановите Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Контакты поддержки
При возникновении проблем обращайтесь:
- Email: your-email@example.com
- GitHub: https://github.com/your-username
