document.addEventListener("DOMContentLoaded",()=>{

    const simulateCard = document.querySelectorAll('.simulate-card')[0]
    const dataInicioInput = document.getElementById("data_inicio")
    const dataFimInput = document.getElementById("data_fim")
    const veiculo_id = simulateCard.id
    const simText = simulateCard.querySelector('.sim-result')
    async function fetchSimulation(inicio,fim,veiculo_id){
        let data = await fetch("/api/simulação",{
            method: "POST",
            headers: {
                    "Content-Type": "application/json"  
                },
            body:JSON.stringify({
                inicio: inicio,
                fim: fim,
                veiculo_id: veiculo_id
            })
        }).then(res => res.json()).then(data => data)
        console.log(data)
        return data
    }   
    async function write(){
        if (dataInicioInput.value && dataFimInput.value){
            simulateCard.classList.remove('hidden')
            let simulation = await fetchSimulation(dataInicioInput.value,dataFimInput.value,veiculo_id)
            if (simulation.msg){
                simText.textContent = `Não foi possível realizar a simulação: ${simulation.msg}`
            }
            else{
                console.log(simulation)
                simText.textContent = `Simulação: R$ ${simulation.valor.toLocaleString('pt-br', {minimumFractionDigits: 2,maximumFractionDigits:2})}`
            }
        }
    }

    dataInicioInput.addEventListener("input",async()=>{

        await write()

    })
    dataFimInput.addEventListener("input",async()=>{

        await write()

    })

})