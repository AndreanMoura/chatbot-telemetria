/* ================= CONFIG ================= */
const API_BASE_URL = "https://chatbot-telemetria.onrender.com";

/* ---------- Tema ---------- */
document.getElementById("themeToggle").addEventListener("click", () => {
    document.body.classList.toggle("light");
});

/* ---------- Helpers ---------- */
function appendMessage(text, who = "bot", html = false) {
    const chat = document.getElementById("chat");

    const el = document.createElement("div");
    el.className = "msg " + (who === "user" ? "user" : "bot");

    if (html) el.innerHTML = text;
    else el.textContent = text;

    const time = document.createElement("span");
    time.className = "time";
    time.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    el.appendChild(time);

    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
}

function formatarNumero(n) {
    const clean = String(n).replace(/\./g, "").replace(/,/g, ".");
    const num = Number(clean);
    return isNaN(num) ? n : num.toLocaleString("pt-BR");
}

/* ---------- Converte Markdown → HTML ---------- */
function gerarTabelaHTML(md) {
    if (!md) return md;

    const linhas = md.split("\n").filter(l => l.trim() !== "");

    // Encontra índice do cabeçalho
    const idxCab = linhas.findIndex(l => l.includes("|"));
    if (idxCab === -1) return `<pre>${md}</pre>`;

    const meta = linhas.slice(0, idxCab).join("<br>");

    // Cabeçalho
    const header = linhas[idxCab]
        .split("|")
        .map(s => s.trim())
        .filter(Boolean);

    // Linhas de dados
    const dados = linhas
        .slice(idxCab + 2) // pula cabeçalho + separador
        .map(l =>
            l.split("|")
                .map(s => s.trim())
                .filter(Boolean)
        )
        .filter(cols => cols.length > 0);

    // Monta HTML
    let html = `<div class="meta">${meta}</div>`;
    html += `<table class="tabela-excel"><thead><tr>`;

    header.forEach(col => html += `<th>${col}</th>`);
    html += `</tr></thead><tbody>`;

    dados.forEach(cols => {
        html += "<tr>";
        cols.forEach(value => {
            if (value.match(/^[0-9\.,-]+$/)) {
                html += `<td class="num">${formatarNumero(value)}</td>`;
            } else {
                html += `<td>${value}</td>`;
            }
        });
        html += "</tr>";
    });

    html += "</tbody></table>";
    return html;
}

/* ---------- Chamada API ---------- */
async function consultar(tipo, re, data) {
    appendMessage(`${tipo.toUpperCase()} • RE:${re} • ${data}`, "user");
    appendMessage(`⏳ Consultando ${tipo}...`, "bot");

    try {
        const url = `${API_BASE_URL}/${tipo}?re=${encodeURIComponent(re)}&data=${encodeURIComponent(data)}`;
        const resp = await fetch(url);

        if (!resp.ok) {
            const err = await resp.json();
            appendMessage(`❌ Erro: ${err.mensagem || err.erro}`, "bot");
            return;
        }

        const json = await resp.json();
        const msg = gerarTabelaHTML(json.resultado);
        appendMessage(msg, "bot", true);

    } catch (e) {
        appendMessage(`⚠️ Erro: ${e.message}`, "bot");
    }
}

/* ---------- Botões ---------- */
document.getElementById("btnEventos").addEventListener("click", () => {
    const re = document.getElementById("inpRe").value.trim();
    const data = document.getElementById("inpDate").value;

    if (!re || !data)
        return appendMessage("❌ Preencha RE e Data", "bot");

    consultar("eventos", re, formatarData(data));
});

document.getElementById("btnMetricas").addEventListener("click", () => {
    const re = document.getElementById("inpRe").value.trim();
    const data = document.getElementById("inpDate").value;

    if (!re || !data)
        return appendMessage("❌ Preencha RE e Data", "bot");

    consultar("metricas", re, formatarData(data));
});

/* ---------- Botão Grupo / Performance ---------- */
document.getElementById("btnGrupo").addEventListener("click", () => {
    const re = document.getElementById("inpRe").value.trim();

    if (!re)
        return appendMessage("❌ Preencha o RE / Chapa", "bot");

    appendMessage(`GRUPO • RE:${re}`, "user");
    appendMessage(`⏳ Consultando grupo/performance...`, "bot");

    fetch(`${API_BASE_URL}/grupo?re=${encodeURIComponent(re)}`)
        .then(resp => resp.json())
        .then(json => {
            const msg = gerarTabelaHTML(json.resultado);
            appendMessage(msg, "bot", true);
        })
        .catch(e => {
            appendMessage(`⚠️ Erro: ${e.message}`, "bot");
        });
});

/* ---------- Util ---------- */
function formatarData(yyyyMMdd) {
    const [y, m, d] = yyyyMMdd.split("-");
    return `${d}/${m}/${y}`;
}

/* ---------- Mensagem inicial ---------- */
setTimeout(() => {
    appendMessage(
        "📋 MENU DE CONSULTA<br>" +
        "1️⃣ Grupo / Performance<br>" +
        "2️⃣ Eventos<br>" +
        "3️⃣ Métricas<br><br>" +
        "Informe RE e Data (se necessário) e clique no botão desejado.",
        "bot",
        true
    );
}, 300);
