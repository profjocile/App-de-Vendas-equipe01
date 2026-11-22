from datetime import date

import pytest

from src.models import cliente, produto, usuario, venda


def _venda(cliente_nome="Maria Silva", forma="Pix", itens=None):
    cliente_id = cliente.listar(cliente_nome)[0]["id"]
    if itens is None:
        produto_id = produto.listar("Mouse sem fio")[0]["id"]
        itens = [{"produto_id": produto_id, "quantidade": 1}]
    return venda.criar(cliente_id, None, forma, itens)


def test_criar_venda_calcula_total_e_baixa_estoque(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    mouse = produto.listar("Mouse sem fio")[0]
    teclado = produto.listar("Teclado mecânico")[0]

    venda_id = venda.criar(
        cliente_id,
        None,
        "Pix",
        [
            {"produto_id": mouse["id"], "quantidade": 2},
            {"produto_id": teclado["id"], "quantidade": 1},
        ],
    )

    registro, itens = venda.detalhes(venda_id)
    assert registro["total"] == pytest.approx(419.70)
    assert len(itens) == 2
    assert produto.obter(mouse["id"])["estoque"] == 13
    assert produto.obter(teclado["id"])["estoque"] == 7


def test_venda_registra_vendedor(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    admin = usuario.autenticar("admin", "admin123")

    venda_id = venda.criar(
        cliente_id,
        admin["id"],
        "Cartão",
        [{"produto_id": produto_id, "quantidade": 1}],
    )

    registro, _ = venda.detalhes(venda_id)
    assert registro["vendedor_nome"] == "Administrador do Sistema"
    assert registro["forma_pagamento"] == "Cartão"


def test_venda_sem_cliente(banco):
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    with pytest.raises(ValueError, match="cliente"):
        venda.criar(None, None, "Pix", [{"produto_id": produto_id, "quantidade": 1}])


def test_venda_sem_itens(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    with pytest.raises(ValueError, match="pelo menos um item"):
        venda.criar(cliente_id, None, "Pix", [])


def test_venda_forma_pagamento_invalida(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    with pytest.raises(ValueError, match="pagamento"):
        venda.criar(
            cliente_id,
            None,
            "Boleto",
            [{"produto_id": produto_id, "quantidade": 1}],
        )


def test_venda_cliente_inexistente(banco):
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    with pytest.raises(ValueError, match="Cliente"):
        venda.criar(
            999999, None, "Pix", [{"produto_id": produto_id, "quantidade": 1}]
        )


def test_venda_produto_inexistente(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    with pytest.raises(ValueError, match="Produto"):
        venda.criar(
            cliente_id, None, "Pix", [{"produto_id": 999999, "quantidade": 1}]
        )


def test_venda_quantidade_invalida(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    with pytest.raises(ValueError, match="Quantidade"):
        venda.criar(
            cliente_id, None, "Pix", [{"produto_id": produto_id, "quantidade": 0}]
        )


def test_venda_estoque_insuficiente_nao_altera_dados(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    produto_id = produto.criar("Item Raro", "Teste", 1.0, 10.0, 1)

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        venda.criar(
            cliente_id, None, "Pix", [{"produto_id": produto_id, "quantidade": 2}]
        )

    assert produto.obter(produto_id)["estoque"] == 1
    with banco.conectar() as con:
        assert con.execute("SELECT COUNT(*) FROM vendas").fetchone()[0] == 0


def test_cancelar_venda_devolve_estoque(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    venda_id = venda.criar(
        cliente_id, None, "Pix", [{"produto_id": produto_id, "quantidade": 3}]
    )

    assert produto.obter(produto_id)["estoque"] == 12
    venda.cancelar(venda_id)

    registro, _ = venda.detalhes(venda_id)
    assert registro["status"] == "cancelada"
    assert produto.obter(produto_id)["estoque"] == 15


def test_cancelar_venda_duas_vezes(banco):
    venda_id = _venda()
    venda.cancelar(venda_id)
    with pytest.raises(ValueError, match="já está cancelada"):
        venda.cancelar(venda_id)


def test_cancelar_venda_inexistente(banco):
    with pytest.raises(ValueError, match="não encontrada"):
        venda.cancelar(999999)


def test_listar_filtra_por_status(banco):
    concluida = _venda()
    cancelada = _venda(forma="Dinheiro")
    venda.cancelar(cancelada)

    ids_concluidas = {registro["id"] for registro in venda.listar(status="concluida")}
    ids_canceladas = {registro["id"] for registro in venda.listar(status="cancelada")}

    assert concluida in ids_concluidas
    assert cancelada not in ids_concluidas
    assert cancelada in ids_canceladas


def test_listar_filtra_por_periodo(banco):
    _venda()
    hoje = date.today().isoformat()

    assert len(venda.listar(hoje, hoje)) == 1
    assert len(venda.listar("2099-01-01", "2099-12-31")) == 0


def test_detalhes_traz_itens(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    mouse = produto.listar("Mouse sem fio")[0]
    teclado = produto.listar("Teclado mecânico")[0]
    venda_id = venda.criar(
        cliente_id,
        None,
        "Dinheiro",
        [
            {"produto_id": mouse["id"], "quantidade": 1},
            {"produto_id": teclado["id"], "quantidade": 2},
        ],
    )

    registro, itens = venda.detalhes(venda_id)
    assert registro["cliente_nome"] == "Maria Silva"
    nomes = {item["produto_nome"] for item in itens}
    assert nomes == {"Mouse sem fio", "Teclado mecânico"}
    assert sum(item["subtotal"] for item in itens) == pytest.approx(
        registro["total"]
    )


def test_ultimas_vendas_respeita_limite(banco):
    for _ in range(3):
        _venda()
    assert len(venda.ultimas(2)) == 2
    assert len(venda.ultimas(10)) == 3


def test_resumo_dia_ignora_canceladas(banco):
    venda_id = _venda(forma="Pix")
    resumo = venda.resumo_dia()
    assert resumo["quantidade"] == 1
    assert resumo["total"] == pytest.approx(59.90)

    venda.cancelar(venda_id)
    resumo = venda.resumo_dia()
    assert resumo["quantidade"] == 0
    assert resumo["total"] == 0
