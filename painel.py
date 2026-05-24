from flask import Flask
import threading
import requests
import time
import logging

app = Flask(__name__)

# Configuração fixa
URL = "https://visa.vfsglobal.com/ago/en/pol/"
CHECK_INTERVAL = 60
BOT_TOKEN = "8898640547:AAE418hCgxfTSLr2ysCwXPnsmSizwFxBn_0"
CHAT_ID = "5235730100"

# Estado partilhado
monitor = {
    "status": "A iniciar...",
    "vaga": False,
    "ultimo_check": "-"
}

# Logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

def enviar_telegram(msg):
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                     params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        logging.error(f"Erro Telegram: {e}")

def monitor_logic():
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    while True:
        try:
            r = session.get(URL, headers=headers, timeout=15)
            texto = r.text.lower()
            monitor["ultimo_check"] = time.strftime("%H:%M:%S")
            vaga = any([x in texto for x in ["book now", "available", "slots"]])

            if vaga and not monitor["vaga"]:
                monitor["status"] = "⚠️ VAGA DETETADA!"
                monitor["vaga"] = True
                enviar_telegram("⚠️ Vaga VFS encontrada!")
            elif not vaga:
                monitor["vaga"] = False
                monitor["status"] = "A monitorizar..."

            logging.info(f"Status: {monitor['status']}")
        except Exception as e:
            monitor["status"] = "Erro de rede"
            logging.error(e)
        time.sleep(CHECK_INTERVAL)

@app.route("/")
def home():
    return f"""<html><head><meta http-equiv="refresh" content="10"></head>
    <body style="font-family:Arial">
        <h1>Monitor VFS</h1>
        <p><b>Status:</b> {monitor["status"]}</p>
        <p><b>Última verificação:</b> {monitor["ultimo_check"]}</p>
    </body></html>"""

if __name__ == "__main__":
    threading.Thread(target=monitor_logic, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
