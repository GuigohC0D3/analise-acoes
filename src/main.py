import os
import pandas as pd
import yfinance as yf
import schedule
import time
import json

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

            # Critérios para compra: preço acima da média móvel
            if ultima_linha['Close'] > ultima_linha['SMA7']:
                resultados.append({
                    "Acao": acao,
                    "Preco": round(ultima_linha["Close"], 2),
                    "Media_Movel": round(ultima_linha["SMA7"], 2),
                    "Retorno": round(ultima_linha['Return'], 4)
                })
        except Exception as e:
            print(f"Erro ao buscar dados para {acao}: {e}")

    # Ordenar pelo maior retorno intradiário e pegar as 5 melhores ações
    melhores_acoes = sorted(resultados, key=lambda x: x["Retorno"], reverse=True)[:5]

    # Criar pasta data se não existir
    if not os.path.exists('data'):
        os.makedirs('data')

    # Atualizar o arquivo JSON com os resultados
    with open('data/melhores_acoes_5min.json', 'w') as file:
        json.dump(melhores_acoes, file, indent=4)

    print("\nAs 5 melhores ações com base no intervalo de 5 minutos foram salvas no arquivo JSON!")
    return melhores_acoes

# Agendar a execução a cada 5 minutos
schedule.every(5).minutes.do(analisar_acoes)

print("Automação iniciada... O script será executado a cada 5 minutos durante o pregão.")

while True:
    schedule.run_pending()
    time.sleep(1)
