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

function removeSelectedTags() {
    const select   = document.getElementById('tags');
    const selected = Array.from(select.selectedOptions);

    // ничего не выбрано — выходим
    if (!selected.length) return;

    // проходим с конца, чтобы индексы не «плыли»
    for (let i = selected.length - 1; i >= 0; i--) {
        select.remove(selected[i].index);
    }
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


function removeSelectedActors() {
    const select   = document.getElementById('actors');
    const selected = Array.from(select.selectedOptions);

    // ничего не выбрано — выходим
    if (!selected.length) return;

    // проходим с конца, чтобы индексы не «плыли»
    for (let i = selected.length - 1; i >= 0; i--) {
        select.remove(selected[i].index);
    }
}
