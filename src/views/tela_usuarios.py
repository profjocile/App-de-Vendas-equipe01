import tkinter as tk
from tkinter import messagebox, ttk

from src.models import usuario
from src.sessao import Sessao
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
from src.utils.validacao import somente_digitos

PERFIS_EXIBICAO = {"admin": "Administrador", "vendedor": "Vendedor"}
PERFIS_VALORES = {"Administrador": "admin", "Vendedor": "vendedor"}

COLUNAS = [
    ("id", "ID", 50, "center"),
    ("nome", "Nome", 220, "w"),
    ("login", "Login", 140, "w"),
    ("perfil", "Perfil", 120, "center"),
    ("status", "Status", 90, "center"),
]


class TelaUsuarios(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CORES["fundo"])
        self.app = app
        self._montar()
        self.carregar()

    def _montar(self):
        topo = tk.Frame(self, bg=CORES["fundo"])
        topo.pack(fill="x", padx=28, pady=(24, 14))
        criar_titulo(
            topo, "Usuários", "Gestão de acessos e permissões"
        ).pack(side="left")

        barra = tk.Frame(self, bg=CORES["fundo"])
        barra.pack(fill="x", padx=28, pady=(0, 12))
        criar_botao(barra, "Novo usuário", self._novo, icone="plus").pack(
            side="right"
        )
        criar_botao(
            barra,
            "Redefinir senha",
            self._redefinir_senha,
            "Secondary.TButton",
            icone="lock",
        ).pack(side="right", padx=(0, 8))
        criar_botao(
            barra,
            "Ativar/Desativar",
            self._alternar,
            "Secondary.TButton",
            icone="power",
        ).pack(side="right", padx=(0, 8))
        criar_botao(
            barra, "Editar", self._editar, "Secondary.TButton", icone="pencil"
        ).pack(side="right", padx=(0, 8))

        container, self.tree = criar_treeview(self, COLUNAS)
        container.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.tree.tag_configure("inativo", foreground=CORES["texto_claro"])
        self.tree.bind("<Double-1>", lambda e: self._editar())

    def carregar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for registro in usuario.listar():
            self.tree.insert(
                "",
                "end",
                iid=str(registro["id"]),
                values=(
                    registro["id"],
                    registro["nome"],
                    registro["login"],
                    PERFIS_EXIBICAO.get(registro["perfil"], registro["perfil"]),
                    "Ativo" if registro["ativo"] else "Inativo",
                ),
                tags=() if registro["ativo"] else ("inativo",),
            )

    def _selecionado(self):
        selecao = self.tree.selection()
        if not selecao:
            notificar_aviso(self, "Selecione um usuário na lista.", "Seleção")
            return None
        return int(selecao[0])

    def _novo(self):
        FormularioUsuario(self, None, self.carregar)

    def _editar(self):
        usuario_id = self._selecionado()
        if usuario_id:
            FormularioUsuario(self, usuario.obter(usuario_id), self.carregar)

    def _redefinir_senha(self):
        usuario_id = self._selecionado()
        if usuario_id:
            RedefinirSenha(self, usuario_id)

    def _alternar(self):
        usuario_id = self._selecionado()
        if not usuario_id:
            return
        registro = usuario.obter(usuario_id)
        acao = "desativar" if registro["ativo"] else "ativar"
        if not messagebox.askyesno(
            "Confirmar",
            f"Deseja {acao} o usuário '{registro['nome']}'?",
            parent=self,
        ):
            return
        try:
            usuario.alternar_ativo(usuario_id, Sessao.usuario()["id"])
        except ValueError as erro:
            notificar_erro(self, str(erro), "Não foi possível alterar")
            return
        self.carregar()
        notificar_sucesso(
            self,
            f"Usuário '{registro['nome']}' {acao}do com sucesso.",
            "Status atualizado",
        )


class FormularioUsuario(tk.Toplevel):
    def __init__(self, master, registro, ao_salvar):
        super().__init__(master)
        self.registro = registro
        self.ao_salvar = ao_salvar
        self.title("Editar usuário" if registro else "Novo usuário")
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
            "Editar usuário" if self.registro else "Novo usuário",
            "Defina os dados de acesso",
        )

        self.entry_nome = self._campo(corpo, "Nome *")
        self.entry_login = self._campo(corpo, "Login *")
        if not self.registro:
            self.entry_senha = self._campo(corpo, "Senha * (mínimo 6 caracteres)", show="•")
        else:
            self.entry_senha = None

        tk.Label(
            corpo,
            text="Perfil",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w")
        self.combo_perfil = ttk.Combobox(
            corpo,
            state="readonly",
            width=36,
            values=list(PERFIS_VALORES.keys()),
        )
        self.combo_perfil.pack(fill="x", pady=(3, 10))

        if self.registro:
            self.entry_nome.insert(0, self.registro["nome"])
            self.entry_login.insert(0, self.registro["login"])
            self.combo_perfil.set(
                PERFIS_EXIBICAO.get(self.registro["perfil"], "Vendedor")
            )
            if self.registro["id"] == Sessao.usuario()["id"]:
                self.combo_perfil.configure(state="disabled")
        else:
            self.combo_perfil.current(1)

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

    def _campo(self, parent, rotulo, show=None):
        tk.Label(
            parent,
            text=rotulo,
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w")
        entry = ttk.Entry(parent, width=38, show=show) if show else ttk.Entry(
            parent, width=38
        )
        entry.pack(fill="x", pady=(3, 10))
        return entry

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        try:
            perfil = PERFIS_VALORES.get(self.combo_perfil.get())
            if not perfil:
                raise ValueError("Selecione um perfil.")
            if self.registro:
                usuario.atualizar(
                    self.registro["id"],
                    nome,
                    self.entry_login.get(),
                    perfil,
                )
            else:
                usuario.criar(
                    nome,
                    self.entry_login.get(),
                    self.entry_senha.get(),
                    perfil,
                )
        except ValueError as erro:
            tocar_som("erro")
            self.label_erro.configure(text=f"• {erro}")
            return
        self.ao_salvar()
        notificar_sucesso(
            self.master,
            f"Usuário '{nome}' salvo com sucesso!",
            "Usuário salvo",
        )
        self.destroy()


class RedefinirSenha(tk.Toplevel):
    def __init__(self, master, usuario_id):
        super().__init__(master)
        self.usuario_id = usuario_id
        self.title("Redefinir senha")
        self.configure(bg=CORES["branco"])
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self._montar()
        posicionar_sobre(self, master.winfo_toplevel())
        self.grab_set()
        self.entry_senha.focus_set()
        self.wait_window(self)

    def _montar(self):
        corpo = tk.Frame(self, bg=CORES["branco"])
        corpo.pack(padx=26, pady=22, fill="both")

        criar_cabecalho(
            corpo,
            "Redefinir senha",
            "Defina uma nova senha de acesso",
        )

        tk.Label(
            corpo,
            text="Nova senha (mínimo 6 caracteres)",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w")
        self.entry_senha = ttk.Entry(corpo, width=34, show="•")
        self.entry_senha.pack(fill="x", pady=(3, 10))

        tk.Label(
            corpo,
            text="Confirmar nova senha",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(anchor="w")
        self.entry_confirmar = ttk.Entry(corpo, width=34, show="•")
        self.entry_confirmar.pack(fill="x", pady=(3, 10))

        self.label_erro = tk.Label(
            corpo,
            text="",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["vermelho"],
            wraplength=300,
            justify="left",
        )
        self.label_erro.pack(fill="x", pady=(2, 0))

        botoes = tk.Frame(corpo, bg=CORES["branco"])
        botoes.pack(fill="x", pady=(12, 0))
        criar_botao(botoes, "Salvar", self._salvar, icone="check").pack(
            side="right"
        )
        criar_botao(
            botoes, "Cancelar", self.destroy, "Secondary.TButton", icone="x"
        ).pack(side="right", padx=(0, 8))

    def _salvar(self):
        senha = self.entry_senha.get()
        confirmacao = self.entry_confirmar.get()
        if senha != confirmacao:
            tocar_som("erro")
            self.label_erro.configure(text="• A confirmação de senha não confere.")
            return
        try:
            usuario.redefinir_senha(self.usuario_id, senha)
        except ValueError as erro:
            tocar_som("erro")
            self.label_erro.configure(text=f"• {erro}")
            return
        notificar_sucesso(
            self.master, "A senha foi redefinida com sucesso.", "Senha atualizada"
        )
        self.destroy()
