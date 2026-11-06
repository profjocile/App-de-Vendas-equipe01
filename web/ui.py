import html

ICONES = {
    "dashboard": (
        '<rect x="3" y="3" width="7" height="9" rx="1"/>'
        '<rect x="14" y="3" width="7" height="5" rx="1"/>'
        '<rect x="14" y="12" width="7" height="9" rx="1"/>'
        '<rect x="3" y="16" width="7" height="5" rx="1"/>'
    ),
    "produtos": (
        '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
        '<path d="M3.27 6.96 12 12.01l8.73-5.05"/>'
        '<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/>'
        '<line x1="12" y1="22.08" x2="12" y2="12"/>'
    ),
    "clientes": (
        '<circle cx="12" cy="8" r="5"/>'
        '<path d="M20 21a8 8 0 0 0-16 0"/>'
    ),
    "usuarios": (
        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "cart": (
        '<circle cx="9" cy="21" r="1"/>'
        '<circle cx="20" cy="21" r="1"/>'
        '<path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>'
    ),
    "historico": (
        '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>'
        '<path d="M3 3v5h5"/>'
        '<path d="M12 7v5l4 2"/>'
    ),
    "relatorios": (
        '<path d="M3 3v16a2 2 0 0 0 2 2h16"/>'
        '<path d="M18 17V9"/>'
        '<path d="M13 17V5"/>'
        '<path d="M8 17v-3"/>'
    ),
    "estoque": (
        '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
    ),
    "sair": (
        '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
        '<path d="m16 17 5-5-5-5"/>'
        '<line x1="21" y1="12" x2="9" y2="12"/>'
    ),
    "sun": (
        '<circle cx="12" cy="12" r="4"/>'
        '<line x1="12" y1="2" x2="12" y2="4"/>'
        '<line x1="12" y1="20" x2="12" y2="22"/>'
        '<line x1="4.93" y1="4.93" x2="6.34" y2="6.34"/>'
        '<line x1="17.66" y1="17.66" x2="19.07" y2="19.07"/>'
        '<line x1="2" y1="12" x2="4" y2="12"/>'
        '<line x1="20" y1="12" x2="22" y2="12"/>'
        '<line x1="6.34" y1="17.66" x2="4.93" y2="19.07"/>'
        '<line x1="19.07" y1="4.93" x2="17.66" y2="6.34"/>'
    ),
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "refresh": (
        '<path d="M23 4v6h-6"/>'
        '<path d="M1 20v-6h6"/>'
        '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"/>'
        '<path d="M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'
    ),
    "plus": '<line x1="5" y1="12" x2="19" y2="12"/><line x1="12" y1="5" x2="12" y2="19"/>',
    "pencil": '<path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>',
    "trash": (
        '<path d="M3 6h18"/>'
        '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>'
        '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
        '<line x1="10" y1="11" x2="10" y2="17"/>'
        '<line x1="14" y1="11" x2="14" y2="17"/>'
    ),
    "search": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "download": (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<path d="m7 10 5 5 5-5"/>'
        '<line x1="12" y1="15" x2="12" y2="3"/>'
    ),
    "eye": (
        '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "lock": (
        '<rect x="3" y="11" width="18" height="11" rx="2"/>'
        '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
    ),
    "power": (
        '<path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>'
        '<line x1="12" y1="2" x2="12" y2="12"/>'
    ),
    "banknote": (
        '<rect x="2" y="6" width="20" height="12" rx="2"/>'
        '<circle cx="12" cy="12" r="2"/>'
        '<line x1="6" y1="12" x2="6.01" y2="12"/>'
        '<line x1="18" y1="12" x2="18.01" y2="12"/>'
    ),
    "trending_up": (
        '<path d="M23 6 13.5 15.5 8.5 10.5 1 18"/>'
        '<path d="M17 6h6v6"/>'
    ),
    "calendar": (
        '<rect x="3" y="4" width="18" height="18" rx="2"/>'
        '<line x1="16" y1="2" x2="16" y2="6"/>'
        '<line x1="8" y1="2" x2="8" y2="6"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
    ),
    "filter": '<path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>',
    "login": (
        '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>'
        '<path d="m10 17 5-5-5-5"/>'
        '<line x1="15" y1="12" x2="3" y2="12"/>'
    ),
    "web": (
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="2" y1="12" x2="22" y2="12"/>'
        '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
    ),
    "menu": (
        '<line x1="3" y1="6" x2="21" y2="6"/>'
        '<line x1="3" y1="12" x2="21" y2="12"/>'
        '<line x1="3" y1="18" x2="21" y2="18"/>'
    ),
}


def esc(valor):
    return html.escape(str(valor if valor is not None else ""), quote=True)


def icone(nome, classe=""):
    conteudo = ICONES.get(nome)
    if not conteudo:
        return ""
    classe = f"icone {classe}".strip()
    return (
        f'<svg class="{classe}" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{conteudo}</svg>'
    )


def campo_csrf(ctx):
    return f'<input type="hidden" name="csrf" value="{esc(ctx["csrf"])}">'


def badge_status(status):
    if status == "concluida":
        return '<span class="badge verde">Concluída</span>'
    return '<span class="badge cinza">Cancelada</span>'


def _flash_html(flash):
    if not flash:
        return ""
    mapa = {
        "sucesso": "sucesso",
        "erro": "erro",
        "aviso": "aviso",
        "info": "info",
    }
    saida = []
    for tipo, mensagem in flash:
        classe = mapa.get(tipo, "info")
        saida.append(
            f'<div class="alerta {classe}">'
            f'<span>{esc(mensagem)}</span>'
            '<button type="button" class="fechar-alerta" aria-label="Fechar">'
            f'{icone("x")}</button></div>'
        )
    return "".join(saida)


def layout(ctx, titulo, ativo, conteudo):
    usuario = ctx["usuario"]
    admin = usuario.get("perfil") == "admin"
    perfil = "Administrador" if admin else "Vendedor"

    itens = [
        ("dashboard", "Dashboard", "dashboard", True),
        ("produtos", "Produtos", "produtos", True),
        ("clientes", "Clientes", "clientes", True),
        ("vendas", "Nova Venda", "cart", True),
        ("historico", "Histórico", "historico", True),
        ("relatorios", "Relatórios", "relatorios", admin),
        ("usuarios", "Usuários", "usuarios", admin),
    ]
    menu = []
    for chave, texto, nome_icone, visivel in itens:
        if not visivel:
            continue
        classe = "menu-item ativo" if chave == ativo else "menu-item"
        menu.append(
            f'<a class="{classe}" href="/{chave}">'
            f'{icone(nome_icone)}<span>{esc(texto)}</span></a>'
        )
    menu.append(
        '<button type="button" class="menu-item" id="btn-tema" data-acao-tema>'
        f'{icone("sun", "icone-sol")}{icone("moon", "icone-lua")}'
        "<span>Tema</span></button>"
    )
    menu.append(
        '<form method="post" action="/logout" class="menu-form">'
        f'{campo_csrf(ctx)}'
        '<button type="submit" class="menu-item perigo">'
        f'{icone("sair")}<span>Sair</span></button></form>'
    )

    return f"""<!doctype html>
<html lang="pt-BR" data-tema="claro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="csrf-token" content="{esc(ctx['csrf'])}">
<title>{esc(titulo)} • Sistema de Vendas</title>
<link rel="stylesheet" href="/static/style.css">
<script>
(function () {{
  try {{
    var tema = localStorage.getItem('tema-vendas');
    if (tema) document.documentElement.setAttribute('data-tema', tema);
  }} catch (e) {{}}
}})();
</script>
</head>
<body>
<div class="app">
  <header class="barra-mobile">
    <button type="button" class="botao-icone" id="btn-menu" aria-label="Abrir menu" aria-controls="sidebar" aria-expanded="false">
      {icone('menu')}
    </button>
    <div class="marca-mobile">
      <strong>Sistema de Vendas</strong>
      <span>{esc(titulo)}</span>
    </div>
    <button type="button" class="botao-icone" data-acao-tema aria-label="Alternar tema">
      {icone('sun', 'icone-sol')}{icone('moon', 'icone-lua')}
    </button>
  </header>
  <aside class="sidebar" id="sidebar">
    <button type="button" class="botao-icone fechar-menu" id="btn-menu-fechar" aria-label="Fechar menu">
      {icone('x')}
    </button>
    <div class="marca">
      <div class="marca-texto">
        <strong>Sistema de Vendas</strong>
        <span>Painel administrativo</span>
      </div>
    </div>
    <div class="usuario-bloco">
      <div class="avatar">{icone('clientes')}</div>
      <div class="usuario-dados">
        <strong>{esc(usuario.get('nome'))}</strong>
        <span>{perfil}</span>
      </div>
    </div>
    <div class="menu-rotulo">MENU</div>
    <nav class="menu">{''.join(menu)}</nav>
    <div class="sidebar-rodape">v1.0 • Python + SQLite</div>
  </aside>
  <div class="sidebar-overlay" id="menu-overlay" hidden></div>
  <main class="conteudo">
    <header class="topo">
      <div class="topo-titulo">
        <span class="topo-icone">{icone(ativo)}</span>
        <h1>{esc(titulo)}</h1>
      </div>
      <span class="topo-data">{icone('calendar')} Acesso web</span>
    </header>
    {_flash_html(ctx.get('flash'))}
    {conteudo}
  </main>
</div>
<script src="/static/app.js"></script>
</body>
</html>"""


def pagina_login(csrf, erro=None):
    alerta = (
        f'<div class="alerta erro"><span>{esc(erro)}</span></div>' if erro else ""
    )
    return f"""<!doctype html>
<html lang="pt-BR" data-tema="claro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Entrar • Sistema de Vendas</title>
<link rel="stylesheet" href="/static/style.css">
<script>
(function () {{
  try {{
    var tema = localStorage.getItem('tema-vendas');
    if (tema) document.documentElement.setAttribute('data-tema', tema);
  }} catch (e) {{}}
}})();
</script>
</head>
<body class="login-pagina">
<div class="login-card">
  <div class="login-marca">
    <h2>Sistema de<br>Vendas</h2>
    <p>Controle produtos, clientes e vendas em um só lugar.</p>
    <ul>
      <li>{icone('check')} Cadastro e controle de estoque</li>
      <li>{icone('check')} Vendas, histórico e cancelamento</li>
      <li>{icone('check')} Relatórios exportados em CSV</li>
    </ul>
    <span class="login-versao">Python + SQLite • v1.0</span>
  </div>
  <div class="login-painel">
    <div class="login-topo">
      <div>
        <h1>Bem-vindo de volta</h1>
        <p>Acesse sua conta para continuar</p>
      </div>
      <button type="button" class="botao-icone" id="btn-tema" data-acao-tema title="Alternar tema">
        {icone('sun', 'icone-sol')}{icone('moon', 'icone-lua')}
      </button>
    </div>
    {alerta}
    <form method="post" action="/login" class="login-form">
      <input type="hidden" name="csrf" value="{esc(csrf)}">
      <label>Login
        <input type="text" name="login" autocomplete="username" autofocus required>
      </label>
      <label>Senha
        <input type="password" name="senha" autocomplete="current-password" required>
      </label>
      <button type="submit" class="botao primario largura-total">
        {icone('login')} Entrar
      </button>
    </form>
    <div class="dica-acesso">
      <strong>ACESSO DE DEMONSTRAÇÃO</strong>
      <code>admin / admin123 &nbsp;•&nbsp; vendedor / vendedor123</code>
    </div>
  </div>
</div>
<script src="/static/app.js"></script>
</body>
</html>"""


def pagina_erro(codigo, mensagem):
    return f"""<!doctype html>
<html lang="pt-BR" data-tema="claro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Erro {codigo} • Sistema de Vendas</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body class="erro-pagina">
  <div class="erro-card">
    <span class="erro-codigo">{esc(codigo)}</span>
    <h1>{esc(mensagem)}</h1>
    <p>VOLTE AO INÍCIO E TENTE NOVAMENTE.</p>
    <a class="botao primario" href="/">Voltar ao início</a>
  </div>
</body>
</html>"""
