"""
Simulador de sensor.

Fica enviando leituras falsas de temperatura/umidade pro servidor Flask,
no mesmo formato que o Arduino vai usar depois. Serve pra testar o
backend e o site sem precisar de nenhum hardware.

Uso:
    pip install requests
    python simulador.py
"""

import requests
import random
import time
import os

# Troque pela URL do seu servidor (local ou já no Render)
#API_URL = "http://localhost:5000/dados"
API_URL = "https://bio-digestor-medidor.onrender.com/dados"

# Exemplo quando já estiver no Render:
# API_URL = "https://seu-app.onrender.com/dados"

# A chave NUNCA fica escrita aqui no código — é lida da variável de
# ambiente API_KEY, a mesma configurada no servidor. Isso evita que a
# chave vá parar no GitHub junto com esse arquivo.
API_KEY = os.environ.get("API_KEY")

INTERVALO_SEGUNDOS = 10

# valores iniciais, pra simular uma variação "realista" e não números
# totalmente aleatórios a cada leitura
temperatura_atual = 24.0
umidade_atual = 55.0


def proxima_leitura():
    global temperatura_atual, umidade_atual

    # cada leitura varia um pouquinho em relação à anterior
    temperatura_atual += random.uniform(-0.4, 0.4)
    umidade_atual += random.uniform(-1.5, 1.5)

    # mantém dentro de faixas plausíveis
    temperatura_atual = max(15, min(35, temperatura_atual))
    umidade_atual = max(20, min(90, umidade_atual))

    return {
        "temperatura": round(temperatura_atual, 1),
        "umidade": round(umidade_atual, 1),
    }


def enviar(dados):
    headers = {"X-API-Key": API_KEY}
    try:
        resposta = requests.post(API_URL, json=dados, headers=headers, timeout=10)
        print(f"Enviado {dados} -> status {resposta.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar: {e}")


if __name__ == "__main__":
    if not API_KEY:
        print("AVISO: variável de ambiente API_KEY não definida.")
        print("Defina antes de rodar, ex (PowerShell): $env:API_KEY = \"sua-chave\"\n")

    print(f"Simulador rodando. Enviando para {API_URL} a cada {INTERVALO_SEGUNDOS}s.")
    print("Pressione Ctrl+C para parar.\n")
    try:
        while True:
            dados = proxima_leitura()
            enviar(dados)
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\nSimulador encerrado.")