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

/* ---------- Converte Markdown → Tabela HTML ---------- */
function gerarTabelaHTML(md) {
    if (!md) return md;

    const linhas = md.split("\n").map(l => l.trim()).filter(l => l !== "");

    const idxCab = linhas.findIndex(l => l.includes("|"));
    if (idxCab === -1) return `<pre>${md}</pre>`;

    const meta = linhas.slice(0, idxCab).join("<br>");
    const header = linhas[idxCab];
    const dados = linhas.slice(idxCab + 2);

    const colunas = header.replace(/\|/g, " ").trim().split(/\s+/);

    let html = `<div class="meta">${meta}</div>`;
    html += `<table class="tabela-excel"><thead><tr>`;

    colunas.forEach(c => html += `<th>${c}</th>`);
    html += `</tr></thead><tbody>`;

    dados.forEach(l => {
        if (!l.includes("|")) return;

        let partes = l.replace(/\|/g, " ").trim().split(/\s+/);

        if (partes.length === colunas.length) {
            html += "<tr>";
            partes.forEach((p) => {
                if (p.match(/^[0-9\.,]+$/)) html += `<td class="num">${formatarNumero(p)}</td>`;
                else html += `<td>${p}</td>`;
            });
            html += "</tr>";
        }
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

    if (!re || !data) return appendMessage("❌ Preencha RE e Data", "bot");

    consultar("eventos", re, formatarData(data));
});

document.getElementById("btnMetricas").addEventListener("click", () => {
    const re = document.getElementById("inpRe").value.trim();
    const data = document.getElementById("inpDate").value;

    if (!re || !data) return appendMessage("❌ Preencha RE e Data", "bot");

    consultar("metricas", re, formatarData(data));
});

/* ---------- Util ---------- */
function formatarData(yyyyMMdd) {
    const [y, m, d] = yyyyMMdd.split("-");
    return `${d}/${m}/${y}`;
}

/* Mensagem inicial */
setTimeout(() => {
    appendMessage("Olá! Informe RE + Data e clique em Eventos ou Métricas.", "bot");
}, 300);
