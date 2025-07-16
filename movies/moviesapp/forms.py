# app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Tag, Actor, Picture, Record


# --- Вспомогательные валидаторы ------------------------------------------------


def validate_file_size(value, max_mb=50):
    """Проверка, что загружаемый файл не превышает N мегабайт."""
    limit = max_mb * 1024 * 1024
    if value.size > limit:
        raise ValidationError(f"Размер файла не должен превышать {max_mb} МБ.")


def normalize_name(value: str) -> str:
    """Приводим имя к аккуратной форме (trim + один пробел)."""
    return " ".join(value.strip().split())


# --- Form‑классы ---------------------------------------------------------------


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tag name"}),
        }

    def clean_name(self):
        name = normalize_name(self.cleaned_data["name"])
        if Tag.objects.filter(name__iexact=name).exists():
            raise ValidationError("Тег с таким названием уже есть.")
        return name


class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ["name", "age", "bio", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_name(self):
        return normalize_name(self.cleaned_data["name"])


class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ["name", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_image(self):
        image = self.cleaned_data["image"]
        validate_file_size(image, max_mb=20)
        return image

    def clean_name(self):
        # заодно под‑правим slug‑часть папки (если будете использовать)
        return normalize_name(self.cleaned_data["name"])


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = [
            "title",
            "description",
            "release_date",
            "genre",
            "extension",
            "size",
            "download_url",
            "picture",
            "tags",
            "actors",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "release_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "genre": forms.TextInput(attrs={"class": "form-control"}),
            "extension": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. mkv"}),
            "size": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "download_url": forms.URLInput(attrs={"class": "form-control"}),
            "picture": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "actors": forms.SelectMultiple(attrs={"class": "form-select"}),
        }
        help_texts = {
            "size": "Укажите размер файла в байтах.",
            "extension": "Без точки. Пример: mp4, pdf, flac…",
        }

    # --- Примеры точечной валидации -------------------------------------------

    def clean_title(self):
        return normalize_name(self.cleaned_data["title"])

    def clean_extension(self):
        ext = self.cleaned_data["extension"].lower()
        if not ext.isalnum() or len(ext) > 10:
            raise ValidationError("Неверное расширение файла.")
        return ext

    def clean(self):
        """Пример общей проверки: чтобы размер соотносился с расширением."""
        cleaned = super().clean()
        size = cleaned.get("size")
        ext = cleaned.get("extension")
        if ext == "txt" and size and size > 10_000_000:
            self.add_error("size", "Слишком большой .txt файл (более 10 МБ).")

