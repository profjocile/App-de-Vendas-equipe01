import tkinter as tk

from src.database import init_db
from src.sessao import Sessao
from src.utils.ui import (
    CORES,
    carregar_tema,
    centralizar,
    configurar_estilos,
)
from src.views.app import App
from src.views.tela_login import TelaLogin


def main():
    init_db()
    carregar_tema()
    root = tk.Tk()
    configurar_estilos(root)
    root.title("Sistema de Vendas")
    root.configure(bg=CORES["login_fundo"])

    def abrir_login():
        for widget in root.winfo_children():
            widget.destroy()
        Sessao.encerrar()
        root.resizable(False, False)
        root.minsize(0, 0)
        root.configure(bg=CORES["login_fundo"])
        centralizar(root, 840, 560)
        TelaLogin(root, abrir_app)

    def abrir_app(usuario):
        Sessao.iniciar(usuario)
        for widget in root.winfo_children():
            widget.destroy()
        root.resizable(True, True)
        root.minsize(1024, 640)
        root.configure(bg=CORES["fundo"])
        centralizar(root, 1200, 720)
        App(root, abrir_login)

    abrir_login()
    root.mainloop()


if __name__ == "__main__":
    main()
