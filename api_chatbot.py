import pandas as pd
import os
import openpyxl
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# ===============================================================
# APP FLASK
# ===============================================================
app = Flask(__name__)
CORS(app)

# ===============================================================
# CAMINHOS DAS BASES (AJUSTADO PARA SERVIDOR NUVEM)
# ===============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# O Render precisa que esses arquivos estejam no seu GitHub
CAMINHO_BASE_GRUPO = os.path.join(BASE_DIR, "Base Grafico Painel.xlsx")
ABA_BASE_GRUPO = "Base detalhamento"

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
        return None, f"🚨 Arquivo Excel não encontrado no servidor: Base Grafico Painel.xlsx"

    try:
        df = pd.read_excel(CAMINHO_BASE_GRUPO, sheet_name=ABA_BASE_GRUPO, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        return df, None
    except Exception as e:
        return None, f"🚨 Erro ao ler a base: {e}"

def consultar_base_grupo(chapa):
    df, erro = carregar_base_grupo()
    if erro: return erro

    if "chapa" not in df.columns:
        return "❌ Coluna 'chapa' não encontrada no Excel."

    df["chapa"] = df["chapa"].astype(str).str.strip()
    chapa = str(chapa).strip()
    registro = df[df["chapa"] == chapa]

    if registro.empty:
        return f"ℹ️ Nenhum registro encontrado para a chapa {chapa}"

    motorista = registro.iloc[0]

    # Extração de dados (com tratamento para não quebrar)
    try:
        mesano = pd.to_datetime(motorista.get("mesano")).strftime("%m/%Y")
    except:
        mesano = motorista.get("mesano", "N/D")

    nome = str(motorista.get("nome", "N/D")).strip().title()
    
    # Montagem da resposta formatada para o Chatbot/Monitor
    return (
        f"✅ BASE DE GRUPO - Dados do Motorista\n\n"
        f"👤 Nome: {nome}\n"
        f"🆔 Chapa: {chapa}\n"
        f"📅 Mês/Ano: {mesano}\n"
        f"📊 Status: {motorista.get('status', 'N/D')}\n"
        f"🏢 Grupo: {motorista.get('grupo', 'N/D')}\n"
        f"🛣️ KM: {formatar_numero(motorista.get('km'))}\n"
        f"⛽ Litros: {formatar_numero(motorista.get('litros'))}\n"
        f"📉 Performance: {motorista.get('performance', 'N/D')}"
    )

# ===============================================================
# CONSULTA - EVENTOS (LÓGICA MANTIDA)
# ===============================================================
def consultar_eventos_detalhados(chapa, data_input):
    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except ValueError:
        return f"❌ Data inválida: {data_input}. Use DD/MM/YYYY."

    if not os.path.exists(CAMINHO_TELEMETRIA):
        return "🚨 Arquivo de Telemetria não encontrado no servidor."

    df = pd.read_excel(CAMINHO_TELEMETRIA, sheet_name=ABA_TELEMETRIA, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
    df["chapa"] = df["chapa"].astype(str).str.strip()

    df_filtrado = df[(df["chapa"] == chapa) & (df["data"] == data_consulta)]

    if df_filtrado.empty:
        return f"ℹ️ Nenhum evento para a chapa {chapa} em {data_input}."

    resultado = [f"📊 EVENTOS - {data_input}", f"Motorista: {df_filtrado.iloc[0]['nome']}", ""]
    for _, row in df_filtrado.iterrows():
        resultado.append(f"• {row['evento']}: {int(float(row['quantidade']))}")
    
    return "\n".join(resultado)

# ===============================================================
# ROTAS DA API
# ===============================================================

@app.route("/")
def home():
    return jsonify({
        "mensagem": "🚀 API Telemetria HSGP Online",
        "endpoints": ["/grupo?re=CHAPA", "/eventos?re=CHAPA&data=DD/MM/YYYY"]
    })

@app.route("/grupo")
def api_grupo():
    re = request.args.get("re")
    if not re: return jsonify({"resultado": "Informe o 're' (chapa)"})
    resultado = consultar_base_grupo(re)
    return jsonify({"resultado": resultado})

@app.route("/eventos")
def api_eventos():
    re = request.args.get("re")
    data = request.args.get("data")
    if not re or not data: return jsonify({"resultado": "Informe 're' e 'data'."})
    resultado = consultar_eventos_detalhados(re, data)
    return jsonify({"resultado": resultado})

# ===============================================================
# CONFIGURAÇÃO DE PORTA PARA O RENDER
# ===============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)