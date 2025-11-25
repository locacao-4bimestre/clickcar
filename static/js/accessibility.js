document.addEventListener("DOMContentLoaded", function () {

    
    // 1. CONTROLE DE FONTE
    let fontSize = parseFloat(localStorage.getItem("fontSize")) || 1.0;
    document.body.style.fontSize = fontSize + "em";
    function reset(){
        if(fontSize < 0.7){
            fontSize = 0.7
            document.body.style.fontSize = fontSize + "em";
            localStorage.setItem("fontSize", fontSize);
        }
        else if (fontSize > 1.5){
            fontSize = 1.5
            document.body.style.fontSize = fontSize + "em";
            localStorage.setItem("fontSize", fontSize);
        }
    }
    reset()
    document.getElementById("increaseFont").addEventListener("click", (e) => {
        e.stopPropagation(); // Evita fechar o menu
        if (fontSize < 1.5) { // Limite máximo
            fontSize += 0.1;
            document.body.style.fontSize = fontSize + "em";
            localStorage.setItem("fontSize", fontSize);
        }
    });

    document.getElementById("decreaseFont").addEventListener("click", (e) => {
        e.stopPropagation();
        if (fontSize > 0.7) { // Limite mínimo
            fontSize -= 0.1;
            document.body.style.fontSize = fontSize + "em";
            localStorage.setItem("fontSize", fontSize);
        }
    });

    // 2. MODO ESCURO
    const darkModeActive = localStorage.getItem("darkMode") === "true";
    if (darkModeActive) document.body.classList.add("dark-mode");

    document.getElementById("toggleDarkMode").addEventListener("click", (e) => {
        e.stopPropagation();
        document.body.classList.toggle("dark-mode");
        localStorage.setItem("darkMode", document.body.classList.contains("dark-mode"));
    });

    // 3. IDIOMA (PT <-> EN)
    const langBtn = document.getElementById("toggleLanguage");
    let currentLang = localStorage.getItem("lang") || "pt";

    // Dicionário de Traduções
    const translations = {
        pt: {
            accessibility: "Acessibilidade",
            increase_font: "Aumentar letra",
            decrease_font: "Diminuir letra",
            dark_mode: "Alternar modo escuro",
            reset: "Restaurar Padrão",
            vehicles: "Veículos",
            requirements: "Requisitos",
            faq: "Dúvidas",
            login: "Entrar",
            create_account: "Criar Conta",
            my_area: "Minha Área",
            logout: "Sair",
            admin: "Admin",
            search_placeholder: "Modelo, marca...",
            search_btn: "Buscar",
            clean_filter: "Limpar filtros",
            details: "Ver detalhes",
            per_day: "/ dia"
        },
        en: {
            accessibility: "Accessibility",
            increase_font: "Increase font",
            decrease_font: "Decrease font",
            dark_mode: "Toggle dark mode",
            reset: "Reset Defaults",
            vehicles: "Vehicles",
            requirements: "Requirements",
            faq: "FAQ",
            login: "Login",
            create_account: "Sign Up",
            my_area: "My Dashboard",
            logout: "Logout",
            admin: "Admin",
            search_placeholder: "Model, brand...",
            search_btn: "Search",
            clean_filter: "Clear filters",
            details: "View details",
            per_day: "/ day"
        }
    };

    function translatePage() {
        const t = translations[currentLang];

        // Traduz todos os elementos com data-i18n
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (t[key]) {
                el.innerText = t[key];
            }
        });

        // Atualiza o texto do botão de trocar idioma
        langBtn.innerText = currentLang === "pt" ? "Switch to English" : "Mudar para Português";
    }

    // Aplica tradução ao carregar
    translatePage();

    langBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        currentLang = currentLang === "pt" ? "en" : "pt";
        localStorage.setItem("lang", currentLang);
        translatePage();
    });

    // 4. RESET TOTAL
    document.getElementById("resetAccessibility").addEventListener("click", () => {
        // Remove tudo do localStorage relacionado a acessibilidade
        localStorage.removeItem("fontSize");
        localStorage.removeItem("darkMode");
        localStorage.removeItem("lang");
        
        // Recarrega a página para aplicar o padrão limpo
        location.reload(); 
    });
});