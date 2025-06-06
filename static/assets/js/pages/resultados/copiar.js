document.addEventListener("DOMContentLoaded", () => {
    // Adiciona evento para copiar o link encurtado ao clicar no botão
    // Utiliza a API de clipboard do navegador
    // Exibe alertas de sucesso ou erro
    const button = document.querySelector('input[type="submit"]')
    const input = document.querySelector('input[type="text"]')
    const aviso = document.querySelector('.alerta.sucesso')

    button.addEventListener("click", (e) => {
        e.preventDefault();
        const texto = input.value;
        navigator.clipboard.writeText(texto)
            .then(() => {
                aviso.classList.remove("hidden")
            })
            .catch(err => {
                aviso.classList.remove("add")
            });
    });
});
