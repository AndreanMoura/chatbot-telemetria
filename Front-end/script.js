const API_BASE_URL = "https://chatbot-telemetria.onrender.com"; // Verifique se é este o link no Render

let estado = { chapa: null };

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const quickActions = document.getElementById("quickActions");

function appendMessage(text, who = "bot") {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  
  // Converte Markdown de tabela e negrito vindo do Python
  let formattedText = text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  if (text.includes("|")) {
    const lines = text.split("\n");
    let tableHtml = "<table style='width:100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 10px;'>";
    lines.forEach(line => {
      if (line.trim().startsWith("|") && !line.includes("---")) {
        const cols = line.split("|").filter(c => c.trim() !== "");
        tableHtml += "<tr>" + cols.map(c => `<td style='border: 1px solid #4a3a8a; padding: 4px;'>${c.trim()}</td>`).join("") + "</tr>";
      }
    });
    tableHtml += "</table>";
    formattedText = formattedText.split("<br>|")[0] + tableHtml;
  }

  div.innerHTML = formattedText;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function consultarServidor(endpoint, params) {
  const query = new URLSearchParams(params).toString();
  const url = `${API_BASE_URL}/${endpoint}?${query}`;
  
  appendMessage("⏳ Consultando base...");

  try {
    const response = await fetch(url, { method: 'GET', mode: 'cors' });
    if (!response.ok) throw new Error(`Erro: ${response.status}`);

    const data = await response.json();
    removerUltimaMensagem("⏳ Consultando");

    // O Python retorna na chave 'resultado'
    appendMessage(data.resultado || "Sem dados encontrados.");
    quickActions.style.display = "flex";
  } catch (error) {
    removerUltimaMensagem("⏳ Consultando");
    appendMessage(`🚨 Erro de conexão: ${error.message}`);
  }
}

function enviar() {
  const valor = input.value.trim();
  if (!valor) return;
  appendMessage(valor, "user");
  input.value = "";

  if (!estado.chapa) {
    estado.chapa = valor;
    // Primeira consulta busca na Base de Grupo
    consultarServidor("grupo", { re: valor });
  }
}

function selecionarAcao(tipo) {
    if (!estado.chapa) return;
    const hoje = new Date().toLocaleDateString('pt-BR');
    
    if (tipo === 'performance') consultarServidor("grupo", { re: estado.chapa });
    if (tipo === 'eventos') consultarServidor("eventos", { re: estado.chapa, data: hoje });
    if (tipo === 'metricas') consultarServidor("metricas", { re: estado.chapa, data: hoje });
}

function removerUltimaMensagem(texto) {
    const mensagens = document.querySelectorAll('.msg.bot');
    for (let i = mensagens.length - 1; i >= 0; i--) {
        if (mensagens[i].innerText.includes(texto)) { mensagens[i].remove(); break; }
    }
}

function limparChat() {
    estado.chapa = null;
    chat.innerHTML = "";
    quickActions.style.display = "none";
    appendMessage("👋 Olá! Informe o **RE ou Chapa** para iniciar:");
}

window.onload = () => appendMessage("👋 Olá! Informe o **RE ou Chapa** para iniciar:");
input.addEventListener("keypress", (e) => { if (e.key === "Enter") enviar(); });