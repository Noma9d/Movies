document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("theme-toggle");
    const body = document.body;
    // Загрузить сохранённую тему
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-theme");
        toggle.textContent = "☀️";
    }
    toggle.addEventListener("click", function () {
        body.classList.toggle("dark-theme");
        if (body.classList.contains("dark-theme")) {
            localStorage.setItem("theme", "dark");
            toggle.textContent = "☀️";
        } else {
            localStorage.setItem("theme", "light");
            toggle.textContent = "🌙";
        }
    });
});
