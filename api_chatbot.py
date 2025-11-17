from flask import Flask, request, jsonify
from consulta_motorista import buscar_eventos_do_mes, buscar_metricas_do_dia, teste_estrutura_da_planilha
import os

# Cria o aplicativo Flask
app = Flask(__name__)

# Rota de teste para verificar se o servidor está no ar
@app.route('/', methods=['GET'])
def home():
    """Página inicial para verificar a saúde da API."""
    return "<h1>API de Consulta de Motorista Ativa!</h1><p>Use as rotas /eventos e /metricas.</p>"

# Rota de diagnóstico para verificar o arquivo Excel
@app.route('/diagnostico', methods=['GET'])
def diagnostico():
    """Retorna o resultado do teste de estrutura da planilha."""
    resultado = teste_estrutura_da_planilha()
    
    # Verifica se o resultado é um relatório de sucesso (começa com "✅")
    if resultado.startswith("✅"):
        status = "sucesso"
    else:
        status = "erro"
        
    return jsonify({
        "status": status,
        "mensagem": resultado
    })


# Rota para consultar Eventos do Mês
# Exemplo de uso: GET /eventos?re=12345
@app.route('/eventos', methods=['GET'])
def api_eventos_do_mes():
    # Pega o parâmetro 're' (Registro de Empregado/Chapa) da URL
    chapa = request.args.get('re')
    
    if not chapa:
        return jsonify({
            "erro": "Parâmetro 're' é obrigatório. Ex: /eventos?re=12345"
        }), 400
    
    # Chama a função de consulta existente
    try:
        resultado = buscar_eventos_do_mes(chapa)
        return jsonify({
            "chapa": chapa,
            "resultado": resultado
        })
    except Exception as e:
        return jsonify({
            "erro": "Erro interno do servidor ao processar a consulta.",
            "detalhe": str(e)
        }), 500

# Rota para consultar Métricas Diárias
# Exemplo de uso: GET /metricas?re=12345&data=15/05/2024
@app.route('/metricas', methods=['GET'])
def api_metricas_do_dia():
    # Pega os parâmetros 're' e 'data' da URL
    chapa = request.args.get('re')
    data_str = request.args.get('data') # Pode ser None, buscando o dia atual
    
    if not chapa:
        return jsonify({
            "erro": "Parâmetro 're' é obrigatório. Ex: /metricas?re=12345"
        }), 400

    # Chama a função de consulta existente
    try:
        resultado = buscar_metricas_do_dia(chapa, data_str)
        return jsonify({
            "chapa": chapa,
            "data_buscada": data_str if data_str else "Hoje",
            "resultado": resultado
        })
    except ValueError as e:
        if "time data" in str(e):
             return jsonify({
                "erro": "Formato de data inválido. Use DD/MM/YYYY.",
                "detalhe": str(e)
            }), 400
        return jsonify({
            "erro": "Erro interno do servidor ao processar a consulta.",
            "detalhe": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "erro": "Erro interno do servidor ao processar a consulta.",
            "detalhe": str(e)
        }), 500

# Esta parte só é executada se você rodar o script diretamente
if __name__ == '__main__':
    # Define o host para 0.0.0.0 (acessível externamente no servidor) e a porta 5000
    print("Iniciando o servidor Flask na porta 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)