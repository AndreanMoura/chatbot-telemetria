from flask import Flask, jsonify, request
from flask_cors import CORS

# ===============================================================
# IMPORTAÇÕES DOS SEUS SCRIPTS (AJUSTADAS)
# ===============================================================
try:
    # Importando do arquivo consulta_motorista.py
    from consulta_motorista import consultar_motorista_por_chapa, formatar_motorista_para_chat
    
    # IMPORTANTE: Agora chamando a função correta do arquivo consulta_base_grupo.py
    from consulta_base_grupo import obter_desempenho_motorista
    
    print("✅ Módulos carregados com sucesso!")
except Exception as e:
    print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
    raise

app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False

def limpar_chapa_entrada(chapa):
    return str(chapa).strip().lstrip('0')

# ===============================================================
# ROTA DE TESTE (Acesse: http://localhost:5000/)
# ===============================================================
@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "servidor": "API Chatbot Motorista",
        "instrucao": "Use /chatbot/<chapa> para consultar"
    })

# ===============================================================
# ROTA: RETORNO TEXTO (CHATBOT)
# ===============================================================
@app.route("/chatbot/<chapa>", methods=["GET"])
def api_chatbot_text(chapa):
    chapa_limpa = limpar_chapa_entrada(chapa)
    print(f"🤖 Requisição Chatbot para chapa: {chapa_limpa}")

    # 1. Busca dados cadastrais no consulta_motorista.py
    dados_motorista = consultar_motorista_por_chapa(chapa_limpa)
    
    # 2. Formata o texto inicial
    texto = formatar_motorista_para_chat(dados_motorista)

    # 3. Tenta buscar desempenho no consulta_base_grupo.py
    try:
        # Aqui chamamos a função que você confirmou o nome
        resultado_desempenho = obter_desempenho_motorista(chapa_limpa)
        
        if isinstance(resultado_desempenho, dict) and "desempenho_mensal" in resultado_desempenho:
            d = resultado_desempenho["desempenho_mensal"]
            
            if d and "referencia" in d:
                texto += "\n\n📊 *DESEMPENHO MENSAL*"
                texto += f"\nReferência: {d.get('referencia')}"
                texto += f"\nStatus: {d.get('status')}"
                texto += f"\nKm rodado: {d.get('km_rodado')}"
                texto += f"\nKm/L: {d.get('km_por_litro')}"
                
                premio = d.get('premio_total', 0)
                # Garante que o prêmio seja tratado como número antes de formatar
                try:
                    texto += f"\nPrêmio: R$ {float(premio):.2f}"
                except:
                    texto += f"\nPrêmio: {premio}"
    except Exception as e:
        print(f"⚠️ Erro ao complementar desempenho: {e}")

    return jsonify({"texto": texto})

# ===============================================================
# INICIALIZAÇÃO
# ===============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)