import pytest

from src.models import produto


def test_total_inicial(banco):
    assert produto.total() == 5


def test_criar_produto_formata_nome_e_categoria(banco):
    produto_id = produto.criar("  mouse   gamer ", "PERIFÉRICOS", 10.0, 20.0, 3)
    registro = produto.obter(produto_id)

    assert registro["nome"] == "Mouse gamer"
    assert registro["categoria"] == "Periféricos"
    assert registro["preco_venda"] == pytest.approx(20.0)
    assert registro["estoque"] == 3


def test_criar_produto_sem_nome(banco):
    with pytest.raises(ValueError, match="nome"):
        produto.criar("   ", "Teste", 1.0, 2.0, 1)


def test_listar_busca_por_nome(banco):
    resultados = produto.listar("mouse")
    assert [registro["nome"] for registro in resultados] == ["Mouse sem fio"]


def test_listar_busca_por_categoria(banco):
    resultados = produto.listar("Periféricos")
    nomes = {registro["nome"] for registro in resultados}
    assert nomes == {"Mouse sem fio", "Teclado mecânico", "Webcam HD"}


def test_atualizar_produto(banco, produto_id):
    produto.atualizar(produto_id, "mouse sem fio novo", "ACESSÓRIOS", 30.0, 79.9, 20)
    registro = produto.obter(produto_id)

    assert registro["nome"] == "Mouse sem fio novo"
    assert registro["categoria"] == "Acessórios"
    assert registro["preco_custo"] == pytest.approx(30.0)
    assert registro["preco_venda"] == pytest.approx(79.9)
    assert registro["estoque"] == 20


def test_atualizar_produto_sem_nome(banco, produto_id):
    with pytest.raises(ValueError, match="nome"):
        produto.atualizar(produto_id, "", "Teste", 1.0, 2.0, 1)


def test_excluir_produto(banco):
    produto_id = produto.criar("Produto Temporario", "Teste", 1.0, 2.0, 1)
    produto.excluir(produto_id)
    assert produto.obter(produto_id) is None


def test_excluir_produto_com_venda_bloqueado(banco):
    from src.models import cliente, venda

    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    produto_id = produto.criar("Produto Vendido", "Teste", 1.0, 2.0, 5)
    venda.criar(
        cliente_id, None, "Pix", [{"produto_id": produto_id, "quantidade": 1}]
    )

    with pytest.raises(ValueError, match="vendas registradas"):
        produto.excluir(produto_id)

    assert produto.obter(produto_id) is not None


def test_estoque_baixo(banco):
    baixos = produto.listar_estoque_baixo()
    nomes = {registro["nome"] for registro in baixos}
    assert nomes == {'Monitor 24"', "Webcam HD"}
    assert produto.contar_estoque_baixo() == 2


def test_estoque_baixo_com_limite_personalizado(banco):
    assert produto.contar_estoque_baixo(limite=10) == 4
    assert produto.contar_estoque_baixo(limite=0) == 0
