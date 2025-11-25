import os
import re
from datetime import datetime

# Importa as funções corretas do módulo de consulta
# 👉 Usa "as" para renomear a função e manter compatibilidade
from consulta_motorista import consultar_eventos_detalhados as buscar_eventos_detalhados, buscar_metricas_do_dia

# ============================================================
# === FUNÇÃO AUXILIAR: COLETAR E VALIDAR DATA ================
# ============================================================
def coletar_e_validar_data(nome):
    """Solicita e valida uma data no formato DD/MM/YYYY."""
    print(f'\n--- SELEÇÃO DE DATA ---')
    data_input = input(f'{nome}, por favor, digite a data que deseja consultar (Ex: 01/09/2025): ').strip()

    # Validação simples com regex
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', data_input):
        print("❌ Formato de data inválido. Use o formato DD/MM/YYYY.")
        return None

    try:
        datetime.strptime(data_input, '%d/%m/%Y')  # Verifica se é válida
        return data_input
    except ValueError:
        print(f"❌ A data '{data_input}' é inválida. Verifique o dia, mês e ano.")
        return None


# ============================================================
# === FUNÇÃO PRINCIPAL DE PROCESSAMENTO ======================
# ============================================================
def Processar_resposta(Resposta, nome, chapa):
    """Processa a escolha feita pelo usuário no menu principal."""
    Resposta = Resposta.strip()
    data_consulta = None

    # === OPÇÃO 1: EVENTOS POR DATA ===
    if Resposta == '1':
        data_consulta = coletar_e_validar_data(nome)
        if not data_consulta:
            return True

        print(f'\n>> {nome}, buscando todos os Eventos e Pontos para o dia {data_consulta}...')
        resultado = buscar_eventos_detalhados(chapa, data_consulta)
        print(f'\n{resultado}\n')
        return True

    # === OPÇÃO 2: MÉTRICAS DIÁRIAS (RESUMO) ===
    elif Resposta == '2':
        data_consulta = coletar_e_validar_data(nome)
        if not data_consulta:
            return True

        print(f'\n>> {nome}, buscando suas Métricas Diárias para {data_consulta}...')
        try:
            resultado = buscar_metricas_do_dia(chapa, data_consulta)
        except ValueError:
            resultado = f"❌ Erro de formato: a data informada ({data_consulta}) é inválida."
        print(f'\n{resultado}\n')
        return True

    # === OPÇÃO 3: RELATÓRIO COMPLETO (EVENTOS + MÉTRICAS) ===
    elif Resposta == '3':
        data_consulta = coletar_e_validar_data(nome)
        if not data_consulta:
            return True

        print(f'\n>> {nome}, buscando TODAS as suas métricas e eventos do dia {data_consulta}...')
        resultado_eventos = buscar_eventos_detalhados(chapa, data_consulta)
        try:
            resultado_metricas = buscar_metricas_do_dia(chapa, data_consulta)
        except ValueError:
            resultado_metricas = f'❌ Erro ao buscar métricas: a data {data_consulta} é inválida.'

        # Monta relatório
        data_execucao = datetime.now().strftime('%d/%m/%Y')
        resposta_final = [
            "========================================",
            f"📊 **Relatório Completo para o RE: {chapa}**",
            f"📅 Data da Execução: {data_execucao}",
            "========================================",
            "",
            f"--- **Eventos e Pontos ({data_consulta})** ---",
            resultado_eventos,
            "",
            f"--- **Resumo de Métricas ({data_consulta})** ---",
            resultado_metricas
        ]
        print("\n" + "\n".join(resposta_final) + "\n")
        return True

    # === OPÇÃO 4: SAIR ===
    elif Resposta == '4':
        print(f'\n>> Obrigado, {nome}! Encerrando o sistema.')
        return False

    # === OPÇÃO INVÁLIDA ===
    else:
        print(f'\n>> Opção "{Resposta}" inválida. Escolha [1], [2], [3] ou [4].')
        return True


# ============================================================
# === FUNÇÃO INICIAL DO SISTEMA ==============================
# ============================================================
def start():
    """Inicia o sistema interativo no terminal."""
    print('Olá, Seja Bem-vindo ao Sistema de Consulta de Telemetria!')

    nome = input('Digite seu nome: ').strip()
    chapa = input('Digite seu número de RE: ').strip()

    while True:
        Resposta = input(
            f'\nO que gostaria de saber hoje, {nome}? \n'
            f' [1] - Todos os Eventos e Pontos de uma DATA ESPECÍFICA.\n'
            f' [2] - Suas Métricas Diárias (Quantidade e Pontos) de uma DATA ESPECÍFICA.\n'
            f' [3] - Relatório Completo (Eventos + Métricas).\n'
            f' [4] - Sair\n'
            f' Digite a opção (1, 2, 3 ou 4): '
        )

        if not Processar_resposta(Resposta, nome, chapa):
            break

    print(f'\n✅ Sessão encerrada. Até mais, {nome}!')


# ============================================================
# === EXECUÇÃO DIRETA ========================================
# ============================================================
if __name__ == "__main__":
    start()

