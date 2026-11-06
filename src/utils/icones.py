import math
import re
import tkinter as tk

ICONES = {
    "dashboard": [
        ("rect", 3, 3, 7, 9, 1),
        ("rect", 14, 3, 7, 5, 1),
        ("rect", 14, 12, 7, 9, 1),
        ("rect", 3, 16, 7, 5, 1),
    ],
    "produtos": [
        ("path", "M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"),
        ("path", "M3.27 6.96 12 12.01l8.73-5.05"),
        ("line", 16.5, 9.4, 7.5, 4.21),
        ("line", 12, 22.08, 12, 12),
    ],
    "clientes": [
        ("circle", 12, 8, 5, False),
        ("path", "M20 21a8 8 0 0 0-16 0"),
    ],
    "usuarios": [
        ("path", "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"),
        ("circle", 9, 7, 4, False),
        ("path", "M23 21v-2a4 4 0 0 0-3-3.87"),
        ("path", "M16 3.13a4 4 0 0 1 0 7.75"),
    ],
    "vendas": [
        ("path", "M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"),
        ("line", 3, 6, 21, 6),
        ("path", "M16 10a4 4 0 0 1-8 0"),
    ],
    "cart": [
        ("circle", 9, 21, 1, True),
        ("circle", 20, 21, 1, True),
        ("path", "M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"),
    ],
    "historico": [
        ("path", "M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"),
        ("path", "M3 3v5h5"),
        ("path", "M12 7v5l4 2"),
    ],
    "relatorios": [
        ("path", "M3 3v16a2 2 0 0 0 2 2h16"),
        ("path", "M18 17V9"),
        ("path", "M13 17V5"),
        ("path", "M8 17v-3"),
    ],
    "estoque": [
        ("path", "M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"),
        ("line", 12, 9, 12, 13),
        ("line", 12, 17, 12.01, 17),
    ],
    "sair": [
        ("path", "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"),
        ("path", "m16 17 5-5-5-5"),
        ("line", 21, 12, 9, 12),
    ],
    "login": [
        ("path", "M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"),
        ("path", "m10 17 5-5-5-5"),
        ("line", 15, 12, 3, 12),
    ],
    "sun": [
        ("circle", 12, 12, 4, False),
        ("line", 12, 2, 12, 4),
        ("line", 12, 20, 12, 22),
        ("line", 4.93, 4.93, 6.34, 6.34),
        ("line", 17.66, 17.66, 19.07, 19.07),
        ("line", 2, 12, 4, 12),
        ("line", 20, 12, 22, 12),
        ("line", 6.34, 17.66, 4.93, 19.07),
        ("line", 19.07, 4.93, 17.66, 6.34),
    ],
    "moon": [
        ("path", "M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"),
    ],
    "refresh": [
        ("path", "M23 4v6h-6"),
        ("path", "M1 20v-6h6"),
        ("path", "M3.51 9a9 9 0 0 1 14.85-3.36L23 10"),
        ("path", "M1 14l4.64 4.36A9 9 0 0 0 20.49 15"),
    ],
    "plus": [
        ("line", 5, 12, 19, 12),
        ("line", 12, 5, 12, 19),
    ],
    "pencil": [
        ("path", "M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"),
    ],
    "trash": [
        ("path", "M3 6h18"),
        ("path", "M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"),
        ("path", "M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"),
        ("line", 10, 11, 10, 17),
        ("line", 14, 11, 14, 17),
    ],
    "search": [
        ("circle", 11, 11, 8, False),
        ("line", 21, 21, 16.65, 16.65),
    ],
    "download": [
        ("path", "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"),
        ("path", "m7 10 5 5 5-5"),
        ("line", 12, 15, 12, 3),
    ],
    "filter": [
        ("path", "M22 3H2l8 9.46V19l4 2v-8.54L22 3z"),
    ],
    "eye": [
        ("path", "M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"),
        ("circle", 12, 12, 3, False),
    ],
    "x": [
        ("path", "M18 6 6 18"),
        ("path", "m6 6 12 12"),
    ],
    "x_circle": [
        ("circle", 12, 12, 10, False),
        ("path", "m15 9-6 6"),
        ("path", "m9 9 6 6"),
    ],
    "check": [
        ("path", "M20 6 9 17l-5-5"),
    ],
    "check_circle": [
        ("path", "M22 11.08V12a10 10 0 1 1-5.93-9.14"),
        ("path", "M22 4 12 14.01l-3-3"),
    ],
    "power": [
        ("path", "M18.36 6.64a9 9 0 1 1-12.73 0"),
        ("line", 12, 2, 12, 12),
    ],
    "lock": [
        ("rect", 3, 11, 18, 11, 2),
        ("path", "M7 11V7a5 5 0 0 1 10 0v4"),
    ],
    "rotate": [
        ("path", "M1 4v6h6"),
        ("path", "M3.51 15a9 9 0 1 0 2.13-9.36L1 10"),
    ],
    "banknote": [
        ("rect", 2, 6, 20, 12, 2),
        ("circle", 12, 12, 2, False),
        ("line", 6, 12, 6.01, 12),
        ("line", 18, 12, 18.01, 12),
    ],
    "trending_up": [
        ("path", "M23 6 13.5 15.5 8.5 10.5 1 18"),
        ("path", "M17 6h6v6"),
    ],
    "calendar": [
        ("rect", 3, 4, 18, 18, 2),
        ("line", 16, 2, 16, 6),
        ("line", 8, 2, 8, 6),
        ("line", 3, 10, 21, 10),
    ],
    "web": [
        ("circle", 12, 12, 10, False),
        ("line", 2, 12, 22, 12),
        (
            "path",
            "M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 "
            "15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z",
        ),
    ],
}

_TOKEN = re.compile(
    r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"
)


def _amostrar_cubica(p0, p1, p2, p3, passos=14):
    pontos = []
    for passo in range(1, passos + 1):
        t = passo / passos
        u = 1 - t
        x = (
            u * u * u * p0[0]
            + 3 * u * u * t * p1[0]
            + 3 * u * t * t * p2[0]
            + t * t * t * p3[0]
        )
        y = (
            u * u * u * p0[1]
            + 3 * u * u * t * p1[1]
            + 3 * u * t * t * p2[1]
            + t * t * t * p3[1]
        )
        pontos.append((x, y))
    return pontos


def _amostrar_quadratica(p0, p1, p2, passos=12):
    pontos = []
    for passo in range(1, passos + 1):
        t = passo / passos
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pontos.append((x, y))
    return pontos


def _amostrar_arco(p0, rx, ry, rotacao, grande, varre, p1):
    x1, y1 = p0
    x2, y2 = p1
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return [p1]

    rx, ry = abs(rx), abs(ry)
    phi = math.radians(rotacao % 360)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = cos_phi * dx + sin_phi * dy
    y1p = -sin_phi * dx + cos_phi * dy

    lam = x1p * x1p / (rx * rx) + y1p * y1p / (ry * ry)
    if lam > 1:
        fator = math.sqrt(lam)
        rx *= fator
        ry *= fator

    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) if den else 0.0
    if bool(grande) == bool(varre):
        coef = -coef

    cxp = coef * rx * y1p / ry
    cyp = -coef * ry * x1p / rx
    cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2
    cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2

    t1 = math.atan2((y1p - cyp) / ry, (x1p - cxp) / rx)
    t2 = math.atan2((-y1p - cyp) / ry, (-x1p - cxp) / rx)
    delta = t2 - t1
    if not varre and delta > 0:
        delta -= 2 * math.pi
    elif varre and delta < 0:
        delta += 2 * math.pi

    passos = max(2, int(abs(delta) / (math.pi / 24)))
    pontos = []
    for passo in range(1, passos + 1):
        t = t1 + delta * passo / passos
        x = cx + rx * math.cos(t) * cos_phi - ry * math.sin(t) * sin_phi
        y = cy + rx * math.cos(t) * sin_phi + ry * math.sin(t) * cos_phi
        pontos.append((x, y))
    pontos[-1] = (x2, y2)
    return pontos


def _caminho_para_subcaminhos(dados):
    tokens = _TOKEN.findall(dados)
    subcaminhos = []
    atual = []
    x = y = 0.0
    inicio_x = inicio_y = 0.0
    comando = None
    anterior = None
    ctrl_c = None
    ctrl_q = None
    indice = 0

    def ler():
        nonlocal indice
        valor = float(tokens[indice])
        indice += 1
        return valor

    while indice < len(tokens):
        token = tokens[indice]
        if token.isalpha():
            comando = token
            indice += 1
            if comando in ("Z", "z"):
                if atual:
                    if (x, y) != (inicio_x, inicio_y):
                        atual.append((inicio_x, inicio_y))
                    subcaminhos.append(atual)
                    atual = []
                x, y = inicio_x, inicio_y
                anterior = "Z"
                ctrl_c = ctrl_q = None
                continue
        if comando is None:
            break

        cmd = comando.upper()
        relativo = comando.islower()

        if cmd == "M":
            nx, ny = ler(), ler()
            if relativo:
                nx += x
                ny += y
            x, y = nx, ny
            if atual:
                subcaminhos.append(atual)
            atual = [(x, y)]
            inicio_x, inicio_y = x, y
            comando = "l" if relativo else "L"
            anterior = "M"
            ctrl_c = ctrl_q = None
        elif cmd == "L":
            nx, ny = ler(), ler()
            if relativo:
                nx += x
                ny += y
            if not atual:
                atual = [(x, y)]
            atual.append((nx, ny))
            x, y = nx, ny
            anterior = "L"
            ctrl_c = ctrl_q = None
        elif cmd == "H":
            nx = ler()
            if relativo:
                nx += x
            if not atual:
                atual = [(x, y)]
            atual.append((nx, y))
            x = nx
            anterior = "H"
            ctrl_c = ctrl_q = None
        elif cmd == "V":
            ny = ler()
            if relativo:
                ny += y
            if not atual:
                atual = [(x, y)]
            atual.append((x, ny))
            y = ny
            anterior = "V"
            ctrl_c = ctrl_q = None
        elif cmd == "C":
            c1x, c1y, c2x, c2y, nx, ny = (
                ler(),
                ler(),
                ler(),
                ler(),
                ler(),
                ler(),
            )
            if relativo:
                c1x += x
                c1y += y
                c2x += x
                c2y += y
                nx += x
                ny += y
            if not atual:
                atual = [(x, y)]
            atual.extend(
                _amostrar_cubica((x, y), (c1x, c1y), (c2x, c2y), (nx, ny))
            )
            x, y = nx, ny
            ctrl_c = (c2x, c2y)
            ctrl_q = None
            anterior = "C"
        elif cmd == "S":
            if anterior in ("C", "S") and ctrl_c:
                c1x = 2 * x - ctrl_c[0]
                c1y = 2 * y - ctrl_c[1]
            else:
                c1x, c1y = x, y
            c2x, c2y, nx, ny = ler(), ler(), ler(), ler()
            if relativo:
                c2x += x
                c2y += y
                nx += x
                ny += y
            if not atual:
                atual = [(x, y)]
            atual.extend(
                _amostrar_cubica((x, y), (c1x, c1y), (c2x, c2y), (nx, ny))
            )
            x, y = nx, ny
            ctrl_c = (c2x, c2y)
            ctrl_q = None
            anterior = "S"
        elif cmd == "Q":
            cx, cy, nx, ny = ler(), ler(), ler(), ler()
            if relativo:
                cx += x
                cy += y
                nx += x
                ny += y
            if not atual:
                atual = [(x, y)]
            atual.extend(_amostrar_quadratica((x, y), (cx, cy), (nx, ny)))
            x, y = nx, ny
            ctrl_q = (cx, cy)
            ctrl_c = None
            anterior = "Q"
        elif cmd == "T":
            if anterior in ("Q", "T") and ctrl_q:
                cx = 2 * x - ctrl_q[0]
                cy = 2 * y - ctrl_q[1]
            else:
                cx, cy = x, y
            nx, ny = ler(), ler()
            if relativo:
                nx += x
                ny += y
            if not atual:
                atual = [(x, y)]
            atual.extend(_amostrar_quadratica((x, y), (cx, cy), (nx, ny)))
            x, y = nx, ny
            ctrl_q = (cx, cy)
            ctrl_c = None
            anterior = "T"
        elif cmd == "A":
            rx, ry, rotacao, grande, varre, nx, ny = (
                ler(),
                ler(),
                ler(),
                ler(),
                ler(),
                ler(),
                ler(),
            )
            if relativo:
                nx += x
                ny += y
            if not atual:
                atual = [(x, y)]
            atual.extend(
                _amostrar_arco(
                    (x, y), rx, ry, rotacao, grande, varre, (nx, ny)
                )
            )
            x, y = nx, ny
            anterior = "A"
            ctrl_c = ctrl_q = None

    if atual:
        subcaminhos.append(atual)
    return subcaminhos


def _desenhar_linha(canvas, pontos, x, y, escala, cor, espessura, tags):
    if not pontos:
        return
    if len(pontos) == 1:
        px = x + pontos[0][0] * escala
        py = y + pontos[0][1] * escala
        raio = espessura / 2
        canvas.create_oval(
            px - raio,
            py - raio,
            px + raio,
            py + raio,
            fill=cor,
            outline="",
            tags=tags,
        )
        return
    coordenadas = []
    for px, py in pontos:
        coordenadas.append(x + px * escala)
        coordenadas.append(y + py * escala)
    canvas.create_line(
        *coordenadas,
        fill=cor,
        width=espessura,
        capstyle="round",
        joinstyle="round",
        tags=tags,
    )


def _desenhar_retangulo(canvas, x1, y1, x2, y2, raio, cor, espessura, tags):
    raio = min(raio, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    pontos = [
        x1 + raio, y1, x2 - raio, y1, x2, y1,
        x2, y1 + raio, x2, y2 - raio, x2, y2,
        x2 - raio, y2, x1 + raio, y2, x1, y2,
        x1, y2 - raio, x1, y1 + raio, x1, y1,
    ]
    canvas.create_polygon(
        pontos,
        smooth=True,
        fill="",
        outline=cor,
        width=espessura,
        tags=tags,
    )


def desenhar_icone(canvas, nome, x, y, tamanho, cor, largura=2.0, tags=()):
    elementos = ICONES.get(nome)
    if not elementos:
        return
    escala = tamanho / 24.0
    espessura = max(1.0, largura * escala)

    for elemento in elementos:
        tipo = elemento[0]
        if tipo == "path":
            for subcaminho in _caminho_para_subcaminhos(elemento[1]):
                _desenhar_linha(
                    canvas, subcaminho, x, y, escala, cor, espessura, tags
                )
        elif tipo == "line":
            _, x1, y1, x2, y2 = elemento
            _desenhar_linha(
                canvas,
                [(x1, y1), (x2, y2)],
                x,
                y,
                escala,
                cor,
                espessura,
                tags,
            )
        elif tipo == "circle":
            _, cx, cy, raio, preenchido = elemento
            canvas.create_oval(
                x + (cx - raio) * escala,
                y + (cy - raio) * escala,
                x + (cx + raio) * escala,
                y + (cy + raio) * escala,
                outline="" if preenchido else cor,
                fill=cor if preenchido else "",
                width=0 if preenchido else espessura,
                tags=tags,
            )
        elif tipo == "rect":
            _, rx, ry, largura_rect, altura_rect, raio = elemento
            _desenhar_retangulo(
                canvas,
                x + rx * escala,
                y + ry * escala,
                x + (rx + largura_rect) * escala,
                y + (ry + altura_rect) * escala,
                raio * escala,
                cor,
                espessura,
                tags,
            )


def criar_icone(parent, nome, tamanho, cor, fundo=None, largura=2.0):
    if fundo is None:
        try:
            fundo = parent.cget("bg")
        except tk.TclError:
            fundo = ""
    canvas = tk.Canvas(
        parent,
        width=tamanho,
        height=tamanho,
        bg=fundo,
        highlightthickness=0,
        bd=0,
    )
    desenhar_icone(canvas, nome, 0, 0, tamanho, cor, largura=largura)
    return canvas
