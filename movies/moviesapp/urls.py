from django.urls import path
from . views import Authorization, Movies, MoviePicture, MovieTag, main, movies, about, contact, upload_image


app_name = "moviesapp"


urlpatterns = [
    path("", main, name="main"),
    path("register/", Authorization.register, name="register"),
    path("login/", Authorization.login_view, name="login"),
    path("logout/", Authorization.logout_view, name="logout"),
    path("movies/", movies, name="movies"),
    path("movies/add_movie/", Movies.add_movie , name="add_movie"),
    path("movies/<int:movie_id>/", Movies.movie_detail, name="movie_detail"),
    path("movies/<int:movie_id>/edit/", Movies.edit_movie, name="edit_movie"),
    path("movies/<int:movie_id>/delete/", Movies.delete_movie, name="delete_movie"),
    path("pictures/", MoviePicture.pictures_list, name="pictures_list"),
    path("upload_image/", upload_image, name="upload_image"),
    path("pictures/<int:picture_id>/", MoviePicture.picture_detail, name="picture_detail"),
    path(
        "pictures/<int:picture_id>/delete/", MoviePicture.delete_picture, name="delete_picture"
    ),
    path("picture/add_picture/", MoviePicture.add_picture, name="add_picture"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
    # path('search/', views.search, name='search'),
    path("tag/<str:tag_name>/", MovieTag.tag_detail, name="tag_detail"),
]

"""
    TODO:
    Заменить базу данных на PostgreSQL
    Реализовать поиск по фильмам и картинкам
    Реализовать топ-10 тегов на главной странице, сейчас выводятся только первые 10 тегов
    Реализовать кликабельность актеров что бы можно было перейти на страницу актера и увидеть все фильмы с его участием
    Реализовать добавление информации о актерах, ее удаление и редактирование
    Сделать файл с настройками для хранения конфигурации приложения
    Реализовать возможность добавления нескольких картинок к одному фильму
    Реализовать отображение информции о том кто добавил фильм и картинку
    
"""
