import pandas as pd
import requests
import os

# ===============================================================
# CONFIGURAÇÕES
# ===============================================================
API_URL = "https://siannet.gestaosian.com/api/WsPrime?campanha=2025/2026&resultado=performance_sintetico"  # <--- Coloque sua URL aqui
API_USER = "jbs"
API_PASS = "SUA_SENHA" # <--- Coloque sua senha aqui
TIMEOUT_API = 600

CAMINHO_BASE = r"C:\Users\andrean.miranda\OneDrive - Grupo HSGP\Arquivos de Mohamed Hally Alves do Nascimento - GESTAO DE BI 1\Operação\Guilherme\Python\Chatbot\Base Grafico Painel.xlsx"
NOME_ABA = "Base detalhamento"

# ===============================================================
# FUNÇÃO AUXILIAR: LIMPEZA DE CHAPA
# ===============================================================
def limpar_chapa(valor):
    """Remove espaços, zeros à esquerda e garante que seja string para comparação."""
    return str(valor).strip().lstrip('0')

# ===============================================================
# BASE OPERACIONAL (EXCEL)
# ===============================================================
def carregar_base_excel():
    if not os.path.exists(CAMINHO_BASE):
        raise FileNotFoundError(f"Arquivo não encontrado em: {CAMINHO_BASE}")

    df = pd.read_excel(
        CAMINHO_BASE,
        sheet_name=NOME_ABA,
        engine="openpyxl"
    )

    # Normalizar colunas
    df.columns = df.columns.str.lower().str.strip()
    
    # Criar coluna limpa para comparação (Ex: "000123" vira "123")
    df["chapa_limpa"] = df["chapa"].apply(limpar_chapa)

    return df

# ===============================================================
# API DE DESEMPENHO
# ===============================================================
def carregar_desempenho_api(chapa_alvo_limpa):
    try:
        response = requests.get(
            API_URL,
            auth=(API_USER, API_PASS),
            timeout=TIMEOUT_API
        )
        response.raise_for_status()
        retorno = response.json()

        if "dados" not in retorno:
            print("⚠️ Chave 'dados' não encontrada no JSON da API.")
            return pd.DataFrame()

        df = pd.DataFrame(retorno["dados"])
        df.columns = df.columns.str.lower().str.strip()
        
        # Limpar as chapas que vêm da API
        df["chapa_limpa"] = df["chapa"].apply(limpar_chapa)

        # Filtrar apenas o motorista desejado
        resultado = df[df["chapa_limpa"] == chapa_alvo_limpa]
        return resultado

    except Exception as e:
        print(f"❌ Erro ao acessar API de Desempenho: {e}")
        return pd.DataFrame()

# ===============================================================
# FUNÇÃO PRINCIPAL
# ===============================================================
def obter_desempenho_motorista(chapa_entrada):
    # 1. Limpa a chapa que o usuário digitou
    chapa_limpa = limpar_chapa(chapa_entrada)

    # 2. Carregar Excel
    try:
        base_df = carregar_base_excel()
    except Exception as e:
        return {"erro": str(e)}

    # 3. Buscar no Excel
    motorista_df = base_df[base_df["chapa_limpa"] == chapa_limpa]

    if motorista_df.empty:
        return {"mensagem": f"Motorista com chapa {chapa_entrada} não encontrado no Excel."}

    m = motorista_df.iloc[0]

    # 4. Buscar Desempenho na API
    desempenho_df = carregar_desempenho_api(chapa_limpa)

    desempenho = {}
    if not desempenho_df.empty:
        d = desempenho_df.iloc[0]
        
        # Tratamento especial para o campo de prêmio que é um JSON aninhado
        premio = d.get("premio-final")
        valor_premio = 0
        if isinstance(premio, dict):
            valor_premio = premio.get("dados", {}).get("total", 0)

        desempenho = {
            "referencia": d.get("mesano"),
            "status": d.get("status"),
            "meta_km_l": d.get("meta"),
            "km_rodado": d.get("km_rodada"),
            "litros_consumidos": d.get("litros_consumidos"),
            "km_por_litro": d.get("km_por_litro"),
            "economia": d.get("economia"),
            "co2": d.get("co2"),
            "premio_total": valor_premio
        }
    else:
        desempenho = {"aviso": "Dados de desempenho não encontrados na API para este mês."}

    return {
        "motorista": {
            "chapa": m.get("chapa"),
            "nome": m.get("nome"),
            "funcao": m.get("funcao"),
            "grupo": m.get("grupo")
        },
        "desempenho_mensal": desempenho
    }

# ===============================================================
# CAMPO DE TESTE LOCAL
# ===============================================================
if __name__ == "__main__":
    print("🚀 Iniciando Teste de Consulta de Desempenho...")
    
    # Substitua pelo número da chapa que você quer testar
    CHAPA_TESTE = "14594" 
    
    resultado = obter_desempenho_motorista(CHAPA_TESTE)
    
    print("\n--- RESULTADO DA BUSCA ---")
    if "motorista" in resultado:
        m = resultado["motorista"]
        d = resultado["desempenho_mensal"]
        print(f"👤 Motorista: {m['nome']} ({m['chapa']})")
        print(f"💼 Função: {m['funcao']} | Grupo: {m['grupo']}")
        print(f"📊 Desempenho: {d}")
    else:
        print(f"ℹ️ {resultado.get('mensagem', 'Erro desconhecido')}")