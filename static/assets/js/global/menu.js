document.addEventListener("DOMContentLoaded", () => {
    const menu = document.querySelectorAll('#menu a');
    const slug = window.location.pathname;
    for (let i of menu) {
        if (slug === i.attributes.href.value) {
            i.classList.add("menu-active");
            if (slug == '/resultado') {
                i.classList.remove('hidden')
            }
            break;
        }
    }
});