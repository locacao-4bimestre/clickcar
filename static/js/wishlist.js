document.addEventListener("DOMContentLoaded", () => {
    console.log("Wishlist.js carregado com sucesso!"); // PROVA QUE O ARQUIVO CARREGOU

    const heartButtons = document.querySelectorAll(".btn-favorite");
    console.log(`Encontrei ${heartButtons.length} botões de favorito.`);

    heartButtons.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            console.log("Botão clicado!"); // PROVA QUE O CLIQUE FUNCIONOU

            const veiculoId = btn.dataset.id;
            const icon = btn.querySelector("i");
            
            console.log(`Tentando favoritar veículo ID: ${veiculoId}`);

            try {
                const response = await fetch(`/api/favorite/${veiculoId}`, {
                    method: "POST"
                });

                console.log("Status da resposta:", response.status); // MOSTRA O CÓDIGO HTTP (200, 401, 500)

                if (response.status === 401) {
                    alert("Faça login para salvar favoritos!");
                    window.location.href = "/login";
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }

                const data = await response.json();
                console.log("Dados recebidos:", data); // MOSTRA O QUE O PYTHON RESPONDEU

                if (data.action === 'added') {
                    icon.classList.remove("bi-heart");
                    icon.classList.add("bi-heart-fill");
                    icon.style.color = "red";
                } else {
                    icon.classList.remove("bi-heart-fill");
                    icon.classList.add("bi-heart");
                    icon.style.color = ""; 
                }

            } catch (error) {
                console.error("ERRO CRÍTICO NO JS:", error);
                alert("Erro ao processar favorito. Veja o console.");
            }
        });
    });
});