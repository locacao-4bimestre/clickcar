document.addEventListener('DOMContentLoaded',()=>{

    const q = document.getElementById("q")
    const marca = document.getElementById("marca")
    const ano = document.getElementById("ano")

    const clean_filter_btn = document.getElementById('clean_filter_btn')
    clean_filter_btn.addEventListener("click",(e)=>{
        e.preventDefault()
        q.value = ''
        marca.value = ''
        ano.value = ''
    })


})