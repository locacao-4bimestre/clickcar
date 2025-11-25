 document.addEventListener("DOMContentLoaded",()=>{
        console.log("Aqui")
        const cepInput = document.getElementById("cep")
        const logradouroInput = document.getElementById("logradouro")
        const bairroInput = document.getElementById("bairro")
        const cidadeInput = document.getElementById("cidade")
        const estadoInput = document.getElementById("estado")
        const numeroInput = document.getElementById("numero")
        const complementoInput = document.getElementById("complemento")
        async function fetchingCep(cep) {
            data = await fetch(`https://viacep.com.br/ws/${cep}/json/`).then(res=>res.json()).then(data => data)
            return data
        }

        async function write(cep,bairro,logradouro,cidade,estado,complemento){
            cepInput.value = cep
            bairroInput.value = bairro
            logradouroInput.value = logradouro
            cidadeInput.value = cidade
            estadoInput.value = estado
            complementoInput.value = complemento         

        }
        cepInput.addEventListener("input",async ()=>{
        
            if (cepInput.value.length == 8){
                data = await fetchingCep(cepInput.value)
                console.log(data)
                if (data.erro == 'true'){
                    cepInput.value = ""
                    cepInput.placeholder = "Não foi possível encontrar o cep"
                }
                else{
                    write(data.cep,data.bairro,data.logradouro,data.localidade,data.uf,data.complemento)
                }
            }
        })


    })