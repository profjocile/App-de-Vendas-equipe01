import tkinter as tk
from tkinter import messagebox

from src.sessao import Sessao
from src.utils.icones import desenhar_icone
from src.utils.webapp import abrir_versao_web
from src.utils.ui import (
    CORES,
    configurar_estilos,
    definir_tema,
    retangulo_arredondado,
    salvar_tema,
    tema_atual,
)
from src.views.tela_clientes import TelaClientes
from src.views.tela_dashboard import TelaDashboard
from src.views.tela_historico import TelaHistorico
from src.views.tela_produtos import TelaProdutos
from src.views.tela_relatorios import TelaRelatorios
from src.views.tela_usuarios import TelaUsuarios
from src.views.tela_vendas import TelaVendas

TELAS = {
    "dashboard": TelaDashboard,
    "produtos": TelaProdutos,
    "clientes": TelaClientes,
    "vendas": TelaVendas,
    "historico": TelaHistorico,
    "relatorios": TelaRelatorios,
    "usuarios": TelaUsuarios,
}


class ItemMenu(tk.Canvas):
    def __init__(self, master, texto, comando, perigo=False, icone=None):
        super().__init__(
            master,
            bg=CORES["sidebar"],
            height=44,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._texto = texto
        self._comando = comando
        self._perigo = perigo
        self._icone = icone
        self._ativo = False
        self._hover = False
        self.bind("<Configure>", lambda e: self._desenhar())
        self.bind("<Enter>", self._entrar)
        self.bind("<Leave>", self._sair)
        self.bind("<Button-1>", lambda e: self._comando())

    def _entrar(self, evento=None):
        self._hover = True
        self._desenhar()

    def _sair(self, evento=None):
        self._hover = False
        self._desenhar()

    def definir_ativo(self, ativo):
        self._ativo = ativo
        self._desenhar()

    def _desenhar(self):
        largura = max(self.winfo_width(), 2)
        altura = max(self.winfo_height(), 2)
        self.delete("all")
        if self._ativo:
            cor = CORES["sidebar_ativo"]
        elif self._hover:
            cor = (
                CORES["sidebar_perigo_hover"]
                if self._perigo
                else CORES["sidebar_hover"]
            )
        else:
            cor = CORES["sidebar"]
        if cor != CORES["sidebar"]:
            retangulo_arredondado(
                self, 0, 3, largura, altura - 3, 10, fill=cor, outline=""
            )
        if self._ativo:
            cor_texto = CORES["sidebar_texto_forte"]
        elif self._perigo:
            cor_texto = CORES["sidebar_perigo"]
        else:
            cor_texto = CORES["sidebar_texto"]
        if self._icone:
            nome_icone = self._icone
            if nome_icone == "tema":
                nome_icone = "sun" if tema_atual() == "escuro" else "moon"
            desenhar_icone(
                self,
                nome_icone,
                11,
                (altura - 20) / 2,
                20,
                cor_texto,
                largura=2.0,
            )
        self.create_text(
            44 if self._icone else 18,
            altura / 2,
            text=self._texto,
            anchor="w",
            fill=cor_texto,
            font=("Segoe UI", 10, "bold" if self._ativo else "normal"),
        )


class App:
    def __init__(self, root, ao_sair):
        self.root = root
        self.ao_sair = ao_sair
        self.usuario = Sessao.usuario()
        self.admin = Sessao.e_admin()
        self.botoes = {}
        self.tela_atual = "dashboard"
        self._montar()

    def _montar(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.botoes = {}

        self.sidebar = tk.Frame(self.root, bg=CORES["sidebar"], width=248)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        marca = tk.Frame(self.sidebar, bg=CORES["sidebar"])
        marca.pack(fill="x", padx=20, pady=(26, 24))
        textos = tk.Frame(marca, bg=CORES["sidebar"])
        textos.pack(side="left")
        tk.Label(
            textos,
            text="Sistema de Vendas",
            font=("Segoe UI", 13, "bold"),
            bg=CORES["sidebar"],
            fg=CORES["sidebar_texto_forte"],
        ).pack(anchor="w")

        bloco_usuario = tk.Frame(self.sidebar, bg=CORES["sidebar_bloco"])
        bloco_usuario.pack(fill="x", padx=14, pady=(0, 22))
        avatar = tk.Canvas(
            bloco_usuario,
            width=36,
            height=36,
            bg=CORES["sidebar_bloco"],
            highlightthickness=0,
        )
        avatar.pack(side="left", padx=(12, 10), pady=12)
        avatar.create_oval(
            0, 0, 36, 36, fill=CORES["sidebar_avatar"], outline=""
        )
        desenhar_icone(
            avatar,
            "clientes",
            9,
            9,
            18,
            CORES["sidebar_texto_forte"],
            largura=1.8,
        )
        dados = tk.Frame(bloco_usuario, bg=CORES["sidebar_bloco"])
        dados.pack(side="left")
        tk.Label(
            dados,
            text=self.usuario["nome"],
            font=("Segoe UI", 9, "bold"),
            bg=CORES["sidebar_bloco"],
            fg=CORES["sidebar_texto_forte"],
        ).pack(anchor="w")
        perfil = "Administrador" if self.admin else "Vendedor"
        tk.Label(
            dados,
            text=perfil,
            font=("Segoe UI", 8),
            bg=CORES["sidebar_bloco"],
            fg=CORES["sidebar_perfil"],
        ).pack(anchor="w", pady=(1, 0))

        tk.Label(
            self.sidebar,
            text="MENU",
            font=("Segoe UI", 8, "bold"),
            bg=CORES["sidebar"],
            fg=CORES["sidebar_muted"],
        ).pack(anchor="w", padx=24, pady=(0, 6))

        itens = [
            ("dashboard", "Dashboard", "dashboard"),
            ("produtos", "Produtos", "produtos"),
            ("clientes", "Clientes", "clientes"),
            ("vendas", "Nova Venda", "cart"),
            ("historico", "Histórico", "historico"),
        ]
        if self.admin:
            itens.append(("relatorios", "Relatórios", "relatorios"))
            itens.append(("usuarios", "Usuários", "usuarios"))

        for chave, texto, icone in itens:
            self._criar_botao_nav(chave, texto, icone)

        rodape = tk.Frame(self.sidebar, bg=CORES["sidebar"])
        rodape.pack(side="bottom", fill="x", pady=16)
        rotulo_tema = "Tema claro" if tema_atual() == "escuro" else "Tema escuro"
        ItemMenu(
            rodape, "Versão Web", self._abrir_web, icone="web"
        ).pack(fill="x", padx=12, pady=2)
        ItemMenu(
            rodape, rotulo_tema, self.alternar_tema, icone="tema"
        ).pack(fill="x", padx=12, pady=2)
        ItemMenu(
            rodape, "Sair", self._sair, perigo=True, icone="sair"
        ).pack(fill="x", padx=12, pady=2)
        tk.Label(
            rodape,
            text="v1.0 • Python + SQLite",
            font=("Segoe UI", 8),
            bg=CORES["sidebar"],
            fg=CORES["sidebar_versao"],
        ).pack(pady=(10, 0))

        self.container = tk.Frame(self.root, bg=CORES["fundo"])
        self.container.pack(side="right", fill="both", expand=True)

        self.mostrar(self.tela_atual)

    def _criar_botao_nav(self, chave, texto, icone):
        botao = ItemMenu(
            self.sidebar, texto, lambda: self.mostrar(chave), icone=icone
        )
        botao.pack(fill="x", padx=12, pady=2)
        self.botoes[chave] = botao

    def mostrar(self, nome):
        if nome not in TELAS:
            return
        for widget in self.container.winfo_children():
            widget.destroy()
        tela = TELAS[nome](self.container, self)
        tela.pack(fill="both", expand=True)
        self.tela_atual = nome
        for chave, botao in self.botoes.items():
            botao.definir_ativo(chave == nome)

    def alternar_tema(self):
        novo = "claro" if tema_atual() == "escuro" else "escuro"
        definir_tema(novo)
        salvar_tema(novo)
        configurar_estilos(self.root)
        self.root.configure(bg=CORES["fundo"])
        self._montar()

    def _abrir_web(self):
        try:
            abrir_versao_web()
        except Exception as erro:
            messagebox.showerror(
                "Versão Web",
                f"Não foi possível abrir a versão web:\n{erro}",
            )

    def _sair(self):
        if messagebox.askyesno("Sair", "Deseja encerrar a sessão?"):
            self.ao_sair()
