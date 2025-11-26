// ATENÇÃO: Se você hospedar sua API em outro lugar, mude este endereço!
const API_BASE_URL = 'http://127.0.0.1:5000'; 

/**
 * Função principal para consultar a API Flask (Rotas /eventos e /metricas)
 * @param {string} tipo - 'eventos' ou 'metricas', define qual rota chamar.
 */
async function consultar(tipo) {
    const chapa = document.getElementById('chapa').value.trim();
    const data = document.getElementById('data').value.trim();
    const resultadoDiv = document.getElementById('resultado');
    
    // 1. Validação de Inputs
    if (!chapa || !data) {
        // Estilo com base no tema dark
        resultadoDiv.innerHTML = '<p style="color: #FF6347; font-weight: bold;">❌ Por favor, preencha o RE/Chapa e a Data.</p>';
        return;
    }

    // 2. Feedback Visual
    resultadoDiv.innerHTML = '<p style="color: #6A5ACD;">⏳ Buscando dados no servidor...</p>';

    // 3. Construção da URL de requisição
    const url = `${API_BASE_URL}/${tipo}?re=${chapa}&data=${data}`;

    try {
        // 4. Faz a requisição GET para a API Flask
        const response = await fetch(url);
        
        // 5. Verifica se a resposta HTTP é um erro (4xx ou 5xx)
        if (!response.ok) {
            const errorData = await response.json();
            // A API retorna a mensagem do Python na chave 'mensagem' (404) ou 'erro' (500)
            const msg = errorData.mensagem || errorData.erro || "Falha desconhecida da API.";

            resultadoDiv.innerHTML = `
                <p style="color: #FF4500; font-weight: bold;">🚨 Falha na Consulta (${response.status})</p>
                <p style="font-size: 0.9em;">${msg}</p>
            `;
            return;
        }

        // 6. Converte a resposta JSON em um objeto JavaScript
        const dataJson = await response.json();
        
        // 7. Processa e exibe o resultado
        let rawOutput = dataJson.resultado; 
        
        // Tenta converter o Markdown de Tabela para HTML de Tabela
        const htmlOutput = rawOutput.includes('|') ? convertMarkdownTableToHTML(rawOutput) : rawOutput;

        resultadoDiv.innerHTML = `
            <div style="font-weight: bold; color: #3CB371; margin-bottom: 15px;">✅ Consulta de ${tipo} concluída!</div>
            ${htmlOutput}
        `;

    } catch (error) {
        // Erros de rede (API não está no ar, problema de CORS, etc.)
        resultadoDiv.innerHTML = `
            <p style="color: #8B0000; font-weight: bold;">⚠️ Erro de Comunicação: Não foi possível conectar à API.</p>
            <p style="font-size: 0.8em;">Verifique se o servidor Flask está rodando. Detalhe: ${error.message}</p>
        `;
        console.error('Fetch Error:', error);
    }
}

/**
 * Função auxiliar para converter a tabela formatada em Markdown (do Python) 
 * em HTML real para melhor exibição dentro da div #resultado.
 */
function convertMarkdownTableToHTML(markdown) {
    // Quebra em linhas e remove linhas vazias
    const lines = markdown.split('\n').filter(line => line.trim() !== '');
    
    // O cabeçalho da tabela começa na linha 4 (índice 3) do output Python
    if (lines.length < 5) return markdown; 

    // O início das linhas de dados está na linha 6 (índice 5)
    
    // Extrai o cabeçalho
    const headerLine = lines[3]; 
    const headerCells = headerLine.replace(/\|/g, ' ').trim().split(/\s*\|\s*/).filter(cell => cell);
    
    // Cria o cabeçalho HTML
    let html = '<table><thead><tr>';
    headerCells.forEach(cell => {
        html += `<th>${cell.replace(/\*\*/g, '').trim()}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Processa as linhas de dados (começa do índice 5 em diante)
    for (let i = 5; i < lines.length; i++) {
        const dataLine = lines[i];
        // Divide a linha de dados removendo as barras
        const dataCells = dataLine.replace(/\|/g, ' ').trim().split(/\s*\|\s*/).filter(cell => cell);
        
        if (dataCells.length === headerCells.length) {
            html += '<tr>';
            dataCells.forEach(cell => {
                const cleanedCell = cell.replace(/\*\*/g, '').trim();
                const isTotal = cell.includes('**TOTAL**');
                html += `<td>${isTotal ? `<strong>${cleanedCell}</strong>` : cleanedCell}</td>`;
            });
            html += '</tr>';
        }
    }
    
    html += '</tbody></table>';
    
    // Adiciona as informações do motorista que vêm antes da tabela
    const metaInfoLines = lines.slice(0, 3).join('\n');
    
    // Retorna a meta-informação formatada e a tabela HTML
    return `<pre style="font-weight: bold; margin-bottom: 10px; font-family: 'Inter', sans-serif;">${metaInfoLines}</pre>` + html;
}