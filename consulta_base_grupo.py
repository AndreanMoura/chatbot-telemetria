import pandas as pd
import requests
import os

# ===============================================================
# CONFIGURAÇÕES
# ===============================================================
API_URL = "https://siannet.gestaosian.com/api/WsPrime?campanha=2025/2026&resultado=performance_sintetico"
API_USER = "gds"
API_PASS = "SUA_SENHA"
TIMEOUT_API = 600

CAMINHO_BASE = r"C:\Users\andrean.miranda\OneDrive - Grupo HSGP\Arquivos de Mohamed Hally Alves do Nascimento - GESTAO DE BI 1\Operação\Guilherme\Python\Chatbot\Base Grafico Painel.xlsx"
NOME_ABA = "Base detalhamento"


# ===============================================================
# FUNÇÕES AUXILIARES
# ===============================================================
def formatar_numero(valor, casas=3):
    try:
        return f"{float(valor):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor


def carregar_base_excel():
    if not os.path.exists(CAMINHO_BASE):
        return None, f"🚨 Arquivo não encontrado: {CAMINHO_BASE}"

    try:
        df = pd.read_excel(CAMINHO_BASE, sheet_name=NOME_ABA, engine="openpyxl")
        df.columns = df.columns.str.lower().str.strip()
        df["chapa"] = df["chapa"].astype(str).str.zfill(9)
        return df, None
    except Exception as e:
        return None, f"🚨 Erro ao ler a base Excel: {e}"


def carregar_desempenho_api(chapa):
    response = requests.get(
        API_URL,
        auth=(API_USER, API_PASS),
        timeout=TIMEOUT_API
    )

    response.raise_for_status()
    retorno = response.json()

    if "dados" not in retorno or not isinstance(retorno["dados"], list):
        raise ValueError("Formato inesperado da API de desempenho")

    df = pd.DataFrame(retorno["dados"])
    df.columns = df.columns.str.lower().str.strip()
    df["chapa"] = df["chapa"].astype(str).str.zfill(9)

    return df[df["chapa"] == chapa]


# ===============================================================
# FUNÇÃO PRINCIPAL – RESUMO CHATBOT
# ===============================================================
def resumo_motorista_com_desempenho(chapa):
    chapa = str(chapa).zfill(9)

    # ==========================
    # BASE EXCEL
    # ==========================
    base_df, erro = carregar_base_excel()
    if erro:
        return erro

    base_motorista = base_df[base_df["chapa"] == chapa]
    if base_motorista.empty:
        return f"ℹ️ Não encontrei dados cadastrais para a chapa {chapa}."

    m = base_motorista.iloc[0]

    # ==========================
    # API DE DESEMPENHO
    # ==========================
    try:
        desempenho_df = carregar_desempenho_api(chapa)
    except Exception as e:
        return f"🚨 Erro ao consultar desempenho: {e}"

    desempenho = desempenho_df.iloc[0] if not desempenho_df.empty else None

    # ==========================
    # RESPOSTA FORMATADA
    # ==========================
    resposta = []

    resposta.append("🧾 **Resumo do Motorista**")
    resposta.append("")
    resposta.append(f"👤 **Nome:** {m.get('nome', 'N/D').title()}")
    resposta.append(f"🆔 **Chapa:** {chapa}")
    resposta.append(f"💼 **Função:** {m.get('funcao', 'N/D').title()}")
    resposta.append(f"🏢 **Grupo:** {m.get('grupo', 'N/D')}")
    resposta.append("")

    if desempenho is not None:
        resposta.append("📊 **Desempenho Mensal**")
        resposta.append(f"📅 **Referência:** {desempenho.get('mesano')}")
        resposta.append("")

        resposta.append("| Indicador | Resultado |")
        resposta.append("| :--- | :---: |")
        resposta.append(f"| Status | **{desempenho.get('status')}** |")
        resposta.append(f"| Meta (Km/L) | {formatar_numero(desempenho.get('meta'))} |")
        resposta.append(f"| Km Rodado | {formatar_numero(desempenho.get('km_rodada'))} km |")
        resposta.append(f"| Litros Consumidos | {formatar_numero(desempenho.get('litros_consumidos'))} L |")
        resposta.append(f"| Km por Litro | {formatar_numero(desempenho.get('km_por_litro'))} |")
        resposta.append(f"| Economia | {formatar_numero(desempenho.get('economia'), 0)} |")
        resposta.append(f"| CO₂ | {formatar_numero(desempenho.get('co2'), 0)} |")

        premio = desempenho.get("premio-final", {})
        if isinstance(premio, dict):
            total = premio.get("dados", {}).get("total", 0)
            resposta.append(f"| 🏆 **Prêmio Final** | **R$ {formatar_numero(total, 2)}** |")

    else:
        resposta.append("📊 **Desempenho Mensal**")
        resposta.append("ℹ️ Nenhum dado de desempenho disponível para o período.")

    resposta.append("")
    resposta.append("_📌 Informações consolidadas via API e Base Operacional._")

    return "\n".join(resposta)


# ===============================================================
# TESTE LOCAL
# ===============================================================
if __name__ == "__main__":
    print("🔍 Teste rápido:\n")
    print(resumo_motorista_com_desempenho("13899"))
