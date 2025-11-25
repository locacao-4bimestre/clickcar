document.addEventListener("DOMContentLoaded", () => {

    const simulateCard = document.querySelectorAll('.simulate-card')[0];
    const dataInicioInput = document.getElementById("data_inicio");
    const dataFimInput = document.getElementById("data_fim");
    const veiculo_id = simulateCard ? simulateCard.id : null; // Proteção caso não tenha card
    const simText = simulateCard ? simulateCard.querySelector('.sim-result') : null;

    // =========================================================
    // 1. LÓGICA DE BLOQUEIO DE DATAS (UX)
    // =========================================================
    
    // Função para pegar a data de hoje formatada (YYYY-MM-DD)
    function getTodayDate() {
        const today = new Date();
        const year = today.getFullYear();
        // O mês começa em 0, então somamos 1 e garantimos 2 dígitos com padStart
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    const hoje = getTodayDate();

    // Define que não pode escolher data anterior a hoje
    if (dataInicioInput) {
        dataInicioInput.setAttribute('min', hoje);
        
        // Quando o usuário muda a data de início...
        dataInicioInput.addEventListener('change', function() {
            // A data fim não pode ser menor que a data de início
            dataFimInput.setAttribute('min', this.value);
            
            // Se a data fim já estiver preenchida e for menor que a nova data início, limpa ela
            if (dataFimInput.value && dataFimInput.value < this.value) {
                dataFimInput.value = '';
                // Esconde a simulação pois a data ficou inválida
                if (simulateCard) simulateCard.classList.add('hidden');
            }
        });
    }

    if (dataFimInput) {
        dataFimInput.setAttribute('min', hoje);
    }

    // =========================================================
    // 2. LÓGICA DE SIMULAÇÃO DE PREÇO (EXISTENTE)
    // =========================================================

    async function fetchSimulation(inicio, fim, veiculo_id) {
        try {
            let response = await fetch("/api/simulação", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    inicio: inicio,
                    fim: fim,
                    veiculo_id: veiculo_id
                })
            });
            let data = await response.json();
            return data;
        } catch (error) {
            console.error("Erro na simulação:", error);
            return { msg: "Erro ao conectar com servidor" };
        }
    }

    async function write() {
        if (dataInicioInput && dataFimInput && dataInicioInput.value && dataFimInput.value) {
            
            // Verifica se data fim é válida em relação ao início antes de chamar API
            if (dataFimInput.value < dataInicioInput.value) {
                return; // Não simula datas inválidas
            }

            if (simulateCard) simulateCard.classList.remove('hidden');
            
            let simulation = await fetchSimulation(dataInicioInput.value, dataFimInput.value, veiculo_id);
            
            if (simulation.msg) {
                // Se o backend retornar erro (404/msg), exibe o erro
                // (Geralmente validamos no front antes, mas é bom ter o fallback)
                if (simText) simText.textContent = `Atenção: ${simulation.msg}`;
            } else {
                if (simText) simText.textContent = `Simulação: R$ ${simulation.valor.toLocaleString('pt-br', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }
        }
    }

    if (dataInicioInput) dataInicioInput.addEventListener("input", async () => { await write(); });
    if (dataFimInput) dataFimInput.addEventListener("input", async () => { await write(); });

});