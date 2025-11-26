import pandas as pd
from datetime import datetime
import os

# ===============================================================
# CONFIGURAÇÃO DO ARQUIVO (CAMINHO RELATIVO)
# ===============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DO_ARQUIVO_DADOS = os.path.join(BASE_DIR, "Telemetria.xlsx")
NOME_ABA = "Telemetria"

# ===============================================================
# FUNÇÃO AUXILIAR – FORMATAÇÃO DE NÚMEROS
# ===============================================================
def formatar_numero(n):
    """
    Formata números inteiros usando separador de milhar.
    Exemplo: 3549 → 3.549
    """
    try:
        return f"{int(float(n)):,}".replace(",", ".")
    except:
        return n

# ===============================================================
# FUNÇÃO: CONSULTAR EVENTOS DETALHADOS
# ===============================================================
def consultar_eventos_detalhados(re, data_input):
    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use o formato DD/MM/YYYY."

    if not os.path.exists(CAMINHO_DO_ARQUIVO_DADOS):
        return f"🚨 Arquivo não encontrado: {CAMINHO_DO_ARQUIVO_DADOS}"

    try:
        df = pd.read_excel(CAMINHO_DO_ARQUIVO_DADOS, sheet_name=NOME_ABA, engine="openpyxl")
        df.columns = df.columns.str.strip()
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
    except Exception as e:
        return f"🚨 Erro ao ler a planilha: {e}"

    colunas_necessarias = ["Data", "RE", "Tipo de Evento", "Evento", "Quantidade", "Pontos"]
    faltando = [c for c in colunas_necessarias if c not in df.columns]
    if faltando:
        return f"🚨 Colunas ausentes no arquivo: {faltando}"

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True).dt.date
    df["RE"] = df["RE"].astype(str).str.strip().str.replace(".0", "", regex=False)
    re_normalizado = str(re).strip()

    df_filtrado = df[
        (df["RE"] == re_normalizado)
        & (df["Data"] == data_consulta)
    ].copy()

    if df_filtrado.empty:
        return f"ℹ️ Nenhum evento encontrado para o RE '{re}' na data {data_input}."

    resultado = []
    resultado.append(f"👤 **Motorista (RE):** {re_normalizado}")
    resultado.append(f"📅 **Data consultada:** {data_input}")
    resultado.append("")
    resultado.append("| Tipo de Evento | Evento | Quantidade | Pontos |")
    resultado.append("| :--- | :--- | :---: | :---: |")

    for _, row in df_filtrado.iterrows():
        tipo = str(row["Tipo de Evento"])
        evento = str(row["Evento"])
        qtd = formatar_numero(row["Quantidade"])
        pts = formatar_numero(row["Pontos"])
        resultado.append(f"| {tipo} | {evento} | {qtd} | {pts} |")

    total_qtd = formatar_numero(df_filtrado["Quantidade"].astype(float).sum())
    total_pts = formatar_numero(df_filtrado["Pontos"].astype(float).sum())
    resultado.append(f"| **TOTAL** | — | **{total_qtd}** | **{total_pts}** |")

    return "\n".join(resultado)

# ===============================================================
# FUNÇÃO: CONSULTAR MÉTRICAS DO DIA
# ===============================================================
def buscar_metricas_do_dia(re, data_input):
    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use o formato DD/MM/YYYY."

    if not os.path.exists(CAMINHO_DO_ARQUIVO_DADOS):
        return f"🚨 Arquivo não encontrado: {CAMINHO_DO_ARQUIVO_DADOS}"

    try:
        df = pd.read_excel(CAMINHO_DO_ARQUIVO_DADOS, sheet_name=NOME_ABA, engine="openpyxl")
        df.columns = df.columns.str.strip()
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
    except Exception as e:
        return f"🚨 Erro ao ler a planilha: {e}"

    colunas_base = ["Data", "RE", "Quantidade", "Pontos"]
    if not all(c in df.columns for c in colunas_base):
        return f"🚨 Colunas necessárias ausentes: {colunas_base}"

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True).dt.date
    df["RE"] = df["RE"].astype(str).str.strip().str.replace(".0", "", regex=False)
    re_normalizado = str(re).strip()

    df_filtrado = df[
        (df["RE"] == re_normalizado)
        & (df["Data"] == data_consulta)
    ].copy()

    if df_filtrado.empty:
        return f"ℹ️ Nenhum registro encontrado para o RE '{re}' na data {data_input}."

    qtd_total = formatar_numero(df_filtrado["Quantidade"].astype(float).sum())
    pontos_total = formatar_numero(df_filtrado["Pontos"].astype(float).sum())

    return (
        f"👤 **Motorista (RE):** {re_normalizado}\n"
        f"📅 **Data consultada:** {data_input}\n\n"
        f"| Métrica Diária | Valor |\n"
        f"| :--- | :---: |\n"
        f"| Quantidade Total | {qtd_total} |\n"
        f"| Pontos Totais | {pontos_total} |"
    )

# ===============================================================
# TESTE LOCAL
# ===============================================================
if __name__ == "__main__":
    print("🔍 Teste rápido: buscando eventos detalhados\n")
    print(consultar_eventos_detalhados("4639", "01/10/2025"))
