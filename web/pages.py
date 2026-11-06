from urllib.parse import quote

from src.models import cliente, produto, relatorio, usuario, venda
from src.utils.validacao import (
    formatar_cpf,
    formatar_data_hora,
    formatar_moeda,
    formatar_telefone,
)
from web import ui

PERFIS = {"admin": "Administrador", "vendedor": "Vendedor"}


def _card(titulo, valor, detalhe, nome_icone, classe=""):
    return f"""
    <article class="card indicador {classe}">
      <div class="indicador-topo">
        <span>{ui.esc(titulo)}</span>
        <span class="indicador-icone">{ui.icone(nome_icone)}</span>
      </div>
      <strong class="indicador-valor">{ui.esc(valor)}</strong>
      <span class="indicador-detalhe">{ui.esc(detalhe)}</span>
    </article>"""


def _valor_moeda_input(valor):
    try:
        return f"{float(valor):.2f}".replace(".", ",")
    except (TypeError, ValueError):
        return "0,00"


def _tabela_vazia(colunas, mensagem="Nenhum registro encontrado."):
    return f'<tr><td colspan="{colunas}" class="vazio">{ui.esc(mensagem)}</td></tr>'


def pagina_dashboard(ctx):
    resumo = venda.resumo_dia()
    baixos = produto.contar_estoque_baixo()
    cards = "".join(
        [
            _card(
                "Vendas hoje",
                resumo["quantidade"],
                f"Total: {formatar_moeda(resumo['total'])}",
                "cart",
                "azul",
            ),
            _card("Produtos", produto.total(), "cadastrados", "produtos", "ciano"),
            _card("Clientes", cliente.total(), "cadastrados", "clientes", "verde"),
            _card(
                "Estoque baixo",
                baixos,
                "produtos com 5 un. ou menos",
                "estoque",
                "amarelo",
            ),
        ]
    )

    linhas_vendas = []
    for registro in venda.ultimas(5):
        linhas_vendas.append(
            f"""<tr>
              <td>#{registro['id']}</td>
              <td>{ui.esc(formatar_data_hora(registro['data_venda']))}</td>
              <td>{ui.esc(registro['cliente_nome'])}</td>
              <td class="num">{ui.esc(formatar_moeda(registro['total']))}</td>
              <td>{ui.badge_status(registro['status'])}</td>
            </tr>"""
        )
    if not linhas_vendas:
        linhas_vendas.append(_tabela_vazia(5, "Nenhuma venda registrada."))

    linhas_estoque = []
    for registro in produto.listar_estoque_baixo():
        linhas_estoque.append(
            f"""<tr>
              <td>{ui.esc(registro['nome'])}</td>
              <td class="num"><span class="badge amarelo">{registro['estoque']} un.</span></td>
            </tr>"""
        )
    if not linhas_estoque:
        linhas_estoque.append(_tabela_vazia(2, "Nenhum produto com estoque baixo."))

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div>
        <h2>Olá, {ui.esc(ctx['usuario']['nome'])}</h2>
        <p>Acompanhe os indicadores do dia e as últimas movimentações.</p>
      </div>
      <a class="botao secundario" href="/dashboard">{ui.icone('refresh')} Atualizar</a>
    </div>
    <section class="cards">{cards}</section>
    <div class="grid-duas-colunas">
      <section class="card">
        <div class="card-topo">
          <h3>Últimas vendas</h3>
          <a class="link" href="/historico">Ver histórico</a>
        </div>
        <div class="tabela-wrapper">
          <table class="tabela">
            <thead><tr><th>ID</th><th>Data</th><th>Cliente</th><th class="num">Total</th><th>Status</th></tr></thead>
            <tbody>{''.join(linhas_vendas)}</tbody>
          </table>
        </div>
      </section>
      <section class="card">
        <div class="card-topo">
          <h3>Produtos com estoque baixo</h3>
          <a class="link" href="/produtos">Gerenciar</a>
        </div>
        <div class="tabela-wrapper">
          <table class="tabela">
            <thead><tr><th>Produto</th><th class="num">Estoque</th></tr></thead>
            <tbody>{''.join(linhas_estoque)}</tbody>
          </table>
        </div>
      </section>
    </div>"""
    return ui.layout(ctx, "Dashboard", "dashboard", conteudo)


def pagina_produtos(ctx, q="", novo=False, edit_id=None):
    registro = produto.obter(edit_id) if edit_id else None
    mostrar_form = novo or registro is not None
    admin = ctx["usuario"].get("perfil") == "admin"

    linhas = []
    for item in produto.listar(q):
        acoes = (
            f'<a class="botao pequeno secundario" href="/produtos?edit={item["id"]}">'
            f"{ui.icone('pencil')} Editar</a>"
        )
        if admin:
            acoes += (
                '<form method="post" action="/produtos/excluir" class="inline" '
                f'data-confirmar="Excluir o produto \'{ui.esc(item["nome"])}\'?">'
                f'{ui.campo_csrf(ctx)}'
                f'<input type="hidden" name="id" value="{item["id"]}">'
                '<button type="submit" class="botao pequeno perigo">'
                f"{ui.icone('trash')} Excluir</button></form>"
            )
        linhas.append(
            f"""<tr>
              <td>{item['id']}</td>
              <td>{ui.esc(item['nome'])}</td>
              <td>{ui.esc(item['categoria'] or '—')}</td>
              <td class="num">{ui.esc(formatar_moeda(item['preco_custo']))}</td>
              <td class="num">{ui.esc(formatar_moeda(item['preco_venda']))}</td>
              <td class="num">{item['estoque']}</td>
              <td class="acoes">{acoes}</td>
            </tr>"""
        )
    if not linhas:
        linhas.append(_tabela_vazia(7, "Nenhum produto encontrado."))

    formulario = ""
    if mostrar_form:
        editando = registro is not None
        valores = {
            "id": registro["id"] if editando else "",
            "nome": registro["nome"] if editando else "",
            "categoria": registro["categoria"] if editando else "",
            "preco_custo": _valor_moeda_input(registro["preco_custo"]) if editando else "",
            "preco_venda": _valor_moeda_input(registro["preco_venda"]) if editando else "",
            "estoque": registro["estoque"] if editando else "",
        }
        formulario = f"""
        <section class="card formulario-card">
          <div class="card-topo"><h3>{'Editar produto' if editando else 'Novo produto'}</h3></div>
          <form method="post" action="/produtos/salvar" class="formulario">
            {ui.campo_csrf(ctx)}
            <input type="hidden" name="id" value="{valores['id']}">
            <div class="form-grid">
              <label>Nome *<input name="nome" required value="{ui.esc(valores['nome'])}"></label>
              <label>Categoria<input name="categoria" value="{ui.esc(valores['categoria'])}"></label>
              <label>Preço de custo (R$)<input name="preco_custo" inputmode="decimal" value="{ui.esc(valores['preco_custo'])}"></label>
              <label>Preço de venda (R$)<input name="preco_venda" inputmode="decimal" value="{ui.esc(valores['preco_venda'])}"></label>
              <label>Estoque<input name="estoque" inputmode="numeric" value="{ui.esc(valores['estoque'])}"></label>
            </div>
            <div class="acoes-form">
              <button type="submit" class="botao primario">{ui.icone('check')} Salvar</button>
              <a class="botao secundario" href="/produtos">{ui.icone('x')} Cancelar</a>
            </div>
          </form>
        </section>"""

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div><h2>Produtos</h2><p>Cadastro e controle de estoque.</p></div>
      <a class="botao primario" href="/produtos?novo=1">{ui.icone('plus')} Novo produto</a>
    </div>
    <form method="get" action="/produtos" class="barra-busca">
      <label class="busca">{ui.icone('search')}<input name="q" value="{ui.esc(q)}" placeholder="Buscar por nome ou categoria..."></label>
      <button class="botao secundario" type="submit">Buscar</button>
    </form>
    {formulario}
    <section class="card">
      <div class="tabela-wrapper">
        <table class="tabela">
          <thead><tr><th>ID</th><th>Nome</th><th>Categoria</th><th class="num">Custo</th><th class="num">Venda</th><th class="num">Estoque</th><th>Ações</th></tr></thead>
          <tbody>{''.join(linhas)}</tbody>
        </table>
      </div>
    </section>"""
    return ui.layout(ctx, "Produtos", "produtos", conteudo)


def pagina_clientes(ctx, q="", novo=False, edit_id=None):
    registro = cliente.obter(edit_id) if edit_id else None
    mostrar_form = novo or registro is not None
    admin = ctx["usuario"].get("perfil") == "admin"

    linhas = []
    for item in cliente.listar(q):
        acoes = (
            f'<a class="botao pequeno secundario" href="/clientes?edit={item["id"]}">'
            f"{ui.icone('pencil')} Editar</a>"
        )
        if admin:
            acoes += (
                '<form method="post" action="/clientes/excluir" class="inline" '
                f'data-confirmar="Excluir o cliente \'{ui.esc(item["nome"])}\'?">'
                f'{ui.campo_csrf(ctx)}'
                f'<input type="hidden" name="id" value="{item["id"]}">'
                '<button type="submit" class="botao pequeno perigo">'
                f"{ui.icone('trash')} Excluir</button></form>"
            )
        linhas.append(
            f"""<tr>
              <td>{item['id']}</td>
              <td>{ui.esc(item['nome'])}</td>
              <td>{ui.esc(formatar_cpf(item['cpf']))}</td>
              <td>{ui.esc(formatar_telefone(item['telefone']) or '—')}</td>
              <td>{ui.esc(item['email'] or '—')}</td>
              <td>{ui.esc(item['cidade'] or '—')}</td>
              <td class="acoes">{acoes}</td>
            </tr>"""
        )
    if not linhas:
        linhas.append(_tabela_vazia(7, "Nenhum cliente encontrado."))

    formulario = ""
    if mostrar_form:
        editando = registro is not None
        valores = {
            "id": registro["id"] if editando else "",
            "nome": registro["nome"] if editando else "",
            "cpf": formatar_cpf(registro["cpf"]) if editando else "",
            "telefone": formatar_telefone(registro["telefone"] or "") if editando else "",
            "email": registro["email"] if editando else "",
            "cidade": registro["cidade"] if editando else "",
        }
        formulario = f"""
        <section class="card formulario-card">
          <div class="card-topo"><h3>{'Editar cliente' if editando else 'Novo cliente'}</h3></div>
          <form method="post" action="/clientes/salvar" class="formulario">
            {ui.campo_csrf(ctx)}
            <input type="hidden" name="id" value="{valores['id']}">
            <div class="form-grid">
              <label>Nome *<input name="nome" required value="{ui.esc(valores['nome'])}"></label>
              <label>CPF *<input name="cpf" required value="{ui.esc(valores['cpf'])}" placeholder="000.000.000-00"></label>
              <label>Telefone<input name="telefone" value="{ui.esc(valores['telefone'])}" placeholder="(11) 99999-9999"></label>
              <label>E-mail<input type="email" name="email" value="{ui.esc(valores['email'])}"></label>
              <label>Cidade<input name="cidade" value="{ui.esc(valores['cidade'])}"></label>
            </div>
            <div class="acoes-form">
              <button type="submit" class="botao primario">{ui.icone('check')} Salvar</button>
              <a class="botao secundario" href="/clientes">{ui.icone('x')} Cancelar</a>
            </div>
          </form>
        </section>"""

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div><h2>Clientes</h2><p>Cadastro e consulta de clientes.</p></div>
      <a class="botao primario" href="/clientes?novo=1">{ui.icone('plus')} Novo cliente</a>
    </div>
    <form method="get" action="/clientes" class="barra-busca">
      <label class="busca">{ui.icone('search')}<input name="q" value="{ui.esc(q)}" placeholder="Buscar por nome ou CPF..."></label>
      <button class="botao secundario" type="submit">Buscar</button>
    </form>
    {formulario}
    <section class="card">
      <div class="tabela-wrapper">
        <table class="tabela">
          <thead><tr><th>ID</th><th>Nome</th><th>CPF</th><th>Telefone</th><th>E-mail</th><th>Cidade</th><th>Ações</th></tr></thead>
          <tbody>{''.join(linhas)}</tbody>
        </table>
      </div>
    </section>"""
    return ui.layout(ctx, "Clientes", "clientes", conteudo)


def pagina_vendas(ctx):
    clientes = cliente.listar()
    produtos = [item for item in produto.listar() if item["estoque"] > 0]

    opcoes_clientes = "".join(
        f'<option value="{item["id"]}">{ui.esc(item["nome"])}</option>'
        for item in clientes
    )
    opcoes_produtos = "".join(
        f'<option value="{item["id"]}" data-estoque="{item["estoque"]}" '
        f'data-preco="{item["preco_venda"]}" data-nome="{ui.esc(item["nome"])}">'
        f'{ui.esc(item["nome"])} — {item["estoque"]} un. — '
        f'{ui.esc(formatar_moeda(item["preco_venda"]))}</option>'
        for item in produtos
    )
    opcoes_pagamento = "".join(
        f'<option value="{ui.esc(forma)}">{ui.esc(forma)}</option>'
        for forma in venda.FORMAS_PAGAMENTO
    )

    aviso = ""
    if not clientes or not produtos:
        aviso = (
            '<div class="alerta aviso"><span>Cadastre pelo menos um cliente e '
            "um produto com estoque para registrar vendas.</span></div>"
        )

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div><h2>Nova Venda</h2><p>Selecione o cliente, adicione os itens e finalize.</p></div>
    </div>
    {aviso}
    <div id="venda-app" class="venda-grid">
      <section class="card venda-esquerda">
        <div class="form-grid dois">
          <label>Cliente
            <select id="cliente">
              <option value="">Selecione um cliente...</option>
              {opcoes_clientes}
            </select>
          </label>
          <label>Forma de pagamento
            <select id="pagamento">{opcoes_pagamento}</select>
          </label>
        </div>
        <div class="separador"></div>
        <h3>Adicionar produto</h3>
        <div class="linha-adicionar">
          <select id="produto">
            <option value="">Selecione um produto...</option>
            {opcoes_produtos}
          </select>
          <input id="quantidade" type="number" min="1" value="1" inputmode="numeric">
          <button type="button" class="botao secundario" id="btn-adicionar">{ui.icone('plus')} Adicionar</button>
        </div>
        <p class="ajuda" id="estoque-info"></p>
        <div id="mensagem-venda" class="alerta erro oculto"></div>
        <div class="tabela-wrapper carrinho-wrapper">
          <table class="tabela">
            <thead><tr><th>Produto</th><th class="num">Qtd.</th><th class="num">Preço unit.</th><th class="num">Subtotal</th><th></th></tr></thead>
            <tbody id="carrinho-corpo">
              <tr id="carrinho-vazio"><td colspan="5" class="vazio">Carrinho vazio.</td></tr>
            </tbody>
          </table>
        </div>
        <button type="button" class="botao secundario" id="btn-limpar">{ui.icone('refresh')} Limpar carrinho</button>
      </section>
      <aside class="card resumo-venda">
        <h3>Resumo da venda</h3>
        <p class="resumo-cliente" id="resumo-cliente">Cliente: —</p>
        <p class="ajuda" id="resumo-itens">Itens: 0</p>
        <div class="separador"></div>
        <div class="caixa-total">
          <span>TOTAL A PAGAR</span>
          <strong id="total-venda">R$ 0,00</strong>
        </div>
        <button type="button" class="botao primario largura-total" id="btn-finalizar">
          {ui.icone('check')} Finalizar venda
        </button>
      </aside>
    </div>"""
    return ui.layout(ctx, "Nova Venda", "vendas", conteudo)


def pagina_historico(ctx, data_ini=None, data_fim=None, status=None, erro=None):
    registros = venda.listar(data_ini, data_fim, status)
    admin = ctx["usuario"].get("perfil") == "admin"
    linhas = []
    for item in registros:
        acoes = (
            f'<a class="botao pequeno secundario" href="/historico/{item["id"]}">'
            f"{ui.icone('eye')} Detalhes</a>"
        )
        if admin and item["status"] == "concluida":
            acoes += (
                f'<form method="post" action="/historico/{item["id"]}/cancelar" '
                'class="inline" data-confirmar="Cancelar esta venda e devolver os itens ao estoque?">'
                f'{ui.campo_csrf(ctx)}'
                '<button type="submit" class="botao pequeno perigo">'
                f"{ui.icone('x')} Cancelar</button></form>"
            )
        linhas.append(
            f"""<tr>
              <td>#{item['id']}</td>
              <td>{ui.esc(formatar_data_hora(item['data_venda']))}</td>
              <td>{ui.esc(item['cliente_nome'])}</td>
              <td>{ui.esc(item['vendedor_nome'])}</td>
              <td>{ui.esc(item['forma_pagamento'])}</td>
              <td class="num">{ui.esc(formatar_moeda(item['total']))}</td>
              <td>{ui.badge_status(item['status'])}</td>
              <td class="acoes">{acoes}</td>
            </tr>"""
        )
    if not linhas:
        linhas.append(_tabela_vazia(8, "Nenhuma venda encontrada para o filtro."))

    status_opcoes = [
        ("", "Todas"),
        ("concluida", "Concluída"),
        ("cancelada", "Cancelada"),
    ]
    opcoes_status = "".join(
        f'<option value="{valor}" {"selected" if (status or "") == valor else ""}>'
        f"{rotulo}</option>"
        for valor, rotulo in status_opcoes
    )
    alerta = (
        f'<div class="alerta erro"><span>{ui.esc(erro)}</span></div>' if erro else ""
    )

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div><h2>Histórico de Vendas</h2><p>Consulte, detalhe e cancele vendas.</p></div>
    </div>
    {alerta}
    <form method="get" action="/historico" class="card filtros">
      <label>De<input type="date" name="data_ini" value="{ui.esc(data_ini or '')}"></label>
      <label>Até<input type="date" name="data_fim" value="{ui.esc(data_fim or '')}"></label>
      <label>Status<select name="status">{opcoes_status}</select></label>
      <button type="submit" class="botao secundario">{ui.icone('filter')} Filtrar</button>
      <a class="botao secundario" href="/historico">Limpar</a>
    </form>
    <section class="card">
      <div class="tabela-wrapper">
        <table class="tabela">
          <thead><tr><th>ID</th><th>Data</th><th>Cliente</th><th>Vendedor</th><th>Pagamento</th><th class="num">Total</th><th>Status</th><th>Ações</th></tr></thead>
          <tbody>{''.join(linhas)}</tbody>
        </table>
      </div>
    </section>"""
    return ui.layout(ctx, "Histórico de Vendas", "historico", conteudo)


def pagina_detalhes_venda(ctx, venda_id):
    registro, itens = venda.detalhes(venda_id)
    if not registro:
        conteudo = '<section class="card vazio">Venda não encontrada.</section>'
        return ui.layout(ctx, "Venda não encontrada", "historico", conteudo)

    linhas = "".join(
        f"""<tr>
          <td>{ui.esc(item['produto_nome'])}</td>
          <td class="num">{item['quantidade']}</td>
          <td class="num">{ui.esc(formatar_moeda(item['preco_unitario']))}</td>
          <td class="num">{ui.esc(formatar_moeda(item['subtotal']))}</td>
        </tr>"""
        for item in itens
    )
    if not linhas:
        linhas = _tabela_vazia(4, "Nenhum item registrado.")

    admin = ctx["usuario"].get("perfil") == "admin"
    cancelar = ""
    if admin and registro["status"] == "concluida":
        cancelar = f"""
        <form method="post" action="/historico/{registro['id']}/cancelar" class="inline"
              data-confirmar="Cancelar esta venda e devolver os itens ao estoque?">
          {ui.campo_csrf(ctx)}
          <button type="submit" class="botao perigo">{ui.icone('x')} Cancelar venda</button>
        </form>"""

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div><h2>Venda #{registro['id']}</h2><p>Detalhes completos da venda selecionada.</p></div>
      <a class="botao secundario" href="/historico">{ui.icone('historico')} Voltar</a>
    </div>
    <section class="card detalhes-venda">
      <div class="detalhes-grid">
        <div><span>Cliente</span><strong>{ui.esc(registro['cliente_nome'])}</strong></div>
        <div><span>CPF</span><strong>{ui.esc(formatar_cpf(registro['cliente_cpf']))}</strong></div>
        <div><span>Data</span><strong>{ui.esc(formatar_data_hora(registro['data_venda']))}</strong></div>
        <div><span>Vendedor</span><strong>{ui.esc(registro['vendedor_nome'])}</strong></div>
        <div><span>Pagamento</span><strong>{ui.esc(registro['forma_pagamento'])}</strong></div>
        <div><span>Status</span><strong>{ui.badge_status(registro['status'])}</strong></div>
      </div>
    </section>
    <section class="card">
      <div class="tabela-wrapper">
        <table class="tabela">
          <thead><tr><th>Produto</th><th class="num">Qtd.</th><th class="num">Preço unit.</th><th class="num">Subtotal</th></tr></thead>
          <tbody>{linhas}</tbody>
        </table>
      </div>
      <div class="rodape-total">
        <strong>Total: {ui.esc(formatar_moeda(registro['total']))}</strong>
        {cancelar}
      </div>
    </section>"""
    return ui.layout(ctx, f"Venda #{registro['id']}", "historico", conteudo)


def pagina_relatorios(ctx, data_ini, data_fim, erro=None):
    resumo = relatorio.resumo(data_ini, data_fim)
    top = relatorio.top_produtos(data_ini, data_fim)
    formas = relatorio.por_forma_pagamento(data_ini, data_fim)

    cards = "".join(
        [
            _card("Total vendido", formatar_moeda(resumo["total"]), "no período", "banknote", "azul"),
            _card("Vendas no período", resumo["quantidade"], "vendas concluídas", "cart", "ciano"),
            _card("Ticket médio", formatar_moeda(resumo["ticket_medio"]), "por venda", "trending_up", "verde"),
        ]
    )
    linhas_top = "".join(
        f"""<tr>
          <td>{ui.esc(item['nome'])}</td>
          <td class="num">{item['quantidade']}</td>
          <td class="num">{ui.esc(formatar_moeda(item['total']))}</td>
        </tr>"""
        for item in top
    ) or _tabela_vazia(3, "Nenhum produto vendido no período.")
    linhas_formas = "".join(
        f"""<tr>
          <td>{ui.esc(item['forma_pagamento'])}</td>
          <td class="num">{item['quantidade']}</td>
          <td class="num">{ui.esc(formatar_moeda(item['total']))}</td>
        </tr>"""
        for item in formas
    ) or _tabela_vazia(3, "Nenhuma venda no período.")

    alerta = (
        f'<div class="alerta erro"><span>{ui.esc(erro)}</span></div>' if erro else ""
    )
    url_csv = (
        f"/relatorios/exportar?data_ini={quote(data_ini)}&data_fim={quote(data_fim)}"
    )

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div><h2>Relatórios</h2><p>Analise as vendas por período e baixe os dados.</p></div>
      <a class="botao secundario" href="{url_csv}">{ui.icone('download')} Baixar CSV</a>
    </div>
    {alerta}
    <form method="get" action="/relatorios" class="card filtros">
      <label>De<input type="date" name="data_ini" value="{ui.esc(data_ini)}"></label>
      <label>Até<input type="date" name="data_fim" value="{ui.esc(data_fim)}"></label>
      <button type="submit" class="botao primario">{ui.icone('refresh')} Gerar</button>
    </form>
    <section class="cards tres">{cards}</section>
    <div class="grid-duas-colunas">
      <section class="card">
        <div class="card-topo"><h3>Produtos mais vendidos</h3></div>
        <div class="tabela-wrapper">
          <table class="tabela">
            <thead><tr><th>Produto</th><th class="num">Qtd. vendida</th><th class="num">Total</th></tr></thead>
            <tbody>{linhas_top}</tbody>
          </table>
        </div>
      </section>
      <section class="card">
        <div class="card-topo"><h3>Vendas por forma de pagamento</h3></div>
        <div class="tabela-wrapper">
          <table class="tabela">
            <thead><tr><th>Forma</th><th class="num">Qtd.</th><th class="num">Total</th></tr></thead>
            <tbody>{linhas_formas}</tbody>
          </table>
        </div>
      </section>
    </div>"""
    return ui.layout(ctx, "Relatórios", "relatorios", conteudo)


def pagina_usuarios(ctx, novo=False, edit_id=None, senha_id=None):
    registros = usuario.listar()
    registro = usuario.obter(edit_id) if edit_id else None
    senha_registro = usuario.obter(senha_id) if senha_id else None
    mostrar_form = novo or registro is not None
    usuario_atual = ctx["usuario"]
    editando = registro is not None
    editando_proprio = editando and registro["id"] == usuario_atual["id"]

    linhas = []
    for item in registros:
        acoes = (
            f'<a class="botao pequeno secundario" href="/usuarios?edit={item["id"]}">'
            f"{ui.icone('pencil')} Editar</a>"
            f'<a class="botao pequeno secundario" href="/usuarios?senha={item["id"]}">'
            f"{ui.icone('lock')} Senha</a>"
        )
        if item["id"] != usuario_atual["id"]:
            acao = "Desativar" if item["ativo"] else "Ativar"
            acoes += (
                '<form method="post" action="/usuarios/alternar" class="inline" '
                f'data-confirmar="{acao} o usuário \'{ui.esc(item["nome"])}\'?">'
                f'{ui.campo_csrf(ctx)}'
                f'<input type="hidden" name="id" value="{item["id"]}">'
                f'<button type="submit" class="botao pequeno {"perigo" if item["ativo"] else "sucesso"}">'
                f"{ui.icone('power')} {acao}</button></form>"
            )
        status_html = (
            '<span class="badge verde">Ativo</span>'
            if item["ativo"]
            else '<span class="badge cinza">Inativo</span>'
        )
        linhas.append(
            f"""<tr>
              <td>{item['id']}</td>
              <td>{ui.esc(item['nome'])}</td>
              <td>{ui.esc(item['login'])}</td>
              <td>{ui.esc(PERFIS.get(item['perfil'], item['perfil']))}</td>
              <td>{status_html}</td>
              <td class="acoes">{acoes}</td>
            </tr>"""
        )
    if not linhas:
        linhas.append(_tabela_vazia(6, "Nenhum usuário cadastrado."))

    formulario = ""
    if mostrar_form:
        valores = {
            "id": registro["id"] if editando else "",
            "nome": registro["nome"] if editando else "",
            "login": registro["login"] if editando else "",
            "perfil": registro["perfil"] if editando else "vendedor",
        }
        if editando_proprio:
            campo_perfil = (
                f'<input type="hidden" name="perfil" value="{ui.esc(valores["perfil"])}">'
                '<label>Perfil<select disabled>'
                f'<option>{ui.esc(PERFIS.get(valores["perfil"], valores["perfil"]))}</option>'
                "</select></label>"
            )
        else:
            opcoes_perfil = "".join(
                f'<option value="{valor}" {"selected" if valores["perfil"] == valor else ""}>'
                f"{rotulo}</option>"
                for valor, rotulo in PERFIS.items()
            )
            campo_perfil = f"<label>Perfil<select name=\"perfil\">{opcoes_perfil}</select></label>"
        campo_senha = (
            '<label>Senha * (mínimo 6 caracteres)<input type="password" name="senha" required minlength="6"></label>'
            if not editando
            else ""
        )
        formulario = f"""
        <section class="card formulario-card">
          <div class="card-topo"><h3>{'Editar usuário' if editando else 'Novo usuário'}</h3></div>
          <form method="post" action="/usuarios/salvar" class="formulario">
            {ui.campo_csrf(ctx)}
            <input type="hidden" name="id" value="{valores['id']}">
            <div class="form-grid">
              <label>Nome *<input name="nome" required value="{ui.esc(valores['nome'])}"></label>
              <label>Login *<input name="login" required value="{ui.esc(valores['login'])}"></label>
              {campo_senha}
              {campo_perfil}
            </div>
            <div class="acoes-form">
              <button type="submit" class="botao primario">{ui.icone('check')} Salvar</button>
              <a class="botao secundario" href="/usuarios">{ui.icone('x')} Cancelar</a>
            </div>
          </form>
        </section>"""

    formulario_senha = ""
    if senha_registro:
        formulario_senha = f"""
        <section class="card formulario-card">
          <div class="card-topo"><h3>Redefinir senha — {ui.esc(senha_registro['nome'])}</h3></div>
          <form method="post" action="/usuarios/senha" class="formulario">
            {ui.campo_csrf(ctx)}
            <input type="hidden" name="id" value="{senha_registro['id']}">
            <div class="form-grid">
              <label>Nova senha *<input type="password" name="senha" required minlength="6"></label>
              <label>Confirmar senha *<input type="password" name="confirmar" required minlength="6"></label>
            </div>
            <div class="acoes-form">
              <button type="submit" class="botao primario">{ui.icone('check')} Salvar</button>
              <a class="botao secundario" href="/usuarios">{ui.icone('x')} Cancelar</a>
            </div>
          </form>
        </section>"""

    conteudo = f"""
    <div class="cabecalho-pagina">
      <div><h2>Usuários</h2><p>Gestão de acessos e permissões.</p></div>
      <a class="botao primario" href="/usuarios?novo=1">{ui.icone('plus')} Novo usuário</a>
    </div>
    {formulario}
    {formulario_senha}
    <section class="card">
      <div class="tabela-wrapper">
        <table class="tabela">
          <thead><tr><th>ID</th><th>Nome</th><th>Login</th><th>Perfil</th><th>Status</th><th>Ações</th></tr></thead>
          <tbody>{''.join(linhas)}</tbody>
        </table>
      </div>
    </section>"""
    return ui.layout(ctx, "Usuários", "usuarios", conteudo)
