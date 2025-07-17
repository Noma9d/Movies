import os
import django
import sys

# Добавляем корень проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)).rsplit('/', 1)[0])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movies.settings')
django.setup()

from moviesapp.models import Record, Picture, Tag, Actor
from faker import Faker
import random

fake = Faker()


def seed_pictures():
    for _ in range(50):
        Picture.objects.create(
            name=fake.sentence(nb_words=3),
            image=fake.image_url(width=800, height=600),
        )


def seed_tags():
    for _ in range(30):
        Tag.objects.create(
            name=fake.word(),
        )


def seed_actors():
    for _ in range(20):
        Actor.objects.create(
            name=fake.name(),
        )


def seed_movies():
    all_pictures = list(Picture.objects.all())
    all_tags = list(Tag.objects.all())
    all_actors = list(Actor.objects.all())

    for _ in range(50):
        movie = Record.objects.create(
            title=fake.sentence(nb_words=3),
            description=fake.text(max_nb_chars=200),
            release_date=fake.date(),
            genre=fake.word(ext_word_list=['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi']),
            extension=fake.file_extension(),
            size=fake.random_int(min=2000, max=100000),
            download_url=fake.url(),
            created_at=fake.date_time_this_decade(),
            picture=random.choice(all_pictures) if all_pictures else None,
        )

        # Добавляем связи ManyToMany
        movie.tags.set(random.sample(all_tags, k=min(3, len(all_tags))))
        movie.actors.set(random.sample(all_actors, k=min(2, len(all_actors))))
        movie.save()


if __name__ == "__main__":
    seed_pictures()
    seed_tags()
    seed_actors()
    seed_movies()
    print("✅ Seeding completed successfully!")
