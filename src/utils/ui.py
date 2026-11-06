import json
import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from src.utils.icones import desenhar_icone

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

TEMAS = {
    "claro": {
        "fundo": "#F4F6FB",
        "fundo_alt": "#F8FAFC",
        "branco": "#FFFFFF",
        "superficie_hover": "#F1F5F9",
        "campo": "#FFFFFF",
        "sidebar": "#0F172A",
        "sidebar_hover": "#1E293B",
        "sidebar_ativo": "#4F46E5",
        "sidebar_bloco": "#1E293B",
        "sidebar_avatar": "#334155",
        "sidebar_texto": "#CBD5E1",
        "sidebar_texto_forte": "#FFFFFF",
        "sidebar_muted": "#64748B",
        "sidebar_perfil": "#A5B4FC",
        "sidebar_versao": "#475569",
        "sidebar_perigo": "#F87171",
        "sidebar_perigo_hover": "#7F1D1D",
        "azul": "#4F46E5",
        "azul_escuro": "#4338CA",
        "texto_sobre_azul": "#FFFFFF",
        "texto_sobre_vermelho": "#FFFFFF",
        "indigo_claro": "#EEF2FF",
        "texto": "#0F172A",
        "texto_claro": "#64748B",
        "borda": "#E2E8F0",
        "vermelho": "#EF4444",
        "vermelho_escuro": "#DC2626",
        "verde": "#10B981",
        "amarelo": "#F59E0B",
        "ciano": "#06B6D4",
        "cabecalho": "#F1F5F9",
        "cabecalho_hover": "#E2E8F0",
        "cabecalho_texto": "#475569",
        "selecao": "#E0E7FF",
        "scroll": "#CBD5E1",
        "scroll_hover": "#94A3B8",
        "fundo_azul": "#EEF2FF",
        "fundo_ciano": "#ECFEFF",
        "fundo_verde": "#ECFDF5",
        "fundo_amarelo": "#FFFBEB",
        "login_fundo": "#EEF2FF",
        "login_borda": "#E0E7FF",
        "login_gradiente_ini": "#4F46E5",
        "login_gradiente_fim": "#7C3AED",
        "login_texto_suave": "#E0E7FF",
        "login_texto_lista": "#EDE9FE",
        "login_texto_rodape": "#C7D2FE",
        "login_dica_fundo": "#EEF2FF",
        "login_dica_borda": "#E0E7FF",
        "login_dica_titulo": "#4F46E5",
        "login_dica_texto": "#4338CA",
    },
    "escuro": {
        "fundo": "#0B1120",
        "fundo_alt": "#0F172A",
        "branco": "#111827",
        "superficie_hover": "#1E293B",
        "campo": "#0F172A",
        "sidebar": "#020617",
        "sidebar_hover": "#1E293B",
        "sidebar_ativo": "#4F46E5",
        "sidebar_bloco": "#0F172A",
        "sidebar_avatar": "#1E293B",
        "sidebar_texto": "#CBD5E1",
        "sidebar_texto_forte": "#F8FAFC",
        "sidebar_muted": "#64748B",
        "sidebar_perfil": "#A5B4FC",
        "sidebar_versao": "#475569",
        "sidebar_perigo": "#F87171",
        "sidebar_perigo_hover": "#7F1D1D",
        "azul": "#818CF8",
        "azul_escuro": "#6366F1",
        "texto_sobre_azul": "#0B1120",
        "texto_sobre_vermelho": "#FFFFFF",
        "indigo_claro": "#1E1B4B",
        "texto": "#F1F5F9",
        "texto_claro": "#94A3B8",
        "borda": "#1E293B",
        "vermelho": "#F87171",
        "vermelho_escuro": "#EF4444",
        "verde": "#34D399",
        "amarelo": "#FBBF24",
        "ciano": "#22D3EE",
        "cabecalho": "#1E293B",
        "cabecalho_hover": "#334155",
        "cabecalho_texto": "#CBD5E1",
        "selecao": "#312E81",
        "scroll": "#334155",
        "scroll_hover": "#475569",
        "fundo_azul": "#1E1B4B",
        "fundo_ciano": "#164E63",
        "fundo_verde": "#064E3B",
        "fundo_amarelo": "#422006",
        "login_fundo": "#0B1120",
        "login_borda": "#1E293B",
        "login_gradiente_ini": "#312E81",
        "login_gradiente_fim": "#4C1D95",
        "login_texto_suave": "#C7D2FE",
        "login_texto_lista": "#DDD6FE",
        "login_texto_rodape": "#A5B4FC",
        "login_dica_fundo": "#1E1B4B",
        "login_dica_borda": "#312E81",
        "login_dica_titulo": "#A5B4FC",
        "login_dica_texto": "#C7D2FE",
    },
}

TEMA_ATUAL = {"nome": "claro"}
CORES = dict(TEMAS["claro"])

ESTILOS_BOTAO = {
    "Primary.TButton": {
        "fundo": "azul",
        "hover": "azul_escuro",
        "texto": "texto_sobre_azul",
        "borda": None,
    },
    "Secondary.TButton": {
        "fundo": "branco",
        "hover": "superficie_hover",
        "texto": "texto",
        "borda": "borda",
    },
    "Danger.TButton": {
        "fundo": "vermelho",
        "hover": "vermelho_escuro",
        "texto": "texto_sobre_vermelho",
        "borda": None,
    },
}


def tema_atual():
    return TEMA_ATUAL["nome"]


def definir_tema(nome):
    if nome not in TEMAS:
        nome = "claro"
    TEMA_ATUAL["nome"] = nome
    CORES.clear()
    CORES.update(TEMAS[nome])


def carregar_tema():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as arquivo:
            nome = json.load(arquivo).get("tema", "claro")
    except (OSError, ValueError):
        nome = "claro"
    definir_tema(nome)
    return tema_atual()


def salvar_tema(nome=None):
    nome = nome or tema_atual()
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as arquivo:
            json.dump({"tema": nome}, arquivo)
    except OSError:
        pass


def _resolver_cor(valor):
    if isinstance(valor, str) and valor in CORES:
        return CORES[valor]
    return valor


def cor_fundo(widget):
    try:
        return widget.cget("bg")
    except tk.TclError:
        return CORES["branco"]


def centralizar(janela, largura, altura):
    janela.update_idletasks()
    x = (janela.winfo_screenwidth() - largura) // 2
    y = (janela.winfo_screenheight() - altura) // 2
    janela.geometry(f"{largura}x{altura}+{max(x, 0)}+{max(y, 0)}")


def posicionar_sobre(janela, mestre):
    janela.update_idletasks()
    largura = janela.winfo_reqwidth()
    altura = janela.winfo_reqheight()
    x = mestre.winfo_rootx() + (mestre.winfo_width() - largura) // 2
    y = mestre.winfo_rooty() + (mestre.winfo_height() - altura) // 2
    janela.geometry(f"+{max(x, 0)}+{max(y, 0)}")


def retangulo_arredondado(canvas, x1, y1, x2, y2, raio, **kwargs):
    raio = min(raio, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    pontos = [
        x1 + raio, y1,
        x2 - raio, y1,
        x2, y1,
        x2, y1 + raio,
        x2, y2 - raio,
        x2, y2,
        x2 - raio, y2,
        x1 + raio, y2,
        x1, y2,
        x1, y2 - raio,
        x1, y1 + raio,
        x1, y1,
    ]
    return canvas.create_polygon(pontos, smooth=True, **kwargs)


def _interpolar(cor_ini, cor_fim, fator):
    ini = tuple(int(cor_ini[i : i + 2], 16) for i in (1, 3, 5))
    fim = tuple(int(cor_fim[i : i + 2], 16) for i in (1, 3, 5))
    return tuple(int(ini[i] + (fim[i] - ini[i]) * fator) for i in range(3))


def desenhar_gradiente(canvas, cor_ini, cor_fim, largura, altura, tag="gradiente"):
    canvas.delete(tag)
    for y in range(altura):
        vermelho, verde, azul = _interpolar(
            cor_ini, cor_fim, y / max(altura - 1, 1)
        )
        canvas.create_line(
            0,
            y,
            largura,
            y,
            fill=f"#{vermelho:02x}{verde:02x}{azul:02x}",
            tags=tag,
        )
    canvas.tag_lower(tag)


def configurar_estilos(root):
    estilo = ttk.Style(root)
    estilo.theme_use("clam")

    root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))
    root.option_add("*TCombobox*Listbox.background", CORES["branco"])
    root.option_add("*TCombobox*Listbox.foreground", CORES["texto"])
    root.option_add("*TCombobox*Listbox.selectBackground", CORES["azul"])
    root.option_add(
        "*TCombobox*Listbox.selectForeground", CORES["texto_sobre_azul"]
    )

    estilo.configure(
        ".",
        font=("Segoe UI", 10),
        background=CORES["fundo"],
        foreground=CORES["texto"],
    )
    estilo.configure("TFrame", background=CORES["fundo"])
    estilo.configure(
        "TLabel", background=CORES["fundo"], foreground=CORES["texto"]
    )
    estilo.configure(
        "TEntry",
        padding=(10, 8),
        fieldbackground=CORES["campo"],
        foreground=CORES["texto"],
        insertcolor=CORES["texto"],
        bordercolor=CORES["borda"],
        lightcolor=CORES["borda"],
        darkcolor=CORES["borda"],
        selectbackground=CORES["azul"],
        selectforeground=CORES["texto_sobre_azul"],
    )
    estilo.map(
        "TEntry",
        bordercolor=[("focus", CORES["azul"])],
        lightcolor=[("focus", CORES["azul"])],
        darkcolor=[("focus", CORES["azul"])],
    )
    estilo.configure(
        "TCombobox",
        padding=(10, 7),
        fieldbackground=CORES["campo"],
        background=CORES["campo"],
        foreground=CORES["texto"],
        bordercolor=CORES["borda"],
        lightcolor=CORES["borda"],
        darkcolor=CORES["borda"],
        arrowcolor=CORES["texto_claro"],
    )
    estilo.map(
        "TCombobox",
        fieldbackground=[("readonly", CORES["campo"])],
        background=[("readonly", CORES["campo"])],
        foreground=[("readonly", CORES["texto"])],
        selectbackground=[("readonly", CORES["campo"])],
        selectforeground=[("readonly", CORES["texto"])],
        bordercolor=[("focus", CORES["azul"])],
        lightcolor=[("focus", CORES["azul"])],
        darkcolor=[("focus", CORES["azul"])],
    )
    estilo.configure(
        "TSpinbox",
        padding=(8, 5),
        fieldbackground=CORES["campo"],
        background=CORES["campo"],
        foreground=CORES["texto"],
        insertcolor=CORES["texto"],
        bordercolor=CORES["borda"],
        lightcolor=CORES["borda"],
        darkcolor=CORES["borda"],
        arrowcolor=CORES["texto_claro"],
    )
    estilo.map(
        "TSpinbox",
        fieldbackground=[("readonly", CORES["campo"])],
        foreground=[("readonly", CORES["texto"])],
        bordercolor=[("focus", CORES["azul"])],
        lightcolor=[("focus", CORES["azul"])],
        darkcolor=[("focus", CORES["azul"])],
    )
    estilo.configure(
        "Treeview",
        background=CORES["branco"],
        fieldbackground=CORES["branco"],
        foreground=CORES["texto"],
        rowheight=32,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    estilo.configure(
        "Treeview.Heading",
        font=("Segoe UI", 9, "bold"),
        background=CORES["cabecalho"],
        foreground=CORES["cabecalho_texto"],
        relief="flat",
        padding=(8, 8),
        borderwidth=0,
    )
    estilo.map(
        "Treeview.Heading", background=[("active", CORES["cabecalho_hover"])]
    )
    estilo.map(
        "Treeview",
        background=[("selected", CORES["selecao"])],
        foreground=[("selected", CORES["texto"])],
    )
    estilo.configure(
        "Vertical.TScrollbar",
        background=CORES["scroll"],
        troughcolor=CORES["fundo"],
        bordercolor=CORES["fundo"],
        arrowcolor=CORES["texto_claro"],
        width=10,
        arrowsize=12,
    )
    estilo.map(
        "Vertical.TScrollbar",
        background=[("active", CORES["scroll_hover"])],
    )


def criar_card(parent, **kwargs):
    return tk.Frame(
        parent,
        bg=CORES["branco"],
        highlightthickness=1,
        highlightbackground=CORES["borda"],
        **kwargs,
    )


def criar_titulo(parent, titulo, subtitulo=""):
    frame = tk.Frame(parent, bg=CORES["fundo"])
    linha = tk.Frame(frame, bg=CORES["fundo"])
    linha.pack(anchor="w")
    tk.Frame(linha, bg=CORES["azul"], width=5, height=26).pack(
        side="left", padx=(0, 12)
    )
    tk.Label(
        linha,
        text=titulo,
        font=("Segoe UI", 20, "bold"),
        bg=CORES["fundo"],
        fg=CORES["texto"],
    ).pack(side="left")
    if subtitulo:
        tk.Label(
            frame,
            text=subtitulo,
            font=("Segoe UI", 10),
            bg=CORES["fundo"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w", padx=(17, 0), pady=(2, 0))
    return frame


def criar_cabecalho(parent, titulo, subtitulo=""):
    tk.Label(
        parent,
        text=titulo,
        font=("Segoe UI", 15, "bold"),
        bg=CORES["branco"],
        fg=CORES["texto"],
    ).pack(anchor="w")
    if subtitulo:
        tk.Label(
            parent,
            text=subtitulo,
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w", pady=(2, 16))


class BotaoArredondado(tk.Canvas):
    def __init__(
        self,
        master,
        texto,
        comando=None,
        estilo="Primary.TButton",
        largura=None,
        altura=38,
        raio=10,
        fonte=("Segoe UI", 10, "bold"),
        icone=None,
    ):
        config = ESTILOS_BOTAO.get(estilo, ESTILOS_BOTAO["Primary.TButton"])
        super().__init__(
            master,
            bg=cor_fundo(master),
            highlightthickness=0,
            bd=0,
            height=altura,
            cursor="hand2",
        )
        self._texto = texto
        self._comando = comando
        self._config = {
            "fundo": _resolver_cor(config["fundo"]),
            "hover": _resolver_cor(config["hover"]),
            "texto": _resolver_cor(config["texto"]),
            "borda": _resolver_cor(config["borda"]) if config["borda"] else None,
        }
        self._raio = raio
        self._fonte = fonte
        self._cor_atual = self._config["fundo"]
        self._icone = icone
        self._icone_tamanho = max(14, min(20, round(altura * 0.47)))
        self._espaco_icone = self._icone_tamanho + 8 if icone else 0

        medida = tkfont.Font(
            family=fonte[0],
            size=fonte[1],
            weight=fonte[2] if len(fonte) > 2 else "normal",
        )
        self._largura_texto = medida.measure(texto)

        if largura is None:
            largura = self._largura_texto + 36 + self._espaco_icone
        self.configure(width=largura)

        self.bind("<Configure>", lambda e: self._desenhar())
        self.bind("<Enter>", lambda e: self._definir_cor(self._config["hover"]))
        self.bind("<Leave>", lambda e: self._definir_cor(self._config["fundo"]))
        self.bind(
            "<ButtonPress-1>", lambda e: self._definir_cor(self._config["hover"])
        )
        self.bind("<ButtonRelease-1>", self._soltar)

    def _definir_cor(self, cor):
        self._cor_atual = cor
        self._desenhar()

    def _desenhar(self):
        largura = max(self.winfo_width(), 2)
        altura = max(self.winfo_height(), 2)
        self.delete("all")
        borda = self._config["borda"]
        retangulo_arredondado(
            self,
            1,
            1,
            largura - 1,
            altura - 1,
            self._raio,
            fill=self._cor_atual,
            outline=borda if borda else self._cor_atual,
            width=1,
        )
        if self._icone:
            conteudo = self._largura_texto + self._espaco_icone
            inicio = (largura - conteudo) / 2
            desenhar_icone(
                self,
                self._icone,
                inicio,
                (altura - self._icone_tamanho) / 2,
                self._icone_tamanho,
                self._config["texto"],
                largura=2.0,
            )
            self.create_text(
                inicio + self._espaco_icone,
                altura / 2,
                text=self._texto,
                anchor="w",
                fill=self._config["texto"],
                font=self._fonte,
            )
        else:
            self.create_text(
                largura / 2,
                altura / 2,
                text=self._texto,
                fill=self._config["texto"],
                font=self._fonte,
            )

    def _soltar(self, evento):
        dentro = (
            0 <= evento.x <= self.winfo_width()
            and 0 <= evento.y <= self.winfo_height()
        )
        self._definir_cor(
            self._config["hover"] if dentro else self._config["fundo"]
        )
        if dentro and self._comando:
            self._comando()


def criar_botao(parent, texto, comando, estilo="Primary.TButton", icone=None):
    return BotaoArredondado(parent, texto, comando, estilo, icone=icone)


class TreeviewModerna(ttk.Treeview):
    def insert(self, parent, index, iid=None, **kwargs):
        tags = kwargs.get("tags", ())
        if isinstance(tags, str):
            tags = (tags,)
        tags = tuple(tags)
        if len(self.get_children()) % 2 == 1 and "par" not in tags:
            tags += ("par",)
        kwargs["tags"] = tags
        return super().insert(parent, index, iid=iid, **kwargs)


def criar_treeview(parent, colunas, borda=True):
    container = tk.Frame(
        parent,
        bg=CORES["branco"],
        highlightthickness=1 if borda else 0,
        highlightbackground=CORES["borda"],
    )
    tree = TreeviewModerna(
        container, columns=[coluna[0] for coluna in colunas], show="headings"
    )
    for chave, titulo, largura, alinhamento in colunas:
        tree.heading(
            chave, text=titulo, anchor="w" if alinhamento == "w" else "center"
        )
        tree.column(
            chave, width=largura, anchor=alinhamento, stretch=True, minwidth=50
        )
    barra = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=barra.set)
    tree.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    tree.tag_configure("par", background=CORES["fundo_alt"])
    tree.tag_configure("concluida", foreground=CORES["verde"])
    tree.tag_configure("cancelada", foreground=CORES["texto_claro"])
    return container, tree
