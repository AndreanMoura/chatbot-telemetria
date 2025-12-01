import pandas as pd
import os
from datetime import datetime

# ===============================================================
# CONFIGURAÇÃO DE ARQUIVO
# ===============================================================
# 🚨 Verifique e ajuste o caminho absoluto da sua planilha de Grupo!
# Este caminho é um exemplo baseado no erro anterior. AJUSTE-O SE NECESSÁRIO!
CAMINHO_BASE = r"C:\Users\andrean.miranda\OneDrive - Grupo HSGP\Arquivos de Mohamed Hally Alves do Nascimento - GESTAO DE BI 1\Operação\Guilherme\Python\Chatbot\Base Grafico Painel.xlsx"

# Nome da aba na Base Grafico Painel.xlsx 
NOME_ABA = "Base detalhamento" 

# ===============================================================
# FUNÇÕES DE LÓGICA
# ===============================================================

def carregar_base():
    """Carrega o DataFrame da Base Grupo e padroniza os nomes das colunas."""
    if not os.path.exists(CAMINHO_BASE):
        return None, f"🚨 Arquivo não encontrado: Verifique o caminho absoluto: '{CAMINHO_BASE}'"

    try:
        df = pd.read_excel(CAMINHO_BASE, sheet_name=NOME_ABA, engine="openpyxl")
        # Limpa e padroniza os nomes das colunas para minúsculas e sem espaços
        df.columns = df.columns.str.strip().str.lower()
        return df, None
    except Exception as e:
        return None, f"🚨 Erro ao ler a base '{CAMINHO_BASE}' na aba '{NOME_ABA}': {e}"

def buscar_por_chapa(chapa):
    """Busca o registro do motorista pela chapa (RE)."""
    df, erro = carregar_base()
    if erro:
        return erro

    if "chapa" not in df.columns:
         # Se a coluna 'chapa' não existir, tente adivinhar.
         colunas_disponiveis = df.columns.tolist()
         return f"❌ Erro: Coluna 'chapa' não encontrada. Colunas disponíveis: {colunas_disponiveis}"

    # Padroniza a coluna 'chapa' do DataFrame para string limpa
    df["chapa"] = df["chapa"].astype(str).str.strip()
    chapa = str(chapa).strip()

    df_filtrado = df[df["chapa"] == chapa]

    if df_filtrado.empty:
        return f"ℹ️ Nenhum registro de grupo/base encontrado para a chapa {chapa}."

    return df_filtrado

def resumo_motorista(chapa):
    """
    Retorna o resumo formatado do motorista (grupo, nome, função, etc.).
    """
    dados = buscar_por_chapa(chapa)

    if isinstance(dados, str):
        # Retorna mensagem de erro/info do passo anterior
        return dados

    # Mapeamento e extração do primeiro registro
    motorista = dados.iloc[0]
    
    # 1. Formata o Tempo de Casa 
    try:
        # A coluna deve ser 'tempo_de_casa' (minúsculo e sem acento)
        tempo_dias = int(motorista.get('tempo_de_casa', 0)) 
        anos = tempo_dias // 365
        meses = (tempo_dias % 365) // 30
        tempo_formatado = f"{anos} anos e {meses} meses"
    except:
        tempo_formatado = motorista.get('tempo_de_casa', 'N/D')

    # 2. Constrói o resultado (Ajuste 'nome', 'funcao' e 'grupo' conforme o nome real das suas colunas.)
    resultado = (
        f"✅ **Base Grupo - Dados Cadastrais (RE: {chapa})**:\n\n"
        f"| Campo | Valor |\n"
        f"| :--- | :--- |\n"
        f"| Nome | {motorista.get('nome', 'N/D').strip().title()} |\n"
        f"| Função | {motorista.get('funcao', 'N/D').strip().title()} |\n"
        f"| Grupo | {motorista.get('grupo', 'N/D').strip().upper()} |\n"
        f"| Tempo de Casa | {tempo_formatado} |\n"
        f"\n*Fonte: Base Grafico Painel.xlsx, Aba '{NOME_ABA}'.*"
    )

    return resultado