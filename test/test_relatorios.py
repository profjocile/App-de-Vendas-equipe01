import csv
import zipfile
from datetime import date

import pytest

from src.models import cliente, produto, relatorio, venda


def _periodo_hoje():
    hoje = date.today().isoformat()
    return hoje, hoje


def _criar_venda(forma="Pix", quantidade_mouse=2, quantidade_teclado=1):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    mouse = produto.listar("Mouse sem fio")[0]
    teclado = produto.listar("Teclado mecânico")[0]
    return venda.criar(
        cliente_id,
        None,
        forma,
        [
            {"produto_id": mouse["id"], "quantidade": quantidade_mouse},
            {"produto_id": teclado["id"], "quantidade": quantidade_teclado},
        ],
    )


def test_resumo_sem_vendas(banco):
    inicio, fim = _periodo_hoje()
    resumo = relatorio.resumo(inicio, fim)
    assert resumo == {"quantidade": 0, "total": 0, "ticket_medio": 0}


def test_resumo_com_vendas(banco):
    _criar_venda()
    inicio, fim = _periodo_hoje()
    resumo = relatorio.resumo(inicio, fim)

    assert resumo["quantidade"] == 1
    assert resumo["total"] == pytest.approx(419.70)
    assert resumo["ticket_medio"] == pytest.approx(419.70)


def test_resumo_ignora_canceladas(banco):
    venda_id = _criar_venda()
    venda.cancelar(venda_id)
    inicio, fim = _periodo_hoje()

    resumo = relatorio.resumo(inicio, fim)
    assert resumo["quantidade"] == 0
    assert resumo["total"] == 0
    assert resumo["ticket_medio"] == 0


def test_top_produtos(banco):
    _criar_venda(quantidade_mouse=2, quantidade_teclado=1)
    inicio, fim = _periodo_hoje()

    top = relatorio.top_produtos(inicio, fim)
    assert top[0]["nome"] == "Mouse sem fio"
    assert top[0]["quantidade"] == 2
    assert top[0]["total"] == pytest.approx(119.80)


def test_top_produtos_respeita_limite(banco):
    _criar_venda()
    inicio, fim = _periodo_hoje()
    assert len(relatorio.top_produtos(inicio, fim, limite=1)) == 1


def test_por_forma_pagamento(banco):
    _criar_venda(forma="Pix")
    _criar_venda(forma="Pix")
    _criar_venda(forma="Dinheiro")
    inicio, fim = _periodo_hoje()

    formas = {
        registro["forma_pagamento"]: registro
        for registro in relatorio.por_forma_pagamento(inicio, fim)
    }

    assert formas["Pix"]["quantidade"] == 2
    assert formas["Pix"]["total"] == pytest.approx(839.40)
    assert formas["Dinheiro"]["quantidade"] == 1


def _ler_csv(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.reader(arquivo, delimiter=";"))


def _indice_cabecalho(linhas, primeira_coluna):
    for indice, linha in enumerate(linhas):
        if linha and linha[0] == primeira_coluna:
            return indice
    raise AssertionError(f"Cabeçalho '{primeira_coluna}' não encontrado")


def _valor_apos(linhas, rotulo):
    for linha in linhas:
        if linha and linha[0] == rotulo:
            return linha[1]
    raise AssertionError(f"Rótulo '{rotulo}' não encontrado")


def test_exportar_csv(banco, tmp_path):
    _criar_venda()
    inicio, fim = _periodo_hoje()
    caminho = tmp_path / "exports" / "relatorio.csv"

    total = relatorio.exportar_csv(str(caminho), inicio, fim)

    assert total == 1
    assert caminho.exists()
    linhas = _ler_csv(caminho)

    assert linhas[0] == ["Relatório de vendas"]
    assert _indice_cabecalho(linhas, "Período") == 1
    assert _valor_apos(linhas, "Vendas concluídas") == "1"
    assert _valor_apos(linhas, "Total vendido (R$)") == "419,70"
    assert _valor_apos(linhas, "Ticket médio (R$)") == "419,70"

    cabecalho = _indice_cabecalho(linhas, "ID")
    assert linhas[cabecalho] == [
        "ID",
        "Data",
        "Cliente",
        "Vendedor",
        "Forma de pagamento",
        "Status",
        "Total (R$)",
    ]
    registro = linhas[cabecalho + 1]
    assert registro[2] == "Maria Silva"
    assert registro[4] == "Pix"
    assert registro[5] == "Concluída"
    assert registro[6] == "419,70"

    produtos = _indice_cabecalho(linhas, "Produto")
    assert linhas[produtos] == ["Produto", "Quantidade vendida", "Total (R$)"]
    formas = _indice_cabecalho(linhas, "Forma de pagamento")
    assert linhas[formas + 1][0] == "Pix"
    assert linhas[formas + 1][1] == "1"
    assert linhas[formas + 1][2] == "419,70"


def test_exportar_csv_inclui_canceladas(banco, tmp_path):
    venda_id = _criar_venda()
    venda.cancelar(venda_id)
    inicio, fim = _periodo_hoje()
    caminho = tmp_path / "relatorio_cancelado.csv"

    total = relatorio.exportar_csv(str(caminho), inicio, fim)

    assert total == 1
    linhas = _ler_csv(caminho)
    cabecalho = _indice_cabecalho(linhas, "ID")
    assert linhas[cabecalho + 1][5] == "Cancelada"
    assert _valor_apos(linhas, "Vendas concluídas") == "0"
    assert _valor_apos(linhas, "Total vendido (R$)") == "0,00"
    assert _valor_apos(linhas, "Ticket médio (R$)") == "0,00"


def test_exportar_excel(banco, tmp_path):
    _criar_venda()
    inicio, fim = _periodo_hoje()
    caminho = tmp_path / "relatorio.xlsx"

    total = relatorio.exportar_excel(str(caminho), inicio, fim)

    assert total == 1
    assert caminho.exists()
    with zipfile.ZipFile(caminho) as arquivo:
        nomes = arquivo.namelist()
        assert "xl/worksheets/sheet1.xml" in nomes
        assert "xl/styles.xml" in nomes
        planilha = arquivo.read("xl/worksheets/sheet1.xml").decode("utf-8")
        estilos = arquivo.read("xl/styles.xml").decode("utf-8")

    assert "Relatório de vendas" in planilha
    assert "Maria Silva" in planilha
    assert "419.7" in planilha
    assert 'mergeCell ref="A1:G1"' in planilha
    assert "FF2563EB" in estilos
    assert "[$R$-416]" in estilos


def test_exportar_excel_sem_vendas(banco, tmp_path):
    inicio, fim = _periodo_hoje()
    caminho = tmp_path / "relatorio_vazio.xlsx"

    total = relatorio.exportar_excel(str(caminho), inicio, fim)

    assert total == 0
    with zipfile.ZipFile(caminho) as arquivo:
        planilha = arquivo.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert "Nenhuma venda encontrada no período." in planilha
    assert "Nenhum produto vendido no período." in planilha
    assert "Nenhuma venda no período." in planilha
