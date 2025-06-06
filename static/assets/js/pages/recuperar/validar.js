document.addEventListener("DOMContentLoaded", () => {
    // Adiciona evento para manipular opções do formulário principal (personalizar URL e data de expiração)
    // Alterna a visibilidade dos campos extras e o atributo 'required' conforme seleção
    const form = document.querySelector("form")

    const inputUrl = document.querySelector('input[name="url"]')
    const urlInvalido = document.querySelector('form .alerta.invalido');

    // Monitora envios de formulário
    form.addEventListener("submit", (e) => {
        // Verifica, previne e exibe erros no campo url
        if (!isUrlValida(inputUrl.value)) {
            mostrarErroInput(inputUrl, "URL digitada é inválida!");
            e.preventDefault();
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


});