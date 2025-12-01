import pandas as pd
import os
import openpyxl
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ===============================================================
# APP DA API
# ===============================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================================================
# CAMINHOS DAS BASES
# ===============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base de Grupo
CAMINHO_BASE_GRUPO = os.path.join(BASE_DIR, "Base Grafico Painel.xlsx")
ABA_BASE_GRUPO = "Base detalhamento"

# Base de Telemetria
CAMINHO_TELEMETRIA = os.path.join(BASE_DIR, "Telemetria.xlsx")
ABA_TELEMETRIA = "Telemetria"

# ===============================================================
# FUNÇÃO AUXILIAR – FORMATAÇÃO
# ===============================================================
def formatar_numero(n):
    try:
        return f"{int(float(n)):,}".replace(",", ".")
    except:
        return n

# ===============================================================
# CONSULTA - BASE DE GRUPO
# ===============================================================
def carregar_base_grupo():
    if not os.path.exists(CAMINHO_BASE_GRUPO):
        return None, f"🚨 Arquivo não encontrado: {CAMINHO_BASE_GRUPO}"

    try:
        df = pd.read_excel(CAMINHO_BASE_GRUPO, sheet_name=ABA_BASE_GRUPO, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        return df, None
    except Exception as e:
        return None, f"🚨 Erro ao ler a base: {e}"

def consultar_base_grupo(chapa):
    df, erro = carregar_base_grupo()

    if erro:
        return erro

    if "chapa" not in df.columns:
        return f"❌ Coluna 'chapa' não encontrada."

    df["chapa"] = df["chapa"].astype(str).str.strip()
    chapa = str(chapa).strip()

    registro = df[df["chapa"] == chapa]

    if registro.empty:
        return f"ℹ️ Nenhum registro encontrado para a chapa {chapa}"

    motorista = registro.iloc[0]

    # Formatações
    try:
        mesano = pd.to_datetime(motorista.get("mesano")).strftime("%m/%Y")
    except:
        mesano = motorista.get("mesano", "N/D")

    try:
        nome = motorista.get("nome", "N/D").strip().title()
    except:
        nome = motorista.get("nome", "N/D")

    try:
        km = f"{float(motorista.get('km')):,.0f}".replace(",", ".")
    except:
        km = motorista.get("km", "N/D")

    try:
        litros = f"{float(motorista.get('litros')):,.0f}".replace(",", ".")
    except:
        litros = motorista.get("litros", "N/D")

    try:
        litros_meta = f"{float(motorista.get('litros meta')):,.0f}".replace(",", ".")
    except:
        litros_meta = motorista.get("litros meta", "N/D")

    try:
        economia = f"{float(motorista.get('economia')):.1f}".replace(".", ",")
    except:
        economia = motorista.get("economia", "N/D")

    try:
        performance = f"{float(motorista.get('performance')):.2f}".replace(".", ",")
    except:
        performance = motorista.get("performance", "N/D")

    return (
        f"✅ BASE DE GRUPO - Dados do Motorista\n\n"
        f"| Campo | Valor |\n"
        f"| :--- | :--- |\n"
        f"| Chapa | {chapa} |\n"
        f"| Mês/Ano | {mesano} |\n"
        f"| Nome | {nome} |\n"
        f"| Elétrico | {motorista.get('eletrico', 'N/D')} |\n"
        f"| Status | {motorista.get('status', 'N/D')} |\n"
        f"| Grupo | {motorista.get('grupo', 'N/D')} |\n"
        f"| Nº Grupo | {motorista.get('n_grupo', 'N/D')} |\n"
        f"| KM | {km} |\n"
        f"| Litros Consumidos | {litros} |\n"
        f"| Meta de Litros | {litros_meta} |\n"
        f"| Economia | {economia} |\n"
        f"| Performance | {performance} |\n"
    )

# ===============================================================
# CONSULTA - EVENTOS
# ===============================================================
def consultar_eventos_detalhados(chapa, data_input):

    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use DD/MM/YYYY."

    if not os.path.exists(CAMINHO_TELEMETRIA):
        return f"🚨 Arquivo não encontrado: {CAMINHO_TELEMETRIA}"

    try:
        df = pd.read_excel(CAMINHO_TELEMETRIA, sheet_name=ABA_TELEMETRIA, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        return f"🚨 Erro ao ler a planilha: {e}"

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
    df["chapa"] = df["chapa"].astype(str).str.strip()

    df_filtrado = df[(df["chapa"] == chapa) & (df["data"] == data_consulta)]

    if df_filtrado.empty:
        return f"ℹ️ Nenhum evento encontrado para a chapa {chapa} na data {data_input}."

    nome = df_filtrado.iloc[0]["nome"]
    funcao = df_filtrado.iloc[0]["funcao"]

    resultado = [
        f"👤 Motorista: {nome}",
        f"🆔 Chapa: {chapa}",
        f"💼 Função: {funcao}",
        f"📅 Data: {data_input}",
        "",
        "| Evento | Quantidade |",
        "| :--- | :---: |"
    ]

    total_qtd = 0

    for _, row in df_filtrado.iterrows():
        evento = row["evento"]
        qtd = int(float(row["quantidade"]))
        total_qtd += qtd

        resultado.append(f"| {evento} | {formatar_numero(qtd)} |")

    resultado.append(f"| Total Dia | {formatar_numero(total_qtd)} |")

    return "\n".join(resultado)

# ===============================================================
# CONSULTA - MÉTRICAS
# ===============================================================
def buscar_metricas_do_dia(chapa, data_input):

    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use DD/MM/YYYY."

    if not os.path.exists(CAMINHO_TELEMETRIA):
        return f"🚨 Arquivo não encontrado: {CAMINHO_TELEMETRIA}"

    df = pd.read_excel(CAMINHO_TELEMETRIA, sheet_name=ABA_TELEMETRIA, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
    df["chapa"] = df["chapa"].astype(str).str.strip()

    df_filtrado = df[(df["chapa"] == chapa) & (df["data"] == data_consulta)]

    if df_filtrado.empty:
        return f"ℹ️ Nenhum registro encontrado para a chapa {chapa} na data {data_input}."

    qtd_total = int(df_filtrado["quantidade"].astype(float).sum())

    return (
        f"📊 MÉTRICA DO DIA\n\n"
        f"| Campo | Valor |\n"
        f"| :--- | :---: |\n"
        f"| Chapa | {chapa} |\n"
        f"| Data | {data_input} |\n"
        f"| Total de Eventos | {formatar_numero(qtd_total)} |\n"
    )

# ===============================================================
# ROTAS DA API (PARA O FRONT)
# ===============================================================

@app.get("/")
def home():
    return {"status": "online", "rotas": ["/grupo", "/eventos", "/metricas"]}

@app.get("/grupo")
def api_grupo(re: str):
    resultado = consultar_base_grupo(re)
    return {"resultado": resultado}

@app.get("/eventos")
def api_eventos(re: str, data: str):
    resultado = consultar_eventos_detalhados(re, data)
    return {"resultado": resultado}

@app.get("/metricas")
def api_metricas(re: str, data: str):
    resultado = buscar_metricas_do_dia(re, data)
    return {"resultado": resultado}
