import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.templatetags.static import static
from .db import Record, Tag, Actor, Picture, session
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from sqlalchemy.orm import joinedload
from django.core.paginator import Paginator
from logging import getLogger
from datetime import date


logger = getLogger(__name__)

# Create your views here.


class Authorization():

    def __init__(self, request):
        self.request = request


    def register(request) -> render:
        if request.method == "POST":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            if not username or not password1 or not password2:
                messages.error(request, "Все поля обязательны для заполнения")
                return render(request, "moviesapp/register.html")

            if password1 != password2:
                messages.error(request, "Пароли не совпадают")
                return render(request, "moviesapp/register.html")

            if len(password1) < 8:
                messages.error(request, "Пароль должен быть не менее 8 символов")
                return render(request, "moviesapp/register.html")

            # Проверка на существование пользователя
            # Используем User.objects.filter() для проверки существования пользователя
            if User.objects.filter(username=username).exists():
                messages.error(request, "Пользователь с таким именем уже существует")
                return render(request, "moviesapp/register.html")

            user = User.objects.create_user(
                username=username, email=email, password=password1
            )
            user.is_active = False  # Делаем пользователя неактивным до подтверждения
            user.save()
            return redirect("moviesapp:main")

        return render(request, "moviesapp/register.html")
    
    def login_view(request) -> render:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("moviesapp:main")
            else:
                messages.error(request, "Неверное имя пользователя или пароль")
                return render(request, "moviesapp/login.html")

        return render(request, "moviesapp/login.html")
    
    def logout_view(request):
        logout(request)
        return redirect("moviesapp:main")
    

class Movies():

    def __init__(self, request):
        self.request = request

    @login_required
    def add_movie(request) -> render:
        if request.method == "POST":
            title = request.POST.get("title")
            description = request.POST.get("description")
            year = request.POST.get("year")
            genre = request.POST.get("genre")
            extension = request.POST.get("extension")
            size = request.POST.get("size")
            download_url = request.POST.get("download_url")
            actors_name = request.POST.getlist("actors")
            tags_name = request.POST.getlist("tags")

            if not title:
                messages.error(request, "Пожалуйста, укажите название фильма")
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "year": year,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "actors": session.query(Actor).all(),
                        "tags": session.query(Tag).all(),
                    },
                )

            # Валидация года выпуска
            if not year:
                messages.error(request, "Пожалуйста, укажите год выпуска фильма")
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "year": year,
                        "actors": session.query(Actor).all(),
                        "tags": session.query(Tag).all(),
                    },
                )

            try:
                # Преобразуем год в число и проверяем диапазон
                year_num = int(year)
                if year_num < 1900 or year_num > datetime.now().year:
                    raise ValueError()
            except (ValueError, TypeError):
                messages.error(
                    request,
                    "Неверный формат даты. Пожалуйста, укажите корректный год выпуска (от 1900 до 2099)",
                )
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "year": year,  # Возвращаем введенный год
                        "actors": session.query(Actor).all(),
                        "tags": session.query(Tag).all(),
                    },
                )

            if extension not in ["mp4", "mkv", "avi", "mov", "flv"]:
                messages.error(
                    request,
                    "Неверный формат видео. Пожалуйста, выберите один из следующих форматов: mp4, mkv, avi, mov, flv",
                )
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "year": year,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "actors": session.query(Actor).all(),
                        "tags": session.query(Tag).all(),
                    },
                )


            if not size or not size.isdigit() or int(size) <= 0:
                messages.error(request, "Пожалуйста, укажите корректный размер файла")
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "year": year,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "actors": session.query(Actor).all(),
                        "tags": session.query(Tag).all(),
                    },
                )

            if not download_url:
                messages.error(request, "Пожалуйста, укажите ссылку для скачивания фильма")
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "year": year,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "actors": actors_name,
                        "tags": tags_name,
                    },
                )

            # Получаем ID изображения из формы
            picture_id = request.POST.get("picture_id")
            if not picture_id:
                messages.error(request, "Пожалуйста, загрузите постер фильма")
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "year": year,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "actors": actors_name,
                        "tags": tags_name,
                    },
                )


            # Создаем новый фильм
            new_movie = Record(
                title=title,
                description=description,
                release_date=f"{year}-01-01",
                genre=genre,
                extension=extension,
                size=size,
                download_url=download_url,
                picture_id=picture_id,
            )

            # Добавляем существующих актеров и теги
            actors = []
            tags = []

            # Обрабатываем актеров
            for actor_name in actors_name:
                actor = session.query(Actor).filter(Actor.name == actor_name).first()
                if actor:
                    actors.append(actor)
                else:
                    # Если это новое имя актера
                    new_actor = Actor(name=actor_name, age=None, bio=None, image_path=None)
                    session.add(new_actor)
                    session.flush()  # Получаем ID только что добавленного актера
                    actors.append(new_actor)


            # Обрабатываем теги
            for tag_name in tags_name:
                # Проверяем, существует ли тег с таким именем
                tag = session.query(Tag).filter(Tag.name == tag_name).first()
                if tag:
                    tags.append(tag)
                else:
                    # Если это новое имя тега
                    new_tag = Tag(name=tag_name)
                    session.add(new_tag)
                    session.flush()  # Получаем ID только что добавленного тега
                    tags.append(new_tag)

            # Устанавливаем связи
            new_movie.actors = actors
            new_movie.tags = tags

            try:
                # Сохраняем все изменения в базу
                session.add(new_movie)
                session.commit()
                return redirect("moviesapp:movies")
            except Exception as e:
                session.rollback()
                messages.error(request, f"Ошибка при сохранении данных: {str(e)}")
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    {
                        "title": title,
                        "description": description,
                        "year": year,
                        "genre": genre,
                        "extension": extension,
                        "size": size,
                        "download_url": download_url,
                        "actors": actors_name,
                        "tags": tags_name,
                    },
                )

        # Получаем список всех актеров и тегов для формы
        actors = session.query(Actor).all()
        tags = session.query(Tag).all()

        # Возвращаем все необходимые поля формы
        return render(request, "moviesapp/add_movie.html", {"actors": actors, "tags": tags})


    def movie_detail(request, movie_id: int) -> render:
        movie = Record.get_by_id(movie_id)
        if not movie:
            return render(request, "moviesapp/movie_not_found.html", {"movie_id": movie_id})

        picture = Picture.get_by_id(movie.picture_id) if movie.picture_id else None
        if picture and picture.image_path:
            # Убираем ведущий /static/, если есть
            if picture.image_path.startswith("/static/"):
                image_path = picture.image_path
            else:
                image_path = static(picture.image_path)
        else:
            image_path = static("movies/posters/default.jpg")

        data = {
            "movie": {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "release_date": movie.release_date.strftime("%Y-%m-%d"),
                "genre": movie.genre,
                "extension": movie.extension,
                "size": movie.size,
                "download_url": movie.download_url,
                "actors": [actor.name for actor in movie.actors],
                "tags": [tag.name for tag in movie.tags],
                "picture": {
                    "id": picture.id if picture else None,
                    "name": picture.name if picture else None,
                    "image_path": image_path,  # Используем image_path из Picture
                },
            }
        }

        return render(request, "moviesapp/movie_detail.html", data)


    @login_required
    def edit_movie(request, movie_id: int) -> render:
        movie = session.query(Record).get(movie_id)

        # Проверяем, существует ли фильм с таким ID
        if not movie:
            return render(request, "moviesapp/movie_not_found.html", {"movie_id": movie_id})

        if request.method == "POST":
            movie.title = request.POST.get("title")
            movie.description = request.POST.get("description")
            year = request.POST.get("year")
            movie.genre = request.POST.get("genre")
            movie.extension = request.POST.get("extension")
            movie.size = request.POST.get("size")
            movie.download_url = request.POST.get("download_url")
            try:
                movie.release_date = date(int(year), 1, 1)
            except (ValueError, TypeError):
                movie.release_date = None

            # Обновление актеров и тегов
            actors_name = request.POST.getlist("actors")
            tags_name = request.POST.getlist("tags")
            actors = []
            tags = []

            # Обрабатываем актеров
            for actor_name in actors_name:
                actor = session.query(Actor).filter(Actor.name == actor_name).first()
                if actor:
                    actors.append(actor)
                else:
                    # Если это новое имя актера
                    new_actor = Actor(name=actor_name, age=None, bio=None, image_path=None)
                    session.add(new_actor)
                    session.flush()  # Получаем ID только что добавленного актера
                    actors.append(new_actor)

            # Обрабатываем теги
            for tag_name in tags_name:
                # Проверяем, существует ли тег с таким именем
                tag = session.query(Tag).filter(Tag.name == tag_name).first()
                if tag:
                    tags.append(tag)
                else:
                    # Если это новое имя тега
                    new_tag = Tag(name=tag_name)
                    session.add(new_tag)
                    session.flush()  # Получаем ID только что добавленного тега
                    tags.append(new_tag)

            movie.actors = actors
            movie.tags = tags

            # Обновление постера
            picture_id = request.POST.get("picture_id")
            if picture_id:
                movie.picture_id = picture_id

            try:
                session.commit()
                return redirect("moviesapp:movie_detail", movie_id=movie.id)
            except Exception as e:
                session.rollback()
                messages.error(request, f"Ошибка при сохранении изменений: {str(e)}")

        # Для GET-запроса — подготовка данных для формы
        all_actors = session.query(Actor).all()
        all_tags = session.query(Tag).all()
        picture = Picture.get_by_id(movie.picture_id) if movie.picture_id else None
        image_path = picture.image_path if picture and picture.image_path else ""
        return render(
            request,
            "moviesapp/add_movie.html",
            {
                "title": movie.title,
                "description": movie.description,
                "year": movie.release_date.year if movie.release_date else "",
                "genre": movie.genre,
                "extension": movie.extension,
                "size": movie.size,
                "download_url": movie.download_url,
                "actors": all_actors,
                "tags": all_tags,
                "selected_actors": movie.actors,
                "selected_tags": movie.tags,
                "picture_id": movie.picture_id,
                "image_path": image_path,
                "edit_mode": True,
                "movie_id": movie.id,
            },
        )


    @login_required
    def delete_movie(request, movie_id:int) -> render:
        movie = Record.get_by_id(movie_id)
        if not movie:
            return render(request, "moviesapp/movie_not_found.html", {"movie_id": movie_id})

        if request.method == "POST":
            try:
                session.delete(movie)
                session.commit()
                return redirect("moviesapp:movies")
            except Exception as e:
                session.rollback()
                messages.error(request, f"Ошибка при удалении фильма: {str(e)}")

        return render(request, "moviesapp/confirm_delete.html", {"movie": movie})


class MoviePicture():

    def __init__(self, request):
        self.request = request

    def pictures_list(request) -> render:
        pictures = session.query(Picture).all()
        formatted_pictures = []
        for picture in pictures:
            image_path = getattr(picture, "image_path", None)
            if not image_path and hasattr(picture, "image"):
                image_path = (
                    picture.image.url if hasattr(picture.image, "url") else picture.image
                )
            formatted_pictures.append(
                {
                    "id": picture.id,
                    "name": picture.name,
                    "image_path": image_path,
                }
            )

        # Сортируем по ID в обратном порядке, чтобы новые изображения были первыми
        # Это может быть полезно, если вы хотите видеть новые изображения вверху списка
        formatted_pictures.sort(key=lambda x: x["id"], reverse=True)

        # Пагинация: 20 изображений на страницу
        paginator = Paginator(formatted_pictures, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        data = {
            "pictures": page_obj.object_list,  # Используем объект пагинации для получения текущей страницы
            "page_obj": page_obj,  # Передаем объект пагинации в контекст
        }

        return render(request, "moviesapp/pictures.html", data)


    def picture_detail(request, picture_id:int) -> render:

        # Получаем изображение по ID
        picture = session.query(Picture).get(picture_id)

        # Если изображение не найдено, возвращаем страницу с ошибкой
        if not picture:
            return render(
                request, "moviesapp/picture_not_found.html", {"picture_id": picture_id}
            )
        image_path = getattr(picture, "image_path", None)

        # Если image_path не задан, пытаемся получить его из атрибута image
        if not image_path and hasattr(picture, "image"):
            image_path = (
                picture.image.url if hasattr(picture.image, "url") else picture.image
            )

        # Найти фильм, если это постер к фильму
        movie = session.query(Record).filter(Record.picture_id == picture_id).first()

        data = {
            "picture": {
                "id": picture.id,
                "name": picture.name,
                "image_path": image_path,
                "movie": {"id": movie.id, "title": movie.title} if movie else None,
            }
        }

        return render(request, "moviesapp/picture_detail.html", data)


    @login_required
    def delete_picture(request, picture_id:int) -> render:
        picture = session.query(Picture).get(picture_id)
        if not picture:
            return render(
                request, "moviesapp/picture_not_found.html", {"picture_id": picture_id}
            )
        # Проверяем, связано ли изображение с фильмом
        movie = session.query(Record).filter(Record.picture_id == picture_id).first()
        if movie:
            messages.error(request, "Нельзя удалить изображение, связанное с фильмом.")
            return redirect("moviesapp:picture_detail", picture_id=picture_id)
        if request.method == "POST":
            try:
                session.delete(picture)
                session.commit()
                return redirect("moviesapp:pictures_list")
            except Exception as e:
                session.rollback()
                messages.error(request, f"Ошибка при удалении изображения: {str(e)}")
        return render(
            request, "moviesapp/confirm_delete_picture.html", {"picture": picture}
        )


    @login_required
    def add_picture(request) -> render:
        if request.method == "POST" and request.FILES.get("image"):
            image_file = request.FILES["image"]
            name = request.POST.get("name", image_file.name)
            # Сохраняем файл
            image_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "moviesapp",
                "static",
                "movies",
                "posters",
            )
            os.makedirs(image_dir, exist_ok=True)
            filename = image_file.name
            filepath = os.path.join(image_dir, filename)
            with open(filepath, "wb+") as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            image_path = f"/static/movies/posters/{filename}"
            picture = Picture(name=name, image_path=image_path)
            picture.save()
            messages.success(request, "Изображение успешно добавлено!")
            return redirect("moviesapp:pictures_list")
        return render(request, "moviesapp/add_picture.html")


class MovieTag():
    
    def __init__(self, request):
        self.request = request

    def tag_detail(request, tag_name: str) -> render:
        tag = Tag.get_by_name(tag_name)  # Получаем тег по имени

        # Получаем все фильмы, связанные с тегом
        records_tag = session.query(Record).options(joinedload(Record.tags)).all()

        movies = [record for record in records_tag if tag in record.tags]

        # Если тег не найден, возвращаем страницу с ошибкой
        if not tag:
            return render(request, "moviesapp/tag_not_found.html", {"tag_name": tag_name})

        formatted_movies = []

        for movie in movies:
            picture = Picture.get_by_id(movie.picture_id) if movie.picture_id else None
            if picture and picture.image_path:
                # Убираем ведущий /static/, если есть
                if picture.image_path.startswith("/static/"):
                    image_path = picture.image_path
                else:
                    image_path = static(picture.image_path)
            else:
                image_path = static("movies/posters/default.jpg")

            formatted_movies.append(
                {
                    "id": movie.id,
                    "title": movie.title,
                    "description": movie.description,
                    "release_date": movie.release_date.strftime("%Y-%m-%d"),
                    "genre": movie.genre,
                    "extension": movie.extension,
                    "size": movie.size,
                    "download_url": movie.download_url,
                    "actors": [actor.name for actor in movie.actors],
                    "tags": [tag.name for tag in movie.tags],
                    "picture": {
                        "id": picture.id if picture else None,
                        "name": picture.name if picture else None,
                        "image_path": image_path,  # Используем image_path из Picture
                    },
                }
            )

        data = {
            "tag": tag_name,
            "movies": formatted_movies,
        }

        return render(request, "moviesapp/tag_detail.html", data)

def main(request) -> render:
    # Получаем все фильмы
    movies = Record.get_all()

    # Форматируем данные для шаблона
    formatted_movies = []

    for movie in movies:
        picture = Picture.get_by_id(movie.picture_id) if movie.picture_id else None
        
        if picture and picture.image_path:
            # Убираем ведущий /static/, если есть
            if picture.image_path.startswith("/static/"):
                image_path = picture.image_path
            else:
                image_path = static(picture.image_path)
        else:
            image_path = static("movies/posters/default.jpg")
            
        formatted_movies.append(
            {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "release_date": movie.release_date.strftime("%Y-%m-%d"),
                "genre": movie.genre,
                "extension": movie.extension,
                "size": movie.size,
                "download_url": movie.download_url,
                "actors": [actor.name for actor in movie.actors],
                "tags": [tag.name for tag in movie.tags],
                "picture": {
                    "id": movie.picture.id if movie.picture else None,
                    "name": movie.picture.name if movie.picture else None,
                    "image_path": image_path,  # Используем image_path из Picture
                },
            }
        )

    formatted_movies.sort(
        key=lambda x: x["id"], reverse=True
    )  # Сортируем по ID в обратном порядке, чтобы новые фильмы были первыми

    paginator = Paginator(formatted_movies, 10)  # Пагинация: 10 фильмов на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    data = {
        "movies": page_obj.object_list,  # Используем объект пагинации для получения текущей страницы
        "tags": Tag.get_all()[:10],  # Получаем первые 10 тегов
        "page_obj": page_obj,  # Передаем объект пагинации в контекст
    }

    return render(request, "moviesapp/index.html", data)


def about(request) -> render:
    return render(
        request,
        "moviesapp/about.html",
    )


def contact(request) -> render:
    return render(request, "moviesapp/contact.html")


def movies(request):
    movies_years = []
    movies_title = []
    movies_description = []
    data = {
        "title": movies_title,
        "description": movies_description,
        "movies_yesrs": movies_years,
    }
    return render(request, "moviesapp/movies.html", context=data)
    

@login_required
def upload_image(request) -> JsonResponse:
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]

        # Проверка расширения файла
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        filename = image_file.name
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_extensions:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Недопустимый формат файла. Разрешены: jpg, jpeg, png, gif, bmp, webp",
                },
                status=400,
            )

        # Проверка размера файла (например, не более 5 МБ)
        max_size_mb = 5
        if image_file.size > max_size_mb * 1024 * 1024:
            return JsonResponse(
                {"success": False, "error": f"Размер файла превышает {max_size_mb} МБ"},
                status=400,
            )

        # Создаем директорию для изображений, если её нет
        image_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "moviesapp",
            "static",
            "movies",
            "posters",
        )
        os.makedirs(image_dir, exist_ok=True)

        # Сохраняем файл
        filepath = os.path.join(image_dir, filename)
        with open(filepath, "wb+") as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # Получаем относительный путь к файлу
        image_path = f"/static/movies/posters/{filename}"

        # Создаем новую запись для изображения
        picture = Picture(name=filename, image_path=image_path)
        picture.save()

        return JsonResponse(
            {
                "success": True,
                "picture_id": picture.id,
                "image_path": image_path,
                "filename": filename,
            }
        )

    return JsonResponse({"success": False, "error": "No image uploaded"}, status=400)
