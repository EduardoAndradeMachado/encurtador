document.addEventListener("DOMContentLoaded", () => {
    const options = document.querySelectorAll('#options .option')

    let qrcodeGerado = false
    let logGerado = false
    for (let option of options) {
        option.addEventListener("click", (e) => {
            if (e.target.name == "select-qrcode") {
                document.querySelector('#block-qrcode').classList.toggle("hidden")
                if (!qrcodeGerado) {
                    gerarQRCode()
                    qrcodeGerado = true
                }

            } else if (e.target.name == "select-history") {
                document.querySelector('#block-history').classList.toggle("hidden")
                if (!logGerado) {
                    get_logs()
                    logGerado = true
                }
            }
        })
    }
})

function gerarQRCode() {
    let url = document.querySelector('input[name="short_url"]').value
    new QRCode(document.getElementById("qrcode"), {
        text: url,
        width: 720,
        height: 720,
    });
}

function get_logs() {
    const table = document.querySelector('#table-logs tbody')
    const parametros = new URLSearchParams(window.location.search);
    const url_api = `${window.location.origin}/log?short_slug=${parametros.get('short_slug')}`
    fetch(url_api)
        .then(response => response.json())
        .then(data => {
            for (let item of data) {
                let tr = document.createElement('tr')
                // const chaves = ['date', 'dispositivo', 'altura_tela', 'largura_tela', 'idioma', 'localidade', 'ip', 'user_agent']
                const chaves = ['date', 'dispositivo', 'altura_tela', 'largura_tela', 'idioma']
                for (let chave of chaves) {
                    let td = document.createElement('td')
                    if (chave == 'date') {
                        td.textContent = new Date(item[chave].replace(" ", "T") + "Z").toLocaleString("pt-BR")
                    } else {
                        td.textContent = item[chave] ? item[chave] : ''
                    }
                    tr.appendChild(td)
                }
                table.appendChild(tr)
            }
        })
        .catch(error => {
            console.error('Erro ao buscar os dados:', error);
        });
}