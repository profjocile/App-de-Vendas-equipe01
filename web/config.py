import os


def _porta():
    try:
        valor = int(os.environ.get("VENDAS_WEB_PORT", "8765"))
    except (TypeError, ValueError):
        return 8765
    return valor if 1 <= valor <= 65535 else 8765


HOST = os.environ.get("VENDAS_WEB_HOST", "").strip() or "127.0.0.1"
PORT = _porta()
if HOST in ("0.0.0.0", "::"):
    URL_HOST = "127.0.0.1"
elif ":" in HOST:
    URL_HOST = f"[{HOST}]"
else:
    URL_HOST = HOST
URL = f"http://{URL_HOST}:{PORT}"
