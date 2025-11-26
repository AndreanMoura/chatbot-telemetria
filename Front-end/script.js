// URL da API hospedada no Render
const API_BASE_URL = 'https://chatbot-telemetria.onrender.com';

/**
 * Função principal para consultar a API Flask
 */
async function consultar(tipo) {
    const chapa = document.getElementById('chapa').value.trim();
    const data = document.getElementById('data').value.trim();
    const resultadoDiv = document.getElementById('resultado');

    if (!chapa || !data) {
        resultadoDiv.innerHTML = `<p class="erro">❌ Preencha RE/Chapa e Data.</p>`;
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

        // Converte tabela
        const htmlTabela = gerarTabelaHTML(texto);

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
 * Conversor universal - transforma Markdown bagunçado em tabela HTML
 * Funciona mesmo sem pipes "|"
 */
function gerarTabelaHTML(md) {
    const linhas = md.split("\n").map(l => l.trim()).filter(l => l !== "");

    // IDENTIFICA CABEÇALHO
    const idxCabecalho = linhas.findIndex(l =>
        l.includes("|") || l.split(" ").filter(x => x).length >= 4
    );

    if (idxCabecalho === -1) return md;

    const meta = linhas.slice(0, idxCabecalho).join("<br>");

    let header = linhas[idxCabecalho];
    let dados = linhas.slice(idxCabecalho + 1);

    // Se o cabeçalho não tem pipes, adiciona
    if (!header.includes("|")) {
        const partes = header.split(" ").filter(x => x);
        header = "| " + partes.join(" | ") + " |";
    }

    // Extrair colunas
    const colunas = header
        .replace(/\*/g, "")
        .replace(/\|/g, " ")
        .trim()
        .split(/\s+/);

    let html = `
        <div class="meta">${meta}</div>
        <table class="tabela-excel">
            <thead><tr>
                ${colunas.map(c => `<th>${c}</th>`).join("")}
            </tr></thead>
            <tbody>
    `;

    // CONVERTE LINHAS EM TABELA — mesmo sem pipes
    dados.forEach(linha => {
        if (linha.includes("---")) return; // ignora linhas de separador

        let partes;

        if (linha.includes("|")) {
            partes = linha.replace(/\|/g, " ").split(" ").filter(x => x);
        } else {
            partes = linha.split(" ").filter(x => x);
        }

        // Ajuste se vier mais dados que colunas → juntar o meio (nome do evento)
        if (partes.length > colunas.length) {
            partes = [
                partes[0],                             // Tipo
                partes.slice(1, partes.length - 2).join(" "), // Nome do evento
                partes[partes.length - 2],             // Quantidade
                partes[partes.length - 1]              // Pontos
            ];
        }

        if (partes.length === colunas.length) {
            html += "<tr>";
            partes.forEach((p, i) => {
                const limp = p.replace(/\*/g, "");

                // Números formatados
                if (!isNaN(limp.replace(".", "").replace(",", ""))) {
                    html += `<td class="num">${formatarNumero(limp)}</td>`;
                } else {
                    html += `<td>${limp}</td>`;
                }
            });
            html += "</tr>";
        }
    });

    html += "</tbody></table>";
    return html;
}

/**
 * Formata números (1000 → 1.000)
 */
function formatarNumero(n) {
    return Number(n.replace(",", ".")).toLocaleString("pt-BR");
}
