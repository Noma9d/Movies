from django.db import models


# Create your models here.
class Record(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    size = models.IntegerField()
    download_url = models.URLField(max_length=200)
    tags = models.ManyToManyField("Tag", related_name="records", blank=True)
    picture = models.ForeignKey(
        "Picture",
        related_name="records",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    actors = models.ManyToManyField("Actor", related_name="records", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    bio = models.TextField()
    image = models.ImageField(upload_to="actors/")

    def __str__(self):
        return self.name


class Picture(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="pictures/")

    def __str__(self):
        return self.name
