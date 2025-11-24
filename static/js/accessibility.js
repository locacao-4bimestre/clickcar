document.addEventListener("DOMContentLoaded", function () {

    // --- BOTÕES ---
    const increaseBtn  = document.getElementById("increaseFont");
    const decreaseBtn  = document.getElementById("decreaseFont");
    const darkModeBtn  = document.getElementById("toggleDarkMode");
    const langBtn      = document.getElementById("toggleLanguage");

    if (!increaseBtn || !decreaseBtn || !darkModeBtn || !langBtn) {
        console.warn("Botões de acessibilidade não encontrados no DOM.");
        return;
    }

    // --- FONT SIZE ---
    const htmlEl = document.documentElement;
    const minFont = 14;  // px
    const maxFont = 20;  // px

    function getCurrentFontSize() {
        const size = window.getComputedStyle(htmlEl).fontSize;
        return parseFloat(size) || 16;
    }

    function setFontSize(size) {
        const clamped = Math.max(minFont, Math.min(maxFont, size));
        htmlEl.style.fontSize = clamped + "px";
        localStorage.setItem("cc_font_size", clamped);
    }

    // --- DARK MODE ---
    function setDarkMode(enabled) {
        if (enabled) {
            document.body.classList.add("dark-mode");
            darkModeBtn.textContent = "Desativar modo escuro";
        } else {
            document.body.classList.remove("dark-mode");
            darkModeBtn.textContent = "Ativar modo escuro";
        }
        localStorage.setItem("cc_dark_mode", enabled ? "1" : "0");
    }

    // --- LANGUAGE / CURRENCY ---
    // Ideia: usar atributo data-lang no body e spans com data-pt / data-en / data-br / data-usd
    function setLanguage(lang) {
        document.body.setAttribute("data-lang", lang);

        // Textos (data-pt / data-en)
        document.querySelectorAll("[data-pt][data-en]").forEach(el => {
            const text = el.getAttribute(lang === "en" ? "data-en" : "data-pt");
            if (text !== null) el.textContent = text;
        });

        // Preços (data-br / data-usd)
        document.querySelectorAll("[data-br][data-usd]").forEach(el => {
            const price = el.getAttribute(lang === "en" ? "data-usd" : "data-br");
            if (price !== null) el.textContent = price;
        });

        if (lang === "en") {
            langBtn.textContent = "Voltar para Português";
        } else {
            langBtn.textContent = "Switch to English";
        }

        localStorage.setItem("cc_lang", lang);
    }

    // --- CARREGAR CONFIG SALVA ---
    (function loadPreferences() {
        // Fonte
        const storedFont = localStorage.getItem("cc_font_size");
        if (storedFont) {
            setFontSize(parseFloat(storedFont));
        }

        // Modo escuro
        const storedDark = localStorage.getItem("cc_dark_mode");
        setDarkMode(storedDark === "1");

        // Idioma
        const storedLang = localStorage.getItem("cc_lang") || "pt";
        setLanguage(storedLang);
    })();

    // --- EVENTOS DOS BOTÕES ---
    increaseBtn.addEventListener("click", function () {
        const current = getCurrentFontSize();
        setFontSize(current + 1);
    });

    decreaseBtn.addEventListener("click", function () {
        const current = getCurrentFontSize();
        setFontSize(current - 1);
    });

    darkModeBtn.addEventListener("click", function () {
        const isDark = document.body.classList.contains("dark-mode");
        setDarkMode(!isDark);
    });

    langBtn.addEventListener("click", function () {
        const currentLang = document.body.getAttribute("data-lang") || "pt";
        const nextLang = currentLang === "pt" ? "en" : "pt";
        setLanguage(nextLang);
    });

});