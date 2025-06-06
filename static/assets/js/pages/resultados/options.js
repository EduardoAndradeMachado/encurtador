// Adiciona evento para manipular opções extras (QRcode e histórico)
document.addEventListener("DOMContentLoaded", () => {
    // Seleciona todas as opções extras
    const options = document.querySelectorAll('#options .option')

    const qrCodeBlock = document.querySelector('#block-qrcode')
    const qrCodeElement = document.querySelector('#qrcode')

    const historyBlock = document.querySelector('#block-history')
    const tableBody = document.querySelector('#table-logs tbody')

    const inputUrl = document.querySelector('input[name="short_url"]')

    let isQRCodeGenerated = false // Flag para evitar gerar o QRCode mais de uma vez
    let isLogLoaded = false    // Flag para evitar buscar logs mais de uma vez
    for (let option of options) {
        option.addEventListener("click", (e) => {
            switch (e.target.name) {
                case "select-qrcode":
                    qrCodeBlock.classList.toggle("hidden")
                    if (!isQRCodeGenerated) {
                        gerarQRCode()
                        isQRCodeGenerated = true
                    }
                    break
                case "select-history":
                    historyBlock.classList.toggle("hidden")
                    if (!isLogLoaded) {
                        get_logs()
                        isLogLoaded = true
                    }
                    break
            }
        })
    }


    // Gera o QRCode a partir da URL encurtada
    function gerarQRCode() {
        new QRCode(qrCodeElement, {
            text: inputUrl.value,
            width: 720,
            height: 720,
        });
    }

    // Busca e exibe o histórico de acessos detalhado
    function get_logs() {
        const parametrosUrl = new URLSearchParams(window.location.search);
        const url_api = `${window.location.origin}/log?short_slug=${parametrosUrl.get('short_slug')}`
        fetch(url_api)
            .then(response => response.json())
            .then(resposta => {
                for (let item of resposta) {
                    let tr = document.createElement('tr')
                    const keys = ['date', 'dispositivo', 'altura_tela', 'largura_tela', 'idioma']
                    for (let key of keys) {
                        let td = document.createElement('td')
                        if (key == 'date') {
                            // Formata a data para o padrão brasileiro
                            td.textContent = new Date(item[key].replace(" ", "T") + "Z").toLocaleString("pt-BR")
                        } else {
                            td.textContent = item[key] ? item[key] : ''
                        }
                        tr.appendChild(td)
                    }
                    tableBody.appendChild(tr)
                }
            })
            .catch(error => {
                console.error('Erro ao buscar os dados.');
            });
    }
})