document.addEventListener("DOMContentLoaded", () => {
    // Adiciona evento para manipular opções do formulário principal (personalizar URL e data de expiração)
    // Alterna a visibilidade dos campos extras e o atributo 'required' conforme seleção
    const form = document.querySelector("form")
    const options = document.querySelectorAll('#options .option')

    const inputUrl = document.querySelector('input[name="url"]')
    const urlInvalido = document.querySelector('form .alerta.invalido');

    const customUrlBlock = document.querySelector('#custom-url-block');
    const customUrlSelect = document.querySelector('input[name="select-custom-url"]');
    const customUrlInput = document.querySelector('input[name="custom-url"]');
    const customUrlInformativo = document.querySelector('#custom-url-block .informativo');
    const customUrlInvalido = document.querySelector('#custom-url-block .invalido');

    const dateBlock = document.querySelector('#date-block')
    const dateInput = document.querySelector('input[name="date"]')

    // Monitora opções selecionadas
    for (let option of options) {
        option.addEventListener("click", (e) => {
            if (e.target.name == "select-custom-url") {
                showCustomUrl()
            } else if (e.target.name == "select-date") {
                dateBlock.classList.toggle("hidden")
                dateInput.toggleAttribute('required');
            }
        });
    }

    // Monitora envios de formulário
    form.addEventListener("submit", (e) => {
        // Verifica, previne e exibe erros no campo url
        if (!isUrlValida(inputUrl.value)) {
            mostrarErroInput(inputUrl, "URL digitada é inválida!");
            e.preventDefault();
        }
        // Verifica, previne e exibe erros no campo custom url
        if (customUrlSelect.checked) {
            if (!isCustomUrlValida(customUrlInput.value)) {
                mostrarErroInput(customUrlInput, "Caminho digitado é inválido!");
                e.preventDefault();
            }
        }
    });


    // Monitora, valida e exibe mensagens (url)
    inputUrl.addEventListener("keyup", (e) => {
        if (isUrlValida(inputUrl.value)) {
            urlInvalido.classList.add('hidden')
            inputUrl.setCustomValidity("")
        } else {
            urlInvalido.classList.remove('hidden')
        }
    });


    function showCustomUrl() {
        customUrlBlock.classList.toggle("hidden");
        customUrlInput.toggleAttribute('required');
    }

    // Monitora, valida e exibe mensagens (custom url)
    customUrlInput.addEventListener("keyup", (e) => {
        if (isCustomUrlValida(customUrlInput.value)) {
            customUrlInformativo.innerHTML = `Seu link personalizado ficará com o seguinte caminho: ${window.location.origin}/${customUrlInput.value}`
            customUrlInformativo.classList.remove('hidden')
            customUrlInvalido.classList.add('hidden')
            customUrlInput.setCustomValidity("")
        } else {
            customUrlInvalido.classList.remove('hidden')
            customUrlInformativo.classList.add('hidden')
        }
    });


    function mostrarErroInput(input, mensagem) {
        input.setCustomValidity(mensagem);
        input.reportValidity();
    }


    function isUrlValida(inputUrl) {
        if (!/^[^\s]+?\.[^\s]+$/.test(inputUrl)) {
            return false
        } else {
            return true
        }
    }

    function isCustomUrlValida(inputCustomUrl) {
        if (inputCustomUrl.length < 1
            || inputCustomUrl.length > 24
            || !/^[a-zA-Z0-9-]+$/.test(inputCustomUrl)) {
            return false
        } else {
            return true
        }
    }


});