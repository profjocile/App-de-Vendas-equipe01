import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from web.config import URL

VERIFICACAO_URL = URL + "/health"
TEMPO_MAXIMO = 10.0


def _abridor_local():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def servidor_ativo(timeout=0.6):
    try:
        with _abridor_local().open(VERIFICACAO_URL, timeout=timeout) as resposta:
            return resposta.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _iniciar_servidor():
    opcoes = {
        "cwd": BASE_DIR,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        opcoes["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.Popen(
        [sys.executable, "-m", "web.server"],
        **opcoes,
    )


def abrir_versao_web():
    if servidor_ativo():
        webbrowser.open(URL)
        return URL, False

    processo = _iniciar_servidor()
    limite = time.time() + TEMPO_MAXIMO
    while time.time() < limite:
        if servidor_ativo():
            webbrowser.open(URL)
            return URL, True
        if processo.poll() is not None:
            break
        time.sleep(0.3)

    raise RuntimeError(
        "O servidor web não respondeu. Verifique se a porta está livre e "
        "execute 'python -m web.server' para ver os detalhes."
    )
