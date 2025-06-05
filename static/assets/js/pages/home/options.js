document.addEventListener("DOMContentLoaded", () => {
    // Adiciona evento para manipular opções do formulário principal (personalizar URL e data de expiração)
    // Alterna a visibilidade dos campos extras e o atributo 'required' conforme seleção
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
