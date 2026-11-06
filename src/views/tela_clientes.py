import tkinter as tk
from tkinter import messagebox, ttk

from src.models import cliente
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
from src.utils.validacao import formatar_cpf, formatar_telefone

COLUNAS = [
    ("id", "ID", 50, "center"),
    ("nome", "Nome", 200, "w"),
    ("cpf", "CPF", 130, "center"),
    ("telefone", "Telefone", 130, "center"),
    ("email", "E-mail", 180, "w"),
    ("cidade", "Cidade", 140, "w"),
]


class TelaClientes(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CORES["fundo"])
        self.app = app
        self._montar()
        self.carregar()

    def _montar(self):
        topo = tk.Frame(self, bg=CORES["fundo"])
        topo.pack(fill="x", padx=28, pady=(24, 14))
        criar_titulo(topo, "Clientes", "Cadastro de clientes").pack(side="left")

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

        criar_botao(barra, "Novo cliente", self._novo, icone="plus").pack(
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
        self.tree.bind("<Double-1>", lambda e: self._editar())

    def carregar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for registro in cliente.listar(self.entry_busca.get()):
            self.tree.insert(
                "",
                "end",
                iid=str(registro["id"]),
                values=(
                    registro["id"],
                    registro["nome"],
                    formatar_cpf(registro["cpf"]),
                    formatar_telefone(registro["telefone"]) or "—",
                    registro["email"] or "—",
                    registro["cidade"] or "—",
                ),
            )

    def _selecionado(self):
        selecao = self.tree.selection()
        if not selecao:
            notificar_aviso(self, "Selecione um cliente na lista.", "Seleção")
            return None
        return int(selecao[0])

    def _novo(self):
        FormularioCliente(self, None, self.carregar)

    def _editar(self):
        cliente_id = self._selecionado()
        if cliente_id:
            FormularioCliente(self, cliente.obter(cliente_id), self.carregar)

    def _excluir(self):
        cliente_id = self._selecionado()
        if not cliente_id:
            return
        registro = cliente.obter(cliente_id)
        if not messagebox.askyesno(
            "Excluir cliente",
            f"Deseja excluir '{registro['nome']}'?",
            parent=self,
        ):
            return
        try:
            cliente.excluir(cliente_id)
        except ValueError as erro:
            notificar_erro(self, str(erro), "Não foi possível excluir")
            return
        self.carregar()
        notificar_sucesso(
            self,
            f"Cliente '{registro['nome']}' excluído com sucesso.",
            "Cliente excluído",
        )


class FormularioCliente(tk.Toplevel):
    def __init__(self, master, registro, ao_salvar):
        super().__init__(master)
        self.registro = registro
        self.ao_salvar = ao_salvar
        self.title("Editar cliente" if registro else "Novo cliente")
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
            "Editar cliente" if self.registro else "Novo cliente",
            "Preencha os dados do cliente",
        )

        self.entry_nome = self._campo(corpo, "Nome *")
        self.entry_cpf = self._campo(corpo, "CPF *")
        self.entry_telefone = self._campo(corpo, "Telefone (DDD + número)")
        self.entry_email = self._campo(corpo, "E-mail")
        self.entry_cidade = self._campo(corpo, "Cidade")

        if self.registro:
            self.entry_nome.insert(0, self.registro["nome"])
            self.entry_cpf.insert(0, formatar_cpf(self.registro["cpf"]))
            self.entry_telefone.insert(
                0, formatar_telefone(self.registro["telefone"] or "")
            )
            self.entry_email.insert(0, self.registro["email"] or "")
            self.entry_cidade.insert(0, self.registro["cidade"] or "")

        self.entry_cpf.bind("<FocusOut>", self._formatar_cpf_campo)
        self.entry_telefone.bind("<FocusOut>", self._formatar_telefone_campo)

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

    def _formatar_cpf_campo(self, evento=None):
        texto = self.entry_cpf.get().strip()
        if texto:
            self.entry_cpf.delete(0, "end")
            self.entry_cpf.insert(0, formatar_cpf(texto))

    def _formatar_telefone_campo(self, evento=None):
        texto = self.entry_telefone.get().strip()
        if texto:
            self.entry_telefone.delete(0, "end")
            self.entry_telefone.insert(0, formatar_telefone(texto))

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        try:
            if self.registro:
                cliente.atualizar(
                    self.registro["id"],
                    self.entry_nome.get(),
                    self.entry_cpf.get(),
                    self.entry_telefone.get(),
                    self.entry_email.get(),
                    self.entry_cidade.get(),
                )
            else:
                cliente.criar(
                    self.entry_nome.get(),
                    self.entry_cpf.get(),
                    self.entry_telefone.get(),
                    self.entry_email.get(),
                    self.entry_cidade.get(),
                )
        except ValueError as erro:
            tocar_som("erro")
            self.label_erro.configure(text=f"• {erro}")
            return
        self.ao_salvar()
        notificar_sucesso(
            self.master,
            f"Cliente '{nome}' salvo com sucesso!",
            "Cliente salvo",
        )
        self.destroy()
