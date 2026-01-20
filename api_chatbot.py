from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from consulta_motorista import consultar_motorista_por_chapa, formatar_motorista_para_chat
    from consulta_base_grupo import obter_desempenho_motorista
except Exception as e:
    # se importação falhar, levantamos na inicialização para facilitar debug
    raise

app = Flask(__name__)
CORS(app)


@app.route("/motorista/<chapa>", methods=["GET"])
def api_motorista(chapa):
    """Retorna JSON com dados do motorista (da API EscaladoInformacao) e desempenho (da API WsPrime)."""
    motorista = consultar_motorista_por_chapa(chapa)

    # se houver erro/mesagem, repassa
    if isinstance(motorista, dict) and ("erro" in motorista or "mensagem" in motorista):
        return jsonify(motorista)

    desempenho = obter_desempenho_motorista(chapa)

    # estrutura final
    response = {
        "motorista": motorista,
        "desempenho": desempenho.get("desempenho_mensal", desempenho) if isinstance(desempenho, dict) else desempenho
    }

    return jsonify(response)


@app.route("/chatbot/<chapa>", methods=["GET"])
def api_chatbot_text(chapa):
    """Retorna texto formatado para uso em chatbot, combinando motorista + resumo de desempenho."""
    dados = consultar_motorista_por_chapa(chapa)
    texto = formatar_motorista_para_chat(dados)

    # acrescenta resumo de desempenho quando disponível
    try:
        desempenho = obter_desempenho_motorista(chapa)
        if isinstance(desempenho, dict) and desempenho.get("desempenho_mensal"):
            d = desempenho["desempenho_mensal"]
            if d:
                texto += "\n\n📊 *DESEMPENHO MENSAL*"
                texto += f"\nReferência: {d.get('referencia')}"
                texto += f"\nStatus: {d.get('status')}"
                texto += f"\nKm rodado: {d.get('km_rodado')}"
                texto += f"\nKm/L: {d.get('km_por_litro')}"
                texto += f"\nPrêmio: {d.get('premio_total')}"
    except Exception:
        # se falhar ao obter desempenho, ignoramos para não quebrar o chatbot
        pass

    return jsonify({"texto": texto})


if __name__ == "__main__":
    # Executa a API localmente
    app.run(host="0.0.0.0", port=5000, debug=True)