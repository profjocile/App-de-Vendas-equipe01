import tkinter as tk
from tkinter import ttk

from src.models import cliente, produto, venda
from src.sessao import Sessao
from src.utils.notificacao import (
    notificar_aviso,
    notificar_erro,
    notificar_sucesso,
)
from src.utils.ui import CORES, criar_botao, criar_titulo, criar_treeview
from src.utils.validacao import formatar_moeda, parse_inteiro


class TelaVendas(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CORES["fundo"])
        self.app = app
        self.carrinho = []
        self.clientes = {}
        self.produtos = {}
        self._montar()
        self._carregar_combos()

    def _montar(self):
        criar_titulo(
            self,
            "Nova Venda",
            "Selecione o cliente, adicione os itens e finalize",
        ).pack(anchor="w", padx=28, pady=(24, 14))

        corpo = tk.Frame(self, bg=CORES["fundo"])
        corpo.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        esquerda = tk.Frame(corpo, bg=CORES["fundo"])
        esquerda.pack(side="left", fill="both", expand=True, padx=(0, 14))
        direita = tk.Frame(corpo, bg=CORES["fundo"], width=310)
        direita.pack(side="right", fill="y")
        direita.pack_propagate(False)

        card_topo = tk.Frame(
            esquerda,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_topo.pack(fill="x", pady=(0, 12))
        inner = tk.Frame(card_topo, bg=CORES["branco"])
        inner.pack(fill="x", padx=16, pady=14)
        tk.Label(
            inner,
            text="Cliente",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).grid(row=0, column=0, sticky="w")
        self.combo_cliente = ttk.Combobox(inner, state="readonly", width=40)
        self.combo_cliente.grid(row=1, column=0, sticky="w", padx=(0, 18))
        self.combo_cliente.bind(
            "<<ComboboxSelected>>", lambda e: self._atualizar_resumo()
        )
        tk.Label(
            inner,
            text="Forma de pagamento",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).grid(row=0, column=1, sticky="w")
        self.combo_pagamento = ttk.Combobox(
            inner,
            state="readonly",
            width=18,
            values=list(venda.FORMAS_PAGAMENTO),
        )
        self.combo_pagamento.current(0)
        self.combo_pagamento.grid(row=1, column=1, sticky="w")

        card_produtos = tk.Frame(
            esquerda,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_produtos.pack(fill="both", expand=True)
        inner_produtos = tk.Frame(card_produtos, bg=CORES["branco"])
        inner_produtos.pack(fill="both", expand=True, padx=16, pady=14)
        tk.Label(
            inner_produtos,
            text="Adicionar produto",
            font=("Segoe UI", 11, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(anchor="w", pady=(0, 8))

        linha = tk.Frame(inner_produtos, bg=CORES["branco"])
        linha.pack(fill="x")
        self.combo_produto = ttk.Combobox(linha, state="readonly", width=38)
        self.combo_produto.pack(side="left")
        self.combo_produto.bind(
            "<<ComboboxSelected>>", lambda e: self._atualizar_estoque()
        )
        self.spin_qtd = ttk.Spinbox(linha, from_=1, to=999, width=6)
        self.spin_qtd.set("1")
        self.spin_qtd.pack(side="left", padx=8)
        criar_botao(
            linha, "Adicionar", self._adicionar, "Secondary.TButton", icone="plus"
        ).pack(side="left")

        self.label_estoque = tk.Label(
            inner_produtos,
            text="",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        )
        self.label_estoque.pack(anchor="w", pady=(6, 8))

        container, self.tree_carrinho = criar_treeview(
            inner_produtos,
            [
                ("produto", "Produto", 240, "w"),
                ("quantidade", "Qtd.", 60, "center"),
                ("unitario", "Preço unit.", 110, "e"),
                ("subtotal", "Subtotal", 110, "e"),
            ],
            borda=False,
        )
        container.pack(fill="both", expand=True)
        self.tree_carrinho.bind("<Delete>", lambda e: self._remover())

        rodape = tk.Frame(inner_produtos, bg=CORES["branco"])
        rodape.pack(fill="x", pady=(8, 0))
        criar_botao(
            rodape, "Remover item", self._remover, "Secondary.TButton", icone="trash"
        ).pack(side="left")

        card_resumo = tk.Frame(
            direita,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_resumo.pack(fill="both", expand=True)
        resumo = tk.Frame(card_resumo, bg=CORES["branco"])
        resumo.pack(fill="both", expand=True, padx=18, pady=18)
        tk.Label(
            resumo,
            text="Resumo da venda",
            font=("Segoe UI", 12, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(anchor="w")
        self.label_resumo_cliente = tk.Label(
            resumo,
            text="Cliente: —",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
            wraplength=250,
            justify="left",
        )
        self.label_resumo_cliente.pack(anchor="w", pady=(10, 0))
        self.label_resumo_itens = tk.Label(
            resumo,
            text="Itens: 0",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        )
        self.label_resumo_itens.pack(anchor="w", pady=(4, 0))
        tk.Frame(resumo, bg=CORES["borda"], height=1).pack(fill="x", pady=14)
        caixa_total = tk.Frame(resumo, bg=CORES["indigo_claro"])
        caixa_total.pack(fill="x", pady=(0, 6))
        tk.Label(
            caixa_total,
            text="TOTAL A PAGAR",
            font=("Segoe UI", 8, "bold"),
            bg=CORES["indigo_claro"],
            fg=CORES["azul"],
        ).pack(anchor="w", padx=12, pady=(10, 0))
        self.label_total = tk.Label(
            caixa_total,
            text="R$ 0,00",
            font=("Segoe UI", 24, "bold"),
            bg=CORES["indigo_claro"],
            fg=CORES["azul"],
        )
        self.label_total.pack(anchor="w", padx=12, pady=(0, 10))
        criar_botao(
            resumo, "Finalizar venda", self._finalizar, icone="check_circle"
        ).pack(fill="x", pady=(14, 6))
        criar_botao(
            resumo, "Limpar carrinho", self._limpar, "Secondary.TButton", icone="rotate"
        ).pack(fill="x")

    def _carregar_combos(self):
        self.clientes = {
            f"{registro['id']} - {registro['nome']}": dict(registro)
            for registro in cliente.listar()
        }
        self.combo_cliente.configure(values=list(self.clientes.keys()))

        self.produtos = {
            f"{registro['id']} - {registro['nome']}": dict(registro)
            for registro in produto.listar()
            if registro["estoque"] > 0
        }
        self.combo_produto.configure(values=list(self.produtos.keys()))
        self.combo_produto.set("")
        self._atualizar_estoque()

    def _produto_selecionado(self):
        return self.produtos.get(self.combo_produto.get())

    def _atualizar_estoque(self):
        registro = self._produto_selecionado()
        if registro:
            self.spin_qtd.configure(from_=1, to=max(registro["estoque"], 1))
            self.label_estoque.configure(
                text=(
                    f"Estoque disponível: {registro['estoque']} un. — "
                    f"Preço: {formatar_moeda(registro['preco_venda'])}"
                )
            )
        else:
            self.spin_qtd.configure(from_=1, to=999)
            self.label_estoque.configure(text="")

    def _adicionar(self):
        registro = self._produto_selecionado()
        if not registro:
            notificar_aviso(self, "Selecione um produto para adicionar.", "Produto")
            return
        try:
            quantidade = parse_inteiro(self.spin_qtd.get(), "quantidade")
        except ValueError as erro:
            notificar_erro(self, str(erro), "Quantidade inválida")
            return
        if quantidade < 1:
            notificar_erro(
                self, "A quantidade deve ser maior que zero.", "Quantidade inválida"
            )
            return

        existente = next(
            (
                item
                for item in self.carrinho
                if item["produto_id"] == registro["id"]
            ),
            None,
        )
        quantidade_atual = existente["quantidade"] if existente else 0
        if quantidade_atual + quantidade > registro["estoque"]:
            notificar_erro(
                self,
                f"Disponível: {registro['estoque']} un. "
                f"No carrinho: {quantidade_atual} un.",
                "Estoque insuficiente",
            )
            return

        if existente:
            existente["quantidade"] += quantidade
            existente["subtotal"] = round(
                existente["quantidade"] * existente["preco"], 2
            )
        else:
            self.carrinho.append(
                {
                    "produto_id": registro["id"],
                    "nome": registro["nome"],
                    "preco": registro["preco_venda"],
                    "quantidade": quantidade,
                    "estoque": registro["estoque"],
                    "subtotal": round(registro["preco_venda"] * quantidade, 2),
                }
            )
        self._atualizar_carrinho()

    def _remover(self):
        selecao = self.tree_carrinho.selection()
        if not selecao:
            notificar_aviso(self, "Selecione um item do carrinho.", "Seleção")
            return
        indice = self.tree_carrinho.index(selecao[0])
        if 0 <= indice < len(self.carrinho):
            self.carrinho.pop(indice)
        self._atualizar_carrinho()

    def _limpar(self):
        self.carrinho = []
        self._atualizar_carrinho()

    def _atualizar_carrinho(self):
        for item in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(item)
        total = 0.0
        for item in self.carrinho:
            total += item["subtotal"]
            self.tree_carrinho.insert(
                "",
                "end",
                values=(
                    item["nome"],
                    item["quantidade"],
                    formatar_moeda(item["preco"]),
                    formatar_moeda(item["subtotal"]),
                ),
            )
        total = round(total, 2)
        self.label_total.configure(text=formatar_moeda(total))
        quantidade_itens = sum(item["quantidade"] for item in self.carrinho)
        self.label_resumo_itens.configure(
            text=f"Itens: {quantidade_itens} ({len(self.carrinho)} produto(s))"
        )
        self._atualizar_resumo()

    def _atualizar_resumo(self):
        registro = self.clientes.get(self.combo_cliente.get())
        if registro:
            self.label_resumo_cliente.configure(
                text=f"Cliente: {registro['nome']}"
            )
        else:
            self.label_resumo_cliente.configure(text="Cliente: —")

    def _finalizar(self):
        registro = self.clientes.get(self.combo_cliente.get())
        if not registro:
            notificar_aviso(self, "Selecione o cliente da venda.", "Cliente")
            return
        if not self.carrinho:
            notificar_aviso(
                self, "Adicione pelo menos um item à venda.", "Carrinho vazio"
            )
            return
        itens = [
            {"produto_id": item["produto_id"], "quantidade": item["quantidade"]}
            for item in self.carrinho
        ]
        try:
            venda_id = venda.criar(
                registro["id"],
                Sessao.usuario()["id"],
                self.combo_pagamento.get(),
                itens,
            )
        except ValueError as erro:
            notificar_erro(self, str(erro), "Não foi possível finalizar")
            self._carregar_combos()
            return

        total = sum(item["subtotal"] for item in self.carrinho)
        notificar_sucesso(
            self,
            f"Venda #{venda_id} registrada com sucesso!\nTotal: {formatar_moeda(total)}",
            "Venda Finalizada",
        )
        self.carrinho = []
        self.combo_cliente.set("")
        self._carregar_combos()
        self._atualizar_carrinho()
