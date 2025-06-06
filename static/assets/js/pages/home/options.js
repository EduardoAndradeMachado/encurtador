document.addEventListener("DOMContentLoaded", () => {
    // Adiciona evento para manipular opções do formulário principal (personalizar URL e data de expiração)
    // Alterna a visibilidade dos campos extras e o atributo 'required' conforme seleção
    const options = document.querySelectorAll('#options .option')
    for (option of options) {
        option.addEventListener("click", (e) => {
            if (e.target.name == "select-custom-url") {
                customUrl()
            } else if (e.target.name == "select-date") {
                document.querySelector('#date-block').classList.toggle("hidden")
                document.querySelector('input[name="date"]').toggleAttribute('required');
            }
        });
    }
});

let eventoAtivo = false
function customUrl() {
    document.querySelector('#custom-url-block').classList.toggle("hidden")

    const inputCustomUrl = document.querySelector('input[name="custom-url"]');
    inputCustomUrl.toggleAttribute('required');

    if (!eventoAtivo) {
        inputCustomUrl.addEventListener("keyup", (e) => {
            const customUrlMensagem = document.querySelector('#custom-url-block .informativo');
            customUrlMensagem.innerHTML = `Seu link personalizado ficará com o seguinte caminho: ${window.location.origin}/${inputCustomUrl.value}`
            validaCustomUrl(inputCustomUrl.value)
        })
    }
    eventoAtivo = true
}

function validaCustomUrl(inputCustomUrl) {
    const customUrlinvalida = document.querySelector('#custom-url-block .invalido');
    // Se tiver invalido mostre o erro
    if (inputCustomUrl.length < 1
        || inputCustomUrl.length > 24
        || !/^[a-zA-Z0-9-]+$/.test(inputCustomUrl)) {
        document.querySelector('#custom-url-block .informativo').classList.add('hidden')
        customUrlinvalida.classList.remove('hidden')
    } else {
        customUrlinvalida.classList.add('hidden')
        document.querySelector('#custom-url-block .informativo').classList.remove('hidden')
    }
}