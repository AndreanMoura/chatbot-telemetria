import pandas as pd
import requests

# ===============================================================
# CONFIGURAÇÃO DA API
# ===============================================================
API_URL = "https://siannet.gestaosian.com/api/EscaladoInformacao?empresa=2&data_inicio=01/12/2025&data_fim=19/01/2026"
API_USER = "gds"
API_PASS = "GDS@SIANNET"
TIMEOUT_API = 600  # 10 minutos

# ===============================================================
# FUNÇÃO: BUSCAR DADOS DA API
# ===============================================================
def carregar_motoristas_da_api():
    try:
        response = requests.get(
            API_URL,
            auth=(API_USER, API_PASS),
            timeout=TIMEOUT_API
        )
        response.raise_for_status()
        retorno = response.json()

        if "dados" not in retorno or not isinstance(retorno["dados"], list):
            raise ValueError(f"Formato inesperado. Chaves: {list(retorno.keys())}")

        df = pd.DataFrame(retorno["dados"])

        if df.empty:
            return df

        # Normalizar nomes das colunas (minúsculo e sem espaços)
        df.columns = df.columns.str.lower().str.strip()
        return df

    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return pd.DataFrame()

# ===============================================================
# FUNÇÃO: CONSULTAR MOTORISTA POR CHAPA
# ===============================================================
def consultar_motorista_por_chapa(chapa):
    df = carregar_motoristas_da_api()

    if df.empty:
        return {"mensagem": "A API retornou uma base de dados vazia ou houve erro de conexão."}

    # --- NORMALIZAÇÃO DA BUSCA ---
    # Convertemos tudo para string, removemos espaços e tiramos zeros à esquerda
    # Isso garante que '00014594' seja igual a '14594'
    chapa_busca = str(chapa).strip().lstrip('0')
    
    # Criamos uma coluna temporária limpa para comparação
    df["chapa_limpa"] = df["chapa"].astype(str).str.strip().str.lstrip('0')

    # DEBUG: Remova esses prints após funcionar
    print(f"🔍 Buscando por: '{chapa_busca}'")
    print(f"📋 Exemplo de chapas da API: {df['chapa_limpa'].head().tolist()}")

    motorista = df[df["chapa_limpa"] == chapa_busca]

    if motorista.empty:
        return {"mensagem": f"Nenhum motorista encontrado para a chapa {chapa}"}

    row = motorista.iloc[0]

    # Montagem do dicionário com tratamento de erros de coluna
    return {
        "id": row.get("id"),
        "matricula": row.get("matricula"),
        "chapa": row.get("chapa"),
        "nome": row.get("nome"),
        "sexo": row.get("sexo"),
        "idade": row.get("idade"),
        "admissao": row.get("admissao"),
        "demissao": row.get("demissao"),
        "funcao_nome": row.get("nome_funcao") or row.get("funcao"),
        "turno": row.get("turno"),
        "garagem": row.get("garagem"),
        "situacao": row.get("situacao"),
        "cnh_vencimento": row.get("cnh_venc"),
        "inicio": row.get("inicio"),
        "fim": row.get("fim"),
        "folga": row.get("folga"),
        "ultima_folga": row.get("ult_folga"),
        "monitor": {
            "nome": row.get("monitor_desemp_nome"),
            "agrupamento": row.get("monitor_desemp_agrup")
        }
    }

# ===============================================================
# FUNÇÃO: FORMATAR RESPOSTA PARA CHATBOT
# ===============================================================
def formatar_motorista_para_chat(dados):
    if "erro" in dados: return f"🚨 {dados['erro']}"
    if "mensagem" in dados: return f"ℹ️ {dados['mensagem']}"

    # Construção da mensagem amigável
    linhas = [
        "👤 *MOTORISTA*",
        f"Nome: {dados.get('nome')}",
        f"Chapa: {dados.get('chapa')}",
        f"Matrícula: {dados.get('matricula')}",
        f"Sexo: {dados.get('sexo')} | Idade: {dados.get('idade')}",
        "",
        "💼 *STATUS E FUNÇÃO*",
        f"Cargo: {dados.get('funcao_nome')}",
        f"Turno: {dados.get('turno')} | Garagem: {dados.get('garagem')}",
        f"Situação: {dados.get('situacao')}",
        "",
        "📆 *VÍNCULO E ESCALA*",
        f"Admissão: {dados.get('admissao')}",
        f"Escala: {dados.get('inicio')} às {dados.get('fim')}",
        f"Folga: {dados.get('folga')} (Última: {dados.get('ultima_folga')})",
        "",
        "🪪 *CNH*",
        f"Vencimento: {dados.get('cnh_vencimento')}",
        "",
        "👨‍💼 *MONITORAMENTO*",
        f"Monitor: {dados.get('monitor', {}).get('nome')}",
        f"Agrupamento: {dados.get('monitor', {}).get('agrupamento')}"
    ]
    
    return "\n".join(linhas)

def chatbot_motorista_por_chapa(chapa):
    dados = consultar_motorista_por_chapa(chapa)
    return formatar_motorista_para_chat(dados)

# ===============================================================
# TESTE LOCAL
# ===============================================================
if __name__ == "__main__":
    print("🤖 Iniciando consulta...\n")
    # Teste com a chapa enviada (o código vai limpar os zeros e espaços)
    resultado = chatbot_motorista_por_chapa("10850")
    print(resultado)