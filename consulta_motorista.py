import pandas as pd
from datetime import datetime
import os

# ===============================================================
# CONFIGURAÇÕES DO ARQUIVO
# ===============================================================
CAMINHO_DO_ARQUIVO_DADOS = r"C:\Users\andrean.miranda\OneDrive - Grupo HSGP\Documentos\base chatbot\Telemetria.xlsx"
NOME_ABA = "Telemetria"

# ===============================================================
# FUNÇÃO: CONSULTAR EVENTOS DETALHADOS POR DATA
# ===============================================================
def consultar_eventos_detalhados(re, data_input):
    """
    Busca todos os eventos detalhados de um motorista (RE) em uma data específica.
    Retorna um texto formatado (para exibição pelo chatbot).
    """
    # --- Validação da data ---
    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use o formato DD/MM/YYYY."

    # --- Verifica se o arquivo existe ---
    if not os.path.exists(CAMINHO_DO_ARQUIVO_DADOS):
        return f"🚨 Arquivo não encontrado: {CAMINHO_DO_ARQUIVO_DADOS}"

    try:
        df = pd.read_excel(CAMINHO_DO_ARQUIVO_DADOS, sheet_name=NOME_ABA, engine="openpyxl")
        df.columns = df.columns.str.strip()
        # Remove espaços e normaliza textos
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
    except Exception as e:
        return f"🚨 Erro ao ler a planilha: {e}"

    # --- Valida colunas obrigatórias ---
    colunas_necessarias = ["Data", "RE", "Tipo de Evento", "Evento", "Quantidade", "Pontos"]
    faltando = [c for c in colunas_necessarias if c not in df.columns]
    if faltando:
        return f"🚨 Colunas ausentes no arquivo: {faltando}"

    # --- Converte data corretamente ---
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True).dt.date

    # --- Normaliza RE (remove .0 e espaços) ---
    df["RE"] = df["RE"].astype(str).str.strip().str.replace(".0", "", regex=False)
    re_normalizado = str(re).strip()

    # --- Filtra por RE e Data ---
    df_filtrado = df[
        (df["RE"] == re_normalizado)
        & (df["Data"] == data_consulta)
    ].copy()

    if df_filtrado.empty:
        return f"ℹ️ Nenhum evento encontrado para o RE '{re}' na data {data_input}."

    # --- Monta a tabela de resultado ---
    resultado = []
    resultado.append(f"👤 **Motorista (RE):** {re_normalizado}")
    resultado.append(f"📅 **Data consultada:** {data_input}")
    resultado.append("")
    resultado.append("| Tipo de Evento | Evento | Quantidade | Pontos |")
    resultado.append("| :--- | :--- | :---: | :---: |")

    for _, row in df_filtrado.iterrows():
        tipo = str(row["Tipo de Evento"])
        evento = str(row["Evento"])
        qtd = int(float(row["Quantidade"])) if pd.notna(row["Quantidade"]) else 0
        pts = int(float(row["Pontos"])) if pd.notna(row["Pontos"]) else 0
        resultado.append(f"| {tipo} | {evento} | {qtd} | {pts} |")

    # --- Totais ---
    total_qtd = int(df_filtrado["Quantidade"].astype(float).sum())
    total_pts = int(df_filtrado["Pontos"].astype(float).sum())
    resultado.append(f"| **TOTAL** | — | **{total_qtd}** | **{total_pts}** |")

    return "\n".join(resultado)

# ===============================================================
# FUNÇÃO: CONSULTAR MÉTRICAS DIÁRIAS (RESUMO)
# ===============================================================
def buscar_metricas_do_dia(re, data_input):
    """
    Retorna o total de eventos e pontos de um motorista (RE) em uma data específica.
    """
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

    if not all(c in df.columns for c in ["Data", "RE", "Quantidade", "Pontos"]):
        return "🚨 Colunas necessárias não encontradas no arquivo."

    # --- Converte e normaliza ---
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True).dt.date
    df["RE"] = df["RE"].astype(str).str.strip().str.replace(".0", "", regex=False)
    re_normalizado = str(re).strip()

    # --- Filtra ---
    df_filtrado = df[
        (df["RE"] == re_normalizado)
        & (df["Data"] == data_consulta)
    ].copy()

    if df_filtrado.empty:
        return f"ℹ️ Nenhum registro encontrado para o RE '{re}' na data {data_input}."

    qtd_total = int(df_filtrado["Quantidade"].astype(float).sum())
    pontos_total = int(df_filtrado["Pontos"].astype(float).sum())

    return (
        f"👤 **Motorista (RE):** {re_normalizado}\n"
        f"📅 **Data consultada:** {data_input}\n\n"
        f"| Métrica Diária | Valor |\n"
        f"| :--- | :---: |\n"
        f"| Quantidade Total | {qtd_total} |\n"
        f"| Pontos Totais | {pontos_total} |"
    )

# ===============================================================
# TESTE DIRETO
# ===============================================================
if __name__ == "__main__":
    print("🔍 Teste rápido: buscando eventos detalhados\n")
    print(consultar_eventos_detalhados("4639", "01/10/2025"))
