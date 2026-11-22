import pytest

from src.models import cliente


def test_total_inicial(banco):
    assert cliente.total() == 3


def test_criar_cliente_formata_dados(banco):
    cliente_id = cliente.criar(
        "  maria   clara ",
        "111.222.333-44",
        "11988887777",
        " MARIA@X.COM ",
        "são paulo",
    )
    registro = cliente.obter(cliente_id)

    assert registro["nome"] == "Maria Clara"
    assert registro["cpf"] == "11122233344"
    assert registro["telefone"] == "(11) 98888-7777"
    assert registro["email"] == "maria@x.com"
    assert registro["cidade"] == "São Paulo"


def test_criar_cliente_sem_nome(banco):
    with pytest.raises(ValueError, match="nome"):
        cliente.criar("   ", "11122233344")


def test_criar_cliente_cpf_invalido(banco):
    with pytest.raises(ValueError, match="11 dígitos"):
        cliente.criar("Fulano", "123")


def test_criar_cliente_cpf_duplicado(banco):
    with pytest.raises(ValueError, match="CPF"):
        cliente.criar("Outro Cliente", "12345678901")


def test_criar_cliente_telefone_duplicado(banco):
    with pytest.raises(ValueError, match="telefone"):
        cliente.criar("Outro Cliente", "11122233344", "(11) 98888-1111")


def test_criar_cliente_telefone_invalido(banco):
    with pytest.raises(ValueError, match="DDD"):
        cliente.criar("Outro Cliente", "11122233344", "123")


def test_listar_por_nome(banco):
    resultados = cliente.listar("maria")
    assert [registro["nome"] for registro in resultados] == ["Maria Silva"]


def test_listar_por_cpf_com_pontuacao(banco):
    resultados = cliente.listar("123.456.789-01")
    assert [registro["nome"] for registro in resultados] == ["Maria Silva"]


def test_atualizar_cliente(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    cliente.atualizar(
        cliente_id,
        "maria clara",
        "12345678901",
        "(11) 97777-0000",
        "NOVO@X.COM",
        "campinas",
    )
    registro = cliente.obter(cliente_id)

    assert registro["nome"] == "Maria Clara"
    assert registro["telefone"] == "(11) 97777-0000"
    assert registro["email"] == "novo@x.com"
    assert registro["cidade"] == "Campinas"


def test_atualizar_cliente_telefone_de_outro(banco):
    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    with pytest.raises(ValueError, match="telefone"):
        cliente.atualizar(
            cliente_id, "Maria Silva", "12345678901", "(21) 97777-2222"
        )


def test_excluir_cliente(banco):
    cliente_id = cliente.criar("Cliente Temporario", "99988877766")
    cliente.excluir(cliente_id)
    assert cliente.obter(cliente_id) is None


def test_excluir_cliente_com_venda_bloqueado(banco):
    from src.models import produto, venda

    cliente_id = cliente.criar("Cliente Comprador", "99988877766")
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    venda.criar(
        cliente_id, None, "Pix", [{"produto_id": produto_id, "quantidade": 1}]
    )

    with pytest.raises(ValueError, match="vendas registradas"):
        cliente.excluir(cliente_id)

    assert cliente.obter(cliente_id) is not None
