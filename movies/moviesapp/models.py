from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import os
from django.core.files.storage import default_storage


# -------------------------------------------------
# Utility helpers for upload paths
# -------------------------------------------------


def upload_to_picture(instance, filename):
    """Return dynamic upload path for :class:`Picture` images."""
    return os.path.join("pictures", slugify(instance.name), filename)


def upload_to_actor(instance, filename):
    """Return dynamic upload path for :class:`Actor` images."""
    return os.path.join("actors", slugify(instance.name), filename)


# -------------------------------------------------
# Tag Model & Manager
# -------------------------------------------------


class Tag(models.Model):
    """Light-weight label for grouping :class:`Record` instances."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    # --- CRUD convenience wrappers ---
    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, tag_id: int):
        return cls.objects.filter(id=tag_id).first()

    @classmethod
    def get_by_name(cls, name: str):
        return cls.objects.filter(name=name).first()

    def update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=list(kwargs.keys()))
        return self


# -------------------------------------------------
# Actor Model
# -------------------------------------------------


class Actor(models.Model):
    """Human that plays in a :class:`Record` (e.g. movie actor)."""

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to_actor, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Actor"
        verbose_name_plural = "Actors"

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    # --- CRUD helpers ---
    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, actor_id: int):
        return cls.objects.filter(id=actor_id).first()

    @classmethod
    def get_by_name(cls, name: str):
        return cls.objects.filter(name=name).first

    def update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=list(kwargs.keys()))
        return self


# -------------------------------------------------
# Picture Model
# -------------------------------------------------


class Picture(models.Model):
    """Image file that can be referenced by many :class:`Record`s."""

    name = models.CharField(max_length=255)
    unique_name = models.CharField(max_length=255, unique=True, blank=True)  # Unique name for the picture
    # Use a custom upload path to avoid collisions
    image = models.ImageField(upload_to="images/", max_length=255)

    class Meta:
        ordering = ["name"]
        verbose_name = "Picture"
        verbose_name_plural = "Pictures"

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    # --- CRUD helpers ---
    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, picture_id: int):
        return cls.objects.filter(id=picture_id).first()

    @classmethod
    def get_by_path(cls, path: str):
        return cls.objects.filter(image=path).first()

    def update(self, **kwargs):
        # Supports changing name and/or image
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=list(kwargs.keys()))
        return self
    
    def delete(self, *args, **kwargs):
        # Delete the image file from storage
        if self.image and default_storage.exists(self.image.name):
            self.image.delete(save=False)
        # Then delete the Picture instance
        super().delete(*args, **kwargs)
    



# -------------------------------------------------
# Custom manager for Torrent files
# -------------------------------------------------


class TorrentFile(models.Model):

    name = models.CharField(max_length=255)
    unique_name = models.CharField(max_length=255, unique=True, blank=True)  # Unique name for the torrent file
    # Use a custom upload path to avoid collisions
    file_path = models.FileField(upload_to="torrents/", max_length=255)

    class Meta:
        ordering = ["name"]
        verbose_name = "TorrentFile"
        verbose_name_plural = "TorrentFiles"

    def __str__(self) -> str:  # pragma: no cover
        return self.name
    
    def delete(self, *args, **kwargs):
        # Delete the torrent file from storage
        if self.file_path and default_storage.exists(self.file_path.name):
            self.file_path.delete(save=False)
        # Then delete the TorrentFile instance
        super().delete(*args, **kwargs)



# -------------------------------------------------
# Custom queryset & manager for Record
# -------------------------------------------------


class RecordQuerySet(models.QuerySet):
    """Reusable filters for :class:`Record`."""

    def released_in_year(self, year: int):
        return self.filter(release_date__year=year)

    def with_tag(self, tag_name: str):
        return self.filter(tags__name=tag_name)


class RecordManager(models.Manager):
    def get_queryset(self):
        return RecordQuerySet(self.model, using=self._db)

    # The following helpers simply delegate to the queryset for familiarity
    def get_all(self):
        return self.get_queryset().all()

    def get_by_id(self, record_id: int):
        return (
            self.get_queryset().filter(id=record_id).select_related("picture").first()
        )


# -------------------------------------------------
# Record Model
# -------------------------------------------------


class Record(models.Model):
    """A generic downloadable item (movie, track, doc, etc.)."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_date = models.DateField()
    genre = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    size = models.PositiveBigIntegerField(help_text="File size in bytes")
    download_url = models.URLField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    torrent_file = models.ForeignKey(
        TorrentFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="records",
    )

    picture = models.ForeignKey(
        Picture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="records",
    )

    tags = models.ManyToManyField(Tag, related_name="records", blank=True)
    actors = models.ManyToManyField(Actor, related_name="records", blank=True)

    # Attach custom manager
    objects = RecordManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self) -> str:  # pragma: no cover
        return self.title

    # --- Instance‑level helpers ---
    def update(self, **kwargs):
        """Update selected fields and save the model.

        Example::

            record.update(title="New title", size=12345)
        """
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=list(kwargs.keys()))
        return self

    def delete(self, *args, **kwargs):

        # Удаляем файл постера, если есть
        if self.picture and self.picture.image:
            if default_storage.exists(self.picture.image.name):
                self.picture.image.delete(save=False)
            self.picture.delete()

        # Удаляем файл торрент, если есть
        if self.torrent_file and self.torrent_file.file_path:
            if default_storage.exists(self.torrent_file.file_path.name):
                self.torrent_file.file_path.delete(save=False)
            self.torrent_file.delete()

        # Затем удаляем сам объект Record
        super().delete(*args, **kwargs)
