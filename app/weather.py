#!/usr/bin/env python3
"""
Station météo simulée - partie "App" du projet RTOS + App.

- Un thread génère des mesures (température, humidité, pression) chaque seconde.
  Plus tard, ce thread sera remplacé par la lecture des données envoyées par le RTOS.
- Les mesures sont gardées en mémoire (200 dernières) et écrites dans un fichier CSV.
- Un serveur web affiche les données sur http://<ip>:8080

Usage :
    python3 weather.py                  # mesures simulées
    python3 weather.py --tcp 127.0.0.1:5555   # lit "T,H,P" depuis le RTOS (plus tard)
"""
import argparse
import json
import math
import os
import random
import socket
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080
CSV_FILE = "/tmp/mesures.csv"
MAX_POINTS = 200

data = deque(maxlen=MAX_POINTS)
lock = threading.Lock()


def store(t, h, p):
    """Enregistre une mesure en mémoire et dans le fichier CSV."""
    ts = time.strftime("%H:%M:%S")
    with lock:
        data.append({"time": ts, "temp": round(t, 1), "hum": round(h, 1), "press": round(p, 1)})
    try:
        new = not os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a") as f:
            if new:
                f.write("heure,temperature,humidite,pression\n")
            f.write(f"{ts},{t:.1f},{h:.1f},{p:.1f}\n")
    except OSError:
        pass  # le système de fichiers peut être en lecture seule


def simulate():
    """Génère des mesures simulées (variation lente + bruit)."""
    t0 = time.time()
    while True:
        x = time.time() - t0
        temp = 22 + 4 * math.sin(x / 60) + random.uniform(-0.3, 0.3)
        hum = 55 + 10 * math.sin(x / 90 + 1) + random.uniform(-1, 1)
        press = 1013 + 3 * math.sin(x / 300) + random.uniform(-0.2, 0.2)
        store(temp, hum, press)
        time.sleep(1)


def read_tcp(host, port):
    """Lit des lignes 'T,H,P' envoyées par le RTOS via une socket TCP."""
    while True:
        try:
            with socket.create_connection((host, port), timeout=5) as s:
                buf = b""
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            t, h, p = (float(v) for v in line.decode().strip().split(","))
                            store(t, h, p)
                        except ValueError:
                            pass  # ligne mal formée : on l'ignore
        except OSError:
            time.sleep(2)  # on réessaie


PAGE = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Station météo</title>
<style>
 body{font-family:sans-serif;max-width:700px;margin:20px auto;padding:0 10px}
 .cards{display:flex;gap:10px;flex-wrap:wrap}
 .card{flex:1;min-width:140px;background:#eef3f8;border-radius:8px;padding:12px;text-align:center}
 .big{font-size:2em;font-weight:bold}
 table{width:100%;border-collapse:collapse;margin-top:15px}
 td,th{border-bottom:1px solid #ddd;padding:4px;text-align:center}
</style></head><body>
<h1>Station météo embarquée</h1>
<div class="cards">
 <div class="card">Température<div class="big" id="t">--</div>°C</div>
 <div class="card">Humidité<div class="big" id="h">--</div>%</div>
 <div class="card">Pression<div class="big" id="p">--</div>hPa</div>
</div>
<p id="stats"></p>
<table><thead><tr><th>Heure</th><th>Temp (°C)</th><th>Hum (%)</th><th>Pression (hPa)</th></tr></thead>
<tbody id="rows"></tbody></table>
<script>
async function refresh(){
  try{
    const d = await (await fetch('/api/data')).json();
    if(!d.length) return;
    const last = d[d.length-1];
    document.getElementById('t').textContent = last.temp;
    document.getElementById('h').textContent = last.hum;
    document.getElementById('p').textContent = last.press;
    const temps = d.map(x=>x.temp);
    const avg = (temps.reduce((a,b)=>a+b,0)/temps.length).toFixed(1);
    document.getElementById('stats').textContent =
      'Température sur ' + d.length + ' mesures : moyenne ' + avg +
      ' °C, min ' + Math.min(...temps) + ', max ' + Math.max(...temps);
    document.getElementById('rows').innerHTML = d.slice(-15).reverse().map(x =>
      '<tr><td>'+x.time+'</td><td>'+x.temp+'</td><td>'+x.hum+'</td><td>'+x.press+'</td></tr>').join('');
  }catch(e){}
}
refresh(); setInterval(refresh, 1000);
</script></body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/data":
            with lock:
                body = json.dumps(list(data)).encode()
            ctype = "application/json"
        elif self.path in ("/", "/index.html"):
            body = PAGE.encode()
            ctype = "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # pas de logs dans la console


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tcp", help="hote:port d'où lire les mesures du RTOS")
    args = ap.parse_args()

    if args.tcp:
        host, port = args.tcp.rsplit(":", 1)
        target = lambda: read_tcp(host, int(port))
    else:
        target = simulate
    threading.Thread(target=target, daemon=True).start()

    print(f"Station météo sur http://0.0.0.0:{PORT}  (Ctrl+C pour arrêter)")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
