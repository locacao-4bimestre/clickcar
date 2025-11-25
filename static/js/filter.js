document.addEventListener('DOMContentLoaded', () => {

    const q = document.getElementById("q");
    const marca = document.getElementById("marca");
    const ano = document.getElementById("ano");
    const ordem = document.getElementById("ordem");

    const clean_filter_btn = document.getElementById('clean_filter_btn');
    
    if (clean_filter_btn) {
        clean_filter_btn.addEventListener("click", (e) => {
            e.preventDefault();
            

            if(q) q.value = '';
            if(marca) marca.value = '';
            if(ano) ano.value = '';
            if(ordem) ordem.value = ''; 


        });
    }

});