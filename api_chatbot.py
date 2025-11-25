from flask import Flask, request, jsonify
from flask_cors import CORS # 👈 NOVO: Importa a extensão CORS
import os

# Importação de funções corrigida (do passo anterior)
from consulta_motorista import buscar_metricas_do_dia, consultar_eventos_detalhados as buscar_eventos_do_mes 

# Cria o aplicativo Flask
app = Flask(__name__)
CORS(app) # 👈 NOVO: Habilita CORS para todas as rotas da API

# Rota de teste para verificar se o servidor está no ar
@app.route('/', methods=['GET'])
def home():
    """Página inicial para verificar a saúde da API."""
    return "<h1>API de Consulta de Motorista Ativa!</h1><p>Use as rotas /eventos e /metricas.</p>"

# Rota para consultar Eventos Detalhados
# Exemplo de uso: GET /eventos?re=12345&data=01/01/2025
@app.route('/eventos', methods=['GET'])
def api_eventos_do_mes():
    chapa = request.args.get('re')
    data_str = request.args.get('data')
    
    if not chapa or not data_str:
        return jsonify({
            "erro": "Parâmetros 're' e 'data' são obrigatórios. Ex: /eventos?re=12345&data=01/01/2025"
        }), 400

    try:
        resultado = buscar_eventos_do_mes(chapa, data_str) 
        
        if resultado.startswith("❌") or resultado.startswith("🚨") or resultado.startswith("ℹ️"):
             return jsonify({
                "status": "erro_consulta",
                "mensagem": resultado
            }), 404

        return jsonify({
            "chapa": chapa,
            "data_buscada": data_str,
            "resultado": resultado # Este é o texto formatado em Markdown
        })
    except Exception as e:
         return jsonify({
            "erro": "Erro interno do servidor ao processar a consulta.",
            "detalhe": str(e)
        }), 500


# Rota para consultar Métricas do Dia (Resumo)
# Exemplo de uso: GET /metricas?re=12345&data=01/01/2025
@app.route('/metricas', methods=['GET'])
def api_metricas_do_dia():
    chapa = request.args.get('re')
    data_str = request.args.get('data') 
    
    if not chapa or not data_str:
        return jsonify({
            "erro": "Parâmetros 're' e 'data' são obrigatórios. Ex: /metricas?re=12345&data=01/01/2025"
        }), 400

    try:
        resultado = buscar_metricas_do_dia(chapa, data_str)
        
        if resultado.startswith("❌") or resultado.startswith("🚨") or resultado.startswith("ℹ️"):
             return jsonify({
                "status": "erro_consulta",
                "mensagem": resultado
            }), 404
        
        return jsonify({
            "chapa": chapa,
            "data_buscada": data_str,
            "resultado": resultado
        })
    except Exception as e:
        return jsonify({
            "erro": "Erro interno do servidor ao processar a consulta.",
            "detalhe": str(e)
        }), 500

if __name__ == '__main__':
    print("Iniciando API Flask...")
    app.run(debug=True)