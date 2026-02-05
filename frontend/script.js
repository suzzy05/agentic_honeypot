async function send() {
  let text = document.getElementById("msg").value;
  let res = await fetch("http://localhost:8000/honeypot/message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": "SECRET123"
    },
    body: JSON.stringify({
      sessionId: "demo-session",
      message: {
        sender: "scammer",
        text: text,
        timestamp: Date.now()
      },
      conversationHistory: []
    })
  });
  let data = await res.json();
  document.getElementById("out").innerText += "\nAgent: " + data.reply;
}
