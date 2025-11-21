document.addEventListener("DOMContentLoaded",function (){

    token_time_p = document.querySelectorAll(".token_time")[0]
    create_token_btn = document.querySelectorAll("#create_token_btn")[0]
    usuario_id = parseInt(document.querySelectorAll(".user_id")[0].id)
    console.log(token_time_p)
    console.log("Aqui")
    
    const search_time_token = async () =>{
        const resp = await fetch(`/api/token_time/${usuario_id}`)
        const data = await resp.json()
        return data  // <--- ESSENCIAL
    }
    const draw = async () => {
            seconds = await search_time_token()
            console.log("seconds: "+ seconds.time + "menor que 0:" + (seconds.min <= 0 && seconds.sec <=0 ))
            if ((seconds.min <= 0 && seconds.sec <=0 )){
                token_time_p.innerHTML = `<p class='token_time'>O seu token mais recente expirou.</p>`
                create_token_btn.disabled=false
                create_token_btn.classList.remove("disabled")
                console.log(create_token_btn,create_token_btn.disabled)
                clearInterval(write)
                return
            }
            token_time_p.innerText = `O seu token mais recente irá expirar em: ${seconds.min} minutos e ${seconds.sec} segundos`
            return seconds
            }
    draw()    
    const write = setInterval(()=>{
        
        draw()
    
    
    },4000)

})  