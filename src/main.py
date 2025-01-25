import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import yfinance as yf
import schedule
import time
import threading
import json

# Função para realizar a análise
def analisar_acoes():
    print("Analisando o mercado com intervalo de 5 minutos...")

    # Lista de ações para monitorar
    acoes = ["ALLD3.SA", "AURE3.SA", "BBAS3.SA", "BBDC4.SA", "CMIG4.SA", 
             "CXSE3.SA", "PETR4.SA", "SAPR4.SA", "TAEE3.SA", "TIMS3.SA"]

    resultados = []

    for acao in acoes:
        try:
            # Buscar dados do yfinance com intervalo de 5 minutos
            ticker = yf.Ticker(acao)
            dados = ticker.history(period="1d", interval="5m")  # Intervalo de 5 minutos

            if dados.empty:
                print(f"Sem dados suficientes para {acao}.")
                continue

            # Calcular a média móvel dos últimos 7 períodos (35 minutos)
            dados['SMA7'] = dados['Close'].rolling(window=7).mean()

            # Calcular a variação percentual intradiária
            dados['Return'] = dados['Close'].pct_change()

            # Filtrar dados recentes
            ultima_linha = dados.iloc[-1]

            # Verificar se há dados suficientes para análise
            if pd.isna(ultima_linha['SMA7']):
                print(f"Dados insuficientes para calcular a média móvel de {acao}.")
                continue

            # Adicionar resultados independentemente do critério
            resultados.append({
                "Acao": acao,
                "Preco": round(ultima_linha["Close"], 2),
                "Media_Movel": round(ultima_linha["SMA7"], 2),
                "Retorno": round(ultima_linha['Return'], 4),
                "Atende_Criterio": ultima_linha['Close'] > ultima_linha['SMA7']  # True ou False
            })
        except Exception as e:
            print(f"Erro ao buscar dados para {acao}: {e}")

    # Ordenar pelo maior retorno e pegar sempre 5 ações, independentemente do critério
    melhores_acoes = sorted(resultados, key=lambda x: x["Retorno"], reverse=True)[:5]

    # Criar pasta data se não existir
    if not os.path.exists('data'):
        os.makedirs('data')

    # Atualizar o arquivo JSON com os resultados
    with open('data/melhores_acoes_5min.json', 'w') as file:
        json.dump(melhores_acoes, file, indent=4)

    print("\nAs 5 melhores ações com base no intervalo de 5 minutos foram salvas no arquivo JSON!")
    return melhores_acoes

# Função para iniciar a automação
def iniciar_automacao():
    def rodar_agendador():
        while True:
            schedule.run_pending()
            time.sleep(1)

    # Agendar a execução a cada 5 minutos
    schedule.every(5).minutes.do(analisar_acoes)

    # Exibir mensagem de sucesso e iniciar o agendador
    messagebox.showinfo("Automação", "Automação iniciada! O script será executado a cada 5 minutos.")
    threading.Thread(target=rodar_agendador, daemon=True).start()

# Configurar a interface gráfica
def criar_painel():
    janela = tk.Tk()
    janela.title("Painel de Automação - Ações")
    janela.geometry("500x300")

    # Título
    titulo = tk.Label(janela, text="Painel de Automação de Ações", font=("Helvetica", 16))
    titulo.pack(pady=10)

    # Botão para iniciar a automação
    botao_iniciar = ttk.Button(janela, text="Iniciar Automação", command=iniciar_automacao)
    botao_iniciar.pack(pady=20)

    # Texto explicativo
    texto_info = tk.Label(
        janela,
        text="Clique no botão acima para iniciar a análise automática das ações\ncom intervalo de 5 minutos.",
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
