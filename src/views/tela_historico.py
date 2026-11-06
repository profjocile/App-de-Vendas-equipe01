import tkinter as tk
from tkinter import messagebox, ttk

from src.models import venda
from src.utils.notificacao import (
    notificar_aviso,
    notificar_erro,
    notificar_sucesso,
)
from src.utils.ui import (
    CORES,
    criar_botao,
    criar_titulo,
    criar_treeview,
    posicionar_sobre,
)
from src.utils.validacao import (
    formatar_cpf,
    formatar_data_hora,
    formatar_moeda,
    parse_data,
)

COLUNAS = [
    ("id", "ID", 50, "center"),
    ("data", "Data", 130, "center"),
    ("cliente", "Cliente", 170, "w"),
    ("vendedor", "Vendedor", 130, "w"),
    ("pagamento", "Pagamento", 100, "center"),
    ("total", "Total", 100, "e"),
    ("status", "Status", 90, "center"),
]


class TelaHistorico(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CORES["fundo"])
        self.app = app
        self._montar()
        self.carregar()

    def _montar(self):
        topo = tk.Frame(self, bg=CORES["fundo"])
        topo.pack(fill="x", padx=28, pady=(24, 14))
        criar_titulo(
            topo, "Histórico de Vendas", "Consulte, detalhe e cancele vendas"
        ).pack(side="left")

        filtros = tk.Frame(self, bg=CORES["fundo"])
        filtros.pack(fill="x", padx=28, pady=(0, 12))
        tk.Label(
            filtros,
            text="De:",
            font=("Segoe UI", 9),
            bg=CORES["fundo"],
            fg=CORES["texto_claro"],
        ).pack(side="left", padx=(0, 4))
        self.entry_ini = ttk.Entry(filtros, width=13)
        self.entry_ini.pack(side="left")
        tk.Label(
            filtros,
            text="Até:",
            font=("Segoe UI", 9),
            bg=CORES["fundo"],
            fg=CORES["texto_claro"],
        ).pack(side="left", padx=(10, 4))
        self.entry_fim = ttk.Entry(filtros, width=13)
        self.entry_fim.pack(side="left")
        tk.Label(
            filtros,
            text="Status:",
            font=("Segoe UI", 9),
            bg=CORES["fundo"],
            fg=CORES["texto_claro"],
        ).pack(side="left", padx=(10, 4))
        self.combo_status = ttk.Combobox(
            filtros,
            state="readonly",
            width=12,
            values=["Todas", "Concluída", "Cancelada"],
        )
        self.combo_status.current(0)
        self.combo_status.pack(side="left")
        criar_botao(
            filtros, "Filtrar", self.carregar, "Secondary.TButton", icone="filter"
        ).pack(side="left", padx=(10, 0))

        criar_botao(
            filtros, "Ver detalhes", self._detalhes, icone="eye"
        ).pack(side="right")
        if self.app.admin:
            criar_botao(
                filtros,
                "Cancelar venda",
                self._cancelar,
                "Danger.TButton",
                icone="x_circle",
            ).pack(side="right", padx=(0, 8))

        container, self.tree = criar_treeview(self, COLUNAS)
        container.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.tree.tag_configure("cancelada", foreground=CORES["texto_claro"])
        self.tree.bind("<Double-1>", lambda e: self._detalhes())

    def _filtros(self):
        data_ini = None
        data_fim = None
        if self.entry_ini.get().strip():
            data_ini = parse_data(self.entry_ini.get()).isoformat()
        if self.entry_fim.get().strip():
            data_fim = parse_data(self.entry_fim.get()).isoformat()
        if data_ini and data_fim and data_ini > data_fim:
            raise ValueError("A data inicial não pode ser maior que a final.")
        status = {
            "Todas": None,
            "Concluída": "concluida",
            "Cancelada": "cancelada",
        }[self.combo_status.get()]
        return data_ini, data_fim, status

    def carregar(self):
        try:
            data_ini, data_fim, status = self._filtros()
        except ValueError as erro:
            notificar_erro(self, str(erro), "Filtro inválido")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for registro in venda.listar(data_ini, data_fim, status):
            status_texto = (
                "Concluída" if registro["status"] == "concluida" else "Cancelada"
            )
            self.tree.insert(
                "",
                "end",
                iid=str(registro["id"]),
                values=(
                    registro["id"],
                    formatar_data_hora(registro["data_venda"]),
                    registro["cliente_nome"],
                    registro["vendedor_nome"],
                    registro["forma_pagamento"],
                    formatar_moeda(registro["total"]),
                    status_texto,
                ),
                tags=(registro["status"],),
            )

    def _selecionado(self):
        selecao = self.tree.selection()
        if not selecao:
            notificar_aviso(self, "Selecione uma venda na lista.", "Seleção")
            return None
        return int(selecao[0])

    def _detalhes(self):
        venda_id = self._selecionado()
        if venda_id:
            DetalhesVenda(self, venda_id)

    def _cancelar(self):
        venda_id = self._selecionado()
        if not venda_id:
            return
        if not messagebox.askyesno(
            "Cancelar venda",
            f"Deseja cancelar a venda #{venda_id}?\n"
            "Os itens voltarão para o estoque.",
            parent=self,
        ):
            return
        try:
            venda.cancelar(venda_id)
        except ValueError as erro:
            notificar_erro(self, str(erro), "Não foi possível cancelar")
            return
        self.carregar()
        notificar_sucesso(
            self,
            f"A venda #{venda_id} foi cancelada e o estoque foi devolvido.",
            "Venda cancelada",
        )


class DetalhesVenda(tk.Toplevel):
    def __init__(self, master, venda_id):
        super().__init__(master)
        self.venda_id = venda_id
        self.title(f"Detalhes da venda #{venda_id}")
        self.configure(bg=CORES["branco"])
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self._montar()
        posicionar_sobre(self, master.winfo_toplevel())
        self.grab_set()
        self.wait_window(self)

    def _montar(self):
        venda_registro, itens = venda.detalhes(self.venda_id)
        corpo = tk.Frame(self, bg=CORES["branco"])
        corpo.pack(padx=28, pady=20, fill="both")

        if not venda_registro:
            tk.Label(
                corpo,
                text="Venda não encontrada.",
                bg=CORES["branco"],
                fg=CORES["vermelho"],
            ).pack()
            return

        tk.Label(
            corpo,
            text=f"Venda #{venda_registro['id']}",
            font=("Segoe UI", 15, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(anchor="w")
        status = (
            "Concluída"
            if venda_registro["status"] == "concluida"
            else "Cancelada"
        )
        tk.Label(
            corpo,
            text=(
                f"Cliente: {venda_registro['cliente_nome']}  •  "
                f"CPF: {formatar_cpf(venda_registro['cliente_cpf'])}\n"
                f"Data: {formatar_data_hora(venda_registro['data_venda'])}  •  "
                f"Vendedor: {venda_registro['vendedor_nome']}\n"
                f"Pagamento: {venda_registro['forma_pagamento']}  •  "
                f"Status: {status}"
            ),
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
            justify="left",
        ).pack(anchor="w", pady=(6, 14))

        container, self.tree = criar_treeview(
            corpo,
            [
                ("produto", "Produto", 220, "w"),
                ("quantidade", "Qtd.", 60, "center"),
                ("unitario", "Preço unit.", 110, "e"),
                ("subtotal", "Subtotal", 110, "e"),
            ],
        )
        container.pack(fill="both", expand=True)
        for item in itens:
            self.tree.insert(
                "",
                "end",
                values=(
                    item["produto_nome"],
                    item["quantidade"],
                    formatar_moeda(item["preco_unitario"]),
                    formatar_moeda(item["subtotal"]),
                ),
            )

        rodape = tk.Frame(corpo, bg=CORES["branco"])
        rodape.pack(fill="x", pady=(14, 0))
        tk.Label(
            rodape,
            text=f"Total: {formatar_moeda(venda_registro['total'])}",
            font=("Segoe UI", 14, "bold"),
            bg=CORES["branco"],
            fg=CORES["azul"],
        ).pack(side="left")
        criar_botao(
            rodape, "Fechar", self.destroy, "Secondary.TButton", icone="x"
        ).pack(side="right")
