import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.templatetags.static import static
from .models import Record, Tag, Actor, Picture
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from logging import getLogger
from datetime import date
from django.http import Http404


logger = getLogger(__name__)


FILTERS = {
    "tag":   lambda qs, v: qs.filter(tags__name__iexact=v),
    "actor": lambda qs, v: qs.filter(actors__name__iexact=v),
    "year":  lambda qs, v: qs.filter(
    release_date__year=datetime.strptime(v, "%Y-%m-%d").year),
    "genre": lambda qs, v: qs.filter(genre__iexact=v),
}


# Create your views here.


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
        all_actor = Actor.objects.all()
        all_tag = Tag.objects.all()
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
                    "actors": all_actor,
                    "tags": all_tag,
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
                    "actors": all_actor,
                    "tags": all_tag,
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
                    "actors": all_actor,
                    "tags": all_tag,
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
                    "actors": all_actor,
                    "tags": all_tag,
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
                    "actors": all_actor,
                    "tags": all_tag,
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
        new_movie = Record.objects.create(
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
        for name in actors_name:
            actor, _ = Actor.objects.get_or_create(
                name=name.strip(), defaults={"age": None, "bio": "", "image": None}
            )
            new_movie.actors.add(actor)
        # Обрабатываем теги
        for tag_name in tags_name:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            new_movie.tags.add(tag)
    # Получаем список всех актеров и тегов для формы
    actors = Actor.objects.all()
    tags = Tag.objects.all()
    # Возвращаем все необходимые поля формы
    return render(request, "moviesapp/add_movie.html", {"actors": actors, "tags": tags})


@login_required
def movie_detail(request, movie_id: int):
    movie = get_object_or_404(
        Record.objects.select_related("picture").prefetch_related("actors", "tags"),
        pk=movie_id,
    )
    return render(request, "moviesapp/movie_detail.html", {"movie": movie})


@login_required
def edit_movie(request, movie_id: int) -> render:
    movie = get_object_or_404(Record, pk=movie_id)
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
        movie.save()
        # Обновление актеров и тегов
        actors_name = request.POST.getlist("actors")
        tags_name = request.POST.getlist("tags")
        # Обрабатываем актеров
        for actor_name in actors_name:
            actor, _ = Actor.objects.get_or_create(name=actor_name)
            movie.actors.add(actor)
        # Обрабатываем теги
        for tag_name in tags_name:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            movie.tags.add(tag)
        # Обновление постера
        picture_id = request.POST.get("picture_id")
        if picture_id:
            movie.picture_id = picture_id
            movie.save(update_fields=["picture_id"])
        return redirect("moviesapp:movie_detail", movie_id=movie.id)
    # Для GET-запроса — подготовка данных для формы
    all_actors = Actor.objects.all()
    all_tags = Tag.objects.all()
    picture = (
        Picture.objects.filter(id=movie.picture_id).first()
        if movie.picture_id
        else None
    )
    image_path = picture.image if picture else ""
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
            "selected_actors": movie.actors.all(),
            "selected_tags": movie.tags.all(),
            "picture_id": movie.picture_id,
            "image_path": image_path,
            "edit_mode": True,
            "movie_id": movie.id,
        },
    )


@login_required
def delete_movie(request, movie_id: int) -> render:
    movie = get_object_or_404(Record, pk=movie_id)
    if request.method == "POST":
        movie.delete()
        return redirect("moviesapp:main")
    return render(request, "moviesapp/confirm_delete.html", {"movie": movie})


def pictures_list(request) -> render:

    pictures = Picture.objects.all()
    formatted_pictures = []
    for picture in pictures:
        image_path = picture.image
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


def picture_detail(request, picture_id: int) -> render:
    # Получаем изображение по ID
    picture = get_object_or_404(Picture, pk=picture_id)

    image_path = picture.image
    # Найти фильм, если это постер к фильму
    movie = Record.objects.filter(picture_id=picture.id).first()
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
def delete_picture(request, picture_id: int) -> render:
    picture = Picture.objects.get(id=picture_id)
    if not picture:
        return render(
            request, "moviesapp/picture_not_found.html", {"picture_id": picture_id}
        )

    # Проверяем, связано ли изображение с фильмом
    movie = Record.objects.filter(picture_id=picture_id).first()
    if movie:
        messages.error(request, "Нельзя удалить изображение, связанное с фильмом.")
        return redirect("moviesapp:picture_detail", picture_id=picture_id)

    if request.method == "POST":
        try:
            picture.delete()
            return redirect("moviesapp:pictures_list")
        except Exception as e:
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
        picture = Picture(name=name, image=image_path)
        picture.save()
        messages.success(request, "Изображение успешно добавлено!")
        return redirect("moviesapp:pictures_list")
    return render(request, "moviesapp/add_picture.html")





def main(request) -> render:
    # Получаем все фильмы
    movies = Record.objects.all()

    # Форматируем данные для шаблона
    formatted_movies = []

    for movie in movies:
        picture = Picture.objects.filter(id=movie.picture_id).first()

        if picture and picture.image:
            image_path = picture.image
        else:
            image_path = static("movies/default/default_posters.jpg")

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
                "actors": [actor.name for actor in movie.actors.all()],
                "tags": [tag.name for tag in movie.tags.all()],
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
        "tags": Tag.objects.all()[:10],  # Получаем первые 10 тегов
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

        picture, _ = Picture.objects.get_or_create(name=filename, image=image_path)

        return JsonResponse(
            {
                "success": True,
                "picture_id": picture.id,
                "image_path": image_path,
                "filename": filename,
            }
        )

    return JsonResponse({"success": False, "error": "No image uploaded"}, status=400)


def movies_filter(request, filter_type, value):
    """
    Универсальный фильтр фильмов по тегу, актёру, году или жанру.
    """
    print(value)
    try:
        movies = FILTERS[filter_type](Record.objects.all(), value)
    except KeyError:
        raise Http404("Неизвестный критерий фильтрации")

    formatted_movies = []
    for movie in movies:
        picture = (
            Picture.objects.filter(id=movie.picture_id).first()
            if movie.picture_id
            else None
        )
        if picture and picture.image:
            image_path = picture.image
        else:
            image_path = static("movies/defaults/default_posters.jpg")
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
                "actors": [actor.name for actor in movie.actors.all()],
                "tags": [tag.name for tag in movie.tags.all()],
                "picture": {
                    "id": picture.id if picture else None,
                    "name": picture.name if picture else None,
                    "image_path": image_path,  # Используем image_path из Picture
                },
            }
        )

    context = {
        "movies": formatted_movies,
        "filter_type": filter_type,
        "value": value,
    }
    return render(request, "moviesapp/movies_filter.html", context)