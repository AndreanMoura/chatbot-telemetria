import pandas as pd
import requests
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ===============================================================
# CONFIGURAÇÕES E CAMINHOS
# ===============================================================
# Configurações API Motorista (GDS/Escalado)
API_MOTORISTA_URL = "https://siannet.gestaosian.com/api/EscaladoInformacao?empresa=2&data_inicio=01/12/2025&data_fim=30/12/2025"
API_MOTORISTA_USER = "gds"
API_MOTORISTA_PASS = "SUA_SENHA_GDS"

# Configurações API Desempenho (JBS/Performance)
API_DESEMPENHO_URL = "https://siannet.gestaosian.com/api/WsPrime?campanha=2025/2026&resultado=performance_sintetico"
API_DESEMPENHO_USER = "jbs"
API_DESEMPENHO_PASS = "SUA_SENHA_JBS"

TIMEOUT_API = 600

# Caminhos de Arquivos Excel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE_PAINEL = r"C:\Users\andrean.miranda\OneDrive - Grupo HSGP\Arquivos de Mohamed Hally Alves do Nascimento - GESTAO DE BI 1\Operação\Guilherme\Python\Chatbot\Base Grafico Painel.xlsx"
CAMINHO_TELEMETRIA = os.path.join(BASE_DIR, "Telemetria.xlsx")

# ===============================================================
# FUNÇÕES DE FORMATAÇÃO
# ===============================================================
def formatar_numero(valor, casas=2):
    try:
        return f"{float(valor):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

# ===============================================================
# LÓGICA 1: ESCALADO (API MOTORISTAS)
# ===============================================================
def consultar_escalado(chapa):
    chapa_full = str(chapa).zfill(9)
    try:
        response = requests.get(API_MOTORISTA_URL, auth=(API_MOTORISTA_USER, API_MOTORISTA_PASS), timeout=TIMEOUT_API)
        response.raise_for_status()
        dados_api = response.json().get("dados", [])
        
        df = pd.DataFrame(dados_api)
        df.columns = df.columns.str.lower().str.strip()
        df["chapa"] = df["chapa"].astype(str).str.zfill(9)
        
        motorista = df[df["chapa"] == chapa_full]
        if motorista.empty:
            return f"ℹ️ Motorista chapa {chapa} não encontrado no Escalado."
        
        m = motorista.iloc[0]
        res = [
            "👤 *DADOS DO ESCALADO*",
            f"Nome: {str(m.get('nome')).title()}",
            f"Cargo: {m.get('nome_funcao', 'N/D')}",
            f"Garagem: {m.get('garagem', 'N/D')}",
            f"Turno: {m.get('turno', 'N/D')}",
            f"Situação: {m.get('situacao', 'N/D')}",
            f"\n📆 *VÍNCULO*",
            f"Última Folga: {m.get('ult_folga', 'N/D')}",
            f"Venc. CNH: {m.get('cnh_venc', 'N/D')}"
        ]
        return "\n".join(res)
    except Exception as e:
        return f"🚨 Erro ao consultar Escalado: {e}"

# ===============================================================
# LÓGICA 2: PERFORMANCE (EXCEL + API JBS)
# ===============================================================
def consultar_performance(chapa):
    chapa_full = str(chapa).zfill(9)
    try:
        # 1. Carregar Base Excel para dados cadastrais/grupo
        df_excel = pd.read_excel(CAMINHO_BASE_PAINEL, sheet_name="Base detalhamento")
        df_excel.columns = df_excel.columns.str.lower().str.strip()
        df_excel["chapa"] = df_excel["chapa"].astype(str).str.zfill(9)
        
        base_m = df_excel[df_excel["chapa"] == chapa_full]
        
        # 2. Consultar API Desempenho
        resp_api = requests.get(API_DESEMPENHO_URL, auth=(API_DESEMPENHO_USER, API_DESEMPENHO_PASS), timeout=TIMEOUT_API)
        resp_api.raise_for_status()
        dados_desempenho = resp_api.json().get("dados", [])
        
        df_des = pd.DataFrame(dados_desempenho)
        df_des.columns = df_des.columns.str.lower().str.strip()
        df_des["chapa"] = df_des["chapa"].astype(str).str.zfill(9)
        desempenho = df_des[df_des["chapa"] == chapa_full]

        # Montar Resposta
        res = ["📊 *PERFORMANCE MENSAL*"]
        if not base_m.empty:
            res.append(f"Motorista: {base_m.iloc[0].get('nome', 'N/D').title()}")
        
        if not desempenho.empty:
            d = desempenho.iloc[0]
            res.extend([
                f"Referência: {d.get('mesano', 'N/D')}",
                f"\nStatus: **{d.get('status', 'N/D')}**",
                f"Km Rodada: {formatar_numero(d.get('km_rodada'))} km",
                f"Km por Litro: {formatar_numero(d.get('km_por_litro'))}",
                f"Economia: {formatar_numero(d.get('economia'), 0)}"
            ])
            # Prêmio
            premio = d.get("premio-final", {})
            if isinstance(premio, dict):
                total = premio.get("dados", {}).get("total", 0)
                res.append(f"🏆 *Prêmio:* R$ {formatar_numero(total, 2)}")
        else:
            res.append("ℹ️ Dados de performance não disponíveis na API para este mês.")
            
        return "\n".join(res)
    except Exception as e:
        return f"🚨 Erro na Performance: {e}"

# ===============================================================
# LÓGICA 3: EVENTOS (TELEMETRIA EXCEL)
# ===============================================================
def consultar_eventos(chapa):
    if not os.path.exists(CAMINHO_TELEMETRIA):
        return "⚠️ Arquivo de telemetria não encontrado no servidor."
    
    try:
        df = pd.read_excel(CAMINHO_TELEMETRIA)
        df.columns = df.columns.str.lower().str.strip()
        df["chapa"] = df["chapa"].astype(str).str.strip()
        
        hoje = datetime.now().strftime("%d/%m/%Y")
        filtro = df[(df["chapa"] == str(chapa))] # Pode adicionar filtro de data aqui
        
        if filtro.empty:
            return f"ℹ️ Nenhum evento de telemetria para a chapa {chapa}."

        res = [f"📈 *EVENTOS DE TELEMETRIA*", f"Chapa: {chapa}\n"]
        res.append("| Evento | Qtd |")
        res.append("| :--- | :---: |")
        for _, row in filtro.tail(5).iterrows(): # Pega os últimos 5 registros
            res.append(f"| {row.get('evento', 'N/D')} | {int(row.get('quantidade', 0))} |")
            
        return "\n".join(res)
    except Exception as e:
        return f"🚨 Erro na Telemetria: {e}"

# ===============================================================
# ROTAS FLASK
# ===============================================================
@app.route("/motorista", methods=["GET"])
def rota_motorista():
    chapa = request.args.get("chapa")
    tipo = request.args.get("tipo", "escalado") # Default é escalado

    if not chapa:
        return jsonify({"resposta": "Por favor, informe a chapa."}), 400

    if tipo == "escalado":
        resultado = consultar_escalado(chapa)
    elif tipo == "performance":
        resultado = consultar_performance(chapa)
    elif tipo == "eventos":
        resultado = consultar_eventos(chapa)
    else:
        resultado = "Tipo de consulta inválido."

    return jsonify({"resposta": resultado})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)