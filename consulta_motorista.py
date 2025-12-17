import pandas as pd
import requests

# ===============================================================
# CONFIGURAÇÃO DA API
# ===============================================================
API_URL = "https://siannet.gestaosian.com/api/EscaladoInformacao?empresa=2&data_inicio=01/12/2025&data_fim=30/12/2025"
API_USER = "gds"
API_PASS = "SUA_SENHA"
TIMEOUT_API = 600  # 10 minutos


# ===============================================================
# FUNÇÃO: BUSCAR DADOS DA API
# ===============================================================
def carregar_motoristas_da_api():

    response = requests.get(
        API_URL,
        auth=(API_USER, API_PASS),
        timeout=TIMEOUT_API
    )

    response.raise_for_status()

    retorno = response.json()

    # Esperado: { sucesso, param, dados }
    if "dados" not in retorno or not isinstance(retorno["dados"], list):
        raise ValueError(
            f"Formato inesperado da API. Chaves recebidas: {list(retorno.keys())}"
        )

    df = pd.DataFrame(retorno["dados"])

    if df.empty:
        return df

    # Normalizar colunas
    df.columns = df.columns.str.lower().str.strip()

    return df


# ===============================================================
# FUNÇÃO: CONSULTAR MOTORISTA POR CHAPA (RETORNA JSON)
# ===============================================================
def consultar_motorista_por_chapa(chapa):

    try:
        df = carregar_motoristas_da_api()
    except Exception as e:
        return {"erro": f"Erro ao consultar API: {e}"}

    if df.empty:
        return {"mensagem": "Nenhum dado retornado pela API"}

    # Normalizar chapa
    chapa = str(chapa).zfill(9)
    df["chapa"] = df["chapa"].astype(str).str.zfill(9)

    motorista = df[df["chapa"] == chapa]

    if motorista.empty:
        return {"mensagem": f"Nenhum motorista encontrado para a chapa {chapa}"}

    row = motorista.iloc[0]

    return {
        "id": row.get("id"),
        "matricula": row.get("matricula"),
        "chapa": row.get("chapa"),
        "nome": row.get("nome"),
        "sexo": row.get("sexo"),
        "idade": row.get("idade"),
        "admissao": row.get("admissao"),
        "demissao": row.get("demissao"),
        "funcao_codigo": row.get("funcao"),
        "funcao_nome": row.get("nome_funcao"),
        "empresa_id": row.get("id_empresa"),
        "folga": row.get("folga"),
        "ultima_folga": row.get("ult_folga"),
        "ultima_folga_dom": row.get("ult_folga_dom"),
        "turno": row.get("turno"),
        "garagem": row.get("garagem"),
        "equipamento": row.get("equipamento"),
        "inicio": row.get("inicio"),
        "fim": row.get("fim"),
        "situacao": row.get("situacao"),
        "cnh_vencimento": row.get("cnh_venc"),
        "capacitacao": row.get("capacitacao"),
        "monitor": {
            "registro": row.get("monitor_desemp_re"),
            "nome": row.get("monitor_desemp_nome"),
            "agrupamento": row.get("monitor_desemp_agrup"),
            "foto": row.get("monitor_desemp_foto")
        },
        "fotos": {
            "motorista": row.get("escalado_foto")
        }
    }


# ===============================================================
# FUNÇÃO: FORMATAR RESPOSTA PARA CHATBOT
# ===============================================================
def formatar_motorista_para_chat(dados):

    if not isinstance(dados, dict):
        return "🚨 Erro ao processar dados do motorista."

    if "erro" in dados:
        return f"🚨 {dados['erro']}"

    if "mensagem" in dados:
        return f"ℹ️ {dados['mensagem']}"

    linhas = []

    # =========================
    # MOTORISTA
    # =========================
    linhas.append("👤 *MOTORISTA*")
    linhas.append(f"Nome: {dados.get('nome')}")
    linhas.append(f"Chapa: {dados.get('chapa')}")
    linhas.append(f"Matrícula: {dados.get('matricula')}")
    linhas.append(f"Sexo: {dados.get('sexo')} | Idade: {dados.get('idade')}")
    linhas.append("")

    # =========================
    # FUNÇÃO
    # =========================
    linhas.append("💼 *FUNÇÃO*")
    linhas.append(f"Cargo: {dados.get('funcao_nome')}")
    linhas.append(f"Turno: {dados.get('turno')}")
    linhas.append(f"Garagem: {dados.get('garagem')}")
    linhas.append(f"Situação: {dados.get('situacao')}")
    linhas.append("")

    # =========================
    # VÍNCULO
    # =========================
    linhas.append("📆 *VÍNCULO*")
    linhas.append(f"Admissão: {dados.get('admissao')}")
    linhas.append(f"Início: {dados.get('inicio')}")
    linhas.append(f"Fim: {dados.get('fim')}")
    linhas.append(f"Folga: {dados.get('folga')}")
    linhas.append(f"Última folga: {dados.get('ultima_folga')}")
    linhas.append("")

    # =========================
    # CNH
    # =========================
    linhas.append("🪪 *CNH*")
    linhas.append(f"Vencimento: {dados.get('cnh_vencimento')}")
    linhas.append("")

    # =========================
    # MONITOR
    # =========================
    monitor = dados.get("monitor", {})
    linhas.append("👨‍💼 *MONITOR*")
    linhas.append(f"Nome: {monitor.get('nome')}")
    linhas.append(f"Agrupamento: {monitor.get('agrupamento')}")

    return "\n".join(linhas)


# ===============================================================
# FUNÇÃO FINAL DO CHATBOT
# ===============================================================
def chatbot_motorista_por_chapa(chapa):
    dados = consultar_motorista_por_chapa(chapa)
    return formatar_motorista_para_chat(dados)


# ===============================================================
# TESTE LOCAL
# ===============================================================
if __name__ == "__main__":
    print("🤖 Resposta do Chatbot:\n")
    print(chatbot_motorista_por_chapa("4639"))
