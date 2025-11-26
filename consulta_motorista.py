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
    try:
        return f"{int(float(n)):,}".replace(",", ".")
    except:
        return n

# ===============================================================
# FUNÇÃO: CONSULTAR EVENTOS DETALHADOS
# ===============================================================
def consultar_eventos_detalhados(chapa, data_input):
    """
    Consulta os eventos detalhados para uma chapa e uma data.
    Compatível com o layout:
    data | carro | chapa | nome | funcao | evento | quantidade
    """
    
    # Validação da data
    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use o formato DD/MM/YYYY."

    # Validar existência do arquivo
    if not os.path.exists(CAMINHO_DO_ARQUIVO_DADOS):
        return f"🚨 Arquivo não encontrado: {CAMINHO_DO_ARQUIVO_DADOS}"

    # Ler planilha
    try:
        df = pd.read_excel(CAMINHO_DO_ARQUIVO_DADOS, sheet_name=NOME_ABA, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()  # Normaliza colunas
    except Exception as e:
        return f"🚨 Erro ao ler a planilha: {e}"

    # Validar colunas obrigatórias
    colunas_necessarias = ["data", "carro", "chapa", "nome", "funcao", "evento", "quantidade"]
    faltando = [c for c in colunas_necessarias if c not in df.columns]
    if faltando:
        return f"🚨 Colunas ausentes no arquivo: {faltando}"

    # Normalizar dados
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
    df["chapa"] = df["chapa"].astype(str).str.strip()

    chapa = str(chapa).strip()

    # Filtrar
    df_filtrado = df[
        (df["chapa"] == chapa) &
        (df["data"] == data_consulta)
    ]

    if df_filtrado.empty:
        return f"ℹ️ Nenhum evento encontrado para a chapa {chapa} na data {data_input}."

    # Pega dados do motorista
    nome = df_filtrado.iloc[0]["nome"]
    funcao = df_filtrado.iloc[0]["funcao"]

    # Construir tabela em Markdown
    resultado = []
    resultado.append(f"👤 Motorista: {nome}")
    resultado.append(f"🆔 Chapa: {chapa}")
    resultado.append(f"💼 Função: {funcao}")
    resultado.append(f"📅 Data: {data_input}")
    resultado.append("")
    resultado.append("| Evento | Quantidade |")
    resultado.append("| :--- | :---: |")

    total_qtd = 0

    for _, row in df_filtrado.iterrows():
        evento = row["evento"]
        qtd_raw = row["quantidade"]

        try:
            qtd_val = int(float(qtd_raw))
            total_qtd += qtd_val
            qtd_formatada = formatar_numero(qtd_val)
        except:
            qtd_formatada = str(qtd_raw)

        resultado.append(f"| {evento} | {qtd_formatada} |")

    resultado.append(f"| Total Dia | {formatar_numero(total_qtd)} |")

    return "\n".join(resultado)

# ===============================================================
# FUNÇÃO: CONSULTAR MÉTRICAS DO DIA
# ===============================================================
def buscar_metricas_do_dia(chapa, data_input):

    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use o formato DD/MM/YYYY."

    if not os.path.exists(CAMINHO_DO_ARQUIVO_DADOS):
        return f"🚨 Arquivo não encontrado: {CAMINHO_DO_ARQUIVO_DADOS}"

    try:
        df = pd.read_excel(CAMINHO_DO_ARQUIVO_DADOS, sheet_name=NOME_ABA, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        return f"🚨 Erro ao ler a planilha: {e}"

    colunas_necessarias = ["data", "chapa", "quantidade"]
    faltando = [c for c in colunas_necessarias if c not in df.columns]
    if faltando:
        return f"🚨 Colunas necessárias ausentes: {faltando}"

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
    df["chapa"] = df["chapa"].astype(str).str.strip()
    chapa = str(chapa).strip()

    df_filtrado = df[
        (df["chapa"] == chapa) &
        (df["data"] == data_consulta)
    ]

    if df_filtrado.empty:
        return f"ℹ️ Nenhum registro encontrado para a chapa {chapa} na data {data_input}."

    qtd_total = int(df_filtrado["quantidade"].astype(float).sum())

    return (
        f"👤 Chapa: {chapa}\n"
        f"📅 Data consultada: {data_input}\n\n"
        f"| Métrica | Valor |\n"
        f"| :--- | :---: |\n"
        f"| Quantidade Total | {formatar_numero(qtd_total)} |"
    )

# ===============================================================
# TESTE LOCAL
# ===============================================================
if __name__ == "__main__":
    print("🔍 Teste rápido:\n")
    print(consultar_eventos_detalhados("19135", "01/11/2025"))
