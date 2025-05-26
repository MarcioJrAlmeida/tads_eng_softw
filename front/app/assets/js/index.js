// Função para o relógio
function updateClock(){
    const now = new Date();
    const time = now.toLocaleTimeString();
    const clockElement = document.getElementById('clock');
    if (clockElement) {
        clockElement.innerHTML = time;
    }
}
setInterval(updateClock, 1000);
updateClock();

// Função para mostrar Toast
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.display = "block";
    setTimeout(() => {
        toast.style.display = "none";
    }, 4000);
}
