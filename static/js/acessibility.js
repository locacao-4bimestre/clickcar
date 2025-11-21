document.addEventListener("DOMContentLoaded", () => {

    /* =============================
       SALVAR EM LOCALSTORAGE
       ============================= */
    function save(key, value) {
        localStorage.setItem(key, value);
    }
    function load(key, fallback) {
        return localStorage.getItem(key) || fallback;
    }

    /* =============================
       FONTE (Zoom)
       ============================= */
    let fontSize = parseInt(load("fontSize", "100"));
    document.body.style.fontSize = fontSize + "%";

    document.getElementById("increaseFont")?.addEventListener("click", () => {
        fontSize += 10;
        document.body.style.fontSize = fontSize + "%";
        save("fontSize", fontSize);
    });

    document.getElementById("decreaseFont")?.addEventListener("click", () => {
        if (fontSize > 70) {
            fontSize -= 10;
            document.body.style.fontSize = fontSize + "%";
            save("fontSize", fontSize);
        }
    });

    /* =============================
       DARK MODE
       ============================= */
    let darkMode = load("darkMode", "off");

    function applyDarkMode() {
        if (darkMode === "on") {
            document.body.classList.add("dark-mode");
            document.getElementById("toggleDarkMode").innerText = "Modo Claro";
        } else {
            document.body.classList.remove("dark-mode");
            document.getElementById("toggleDarkMode").innerText = "Modo Escuro";
        }
    }

    applyDarkMode();

    document.getElementById("toggleDarkMode")?.addEventListener("click", () => {
        darkMode = darkMode === "on" ? "off" : "on";
        save("darkMode", darkMode);
        applyDarkMode();
    });

    /* =============================
       IDIOMA PT / EN
       ============================= */

    let language = load("language", "pt");

    const translations = {
        "pt": {
            "Veículos": "Veículos",
            "Requisitos": "Requisitos",
            "FAQ": "FAQ",
            "Criar Conta": "Criar Conta",
            "Login": "Login",
            "Minha Área": "Minha Área",
            "Sair": "Sair",
            "Aumentar letra": "Aumentar letra",
            "Diminuir letra": "Diminuir letra",
            "Ativar modo escuro": "Ativar modo escuro",
        },

        "en": {
            "Veículos": "Vehicles",
            "Requisitos": "Requirements",
            "FAQ": "FAQ",
            "Criar Conta": "Sign up",
            "Login": "Login",
            "Minha Área": "My Account",
            "Sair": "Logout",
            "Aumentar letra": "Increase font",
            "Diminuir letra": "Decrease font",
            "Ativar modo escuro": "Dark mode",
        }
    };

    function translatePage() {
        const elements = document.querySelectorAll("*");

        elements.forEach(el => {
            let text = el.innerText.trim();

            if (translations[language][text]) {
                el.innerText = translations[language][text];
            }
        });

        document.getElementById("toggleLanguage").innerText =
            language === "pt" ? "Switch to English" : "Mudar para Português";
    }

    translatePage();

    document.getElementById("toggleLanguage")?.addEventListener("click", () => {
        language = language === "pt" ? "en" : "pt";
        save("language", language);
        translatePage();
    });

    /* =============================
       MOEDA R$ → US$
       ============================= */

    let currency = load("currency", "BRL");

    function formatCurrencyElements() {
        const prices = document.querySelectorAll("[data-price]");

        prices.forEach(item => {
            const value = parseFloat(item.dataset.price);

            if (currency === "BRL") {
                item.innerText = R$ ${value.toFixed(2)};
            } else {
                const converted = value / 5.4; // dólar aproximado
                item.innerText = $ ${converted.toFixed(2)};
            }
        });
    }

    formatCurrencyElements();

});