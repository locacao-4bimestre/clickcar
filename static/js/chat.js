document.addEventListener("DOMContentLoaded",()=>{
    
     const chatButton = document.getElementById("chat-button");
    const chatWindow = document.getElementById("chat-window");
    const chatClose = document.getElementById("chat-close");
    const chatSendBtn = document.getElementById("chat-send")
    const chatInput = document.getElementById("chat-input")
    const chatBody = document.querySelector(".chat-body");
    function addMessage(sender, message) {
        const p = document.createElement("p");
        p.innerHTML = `<strong>${sender}:</strong> ${message}`;
        p.style.marginBottom = "6px";
        p.style.color = "white";

        chatBody.appendChild(p);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    chatButton.addEventListener("click", () => {
        chatWindow.style.display = "flex";
        chatButton.style.display = "none";
    });

    chatClose.addEventListener("click", () => {
        chatWindow.style.display = "none";
        chatButton.style.display = "flex";
    });
    chatSendBtn.addEventListener("click",(e)=>{
        
        async function fetchingBot(){
            text = chatInput.value
            addMessage("Você", text);
            fetch("/api/chatbot",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"  
                },
                body: JSON.stringify({
                    'text': text
                })
            }).then(res=> res.json()).then(data => {
                if (data.text){
                    addMessage("Gemini",data.text)
                }
                else {
                    addMessage("Gemini", "Desculpe, não")
                }
            })
        }
        fetchingBot()
    })
})