import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static
from .models import Record, Tag, Actor, Picture, TorrentFile, ScreeList
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from datetime import date
from django.http import Http404, FileResponse
from django.db.models import Count, Q, F
from .utils import save_uploaded_file
from django.conf import settings as django_settings



FILTERS = {
    "tag":   lambda qs, v: qs.filter(tags__name__iexact=v),
    "actor": lambda qs, v: qs.filter(actors__name__iexact=v),
    "year":  lambda qs, v: qs.filter(
    release_date__year=datetime.strptime(v, "%Y-%m-%d").year),
    "genre": lambda qs, v: qs.filter(genre__iexact=v),
}


# Определяем настройки по расширению
FILE_EXT = {
    # изображения
    ".jpg": {"dir": "movies/posters", "model": "Picture", "max_size_mb": 5},
    ".jpeg": {"dir": "movies/posters", "model": "Picture", "max_size_mb": 5},
    ".png": {"dir": "movies/posters", "model": "Picture", "max_size_mb": 5},
    ".gif": {"dir": "movies/posters", "model": "Picture", "max_size_mb": 5},
    ".bmp": {"dir": "movies/posters", "model": "Picture", "max_size_mb": 5},
    ".webp": {"dir": "movies/posters", "model": "Picture", "max_size_mb": 5},
    # торрент
    ".torrent": {"dir": "movies/torrents", "model": "TorrentFile", "max_size_mb": 10},
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
        picture = request.FILES.get("image")
        torrent_file = request.FILES.get("torrent")
        screenlist = request.FILES.getlist("screenlist")
        all_actor = Actor.objects.all()
        all_tag = Tag.objects.all()

        context = {
            "title": title,
            "description": description,
            "year": year,
            "genre": genre,
            "extension": extension,
            "size": size,
            "download_url": download_url,
            "actors": all_actor,
            "tags": all_tag,
        }


        if not title:
            messages.error(request, "Пожалуйста, укажите название фильма")
            return render(
                request,
                "moviesapp/add_movie.html",
                context,
            )
        # Валидация года выпуска
        if not year:
            messages.error(request, "Пожалуйста, укажите год выпуска фильма")
            return render(
                request,
                "moviesapp/add_movie.html",
                context,
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
                context,
            )
        if extension not in ["mp4", "mkv", "avi", "mov", "flv"]:
            messages.error(
                request,
                "Неверный формат видео. Пожалуйста, выберите один из следующих форматов: mp4, mkv, avi, mov, flv",
            )
            return render(
                request,
                "moviesapp/add_movie.html",
                context,
            )
        if not size or not size.isdigit() or int(size) <= 0:
            messages.error(request, "Пожалуйста, укажите корректный размер файла")
            return render(
                request,
                "moviesapp/add_movie.html",
                context,
            )
        if not download_url:
            messages.error(request, "Пожалуйста, укажите ссылку для скачивания фильма")
            return render(
                request,
                "moviesapp/add_movie.html",
                context,
            )
        
        if not picture:
            messages.error(request, "Пожалуйста, загрузите постер фильма")
            return render(
                request,
                "moviesapp/add_movie.html",
                context,
            )
        
        if picture:

            # Сохраняем загруженный файл
            result, error_message = save_uploaded_file(picture, FILE_EXT)
            if error_message:
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    context,
                )

            (filename, unique_picture_filename, relative_path) = result

            
            # Создаем запись в БД
            picture, _ = Picture.objects.get_or_create(
                name=filename, unique_name=unique_picture_filename, image=relative_path
            )
            picture_id = picture.id
        
        if torrent_file:
            # Сохраняем загруженный торрент файл
            result, error_message = save_uploaded_file(torrent_file, FILE_EXT)
            if error_message:
                messages.error(request, error_message)
                return render(
                    request,
                    "moviesapp/add_movie.html",
                    context,
                )
            
            (filename, unique_torrent_filename, relative_path) = result
            
            # Создаем запись в БД
            torrent_file, _ = TorrentFile.objects.get_or_create(
                name=filename, unique_name = unique_torrent_filename, file_path=relative_path
            )
            torrent_file_id = torrent_file.id

        if screenlist:

            screenlist_ids = []
            for screenlist_file in screenlist:
                # Сохраняем загруженный скринлист
                result, error_message = save_uploaded_file(screenlist_file, FILE_EXT, target_dir="movies/screenlists")
                if error_message:
                    return render(
                        request,
                        "moviesapp/add_movie.html",
                        context,
                    )
                (filename, unique_screenlist_filename, relative_path) = result
                # Создаем запись в БД для скринлиста
                screenlist, _ = ScreeList.objects.get_or_create(
                    name=filename, unique_name=unique_screenlist_filename, image_path=relative_path
                )       
                screenlist_ids.append(screenlist.id) 

            
        
        # Создаем новый фильм
        new_movie = Record.objects.create(
            title=title,
            description=description,
            release_date=f"{year}-01-01",
            genre=genre,
            extension=extension,
            size=size,
            download_url=download_url,
            picture_id=picture_id if picture else None,
            torrent_file_id=torrent_file_id if torrent_file else None,
        )

        if screenlist_ids:
            new_movie.screenlist.set(screenlist_ids)  # Устанавливаем связь со скринлистами

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



def movie_detail(request, movie_id: int):
    movie = get_object_or_404(
        Record.objects.select_related("picture", "torrent_file").prefetch_related("actors", "tags", "screenlist"),
        pk=movie_id,
    )
    return render(request, "moviesapp/movie_detail.html", {"movie": movie})


@login_required
def edit_movie(request, movie_id: int) -> render:
    movie = get_object_or_404(Record, pk=movie_id)
    old_picture = Picture.objects.filter(id=movie.picture_id).first() if movie.picture_id else None
    old_torrent_file = TorrentFile.objects.filter(id=movie.torrent_file_id).first() if movie.torrent_file_id else None
    old_screenlist = movie.screenlist.all()
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
        
        picture = request.FILES.get("image")
        if picture:

            if old_picture:
                old_picture.delete()  # Удаляем старое изображение, если оно есть
                

            # Сохраняем загруженный файл
            result, error_message = save_uploaded_file(picture, FILE_EXT)
            if error_message:
                messages.error(request, error_message)
                return redirect("moviesapp:edit_movie", movie_id=movie.id)

            (filename, unique_picture_name, relative_path) = result

            # Создаем или обновляем запись в БД
            picture_obj, _ = Picture.objects.get_or_create(
                name=filename, unique_name = unique_picture_name, image=relative_path
            )
            movie.picture = picture_obj
            movie.save()

        # Обновление торрент файла
        torrent_file = request.FILES.get("torrent")
        if torrent_file:
            # Удаляем старый торрент файл, если он есть
            if old_torrent_file:
                old_torrent_file.delete()

            # Сохраняем загруженный торрент файл
            result, error_message = save_uploaded_file(torrent_file, FILE_EXT)
            if error_message:
                messages.error(request, error_message)
                return redirect("moviesapp:edit_movie", movie_id=movie.id)

            (filename, unique_torrent_filename, relative_path) = result

            # Создаем или обновляем запись в БД
            torrent_file_obj, _ = TorrentFile.objects.get_or_create(
                name=filename, unique_name=unique_torrent_filename, file_path=relative_path
            )
            movie.torrent_file = torrent_file_obj
            movie.save()

        screen_list = request.FILES.getlist("screenlist")
        if screen_list:

            screen_list_ids = []

            for screenlist_file in old_screenlist:
                screenlist_file.delete()  # Удаляем все старые скринлисты, если они есть

            for screenlist in screen_list:
                # Сохраняем загруженный скринлист
                result, error_message = save_uploaded_file(screenlist, FILE_EXT, target_dir="movies/screenlists")
                if error_message:
                    messages.error(request, error_message)
                    return redirect("moviesapp:edit_movie", movie_id=movie.id)

                (filename, unique_screenlist_filename, relative_path) = result
                # Создаем или обновляем запись в БД для скринлиста
                screenlist, _ = ScreeList.objects.get_or_create(
                    name=filename, unique_name=unique_screenlist_filename, image_path=relative_path
                )
                screen_list_ids.append(screenlist.id)

            movie.screenlist.set(screen_list_ids)  # Устанавливаем связь со скринлистами

        return redirect("moviesapp:movie_detail", movie_id=movie.id)

    
    # Для GET-запроса — подготовка данных для формы
    all_actors = Actor.objects.all()
    all_tags = Tag.objects.all()

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
            "image_path": old_picture.image if old_picture else None,
            "screenlist_path": old_screenlist,
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
        
        result, error_message = save_uploaded_file(image_file, FILE_EXT, target_dir="movies/images")
        if error_message:
            messages.error(request, error_message)
            return render(request, "moviesapp/add_picture.html")
        
        (name, unique_image_name, image_path) = result

        picture = Picture(name=name, unique_name = unique_image_name, image=image_path)
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
                "title": movie.title,  # Ограничиваем длину заголовка
                "description": movie.description[:50] if len(movie.description) > 50 else movie.description,
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

    top_tags = Tag.objects.annotate(movie_count=Count('records')).order_by('-movie_count')[:10]    

    data = {
        "movies": page_obj.object_list,  # Используем объект пагинации для получения текущей страницы
        "tags": top_tags,  # Получаем топ 10 тегов
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


# def movies(request):
    movies_years = []
    movies_title = []
    movies_description = []
    data = {
        "title": movies_title,
        "description": movies_description,
        "movies_yesrs": movies_years,
    }
    return render(request, "moviesapp/movies.html", context=data)


def movies_filter(request, filter_type, value):

    """
    Универсальный фильтр фильмов по тегу, актёру, году или жанру.
    """
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
                "description": movie.description[:50] if len(movie.description) > 50 else movie.description,
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

    paginator = Paginator(formatted_movies, 10)  # Пагинация: 10 фильмов на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "movies": page_obj.object_list,  # Используем только фильмы текущей страницы
        "filter_type": filter_type,
        "value": value,
        "page_obj": page_obj,  # Передаем объект пагинации в контекст
        "params": request.GET.urlencode()  # Сохраняем параметры для пагинации
    }
    return render(request, "moviesapp/movies_filter.html", context)


def search(request):

    qs = Record.objects.get_queryset().select_related("picture").prefetch_related("tags", "actors")
    q = request.GET.get("q")

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(actors__name__icontains=q) |
            Q(tags__name__icontains=q) |
            Q(genre__icontains=q) |
            Q(extension__icontains=q)
        ).distinct()

    formatted_movies = []

    for movie in qs:
        picture = Picture.objects.filter(id=movie.picture_id).first()
        if picture and picture.image:
            image_path = picture.image
        else:
            image_path = static("movies/defaults/default_posters.jpg")
        formatted_movies.append(
            {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description[:50] if len(movie.description) > 50 else movie.description,
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

    paginator = Paginator(formatted_movies, 10)  # Пагинация: 10 фильмов на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "movies": page_obj.object_list,
        "query": q,
        "page_obj": page_obj,  # Передаем объект пагинации в контекст
        "params": request.GET.urlencode()  # Сохраняем параметры для пагинации
    }
    return render(request, "moviesapp/search_results.html", context)


def screenlist_detail(request, screenlist_id: int) -> render:

    screenlist = get_object_or_404(ScreeList, pk=screenlist_id)
    image_path = screenlist.image_path # Для отладки, можно удалить позже
    movie = screenlist.records.first()  # Получаем первый фильм, связанный со скринлистом
    data = {
        "screenlist": {
            "id": screenlist.id,
            "name": screenlist.name,
            "image_path": image_path,
            "movie": {"id": movie.id, "title": movie.title} if movie else None,
        }
    }
    return render(request, "moviesapp/screenlist_detail.html", data)


def download_record_torrent(request, record_id: int):
    record = get_object_or_404(Record, pk=record_id)

    if not record.torrent_file or not record.torrent_file.file_path:
        return render(
            request,
            "moviesapp/error.html",
        )

    # Проверяем, что файл существует
    if not os.path.exists(f"{django_settings.MEDIA_ROOT}" + "/" + f"{record.torrent_file.file_path}"):
        raise Http404("Торрент-файл не найден")

    # Увеличиваем счётчик
    Record.objects.filter(pk=record.pk).update(download_count=F('download_count') + 1)

    # Возвращаем торрент-файл
    return FileResponse(
        record.torrent_file.file_path.open('rb'),
        as_attachment=True,
        filename=record.torrent_file.name
    )