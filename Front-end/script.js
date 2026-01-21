// Substitua pelo endereço que aparece no seu terminal Python
const API_BASE_URL = "http://127.0.0.1:5000"; 

let estado = { chapa: null };

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const quickActions = document.getElementById("quickActions");

function appendMessage(text, who = "bot") {
  // Esconde o círculo central ao começar a conversa
  const welcome = document.querySelector('.welcome-area');
  if (welcome) welcome.style.display = 'none';

  const div = document.createElement("div");
  div.className = `msg ${who}`;
  
  // Converte Markdown e quebras de linha
  let formattedText = text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Formatação de tabela se houver caracteres "|"
  if (text.includes("|")) {
    const lines = text.split("\n");
    let tableHtml = "<table style='width:100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 10px;'>";
    lines.forEach(line => {
      if (line.trim().startsWith("|") && !line.includes("---")) {
        const cols = line.split("|").filter(c => c.trim() !== "");
        tableHtml += "<tr>" + cols.map(c => `<td style='border: 1px solid #333; padding: 4px;'>${c.trim()}</td>`).join("") + "</tr>";
      }
    });
    tableHtml += "</table>";
    formattedText = formattedText.split("<br>|")[0] + tableHtml;
  }

  div.innerHTML = formattedText;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

// FUNÇÃO PRINCIPAL: Agora acessa /chatbot/VALOR
async function consultarServidor(chapa) {
  const url = `${API_BASE_URL}/chatbot/${chapa}`;
  
  appendMessage("⏳ Consultando Webot...");

  try {
    const response = await fetch(url, { method: 'GET' });
    if (!response.ok) throw new Error(`Erro: ${response.status}`);

    const data = await response.json();
    removerUltimaMensagem("⏳ Consultando");

    // O Python retorna os dados na chave 'texto'
    if (data.texto) {
        appendMessage(data.texto);
    } else {
        appendMessage("❌ Não foram encontrados dados para esta chapa.");
    }
    
    quickActions.style.display = "flex";
  } catch (error) {
    removerUltimaMensagem("⏳ Consultando");
    appendMessage(`🚨 Erro de conexão: Verifique se o Python está rodando.`);
    console.error(error);
  }
}

function enviar() {
  const valor = input.value.trim();
  if (!valor) return;
  appendMessage(valor, "user");
  input.value = "";

  estado.chapa = valor;
  // Chama a função passando apenas a chapa
  consultarServidor(valor);
}

function selecionarAcao(tipo) {
    if (!estado.chapa) return;
    // Como sua rota concentra tudo, apenas re-consulta a chapa
    consultarServidor(estado.chapa);
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
    location.reload(); // Recarrega para voltar à tela inicial
}

input.addEventListener("keypress", (e) => { if (e.key === "Enter") enviar(); });