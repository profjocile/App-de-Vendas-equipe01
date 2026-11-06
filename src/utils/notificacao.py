import io
import math
import struct
import threading
import tkinter as tk
import wave

from src.utils.ui import CORES, tema_atual


def _gerar_wav(frequencias, duracao=0.22, volume=2600):
    taxa = 22050
    num_amostras = int(taxa * duracao)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(taxa)
        amostras = []
        n_seg = len(frequencias)
        amostras_por_seg = max(1, num_amostras // n_seg)
        for s, freq in enumerate(frequencias):
            for i in range(amostras_por_seg):
                t_global = (s * amostras_por_seg + i) / taxa
                t_seg = i / taxa
                env = min(1.0, t_seg / 0.012) * math.exp(-t_seg * 13)
                val = int(
                    env * math.sin(2 * math.pi * freq * t_global) * volume
                )
                amostras.append(
                    struct.pack("<h", max(-32767, min(32767, val)))
                )
        wf.writeframes(b"".join(amostras))
    return buf.getvalue()


_SOM_SUCESSO = _gerar_wav([659, 880], duracao=0.22, volume=2600)
_SOM_AVISO = _gerar_wav([587, 740], duracao=0.20, volume=2400)
_SOM_ERRO = _gerar_wav([440, 370], duracao=0.20, volume=2300)


def tocar_som(tipo="info"):
    try:
        import winsound

        if tipo in ("erro", "danger", "error"):
            som = _SOM_ERRO
        elif tipo in ("aviso", "warning"):
            som = _SOM_AVISO
        else:
            som = _SOM_SUCESSO

        threading.Thread(
            target=lambda: winsound.PlaySound(som, winsound.SND_MEMORY),
            daemon=True,
        ).start()
    except Exception:
        pass


CONFIG_TIPOS = {
    "sucesso": {
        "cor": "#10B981",
        "titulo_padrao": "Sucesso",
        "simbolo": "✓",
    },
    "erro": {
        "cor": "#EF4444",
        "titulo_padrao": "Atenção",
        "simbolo": "✕",
    },
    "aviso": {
        "cor": "#F59E0B",
        "titulo_padrao": "Aviso",
        "simbolo": "!",
    },
    "info": {
        "cor": "#4F46E5",
        "titulo_padrao": "Informação",
        "simbolo": "ℹ",
    },
}


class NotificacaoToast(tk.Frame):
    def __init__(self, top, mensagem, tipo="info", titulo=None, duracao_ms=3800):
        self.top = top
        self.duracao_ms = duracao_ms
        self._timer_id = None

        cfg = CONFIG_TIPOS.get(tipo, CONFIG_TIPOS["info"])
        self.cor_accent = cfg["cor"]
        self.titulo = titulo or cfg["titulo_padrao"]
        self.mensagem = str(mensagem).strip()

        escuro = tema_atual() == "escuro"
        fundo_card = "#1E293B" if escuro else "#FFFFFF"
        borda_card = "#334155" if escuro else "#E2E8F0"
        cor_titulo = "#F8FAFC" if escuro else "#0F172A"
        cor_msg = "#CBD5E1" if escuro else "#64748B"

        super().__init__(
            top,
            bg=fundo_card,
            highlightthickness=1,
            highlightbackground=borda_card,
            cursor="hand2",
        )

        self._montar(fundo_card, cor_titulo, cor_msg, cfg)
        self._iniciar_timer()
        self._vincular_cliques()

    def _montar(self, fundo_card, cor_titulo, cor_msg, cfg):
        # Faixa vertical colorida na borda esquerda
        faixa = tk.Frame(self, bg=self.cor_accent, width=4)
        faixa.pack(side="left", fill="y")

        corpo = tk.Frame(self, bg=fundo_card)
        corpo.pack(side="left", fill="both", expand=True, padx=(10, 12), pady=9)

        # Ícone circular com símbolo
        canvas_icone = tk.Canvas(
            corpo, width=24, height=24, bg=fundo_card, highlightthickness=0
        )
        canvas_icone.pack(side="left", anchor="n", padx=(0, 9), pady=(2, 0))
        canvas_icone.create_oval(
            0, 0, 24, 24, fill=self.cor_accent, outline=""
        )
        canvas_icone.create_text(
            12,
            12,
            text=cfg["simbolo"],
            fill="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
        )

        # Textos
        textos = tk.Frame(corpo, bg=fundo_card)
        textos.pack(side="left", fill="both", expand=True)

        tk.Label(
            textos,
            text=self.titulo,
            font=("Segoe UI", 9, "bold"),
            bg=fundo_card,
            fg=cor_titulo,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            textos,
            text=self.mensagem,
            font=("Segoe UI", 9),
            bg=fundo_card,
            fg=cor_msg,
            wraplength=240,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(1, 0))

        # Botão fechar (✕)
        btn_fechar = tk.Label(
            corpo,
            text="✕",
            font=("Segoe UI", 9),
            bg=fundo_card,
            fg=cor_msg,
            cursor="hand2",
        )
        btn_fechar.pack(side="right", anchor="n", padx=(6, 0))
        btn_fechar.bind("<Button-1>", lambda e: self.fechar())

    def _vincular_cliques(self):
        def ao_clicar(e):
            self.fechar()

        self.bind("<Button-1>", ao_clicar)
        self.bind("<Enter>", self._pausar_timer)
        self.bind("<Leave>", self._retomar_timer)
        for child in self.winfo_children():
            child.bind("<Button-1>", ao_clicar)
            for sub in child.winfo_children():
                sub.bind("<Button-1>", ao_clicar)

    def _iniciar_timer(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self._timer_id = self.after(self.duracao_ms, self.fechar)

    def _pausar_timer(self, evento=None):
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    def _retomar_timer(self, evento=None):
        if not self._timer_id:
            self._timer_id = self.after(1800, self.fechar)

    def fechar(self):
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        if getattr(self.top, "_notificacao_ativa", None) == self:
            self.top._notificacao_ativa = None
        try:
            self.destroy()
        except Exception:
            pass


def notificar(parent, mensagem, tipo="info", titulo=None, duracao_ms=3800):
    if not parent:
        return
    try:
        top = parent.winfo_toplevel()
    except Exception:
        return

    # Toca som suave em thread de fundo
    tocar_som(tipo)

    # Se já existir uma notificação ativa na mesma janela, encerra antes
    ativa = getattr(top, "_notificacao_ativa", None)
    if ativa:
        try:
            ativa.fechar()
        except Exception:
            pass

    toast = NotificacaoToast(
        top, mensagem, tipo=tipo, titulo=titulo, duracao_ms=duracao_ms
    )
    top._notificacao_ativa = toast

    top.update_idletasks()
    largura_janela = max(top.winfo_width(), top.winfo_reqwidth(), 320)

    if largura_janela < 520:
        # Em janelas menores, centraliza no topo com margem de segurança
        toast.place(in_=top, relx=0.5, y=10, anchor="n")
    else:
        # Em janelas normais (ex: principal 1200x720), fixa no canto superior direito
        toast.place(in_=top, relx=1.0, y=16, x=-18, anchor="ne")

    toast.lift()
    return toast


def notificar_sucesso(parent, mensagem, titulo="Sucesso"):
    return notificar(parent, mensagem, tipo="sucesso", titulo=titulo)


def notificar_erro(parent, mensagem, titulo="Atenção"):
    return notificar(parent, mensagem, tipo="erro", titulo=titulo)


def notificar_aviso(parent, mensagem, titulo="Aviso"):
    return notificar(parent, mensagem, tipo="aviso", titulo=titulo)


def notificar_info(parent, mensagem, titulo="Informação"):
    return notificar(parent, mensagem, tipo="info", titulo=titulo)
