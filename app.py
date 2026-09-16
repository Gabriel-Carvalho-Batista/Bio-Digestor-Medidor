"""
Servidor Flask para a estação de medição.

Rotas:
  POST /dados   -> recebido do Arduino, salva uma nova leitura
  GET  /dados   -> retorna as últimas leituras (usado pelo site)
  GET  /        -> só pra checar se o servidor está de pé

IMPORTANTE sobre o Render (tier free):
  O disco é "efêmero": toda vez que o serviço reinicia/reimplanta,
  o arquivo dados.db é apagado e recriado do zero. Pra manter
  histórico permanente, no futuro dá pra trocar por um banco externo
  (ex: Render Postgres free tier, ou Supabase).
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timezone
import os

app = Flask(__name__)
CORS(app)  # permite que o site (em outro domínio) acesse essa API

DB_PATH = os.path.join(os.path.dirname(__file__), "dados.db")

# Chave secreta que o Arduino precisa enviar para poder gravar dados.
# É lida de uma variável de ambiente (configurada no painel do Render),
# NUNCA fica escrita no código nem sobe pro GitHub.
API_KEY = os.environ.get("API_KEY")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperatura REAL,
            umidade REAL,
            fluxo REAL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return "Servidor de medições rodando! Use /dados (GET ou POST)."


@app.route("/dados", methods=["POST"])
def receber_dados():
    # Confere a chave de API enviada pelo Arduino no header X-API-Key.
    # Se a variável de ambiente API_KEY não estiver configurada no servidor,
    # a rota fica bloqueada por segurança (fail-safe), em vez de aceitar tudo.
    chave_enviada = request.headers.get("X-API-Key")
    if not API_KEY or chave_enviada != API_KEY:
        return jsonify({"erro": "não autorizado"}), 401

    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"erro": "JSON inválido ou ausente"}), 400

    temperatura = payload.get("temperatura")
    umidade = payload.get("umidade")
    fluxo = payload.get("fluxo")  # opcional, ainda não existe fisicamente

    if temperatura is None or umidade is None:
        return jsonify({"erro": "campos 'temperatura' e 'umidade' são obrigatórios"}), 400

    conn = get_conn()
    conn.execute(
        "INSERT INTO leituras (temperatura, umidade, fluxo, timestamp) VALUES (?, ?, ?, ?)",
        (temperatura, umidade, fluxo, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"}), 201


@app.route("/dados", methods=["GET"])
def listar_dados():
    limite = request.args.get("limite", default=100, type=int)

    conn = get_conn()
    linhas = conn.execute(
        "SELECT * FROM leituras ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()

    resultado = [dict(row) for row in linhas]
    # devolve em ordem cronológica (mais antigo primeiro), melhor pra gráfico
    resultado.reverse()
    return jsonify(resultado)


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)