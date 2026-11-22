import os
import shutil
import subprocess
import tkinter as tk
import webbrowser
from datetime import date
from tkinter import filedialog, ttk

from src.database import BASE_DIR
from src.models import relatorio
from src.utils.icones import desenhar_icone
from src.utils.notificacao import (
    notificar_aviso,
    notificar_erro,
    notificar_sucesso,
)
from src.utils.ui import CORES, criar_botao, criar_titulo, criar_treeview
from src.utils.validacao import formatar_moeda, parse_data

EXCEL_ONLINE_URL = "https://www.office.com/launch/excel"


def _localizar_excel():
    if os.name != "nt":
        return None

    try:
        import winreg
    except ImportError:
        winreg = None

    if winreg:
        chaves = (
            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\App Paths\excel.exe",
            ),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows\CurrentVersion\App Paths\excel.exe",
            ),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\excel.exe",
            ),
        )
        for raiz, chave in chaves:
            try:
                with winreg.OpenKey(raiz, chave) as registro:
                    caminho, _ = winreg.QueryValueEx(registro, "")
            except OSError:
                continue
            caminho = str(caminho).strip().strip('"')
            if os.path.isfile(caminho):
                return caminho

    encontrado = shutil.which("excel") or shutil.which("EXCEL.EXE")
    if encontrado:
        return encontrado

    programas = (
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
    )
    versoes = (
        r"root\Office16",
        r"root\Office15",
        r"root\Office14",
        "Office16",
        "Office15",
        "Office14",
    )
    for base in programas:
        for versao in versoes:
            caminho = os.path.join(base, "Microsoft Office", versao, "EXCEL.EXE")
            if os.path.isfile(caminho):
                return caminho
    return None


def _abrir_no_excel_instalado(caminho):
    excel = _localizar_excel()
    if not excel:
        return False
    try:
        subprocess.Popen([excel, caminho])
        return True
    except OSError:
        return False


class TelaRelatorios(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=CORES["fundo"])
        self.app = app
        self._montar()
        self.gerar()

    def _montar(self):
        topo = tk.Frame(self, bg=CORES["fundo"])
        topo.pack(fill="x", padx=28, pady=(24, 14))
        criar_titulo(
            topo,
            "Relatórios",
            "Analise as vendas por período e exporte os dados",
        ).pack(side="left")

        card_filtros = tk.Frame(
            self,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_filtros.pack(fill="x", padx=28, pady=(0, 14))
        filtros = tk.Frame(card_filtros, bg=CORES["branco"])
        filtros.pack(fill="x", padx=16, pady=(12, 6))

        tk.Label(
            filtros,
            text="De:",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(side="left", padx=(0, 4))
        self.entry_ini = ttk.Entry(filtros, width=13)
        self.entry_ini.pack(side="left")
        tk.Label(
            filtros,
            text="Até:",
            font=("Segoe UI", 9),
            bg=CORES["branco"],
            fg=CORES["texto_claro"],
        ).pack(side="left", padx=(10, 4))
        self.entry_fim = ttk.Entry(filtros, width=13)
        self.entry_fim.pack(side="left")

        hoje = date.today()
        self.entry_ini.insert(0, date(hoje.year, hoje.month, 1).strftime("%d/%m/%Y"))
        self.entry_fim.insert(0, hoje.strftime("%d/%m/%Y"))

        criar_botao(filtros, "Gerar", self.gerar, icone="refresh").pack(
            side="left", padx=(12, 0)
        )

        acoes = tk.Frame(card_filtros, bg=CORES["branco"])
        acoes.pack(fill="x", padx=16, pady=(0, 12))
        criar_botao(
            acoes,
            "Exportar Excel",
            self._exportar_excel,
            "Secondary.TButton",
            icone="download",
        ).pack(side="left")
        criar_botao(
            acoes,
            "Exportar CSV",
            self._exportar,
            "Secondary.TButton",
            icone="download",
        ).pack(side="left", padx=(8, 0))
        criar_botao(
            acoes,
            "Abrir no Excel",
            self._abrir_no_excel,
            "Secondary.TButton",
            icone="eye",
        ).pack(side="left", padx=(8, 0))

        area_cards = tk.Frame(self, bg=CORES["fundo"])
        area_cards.pack(fill="x", padx=28)
        self.cards = {}
        definicoes = [
            ("total", "Total vendido", CORES["azul"], "banknote"),
            ("quantidade", "Vendas no período", CORES["ciano"], "cart"),
            ("ticket", "Ticket médio", CORES["verde"], "trending_up"),
        ]
        for indice, (chave, titulo, cor, icone_nome) in enumerate(definicoes):
            card = tk.Frame(
                area_cards,
                bg=CORES["branco"],
                highlightthickness=1,
                highlightbackground=CORES["borda"],
            )
            card.grid(
                row=0,
                column=indice,
                sticky="nsew",
                padx=(0 if indice == 0 else 12, 0),
            )
            area_cards.columnconfigure(indice, weight=1)
            tk.Frame(card, bg=cor, height=4).pack(fill="x")
            topo_card = tk.Frame(card, bg=CORES["branco"])
            topo_card.pack(fill="x", padx=16, pady=(10, 0))
            tk.Label(
                topo_card,
                text=titulo,
                font=("Segoe UI", 9),
                bg=CORES["branco"],
                fg=CORES["texto_claro"],
            ).pack(side="left", pady=(3, 0))
            icone = tk.Canvas(
                topo_card,
                width=22,
                height=22,
                bg=CORES["branco"],
                highlightthickness=0,
            )
            icone.pack(side="right")
            desenhar_icone(icone, icone_nome, 1, 1, 20, cor, largura=2.0)
            valor = tk.Label(
                card,
                text="—",
                font=("Segoe UI", 20, "bold"),
                bg=CORES["branco"],
                fg=cor,
            )
            valor.pack(anchor="w", padx=16, pady=(0, 14))
            self.cards[chave] = valor

        corpo = tk.Frame(self, bg=CORES["fundo"])
        corpo.pack(fill="both", expand=True, padx=28, pady=(14, 20))
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=2)
        corpo.rowconfigure(0, weight=1)

        card_top = tk.Frame(
            corpo,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_top.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tk.Label(
            card_top,
            text="Produtos mais vendidos",
            font=("Segoe UI", 11, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(anchor="w", padx=16, pady=(14, 8))
        container_top, self.tree_produtos = criar_treeview(
            card_top,
            [
                ("produto", "Produto", 220, "w"),
                ("quantidade", "Qtd. vendida", 110, "center"),
                ("total", "Total", 110, "e"),
            ],
            borda=False,
        )
        container_top.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        card_formas = tk.Frame(
            corpo,
            bg=CORES["branco"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card_formas.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            card_formas,
            text="Vendas por forma de pagamento",
            font=("Segoe UI", 11, "bold"),
            bg=CORES["branco"],
            fg=CORES["texto"],
        ).pack(anchor="w", padx=16, pady=(14, 8))
        container_formas, self.tree_formas = criar_treeview(
            card_formas,
            [
                ("forma", "Forma", 120, "w"),
                ("quantidade", "Qtd.", 60, "center"),
                ("total", "Total", 110, "e"),
            ],
            borda=False,
        )
        container_formas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _periodo(self):
        data_ini = parse_data(self.entry_ini.get()).isoformat()
        data_fim = parse_data(self.entry_fim.get()).isoformat()
        if data_ini > data_fim:
            raise ValueError("A data inicial não pode ser maior que a final.")
        return data_ini, data_fim

    def gerar(self):
        try:
            data_ini, data_fim = self._periodo()
        except ValueError as erro:
            notificar_erro(self, str(erro), "Período inválido")
            return

        resumo = relatorio.resumo(data_ini, data_fim)
        self.cards["total"].configure(text=formatar_moeda(resumo["total"]))
        self.cards["quantidade"].configure(text=str(resumo["quantidade"]))
        self.cards["ticket"].configure(text=formatar_moeda(resumo["ticket_medio"]))

        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        for registro in relatorio.top_produtos(data_ini, data_fim):
            self.tree_produtos.insert(
                "",
                "end",
                values=(
                    registro["nome"],
                    registro["quantidade"],
                    formatar_moeda(registro["total"]),
                ),
            )

        for item in self.tree_formas.get_children():
            self.tree_formas.delete(item)
        for registro in relatorio.por_forma_pagamento(data_ini, data_fim):
            self.tree_formas.insert(
                "",
                "end",
                values=(
                    registro["forma_pagamento"],
                    registro["quantidade"],
                    formatar_moeda(registro["total"]),
                ),
            )

    def _exportar(self):
        try:
            data_ini, data_fim = self._periodo()
        except ValueError as erro:
            notificar_erro(self, str(erro), "Período inválido")
            return

        pasta_exports = os.path.join(BASE_DIR, "exports")
        os.makedirs(pasta_exports, exist_ok=True)
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar relatório",
            initialdir=pasta_exports,
            initialfile=f"relatorio_vendas_{data_ini}_{data_fim}.csv",
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
        )
        if not caminho:
            return
        try:
            total = relatorio.exportar_csv(caminho, data_ini, data_fim)
        except OSError as erro:
            notificar_erro(
                self, f"Não foi possível salvar o arquivo:\n{erro}", "Erro ao exportar"
            )
            return
        notificar_sucesso(
            self,
            f"{total} venda(s) exportada(s) para:\n{caminho}",
            "Relatório exportado",
        )

    def _exportar_excel(self):
        try:
            data_ini, data_fim = self._periodo()
        except ValueError as erro:
            notificar_erro(self, str(erro), "Período inválido")
            return

        pasta_exports = os.path.join(BASE_DIR, "exports")
        os.makedirs(pasta_exports, exist_ok=True)
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar relatório em Excel",
            initialdir=pasta_exports,
            initialfile=f"relatorio_vendas_{data_ini}_{data_fim}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Planilha do Excel", "*.xlsx")],
        )
        if not caminho:
            return
        try:
            total = relatorio.exportar_excel(caminho, data_ini, data_fim)
        except OSError as erro:
            notificar_erro(
                self, f"Não foi possível salvar o arquivo:\n{erro}", "Erro ao exportar"
            )
            return
        notificar_sucesso(
            self,
            f"{total} venda(s) exportada(s) para:\n{caminho}",
            "Planilha exportada",
        )

    def _abrir_no_excel(self):
        try:
            data_ini, data_fim = self._periodo()
        except ValueError as erro:
            notificar_erro(self, str(erro), "Período inválido")
            return

        pasta_exports = os.path.join(BASE_DIR, "exports")
        os.makedirs(pasta_exports, exist_ok=True)
        caminho = os.path.join(
            pasta_exports, f"relatorio_vendas_{data_ini}_{data_fim}.xlsx"
        )
        try:
            total = relatorio.exportar_excel(caminho, data_ini, data_fim)
        except OSError as erro:
            notificar_erro(
                self,
                f"Não foi possível gerar o arquivo:\n{erro}",
                "Erro ao abrir no Excel",
            )
            return

        if _abrir_no_excel_instalado(caminho):
            notificar_sucesso(
                self,
                f"{total} venda(s) exportada(s) para:\n{caminho}",
                "Abrindo no Excel",
            )
            return

        try:
            webbrowser.open(EXCEL_ONLINE_URL)
        except Exception:
            pass
        notificar_aviso(
            self,
            f"O arquivo foi gerado em:\n{caminho}\n"
            "No Excel Online, use 'Abrir' > 'Este dispositivo' para selecioná-lo.",
            "Excel Online",
        )
