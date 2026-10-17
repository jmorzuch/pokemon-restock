#!/usr/bin/env python3
"""Pokemon Restock - local alert receiver.

Listens on 127.0.0.1:8787. When the in-browser bookmarklet sees a Target
product flip to IN STOCK, it POSTs here and we fire a Telegram alert.

Endpoints:
  GET  /status   -> JSON state
  POST /alert    -> body {"name":..., "url":..., "in_stock":true}
  OPTIONS         -> CORS / Private-Network-Access preflight

Run:  python receiver.py
"""
import json, time, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 8787
TG_CHAT = "telegram:1020092160"
HERE = Path(__file__).resolve().parent
LOG = HERE / "alerts.log"
COOLDOWN_SEC = 30 * 60  # don't re-alert the same product within 30 min
_last = {}


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def send_telegram(name: str, url: str) -> bool:
    msg = f"\U0001F389 POKEMON RESTOCK — IN STOCK at Target!\n{name}\n{url}\nGo grab it now."
    try:
        r = subprocess.run(
            ["hermes", "send", "--to", TG_CHAT, msg],
            capture_output=True, text=True, timeout=40,
        )
        log(f"telegram rc={r.returncode} out={r.stdout.strip()[:160]!r} err={r.stderr.strip()[:160]!r}")
        return r.returncode == 0
    except Exception as e:
        log(f"telegram send FAILED: {e!r}")
        return False


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/status"):
            body = json.dumps({
                "service": "pokemon-restock-receiver",
                "time": time.time(),
                "cooldown_sec": COOLDOWN_SEC,
                "last_alerts": _last,
            }).encode()
            ct = "application/json"
        else:
            body, ct = b"ok", "text/plain"
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        ln = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(ln) if ln else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            data = {}
        name = str(data.get("name") or data.get("title") or "Target product")
        url = str(data.get("url") or "")
        in_stock = bool(data.get("in_stock", True))
        log(f"ALERT name={name!r} url={url!r} in_stock={in_stock}")
        sent = False
        if in_stock:
            now = time.time()
            if now - _last.get(name, 0) < COOLDOWN_SEC:
                log("  (within cooldown — not re-sending telegram)")
            else:
                _last[name] = now
                sent = send_telegram(name, url)
        body = json.dumps({"ok": True, "name": name, "in_stock": in_stock,
                           "telegram_sent": sent}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # silence default stderr logging
        pass


if __name__ == "__main__":
    log(f"receiver starting on 127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
