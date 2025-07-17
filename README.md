# Movies - Веб-приложение для каталогизации фильмов

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Веб-приложение для создания и управления каталогом фильмов с возможностью добавления описаний, постеров, тегов и информации об актерах.

## Основные возможности

- 🎬 Каталогизация фильмов с подробным описанием
- 🏷️ Система тегов для удобной навигации
- 👥 Управление информацией об актерах
- 🖼️ Загрузка и управление постерами фильмов
- 🔍 Поиск по названию, описанию, тегам и актерам
- 📱 Адаптивный дизайн
- 👤 Система аутентификации пользователей
- 📊 Пагинация результатов
- 🔒 Разграничение прав доступа

## Технологический стек

- **Backend**: Python 3.12, Django 5.0
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Dependency Management**: Poetry
- **Deployment**: Gunicorn, Nginx

## Установка и запуск

### Предварительные требования

- Python 3.12+
- Poetry
- PostgreSQL

### Локальная установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Noma9d/Movies.git
cd Movies
```

2. Установите зависимости с помощью Poetry:
```bash
poetry install
```

3. Создайте файл .env в корневой директории:
```env
DJANGO_SETTINGS_MODULE=movies.settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DB_NAME=movies_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

4. Примените миграции:
```bash
poetry run python manage.py migrate
```

5. Создайте суперпользователя:
```bash
poetry run python manage.py createsuperuser
```

6. Запустите сервер разработки:
```bash
poetry run python manage.py runserver
```

### Использование Docker (опционально)

```bash
docker-compose up --build
```

## Структура проекта

```
Movies/
├── movies/                  # Основной проект Django
│   ├── moviesapp/          # Основное приложение
│   │   ├── static/         # Статические файлы
│   │   ├── templates/      # HTML шаблоны
│   │   ├── models.py       # Модели данных
│   │   └── views.py        # Представления
│   └── movies/             # Настройки проекта
├── static/                 # Общие статические файлы
├── media/                  # Загружаемые медиа файлы
├── pyproject.toml         # Конфигурация Poetry
└── README.md
```

## API Endpoints

### Фильмы
- `GET /` - Главная страница со списком фильмов
- `GET /movies/<id>/` - Детальная информация о фильме
- `POST /movies/add/` - Добавление нового фильма
- `PUT /movies/<id>/edit/` - Редактирование фильма
- `DELETE /movies/<id>/delete/` - Удаление фильма

### Изображения
- `GET /pictures/` - Галерея изображений
- `GET /pictures/<id>/` - Детальный просмотр изображения
- `POST /pictures/add/` - Добавление нового изображения
- `DELETE /pictures/<id>/delete/` - Удаление изображения

### Поиск и фильтрация
- `GET /search/` - Поиск по фильмам
- `GET /filter/<type>/<value>/` - Фильтрация фильмов

## Тестирование

Запуск тестов:
```bash
poetry run python manage.py test
```

## Развертывание

Подробные инструкции по развертыванию находятся в файле [DEPLOY.md](DEPLOY.md).

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## Участие в проекте

1. Форкните репозиторий
2. Создайте ветку для новой функциональности
3. Внесите изменения
4. Отправьте пулл-реквест

## Авторы

- Noma9d - Основной разработчик

## Поддержка

При возникновении проблем создавайте issues в репозитории проекта или обращайтесь по электронной почте.

## Благодарности

- Спасибо команде Django за отличный фреймворк
- Всем участникам тестирования и разработки
