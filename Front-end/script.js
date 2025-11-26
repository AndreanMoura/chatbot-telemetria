// URL da API hospedada no Render
const API_BASE_URL = 'https://chatbot-telemetria.onrender.com';

/**
 * Função principal para consultar a API Flask (Rotas /eventos e /metricas)
 * @param {string} tipo - 'eventos' ou 'metricas'
 */
async function consultar(tipo) {
    const chapa = document.getElementById('chapa').value.trim();
    const data = document.getElementById('data').value.trim();
    const resultadoDiv = document.getElementById('resultado');

    if (!chapa || !data) {
        resultadoDiv.innerHTML = `
            <p class="erro">❌ Preencha RE/Chapa e Data.</p>
        `;
        return;
    }

    resultadoDiv.innerHTML = `<p class="carregando">⏳ Consultando servidor...</p>`;

    const url = `${API_BASE_URL}/${tipo}?re=${chapa}&data=${data}`;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            const err = await response.json();
            resultadoDiv.innerHTML = `
                <p class="erro">🚨 Erro (${response.status})</p>
                <p>${err.mensagem || err.erro}</p>
            `;
            return;
        }

        const json = await response.json();
        const texto = json.resultado;

        // Converte tabela Markdown → tabela HTML
        const htmlTabela = markdownParaTabela(texto);

        resultadoDiv.innerHTML = `
            <h3 class="ok">✅ Consulta de ${tipo} concluída</h3>
            ${htmlTabela}
        `;

    } catch (error) {
        resultadoDiv.innerHTML = `
            <p class="erro">⚠️ Não foi possível conectar à API.</p>
            <p style="font-size: 0.8em;">Detalhe: ${error.message}</p>
        `;
    }
}

/**
 * Converte tabela em Markdown → HTML formatado
 */
function markdownParaTabela(md) {
    const linhas = md.split("\n").filter(l => l.trim() !== "");

    // Metadados (cabeçalho acima da tabela)
    const meta = linhas.slice(0, 3).join("<br>");

    // Tabela começa após linha "---"
    const tabelaLinhas = linhas.slice(3);

    let cabecalho = tabelaLinhas[0]
        .replace(/\|/g, " ")
        .trim()
        .split(/\s*\|\s*/)
        .filter(c => c !== "");

    let html = `
        <div class="meta">${meta}</div>
        <table class="tabela">
            <thead>
                <tr>
                    ${cabecalho.map(c => `<th>${c}</th>`).join("")}
                </tr>
            </thead>
            <tbody>
    `;

    // Linhas de dados
    for (let i = 2; i < tabelaLinhas.length; i++) {
        const partes = tabelaLinhas[i]
            .replace(/\|/g, " ")
            .trim()
            .split(/\s*\|\s*/)
            .filter(c => c !== "");

        if (partes.length === cabecalho.length) {
            html += `<tr>${partes.map((p, idx) => {
                // Se for número, formatar
                if (!isNaN(p)) {
                    return `<td class="num">${formatarNumero(p)}</td>`;
                }
                return `<td>${p}</td>`;
            }).join("")}</tr>`;
        }
    }

    html += `</tbody></table>`;
    return html;
}

/**
 * Formata números: 1000 → 1.000 | 12000 → 12.000
 */
function formatarNumero(n) {
    return Number(n).toLocaleString("pt-BR");
}
