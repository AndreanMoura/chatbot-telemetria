import pandas as pd
import requests
import os

# ===============================================================
# CONFIGURAÇÕES
# ===============================================================
API_URL = "https://siannet.gestaosian.com/api/WsPrime?campanha=2025/2026&resultado=performance_sintetico"
API_USER = "jbs"
API_PASS = "SUA_SENHA"
TIMEOUT_API = 600

CAMINHO_BASE = r"C:\Users\andrean.miranda\OneDrive - Grupo HSGP\Arquivos de Mohamed Hally Alves do Nascimento - GESTAO DE BI 1\Operação\Guilherme\Python\Chatbot\Base Grafico Painel.xlsx"
NOME_ABA = "Base detalhamento"

# ===============================================================
# BASE OPERACIONAL
# ===============================================================
def carregar_base_excel():
    if not os.path.exists(CAMINHO_BASE):
        raise FileNotFoundError("Arquivo da base operacional não encontrado")

    df = pd.read_excel(
        CAMINHO_BASE,
        sheet_name=NOME_ABA,
        engine="openpyxl"
    )

    df.columns = df.columns.str.lower().str.strip()
    df["chapa"] = df["chapa"].astype(str).str.zfill(9)

    return df


# ===============================================================
# API DE DESEMPENHO
# ===============================================================
def carregar_desempenho_api(chapa):
    response = requests.get(
        API_URL,
        auth=(API_USER, API_PASS),
        timeout=TIMEOUT_API
    )

    response.raise_for_status()

    retorno = response.json()

    if "dados" not in retorno:
        raise ValueError("Formato inesperado da API de desempenho")

    df = pd.DataFrame(retorno["dados"])
    df.columns = df.columns.str.lower().str.strip()
    df["chapa"] = df["chapa"].astype(str).str.zfill(9)

    return df[df["chapa"] == chapa]


# ===============================================================
# FUNÇÃO PRINCIPAL – API
# ===============================================================
def obter_desempenho_motorista(chapa):
    chapa = str(chapa).zfill(9)

    # ---------- Base cadastral ----------
    base_df = carregar_base_excel()
    motorista_df = base_df[base_df["chapa"] == chapa]

    if motorista_df.empty:
        return {"mensagem": "Motorista não encontrado"}

    m = motorista_df.iloc[0]

    # ---------- Desempenho ----------
    desempenho_df = carregar_desempenho_api(chapa)

    desempenho = {}
    if not desempenho_df.empty:
        d = desempenho_df.iloc[0]
        desempenho = {
            "referencia": d.get("mesano"),
            "status": d.get("status"),
            "meta_km_l": d.get("meta"),
            "km_rodado": d.get("km_rodada"),
            "litros_consumidos": d.get("litros_consumidos"),
            "km_por_litro": d.get("km_por_litro"),
            "economia": d.get("economia"),
            "co2": d.get("co2"),
            "premio_total": d.get("premio-final", {}).get("dados", {}).get("total", 0)
        }

    return {
        "motorista": {
            "chapa": chapa,
            "nome": m.get("nome"),
            "funcao": m.get("funcao"),
            "grupo": m.get("grupo")
        },
        "desempenho_mensal": desempenho
    }
