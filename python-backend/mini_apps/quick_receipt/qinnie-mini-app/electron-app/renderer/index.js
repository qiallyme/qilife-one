function sendPrompt() {
    const prompt = document.getElementById("prompt").value;
    fetch("http://localhost:6543/qinnie/say", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("response").innerText = data.response;
    })
    .catch(err => {
        document.getElementById("response").innerText = "Error: " + err;
    });
}
