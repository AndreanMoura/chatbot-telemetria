import pandas as pd
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# ===============================================================
# APP FLASK
# ===============================================================
app = Flask(__name__)
CORS(app)

# ===============================================================
# DIRETÓRIO BASE
# ===============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAMINHO_BASE_GRUPO = os.path.join(BASE_DIR, "Base Grafico Painel.xlsx")
ABA_BASE_GRUPO = "Base detalhamento"

CAMINHO_TELEMETRIA = os.path.join(BASE_DIR, "Telemetria.xlsx")
ABA_TELEMETRIA = "Telemetria"

# ===============================================================
# FUNÇÕES AUXILIARES
# ===============================================================
def formatar_inteiro(valor):
    try:
        return f"{int(float(valor)):,}".replace(",", ".")
    except:
        return "N/D"

def formatar_decimal(valor, casas=2):
    try:
        return f"{float(valor):.{casas}f}".replace(".", ",")
    except:
        return "N/D"

def titulo(texto):
    try:
        return str(texto).strip().title()
    except:
        return texto

# ===============================================================
# BASE DE GRUPO
# ===============================================================
def carregar_base_grupo():
    if not os.path.exists(CAMINHO_BASE_GRUPO):
        return None, "Arquivo da base de grupo não encontrado"

    df = pd.read_excel(CAMINHO_BASE_GRUPO, sheet_name=ABA_BASE_GRUPO)
    df.columns = df.columns.str.strip().str.lower()
    df["chapa"] = df["chapa"].astype(str).str.strip()
    return df, None

def consultar_base_grupo(chapa):
    df, erro = carregar_base_grupo()
    if erro:
        return erro

    registro = df[df["chapa"] == str(chapa)]
    if registro.empty:
        return f"Nenhum dado encontrado para a chapa {chapa}"

    m = registro.iloc[0]

    try:
        mesano = pd.to_datetime(m.get("mesano")).strftime("%m/%Y")
    except:
        mesano = m.get("mesano", "N/D")

    return (
        "📌 *BASE DE GRUPO*\n\n"
        f"🆔 Chapa: {chapa}\n"
        f"📅 Mês/Ano: {mesano}\n"
        f"👤 Nome: {titulo(m.get('nome'))}\n"
        f"⚡ Elétrico: {m.get('eletrico','N/D')}\n"
        f"📊 Status: {m.get('status','N/D')}\n"
        f"👥 Grupo: {m.get('grupo','N/D')} ({m.get('n_grupo','N/D')})\n\n"
        f"🚗 KM Rodado: {formatar_inteiro(m.get('km'))}\n"
        f"⛽ Litros: {formatar_inteiro(m.get('litros'))}\n"
        f"🎯 Meta Litros: {formatar_inteiro(m.get('litros meta'))}\n"
        f"💰 Economia: {formatar_decimal(m.get('economia'),1)}\n"
        f"📈 Performance: {formatar_decimal(m.get('performance'))}"
    )

# ===============================================================
# EVENTOS
# ===============================================================
def consultar_eventos(chapa, data_input):
    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except:
        return "Data inválida. Use DD/MM/YYYY"

    if not os.path.exists(CAMINHO_TELEMETRIA):
        return "Base de telemetria não encontrada"

    df = pd.read_excel(CAMINHO_TELEMETRIA, sheet_name=ABA_TELEMETRIA)
    df.columns = df.columns.str.strip().str.lower()

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
    df["chapa"] = df["chapa"].astype(str)

    df = df[(df["chapa"] == chapa) & (df["data"] == data_consulta)]

    if df.empty:
        return "Nenhum evento encontrado"

    linhas = [
        f"👤 Motorista: {df.iloc[0]['nome']}",
        f"🆔 Chapa: {chapa}",
        f"📅 Data: {data_input}",
        "",
        "📋 *EVENTOS*"
    ]

    total = 0
    for _, r in df.iterrows():
        qtd = int(float(r["quantidade"]))
        total += qtd
        linhas.append(f"- {r['evento']}: {formatar_inteiro(qtd)}")

    linhas.append(f"\n🔢 Total do dia: {formatar_inteiro(total)}")

    return "\n".join(linhas)

# ===============================================================
# MÉTRICAS
# ===============================================================
def buscar_metricas(chapa, data_input):
    try:
        data_consulta = datetime.strptime(data_input, "%d/%m/%Y").date()
    except:
        return "Data inválida"

    df = pd.read_excel(CAMINHO_TELEMETRIA, sheet_name=ABA_TELEMETRIA)
    df.columns = df.columns.str.strip().str.lower()

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce").dt.date
    df["chapa"] = df["chapa"].astype(str)

    df = df[(df["chapa"] == chapa) & (df["data"] == data_consulta)]

    if df.empty:
        return "Nenhum dado encontrado"

    total = int(df["quantidade"].astype(float).sum())

    return (
        "📊 *MÉTRICAS DO DIA*\n\n"
        f"🆔 Chapa: {chapa}\n"
        f"📅 Data: {data_input}\n"
        f"🔢 Total de Eventos: {formatar_inteiro(total)}"
    )

# ===============================================================
# 🔥 NOVO – RECEBER DADOS DE API (JSON)
# ===============================================================
@app.route("/dados-api", methods=["POST"])
def receber_dados_api():
    data = request.json

    return jsonify({
        "resultado": (
            "🚀 *RESULTADO DE DESEMPENHO*\n\n"
            f"👤 Nome: {titulo(data.get('Nome'))}\n"
            f"🆔 Chapa: {data.get('Chapa')}\n"
            f"📅 Mês/Ano: {data.get('Mesano')}\n"
            f"⚡ Elétrico: {data.get('Eletrico')}\n"
            f"📊 Status: {data.get('Status')}\n\n"
            f"🚗 KM Rodado: {data.get('Km_Rodada')}\n"
            f"⛽ Litros Consumidos: {data.get('Litros_Consumidos')}\n"
            f"🎯 Meta Litros: {data.get('Litros_Meta')}\n"
            f"📈 KM/L: {data.get('Km_Por_Litro')}\n\n"
            f"💰 Economia: {data.get('Economia')}\n"
            f"🌱 CO₂: {data.get('Co2')}\n"
            f"🏆 Prêmio Final: {data.get('Premio-Final',{}).get('DADOS',{}).get('Total',0)}"
        )
    })

# ===============================================================
# ROTAS
# ===============================================================
@app.route("/")
def home():
    return jsonify({"status": "online"})

@app.route("/grupo")
def grupo():
    return jsonify({"resultado": consultar_base_grupo(request.args.get("re"))})

@app.route("/eventos")
def eventos():
    return jsonify({"resultado": consultar_eventos(request.args.get("re"), request.args.get("data"))})

@app.route("/metricas")
def metricas():
    return jsonify({"resultado": buscar_metricas(request.args.get("re"), request.args.get("data"))})

# ===============================================================
# RENDER
# ===============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
