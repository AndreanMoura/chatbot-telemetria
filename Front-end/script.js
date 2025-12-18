/**
 * Altere para a URL correta do seu Render.
 * Certifique-se de que não há barra "/" no final.
 */
const API_BASE_URL = "https://chatbot-telemetria.onrender.com";

let estado = {
  chapa: null
};

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const quickActions = document.getElementById("quickActions");

/**
 * Adiciona mensagem na tela com suporte a tabelas simples
 */
function appendMessage(text, who = "bot") {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  
  let formattedText = text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Conversão de tabelas Markdown simples para HTML
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

/**
 * Envio de mensagem
 */
function enviar() {
  const valor = input.value.trim();
  if (!valor) return;

  appendMessage(valor, "user");
  input.value = "";

  if (!estado.chapa) {
    estado.chapa = valor;
    consultarServidor("resumo", { chapa: valor });
  } else {
    // Comandos extras se necessário
    consultarServidor("resumo", { chapa: estado.chapa });
  }
}

/**
 * Função genérica para consultar o servidor
 */
async function consultarServidor(endpoint, params) {
  const query = new URLSearchParams(params).toString();
  const url = `${API_BASE_URL}/${endpoint}?${query}`;
  
  const loadingMsg = "⏳ Consultando base de dados...";
  appendMessage(loadingMsg);

  try {
    // Definimos um timeout para não ficar esperando eternamente
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 segundos

    const response = await fetch(url, {
      method: 'GET',
      mode: 'cors', // Crucial para o Render
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }

    const data = await response.json();
    
    // Remove a mensagem de carregamento antes de mostrar a resposta
    removerUltimaMensagem(loadingMsg);

    // Prioriza o campo 'resposta' ou 'mensagem'
    const textoBot = data.resposta || data.mensagem || JSON.stringify(data);
    appendMessage(textoBot);
    
    if (quickActions) quickActions.style.display = "flex";

  } catch (error) {
    removerUltimaMensagem(loadingMsg);
    console.error("Erro detalhado:", error);
    
    if (error.name === 'AbortError') {
      appendMessage("🚨 A conexão demorou demais (Timeout). O servidor do Render pode estar 'acordando' (Cold Start). Tente novamente em alguns segundos.");
    } else {
      appendMessage(`🚨 Não consegui conectar ao servidor.\n\nMotivo: ${error.message}\nVerifique se o backend está ativo em: ${API_BASE_URL}`);
    }
  }
}

function removerUltimaMensagem(texto) {
    const mensagens = document.querySelectorAll('.msg.bot');
    for (let i = mensagens.length - 1; i >= 0; i--) {
        if (mensagens[i].innerText.includes(texto)) {
            mensagens[i].remove();
            break;
        }
    }
}

function selecionarAcao(tipo) {
    if (!estado.chapa) return;
    if (tipo === 'performance') consultarServidor("resumo", { chapa: estado.chapa });
    if (tipo === 'dados') consultarServidor("motorista", { chapa: estado.chapa });
}

window.onload = () => {
  appendMessage("👋 Olá! Informe o **RE ou Chapa** para iniciar a consulta:");
};

// Suporte ao Enter
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") enviar();
});