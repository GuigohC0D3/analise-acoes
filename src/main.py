import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import schedule
import time
import threading
import json


# Função para realizar a análise semanal e indicar compra
def analisar_acoes_semanais():
    print("Analisando o mercado semanalmente...")

    # Lista de ações para monitorar
    acoes = ["ALLD3.SA", "AURE3.SA", "BBAS3.SA", "BBDC4.SA", "CMIG4.SA",
             "CXSE3.SA", "PETR4.SA", "SAPR4.SA", "TAEE3.SA", "TIMS3.SA"]

    resultados = []

    for acao in acoes:
        try:
            # Buscar dados do yfinance para o último mês
            ticker = yf.Ticker(acao)
            dados = ticker.history(period="1mo", interval="1d")  # Intervalo de 1 dia

            if dados.empty:
                print(f"Sem dados suficientes para {acao}.")
                continue

            # Calcular a média móvel dos últimos 7 dias
            dados['SMA7'] = dados['Close'].rolling(window=7).mean()

            # Calcular o retorno semanal
            dados['Return'] = dados['Close'].pct_change(periods=5)

            # Dados recentes
            ultima_linha = dados.iloc[-1]

            # Verificar se há dados suficientes para análise
            if pd.isna(ultima_linha['SMA7']):
                print(f"Dados insuficientes para calcular a média móvel de {acao}.")
                continue

            # Critérios para compra
            if ultima_linha['Close'] > ultima_linha['SMA7']:
                recomendacao = "Comprar"
            else:
                recomendacao = "Não Comprar"

            resultados.append({
                "Acao": acao,
                "Preco_Atual": round(ultima_linha["Close"], 2),
                "Media_Movel": round(ultima_linha["SMA7"], 2),
                "Retorno_Semanal": round(ultima_linha['Return'], 4),
                "Recomendacao": recomendacao
            })
        except Exception as e:
            print(f"Erro ao buscar dados para {acao}: {e}")

    # Salvar a análise em um arquivo JSON
    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/analise_semanal.json', 'w') as file:
        json.dump(resultados, file, indent=4)

    print("\nAnálise semanal concluída. Resultados salvos em 'data/analise_semanal.json'.")
    return resultados


def plotar_grafico_carteira():
    # Insira os dados da sua carteira manualmente
    carteira = pd.DataFrame({
        "Ticker": ["ALLD3.SA", "AURE3.SA", "BBAS3.SA", "BBDC4.SA", "CMIG4.SA", "CXSE3.SA", "PETR4.SA", "SAPR4.SA", "TAEE3.SA", "TIMS3.SA"],  # Código das ações
        "Quantidade": [40, 42, 58, 36, 74, 33, 44, 46, 32, 20],                   # Quantidade de ações
        "Preco_Medio": [7.61, 10.87, 26.66, 13.28, 10.00, 14.38, 37.45, 5.54, 11.55, 15.92]            # Preço médio de compra
    })

    # Obter os preços atuais
    tickers = carteira["Ticker"].tolist()
    precos_atualizados = yf.download(tickers, period="1d", interval="1d")["Close"].iloc[-1]

    # Atualizar os dados da carteira
    carteira["Preco_Atual"] = [precos_atualizados[ticker] for ticker in carteira["Ticker"]]
    carteira["Valor_Atual"] = carteira["Preco_Atual"] * carteira["Quantidade"]

    # Plotar o gráfico de distribuição da carteira
    plt.figure(figsize=(8, 6))
    plt.pie(carteira["Valor_Atual"], labels=carteira["Ticker"], autopct='%1.1f%%', startangle=140)
    plt.title("Distribuição da Carteira")
    plt.show()



# Função para iniciar a automação
def iniciar_automacao():
    def rodar_agendador():
        while True:
            schedule.run_pending()
            time.sleep(1)

    # Agendar a execução semanal
    schedule.every().monday.at("10:00").do(analisar_acoes_semanais)

    # Exibir mensagem de sucesso e iniciar o agendador
    messagebox.showinfo("Automação", "Automação semanal iniciada! A análise será feita toda segunda-feira às 10h.")
    threading.Thread(target=rodar_agendador, daemon=True).start()


# Configurar a interface gráfica
def criar_painel():
    janela = tk.Tk()
    janela.title("Painel de Automação - Ações")
    janela.geometry("600x400")

    # Título
    titulo = tk.Label(janela, text="Painel de Automação de Ações", font=("Helvetica", 16))
    titulo.pack(pady=10)

    # Botão para iniciar a automação semanal
    botao_iniciar = ttk.Button(janela, text="Iniciar Automação Semanal", command=iniciar_automacao)
    botao_iniciar.pack(pady=20)

    # Botão para exibir o gráfico da carteira
    botao_grafico = ttk.Button(janela, text="Exibir Gráfico da Carteira", command=plotar_grafico_carteira)
    botao_grafico.pack(pady=20)

    # Texto explicativo
    texto_info = tk.Label(
        janela,
        text="Clique em 'Iniciar Automação Semanal' para análise de compra.\n"
             "Clique em 'Exibir Gráfico da Carteira' para ver a distribuição.",
        font=("Helvetica", 10),
        justify="center"
    )
    texto_info.pack(pady=10)

    # Rodapé
    rodape = tk.Label(janela, text="Desenvolvido com Python", font=("Helvetica", 8), fg="gray")
    rodape.pack(side="bottom", pady=10)

    janela.mainloop()


# Iniciar o painel
criar_painel()
