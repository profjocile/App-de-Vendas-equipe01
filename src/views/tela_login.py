import tkinter as tk
from tkinter import ttk

from src.models.usuario import autenticar
from src.utils.icones import desenhar_icone
from src.utils.ui import (
    CORES,
    configurar_estilos,
    criar_botao,
    definir_tema,
    desenhar_gradiente,
    retangulo_arredondado,
    salvar_tema,
    tema_atual,
)


class TelaLogin(tk.Frame):
    def __init__(self, master, ao_autenticar):
        super().__init__(master, bg=CORES["login_fundo"])
        self.pack(fill="both", expand=True)
        self.ao_autenticar = ao_autenticar
        self._foco_id = None
        self._montar()

    def _montar(self):
        centro = tk.Frame(self, bg=CORES["login_fundo"])
        centro.pack(expand=True)

        card = tk.Frame(
            centro,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["login_borda"],
        )
        card.pack()

        marca = tk.Canvas(
            card,
            width=300,
            height=480,
            bg=CORES["azul"],
            highlightthickness=0,
            bd=0,
        )
        marca.pack(side="left", fill="y")
        desenhar_gradiente(
            marca,
            CORES["login_gradiente_ini"],
            CORES["login_gradiente_fim"],
            300,
            480,
        )

        retangulo_arredondado(
            marca, 32, 36, 82, 86, 14, fill="white", outline=""
        )
        marca.create_text(
            57, 61, text="SV", fill="#4F46E5", font=("Segoe UI", 15, "bold")
        )
        marca.create_text(
            32,
            116,
            text="Sistema de\nVendas",
            anchor="nw",
            fill="white",
            font=("Segoe UI", 25, "bold"),
            width=240,
        )
        marca.create_text(
            32,
            225,
            text="Controle produtos, clientes e vendas em um só lugar.",
            anchor="nw",
            fill=CORES["login_texto_suave"],
            font=("Segoe UI", 10),
            width=230,
        )
        recursos = (
            "Cadastro e controle de estoque",
            "Vendas, histórico e cancelamento",
            "Relatórios exportados em CSV",
        )
        for indice, recurso in enumerate(recursos):
            posicao = 326 + indice * 42
            desenhar_icone(
                marca,
                "check_circle",
                32,
                posicao + 2,
                15,
                CORES["login_texto_lista"],
                largura=2.0,
            )
            marca.create_text(
                58,
                posicao,
                text=recurso,
                anchor="nw",
                fill=CORES["login_texto_lista"],
                font=("Segoe UI", 10),
                width=214,
            )
        marca.create_text(
            32,
            440,
            text="Python + SQLite • v1.0",
            anchor="nw",
            fill=CORES["login_texto_rodape"],
            font=("Segoe UI", 8),
        )

        painel = tk.Frame(card, bg=CORES["branco"], width=470, height=480)
        painel.pack(side="left", fill="both", expand=True)
        painel.pack_propagate(False)

        conteudo = tk.Frame(painel, bg=CORES["branco"])
        conteudo.pack(padx=48, pady=44, fill="both", expand=True)

        topo = tk.Frame(conteudo, bg=CORES["branco"])
        topo.pack(fill="x")
        tk.Label(
            topo,
            text="Bem-vindo de volta",
            font=("Segoe UI", 20, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(side="left")
        self.btn_tema = tk.Canvas(
            topo,
            width=36,
            height=36,
            bg=CORES["branco"],
            highlightthickness=0,
            cursor="hand2",
        )
        self.btn_tema.pack(side="right", pady=(4, 0))
        self._desenhar_botao_tema(hover=False)
        self.btn_tema.bind("<Enter>", lambda e: self._desenhar_botao_tema(hover=True))
        self.btn_tema.bind("<Leave>", lambda e: self._desenhar_botao_tema(hover=False))
        self.btn_tema.bind("<Button-1>", lambda e: self._alternar_tema())

        tk.Label(
            conteudo,
            text="Acesse sua conta para continuar",
            font=("Segoe UI", 10),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w", pady=(4, 26))

        tk.Label(
            conteudo,
            text="Login",
            font=("Segoe UI", 9, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w")
        self.entry_login = ttk.Entry(conteudo, width=34)
        self.entry_login.pack(fill="x", pady=(5, 14))

        tk.Label(
            conteudo,
            text="Senha",
            font=("Segoe UI", 9, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w")
        self.entry_senha = ttk.Entry(conteudo, width=34, show="•")
        self.entry_senha.pack(fill="x", pady=(5, 8))

        self.label_erro = tk.Label(
            conteudo,
            text="",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["vermelho"],
            wraplength=330,
            justify="left",
        )
        self.label_erro.pack(anchor="w", pady=(0, 10))

        criar_botao(conteudo, "Entrar", self._entrar, icone="login").pack(fill="x")

        dica = tk.Frame(
            conteudo,
            bg=CORES["login_dica_fundo"],
            highlightthickness=1,
            highlightbackground=CORES["login_dica_borda"],
        )
        dica.pack(fill="x", pady=(24, 0))
        tk.Label(
            dica,
            text="ACESSO DE DEMONSTRAÇÃO",
            font=("Segoe UI", 8, "bold"),
            bg=CORES["login_dica_fundo"],
            fg=CORES["login_dica_titulo"],
        ).pack(anchor="w", padx=14, pady=(10, 2))
        tk.Label(
            dica,
            text="admin / admin123   •   vendedor / vendedor123",
            font=("Consolas", 9),
            bg=CORES["login_dica_fundo"],
            fg=CORES["login_dica_texto"],
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self.entry_login.bind("<Return>", self._entrar)
        self.entry_senha.bind("<Return>", self._entrar)
        self._foco_id = self.after(150, self.entry_login.focus_set)

    def _desenhar_botao_tema(self, hover=False):
        self.btn_tema.delete("all")
        bg_card = CORES["branco"]
        if hover:
            fundo_btn = CORES["superficie_hover"]
            retangulo_arredondado(
                self.btn_tema, 1, 1, 35, 35, 10, fill=fundo_btn, outline=CORES["borda"]
            )
        else:
            retangulo_arredondado(
                self.btn_tema, 1, 1, 35, 35, 10, fill=bg_card, outline=CORES["borda"]
            )

        if tema_atual() == "escuro":
            desenhar_icone(self.btn_tema, "sun", 9, 9, 18, "#FBBF24", largura=2.0)
        else:
            desenhar_icone(
                self.btn_tema, "moon", 9, 9, 18, CORES["azul"], largura=2.0
            )

    def _alternar_tema(self):
        if self._foco_id:
            self.after_cancel(self._foco_id)
            self._foco_id = None
        novo = "claro" if tema_atual() == "escuro" else "escuro"
        definir_tema(novo)
        salvar_tema(novo)
        raiz = self.winfo_toplevel()
        configurar_estilos(raiz)
        raiz.configure(bg=CORES["login_fundo"])
        self.destroy()
        TelaLogin(raiz, self.ao_autenticar)

    def _entrar(self, evento=None):
        login = self.entry_login.get().strip()
        senha = self.entry_senha.get()
        if not login or not senha:
            self.label_erro.configure(text="Informe login e senha.")
            return
        usuario = autenticar(login, senha)
        if not usuario:
            self.label_erro.configure(
                text="Login ou senha inválidos, ou usuário inativo."
            )
            self.entry_senha.delete(0, "end")
            self.entry_senha.focus_set()
            return
        self.ao_autenticar(usuario)
