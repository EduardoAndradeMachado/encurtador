document.addEventListener("DOMContentLoaded", () => {
    const options = document.querySelectorAll('#options .option')

    let qrcodeGerado = false
    for (option of options) {
        option.addEventListener("click", (e) => {
            if (e.target.name == "select-qrcode") {
                document.querySelector('#block-qrcode').classList.toggle("hidden")
                if (!qrcodeGerado) {
                    gerarQRCode()
                    qrcodeGerado = true
                }

            } else if (e.target.name == "select-history") {
                document.querySelector('#block-history').classList.toggle("hidden")
            }
        })
    }
})

function gerarQRCode() {
    let url = document.querySelector('input[name="short_url"]').value
    new QRCode(document.getElementById("qrcode"), {
        text: url,
        width: 1920,
        height: 1920,
    });
}