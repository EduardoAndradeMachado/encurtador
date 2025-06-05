document.addEventListener("DOMContentLoaded", () => {
    // Adiciona evento para copiar o link encurtado ao clicar no botão
    // Utiliza a API de clipboard do navegador
    // Exibe alertas de sucesso ou erro
    const button = document.querySelector('input[type="submit"]')
    button.addEventListener("click", (e) => {
        e.preventDefault(); // evita envio do formulário

        const input = document.querySelector('input[type="text"]')
        const texto = input.value;

        navigator.clipboard.writeText(texto)
            .then(() => {
                alert("Link copiado: " + texto);
            })
            .catch(err => {
                alert("Erro ao copiar: " + err);
            });
    });
});
