import tkinter as tk

from src.models import cliente, produto, venda
from src.utils.icones import desenhar_icone
from src.utils.notificacao import notificar_info
from src.utils.ui import CORES, criar_botao, criar_titulo, criar_treeview
from src.utils.validacao import formatar_data_hora, formatar_moeda


class TelaDashboard(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CORES["fundo"])
        self.app = app
        self.cards = {}
        self._montar()
        self.carregar()

    def _montar(self):
        topo = tk.Frame(self, bg=CORES["fundo"])
        topo.pack(fill="x", padx=28, pady=(24, 14))
        criar_titulo(
            topo,
            "Dashboard",
            f"Bem-vindo(a), {self.app.usuario['nome']}",
        ).pack(side="left")
        criar_botao(
            topo, "Atualizar", self.carregar, "Secondary.TButton", icone="refresh"
        ).pack(side="right")

        area_cards = tk.Frame(self, bg=CORES["fundo"])
        area_cards.pack(fill="x", padx=28)
        definicoes = [
            ("vendas", "Vendas hoje", "vendas", CORES["azul"], CORES["fundo_azul"]),
            ("produtos", "Produtos", "produtos", CORES["ciano"], CORES["fundo_ciano"]),
            ("clientes", "Clientes", "clientes", CORES["verde"], CORES["fundo_verde"]),
            ("estoque", "Estoque baixo", "estoque", CORES["amarelo"], CORES["fundo_amarelo"]),
        ]
        for indice, (chave, titulo, tipo, cor, cor_clara) in enumerate(definicoes):
            card = self._criar_card_indicador(
                area_cards, chave, titulo, tipo, cor, cor_clara
            )
            card.grid(
                row=0,
                column=indice,
                sticky="nsew",
                padx=(0 if indice == 0 else 12, 0),
            )
            area_cards.columnconfigure(indice, weight=1)

        corpo = tk.Frame(self, bg=CORES["fundo"])
        corpo.pack(fill="both", expand=True, padx=28, pady=(16, 24))
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=2)
        corpo.rowconfigure(0, weight=1)

        card_vendas = tk.Frame(
            corpo,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_vendas.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        tk.Label(
            card_vendas,
            text="Últimas vendas",
            font=("Segoe UI", 11, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(anchor="w", padx=18, pady=(16, 10))
        container_vendas, self.tree_vendas = criar_treeview(
            card_vendas,
            [
                ("id", "ID", 50, "center"),
                ("data", "Data", 130, "center"),
                ("cliente", "Cliente", 170, "w"),
                ("total", "Total", 100, "e"),
                ("status", "Status", 90, "center"),
            ],
            borda=False,
        )
        container_vendas.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        card_estoque = tk.Frame(
            corpo,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_estoque.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            card_estoque,
            text="Produtos com estoque baixo",
            font=("Segoe UI", 11, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(anchor="w", padx=18, pady=(16, 10))
        container_estoque, self.tree_estoque = criar_treeview(
            card_estoque,
            [
                ("produto", "Produto", 190, "w"),
                ("estoque", "Estoque", 80, "center"),
            ],
            borda=False,
        )
        container_estoque.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _criar_card_indicador(self, parent, chave, titulo, tipo, cor, cor_clara):
        card = tk.Frame(
            parent,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        conteudo = tk.Frame(card, bg=CORES["branco"])
        conteudo.pack(fill="both", expand=True, padx=18, pady=14)

        topo = tk.Frame(conteudo, bg=CORES["branco"])
        topo.pack(fill="x")
        tk.Label(
            topo,
            text=titulo,
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(side="left", pady=(9, 0))
        icone = tk.Canvas(
            topo, width=42, height=42, bg=CORES["branco"], highlightthickness=0
        )
        icone.pack(side="right")
        icone.create_oval(1, 1, 41, 41, fill=cor_clara, outline="")
        desenhar_icone(icone, tipo, 8, 8, 26, cor, largura=2.0)

        valor = tk.Label(
            conteudo,
            text="—",
            font=("Segoe UI", 22, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        )
        valor.pack(anchor="w")
        detalhe = tk.Label(
            conteudo,
            text="",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        )
        detalhe.pack(anchor="w", pady=(0, 2))
        self.cards[chave] = (valor, detalhe)
        return card

    def carregar(self):
        resumo = venda.resumo_dia()
        self.cards["vendas"][0].configure(text=str(resumo["quantidade"]))
        self.cards["vendas"][1].configure(
            text=f"Total: {formatar_moeda(resumo['total'])}"
        )
        self.cards["produtos"][0].configure(text=str(produto.total()))
        self.cards["produtos"][1].configure(text="cadastrados")
        self.cards["clientes"][0].configure(text=str(cliente.total()))
        self.cards["clientes"][1].configure(text="cadastrados")

        baixos = produto.contar_estoque_baixo()
        self.cards["estoque"][0].configure(
            text=str(baixos), fg=CORES["vermelho"] if baixos else CORES["texto"]
        )
        self.cards["estoque"][1].configure(text="produtos com 5 un. ou menos")

        for item in self.tree_vendas.get_children():
            self.tree_vendas.delete(item)
        for registro in venda.ultimas(5):
            status = (
                "Concluída" if registro["status"] == "concluida" else "Cancelada"
            )
            self.tree_vendas.insert(
                "",
                "end",
                values=(
                    registro["id"],
                    formatar_data_hora(registro["data_venda"]),
                    registro["cliente_nome"],
                    formatar_moeda(registro["total"]),
                    status,
                ),
                tags=(registro["status"],),
            )

        for item in self.tree_estoque.get_children():
            self.tree_estoque.delete(item)
        for registro in produto.listar_estoque_baixo():
            self.tree_estoque.insert(
                "",
                "end",
                values=(registro["nome"], registro["estoque"]),
                tags=("baixo",),
            )
