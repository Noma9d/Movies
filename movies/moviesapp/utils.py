import os
from django.conf import settings as django_settings


def save_uploaded_file(file, file_ext_map):
    """
    Сохраняет загруженный файл в нужную директорию, проверяет размер и расширение.

    :param file: объект файла из request.FILES
    :param file_ext_map: словарь FILE_EXT (с ключами .ext → {dir, max_size_mb})
    :return: (filename, relative_path), error_message
    """
    filename = file.name
    ext = os.path.splitext(filename)[1].lower()

    if ext not in file_ext_map:
        return None, f"Неподдерживаемый формат файла: {ext}"

    config = file_ext_map[ext]
    max_size = config["max_size_mb"] * 1024 * 1024

    if file.size > max_size:
        return None, f"Размер файла превышает {config['max_size_mb']} МБ"

    upload_dir = os.path.join(django_settings.MEDIA_ROOT, config["dir"])
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    relative_path = os.path.join(config["dir"], filename)

    return (filename, relative_path), None
