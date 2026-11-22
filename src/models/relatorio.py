import csv
import os
from datetime import datetime

from src.database import conectar
from src.models import venda
from src.utils import xlsx
from src.utils.validacao import formatar_data_hora


def resumo(data_ini, data_fim):
    with conectar() as con:
        linha = con.execute(
            """SELECT COUNT(*) AS quantidade, COALESCE(SUM(total), 0) AS total
               FROM vendas
               WHERE status = 'concluida' AND date(data_venda) BETWEEN ? AND ?""",
            (data_ini, data_fim),
        ).fetchone()
    quantidade = linha["quantidade"]
    total = linha["total"] or 0
    return {
        "quantidade": quantidade,
        "total": total,
        "ticket_medio": (total / quantidade) if quantidade else 0,
    }


def top_produtos(data_ini, data_fim, limite=10):
    with conectar() as con:
        return con.execute(
            """SELECT p.nome, SUM(i.quantidade) AS quantidade, SUM(i.subtotal) AS total
               FROM itens_venda i
               JOIN vendas v ON v.id = i.venda_id
               JOIN produtos p ON p.id = i.produto_id
               WHERE v.status = 'concluida' AND date(v.data_venda) BETWEEN ? AND ?
               GROUP BY p.id
               ORDER BY quantidade DESC, total DESC
               LIMIT ?""",
            (data_ini, data_fim, limite),
        ).fetchall()


def por_forma_pagamento(data_ini, data_fim):
    with conectar() as con:
        return con.execute(
            """SELECT forma_pagamento, COUNT(*) AS quantidade, SUM(total) AS total
               FROM vendas
               WHERE status = 'concluida' AND date(data_venda) BETWEEN ? AND ?
               GROUP BY forma_pagamento
               ORDER BY total DESC""",
            (data_ini, data_fim),
        ).fetchall()


def _valor(valor):
    try:
        valor = float(valor or 0)
    except (TypeError, ValueError):
        valor = 0.0
    return f"{valor:.2f}".replace(".", ",")


def _escrever_secao(escritor, titulo, cabecalho, linhas, vazio):
    escritor.writerow([])
    escritor.writerow([titulo])
    escritor.writerow(cabecalho)
    if linhas:
        for linha in linhas:
            escritor.writerow(linha)
    else:
        escritor.writerow([vazio])


LARGURAS_EXCEL = (12, 18, 36, 24, 20, 14, 20)
COLUNAS_EXCEL = 7


def _titulo_secao(planilha, titulo):
    planilha.adicionar([None] * COLUNAS_EXCEL, altura=8)
    linha = planilha.adicionar(
        [titulo] + [None] * (COLUNAS_EXCEL - 1),
        [xlsx.ESTILO_SECAO] * COLUNAS_EXCEL,
        altura=24,
    )
    planilha.mesclar(linha, 1, COLUNAS_EXCEL)


def _linha_tabela(planilha, valores, estilos, mesclar_ate=None, altura=20):
    linha = planilha.adicionar(valores, estilos, altura=altura)
    if mesclar_ate:
        planilha.mesclar(linha, 1, mesclar_ate)
    return linha


def exportar_excel(caminho, data_ini, data_fim):
    vendas = venda.listar(data_ini, data_fim)
    resumo_periodo = resumo(data_ini, data_fim)
    produtos = top_produtos(data_ini, data_fim)
    formas = por_forma_pagamento(data_ini, data_fim)

    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    planilha = xlsx.Planilha("Relatório de vendas")
    planilha.definir_larguras(LARGURAS_EXCEL)

    planilha.adicionar(
        ["Relatório de vendas"] + [None] * 6,
        [xlsx.ESTILO_TITULO] * COLUNAS_EXCEL,
        altura=32,
    )
    planilha.mesclar(1, 1, COLUNAS_EXCEL)
    planilha.adicionar(
        ["Período", f"{formatar_data_hora(data_ini)} a {formatar_data_hora(data_fim)}"]
        + [None] * 5,
        [xlsx.ESTILO_ROTULO, xlsx.ESTILO_VALOR] + [xlsx.ESTILO_PADRAO] * 5,
        altura=20,
    )
    planilha.adicionar(
        ["Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M")] + [None] * 5,
        [xlsx.ESTILO_ROTULO, xlsx.ESTILO_VALOR] + [xlsx.ESTILO_PADRAO] * 5,
        altura=20,
    )

    _titulo_secao(planilha, "Resumo do período")
    _linha_tabela(
        planilha,
        ["Indicador", None, None, "Valor", None, None, None],
        [xlsx.ESTILO_CABECALHO] * COLUNAS_EXCEL,
        mesclar_ate=3,
        altura=24,
    )
    _linha_tabela(
        planilha,
        ["Vendas concluídas", None, None, resumo_periodo["quantidade"]]
        + [None] * 3,
        [xlsx.ESTILO_TEXTO] * 3
        + [xlsx.ESTILO_INTEIRO]
        + [xlsx.ESTILO_TEXTO] * 3,
        mesclar_ate=3,
    )
    _linha_tabela(
        planilha,
        ["Total vendido", None, None, resumo_periodo["total"]] + [None] * 3,
        [xlsx.ESTILO_TEXTO] * 3
        + [xlsx.ESTILO_MOEDA]
        + [xlsx.ESTILO_TEXTO] * 3,
        mesclar_ate=3,
    )
    _linha_tabela(
        planilha,
        ["Ticket médio", None, None, resumo_periodo["ticket_medio"]] + [None] * 3,
        [xlsx.ESTILO_TEXTO] * 3
        + [xlsx.ESTILO_MOEDA]
        + [xlsx.ESTILO_TEXTO] * 3,
        mesclar_ate=3,
    )

    _titulo_secao(planilha, "Detalhamento das vendas")
    _linha_tabela(
        planilha,
        [
            "ID",
            "Data",
            "Cliente",
            "Vendedor",
            "Forma de pagamento",
            "Status",
            "Total",
        ],
        [xlsx.ESTILO_CABECALHO] * COLUNAS_EXCEL,
        altura=26,
    )
    if vendas:
        for indice, registro in enumerate(vendas):
            alternado = indice % 2 == 1
            texto = xlsx.ESTILO_TEXTO_ALT if alternado else xlsx.ESTILO_TEXTO
            inteiro = (
                xlsx.ESTILO_INTEIRO_ALT if alternado else xlsx.ESTILO_INTEIRO
            )
            moeda = xlsx.ESTILO_MOEDA_ALT if alternado else xlsx.ESTILO_MOEDA
            status = (
                xlsx.ESTILO_CONCLUIDA
                if registro["status"] == "concluida"
                else xlsx.ESTILO_CANCELADA
            )
            planilha.adicionar(
                [
                    registro["id"],
                    formatar_data_hora(registro["data_venda"]),
                    registro["cliente_nome"],
                    registro["vendedor_nome"],
                    registro["forma_pagamento"],
                    "Concluída" if registro["status"] == "concluida" else "Cancelada",
                    registro["total"],
                ],
                [inteiro, texto, texto, texto, texto, status, moeda],
                altura=20,
            )
    else:
        _linha_tabela(
            planilha,
            ["Nenhuma venda encontrada no período."] + [None] * 6,
            [xlsx.ESTILO_TEXTO] * COLUNAS_EXCEL,
            mesclar_ate=COLUNAS_EXCEL,
            altura=22,
        )

    _titulo_secao(planilha, "Produtos mais vendidos")
    _linha_tabela(
        planilha,
        ["Produto", None, None, "Quantidade vendida", "Total", None, None],
        [xlsx.ESTILO_CABECALHO] * COLUNAS_EXCEL,
        mesclar_ate=3,
        altura=26,
    )
    if produtos:
        for indice, item in enumerate(produtos):
            alternado = indice % 2 == 1
            texto = xlsx.ESTILO_TEXTO_ALT if alternado else xlsx.ESTILO_TEXTO
            inteiro = (
                xlsx.ESTILO_INTEIRO_ALT if alternado else xlsx.ESTILO_INTEIRO
            )
            moeda = xlsx.ESTILO_MOEDA_ALT if alternado else xlsx.ESTILO_MOEDA
            _linha_tabela(
                planilha,
                [
                    item["nome"],
                    None,
                    None,
                    item["quantidade"],
                    item["total"],
                    None,
                    None,
                ],
                [texto, texto, texto, inteiro, moeda, texto, texto],
                mesclar_ate=3,
            )
    else:
        _linha_tabela(
            planilha,
            ["Nenhum produto vendido no período."] + [None] * 6,
            [xlsx.ESTILO_TEXTO] * COLUNAS_EXCEL,
            mesclar_ate=COLUNAS_EXCEL,
            altura=22,
        )

    _titulo_secao(planilha, "Vendas por forma de pagamento")
    _linha_tabela(
        planilha,
        ["Forma de pagamento", None, None, "Quantidade", "Total", None, None],
        [xlsx.ESTILO_CABECALHO] * COLUNAS_EXCEL,
        mesclar_ate=3,
        altura=26,
    )
    if formas:
        for indice, item in enumerate(formas):
            alternado = indice % 2 == 1
            texto = xlsx.ESTILO_TEXTO_ALT if alternado else xlsx.ESTILO_TEXTO
            inteiro = (
                xlsx.ESTILO_INTEIRO_ALT if alternado else xlsx.ESTILO_INTEIRO
            )
            moeda = xlsx.ESTILO_MOEDA_ALT if alternado else xlsx.ESTILO_MOEDA
            _linha_tabela(
                planilha,
                [
                    item["forma_pagamento"],
                    None,
                    None,
                    item["quantidade"],
                    item["total"],
                    None,
                    None,
                ],
                [texto, texto, texto, inteiro, moeda, texto, texto],
                mesclar_ate=3,
            )
    else:
        _linha_tabela(
            planilha,
            ["Nenhuma venda no período."] + [None] * 6,
            [xlsx.ESTILO_TEXTO] * COLUNAS_EXCEL,
            mesclar_ate=COLUNAS_EXCEL,
            altura=22,
        )

    planilha.salvar(caminho)
    return len(vendas)


def exportar_csv(caminho, data_ini, data_fim):
    vendas = venda.listar(data_ini, data_fim)
    resumo_periodo = resumo(data_ini, data_fim)
    produtos = top_produtos(data_ini, data_fim)
    formas = por_forma_pagamento(data_ini, data_fim)

    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")

        escritor.writerow(["Relatório de vendas"])
        escritor.writerow(
            [
                "Período",
                f"{formatar_data_hora(data_ini)} a {formatar_data_hora(data_fim)}",
            ]
        )
        escritor.writerow(
            ["Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M")]
        )

        escritor.writerow([])
        escritor.writerow(["Resumo do período"])
        escritor.writerow(["Indicador", "Valor"])
        escritor.writerow(["Vendas concluídas", resumo_periodo["quantidade"]])
        escritor.writerow(["Total vendido (R$)", _valor(resumo_periodo["total"])])
        escritor.writerow(["Ticket médio (R$)", _valor(resumo_periodo["ticket_medio"])])

        _escrever_secao(
            escritor,
            "Detalhamento das vendas",
            [
                "ID",
                "Data",
                "Cliente",
                "Vendedor",
                "Forma de pagamento",
                "Status",
                "Total (R$)",
            ],
            [
                [
                    registro["id"],
                    formatar_data_hora(registro["data_venda"]),
                    registro["cliente_nome"],
                    registro["vendedor_nome"],
                    registro["forma_pagamento"],
                    "Concluída" if registro["status"] == "concluida" else "Cancelada",
                    _valor(registro["total"]),
                ]
                for registro in vendas
            ],
            "Nenhuma venda encontrada no período.",
        )

        _escrever_secao(
            escritor,
            "Produtos mais vendidos",
            ["Produto", "Quantidade vendida", "Total (R$)"],
            [
                [item["nome"], item["quantidade"], _valor(item["total"])]
                for item in produtos
            ],
            "Nenhum produto vendido no período.",
        )

        _escrever_secao(
            escritor,
            "Vendas por forma de pagamento",
            ["Forma de pagamento", "Quantidade", "Total (R$)"],
            [
                [
                    item["forma_pagamento"],
                    item["quantidade"],
                    _valor(item["total"]),
                ]
                for item in formas
            ],
            "Nenhuma venda no período.",
        )

    return len(vendas)
