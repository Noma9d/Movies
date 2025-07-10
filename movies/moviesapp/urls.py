from django.urls import path
from . import views


app_name = "moviesapp"


urlpatterns = [
    path("", views.main, name="main"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("movies/", views.movies, name="movies"),
    path("movies/add_movie/", views.add_movie, name="add_movie"),
    path("movies/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:movie_id>/edit/", views.edit_movie, name="edit_movie"),
    path("movies/<int:movie_id>/delete/", views.delete_movie, name="delete_movie"),
    path("pictures/", views.pictures_list, name="pictures_list"),
    path("upload_image/", views.upload_image, name="upload_image"),
    path("pictures/<int:picture_id>/", views.picture_detail, name="picture_detail"),
    path(
        "pictures/<int:picture_id>/delete/", views.delete_picture, name="delete_picture"
    ),
    path("picture/add_picture/", views.add_picture, name="add_picture"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    # path('search/', views.search, name='search'),
    path("tag/<str:tag_name>/", views.tag_detail, name="tag_detail"),
]

"""
    TODO:
    Реализовать поиск по фильмам и картинкам
    Реализовать топ-10 тегов на главной странице, сейчас выводятся только первые 10 тегов
    Необходимо исправить добавление нескольких тегов и актеров к фильму, сейчас добавляется только один тег или актер
    Необходимо реализовать хранение изображений с уникальными именами, чтобы избежать конфликтов при загрузке изображений с одинаковыми именами
    
"""
