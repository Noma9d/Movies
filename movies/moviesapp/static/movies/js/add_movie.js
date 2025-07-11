function addNewTag() {
    const input  = document.getElementById('new_tag');
    const select = document.getElementById('tags');
    const value  = input.value.trim();
    if (!value) return;

    // ищем существующий option
    let option = Array.from(select.options)
                       .find(opt => opt.value === value);

    if (option) {
        // уже есть в списке — просто выделяем
        option.selected = true;
    } else {
        // совсем новый — создаём и выделяем
        option = new Option(value, value, true, true);
        select.add(option);
    }

    input.value = '';           // очистили поле
}

function addNewActor() {
    const input  = document.getElementById('new_actor');
    const select = document.getElementById('actors');
    const value  = input.value.trim();
    if (!value) return;

    // ищем существующий option
    let option = Array.from(select.options)
                       .find(opt => opt.value === value);

    if (option) {
        // уже есть в списке — просто выделяем
        option.selected = true;
    } else {
        // совсем новый — создаём и выделяем
        option = new Option(value, value, true, true);
        select.add(option);
    }

    input.value = '';           // очистили поле
}




// Загрузка изображения
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('image', file);

        fetch('/upload_image/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('imagePreview').src = data.image_path;
                document.getElementById('imagePreview').style.display = 'block';
                document.getElementById('pictureId').value = data.picture_id;
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }
}