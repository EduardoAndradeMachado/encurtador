document.addEventListener("DOMContentLoaded", () => {
    const options = document.querySelectorAll('#options .option')
    for (option of options) {
        option.addEventListener("click", (e) => {
            if (e.target.name == "select-custom-url") {
                document.querySelector('#custom-url-block').classList.toggle("hidden")
                document.querySelector('input[name="custom-url"]').toggleAttribute('required');
            } else if (e.target.name == "select-date") {
                document.querySelector('#date-block').classList.toggle("hidden")
                document.querySelector('input[name="date"]').toggleAttribute('required');
            }
        });
    }
});
