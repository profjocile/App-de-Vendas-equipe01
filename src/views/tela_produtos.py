import tkinter as tk
from tkinter import messagebox, ttk

from src.models import produto
from src.utils.notificacao import (
    notificar_aviso,
    notificar_erro,
    notificar_sucesso,
    tocar_som,
)
from src.utils.ui import (
    CORES,
    criar_botao,
    criar_cabecalho,
    criar_titulo,
    criar_treeview,
    posicionar_sobre,
)
from src.utils.validacao import formatar_moeda, parse_inteiro, parse_moeda

COLUNAS = [
    ("id", "ID", 50, "center"),
    ("nome", "Nome", 240, "w"),
    ("categoria", "Categoria", 150, "w"),
    ("custo", "Custo", 110, "e"),
    ("venda", "Venda", 110, "e"),
    ("estoque", "Estoque", 90, "center"),
]


class TelaProdutos(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CORES["fundo"])
        self.app = app
        self._montar()
        self.carregar()

    def _montar(self):
        topo = tk.Frame(self, bg=CORES["fundo"])
        topo.pack(fill="x", padx=28, pady=(24, 14))
        criar_titulo(topo, "Produtos", "Cadastro e controle de estoque").pack(
            side="left"
        )

        barra = tk.Frame(self, bg=CORES["fundo"])
        barra.pack(fill="x", padx=28, pady=(0, 12))
        tk.Label(
            barra,
            text="Buscar:",
            font=("Segoe UI", 9),
            bg=CORES["fundo"],
            fg=CORES["texto_claro"],
        ).pack(side="left", padx=(0, 6))
        self.entry_busca = ttk.Entry(barra, width=32)
        self.entry_busca.pack(side="left")
        self.entry_busca.bind("<KeyRelease>", lambda e: self.carregar())

        criar_botao(barra, "Novo produto", self._novo, icone="plus").pack(
            side="right"
        )
        if self.app.admin:
            criar_botao(
                barra, "Excluir", self._excluir, "Danger.TButton", icone="trash"
            ).pack(side="right", padx=(0, 8))
        criar_botao(
            barra, "Editar", self._editar, "Secondary.TButton", icone="pencil"
        ).pack(side="right", padx=(0, 8))

        container, self.tree = criar_treeview(self, COLUNAS)
        container.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.tree.tag_configure("baixo", foreground=CORES["vermelho"])
        self.tree.bind("<Double-1>", lambda e: self._editar())

    def carregar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for registro in produto.listar(self.entry_busca.get()):
            self.tree.insert(
                "",
                "end",
                iid=str(registro["id"]),
                values=(
                    registro["id"],
                    registro["nome"],
                    registro["categoria"] or "—",
                    formatar_moeda(registro["preco_custo"]),
                    formatar_moeda(registro["preco_venda"]),
                    registro["estoque"],
                ),
                tags=("baixo",) if registro["estoque"] <= 5 else (),
            )

    def _selecionado(self):
        selecao = self.tree.selection()
        if not selecao:
            notificar_aviso(self, "Selecione um produto na lista.", "Seleção")
            return None
        return int(selecao[0])

    def _novo(self):
        FormularioProduto(self, None, self.carregar)

    def _editar(self):
        produto_id = self._selecionado()
        if produto_id:
            FormularioProduto(self, produto.obter(produto_id), self.carregar)

    def _excluir(self):
        produto_id = self._selecionado()
        if not produto_id:
            return
        registro = produto.obter(produto_id)
        if not messagebox.askyesno(
            "Excluir produto",
            f"Deseja excluir '{registro['nome']}'?",
            parent=self,
        ):
            return
        try:
            produto.excluir(produto_id)
        except ValueError as erro:
            notificar_erro(self, str(erro), "Não foi possível excluir")
            return
        self.carregar()
        notificar_sucesso(
            self,
            f"Produto '{registro['nome']}' excluído com sucesso.",
            "Produto excluído",
        )


class FormularioProduto(tk.Toplevel):
    def __init__(self, master, registro, ao_salvar):
        super().__init__(master)
        self.registro = registro
        self.ao_salvar = ao_salvar
        self.title("Editar produto" if registro else "Novo produto")
        self.configure(bg=CORES["branco"])
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self._montar()
        posicionar_sobre(self, master.winfo_toplevel())
        self.grab_set()
        self.entry_nome.focus_set()
        self.wait_window(self)

    def _montar(self):
        corpo = tk.Frame(self, bg=CORES["branco"])
        corpo.pack(padx=26, pady=22, fill="both")

        criar_cabecalho(
            corpo,
            "Editar produto" if self.registro else "Novo produto",
            "Preencha os dados do produto",
        )

        self.entry_nome = self._campo(corpo, "Nome *")
        self.entry_categoria = self._campo(corpo, "Categoria")
        self.entry_custo = self._campo(corpo, "Preço de custo (R$)")
        self.entry_venda = self._campo(corpo, "Preço de venda (R$)")
        self.entry_estoque = self._campo(corpo, "Estoque")

        if self.registro:
            self.entry_nome.insert(0, self.registro["nome"])
            self.entry_categoria.insert(0, self.registro["categoria"] or "")
            self.entry_custo.insert(
                0, f"{self.registro['preco_custo']:.2f}".replace(".", ",")
            )
            self.entry_venda.insert(
                0, f"{self.registro['preco_venda']:.2f}".replace(".", ",")
            )
            self.entry_estoque.insert(0, str(self.registro["estoque"]))

        self.label_erro = tk.Label(
            corpo,
            text="",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["vermelho"],
            wraplength=320,
            justify="left",
        )
        self.label_erro.pack(fill="x", pady=(2, 0))

        botoes = tk.Frame(corpo, bg=CORES["branco"])
        botoes.pack(fill="x", pady=(14, 0))
        criar_botao(botoes, "Salvar", self._salvar, icone="check").pack(
            side="right"
        )
        criar_botao(
            botoes, "Cancelar", self.destroy, "Secondary.TButton", icone="x"
        ).pack(side="right", padx=(0, 8))

    def _campo(self, parent, rotulo):
        tk.Label(
            parent,
            text=rotulo,
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w")
        entry = ttk.Entry(parent, width=38)
        entry.pack(fill="x", pady=(3, 10))
        return entry

    def _salvar(self):
        try:
            nome = self.entry_nome.get().strip()
            if not nome:
                raise ValueError("O nome do produto é obrigatório.")
            preco_custo = parse_moeda(self.entry_custo.get() or "0")
            preco_venda = parse_moeda(self.entry_venda.get() or "0")
            estoque = parse_inteiro(self.entry_estoque.get() or "0", "estoque")
            if preco_custo < 0 or preco_venda < 0:
                raise ValueError("Os preços não podem ser negativos.")
            if estoque < 0:
                raise ValueError("O estoque não pode ser negativo.")
            categoria = self.entry_categoria.get().strip()
            if self.registro:
                produto.atualizar(
                    self.registro["id"],
                    nome,
                    categoria,
                    preco_custo,
                    preco_venda,
                    estoque,
                )
            else:
                produto.criar(nome, categoria, preco_custo, preco_venda, estoque)
        except ValueError as erro:
            tocar_som("erro")
            self.label_erro.configure(text=f"• {erro}")
            return
        self.ao_salvar()
        notificar_sucesso(
            self.master,
            f"Produto '{nome}' salvo com sucesso!",
            "Produto salvo",
        )
        self.destroy()
