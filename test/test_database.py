import pytest

from src import database


def _contar(tabela):
    with database.conectar() as con:
        return con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]


def _tabelas():
    with database.conectar() as con:
        return {
            linha[0]
            for linha in con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }


def test_init_db_cria_tabelas(banco):
    esperadas = {"usuarios", "clientes", "produtos", "vendas", "itens_venda"}
    assert esperadas <= _tabelas()


def test_seed_inicial(banco):
    assert _contar("usuarios") == 2
    assert _contar("clientes") == 3
    assert _contar("produtos") == 5
    assert _contar("vendas") == 0


def test_init_db_idempotente(banco):
    database.init_db()
    database.init_db()
    assert _contar("usuarios") == 2
    assert _contar("clientes") == 3
    assert _contar("produtos") == 5


def test_chaves_estrangeiras_ativas(banco):
    with database.conectar() as con:
        assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_banco_isolado_por_teste(banco, tmp_path):
    assert banco.DB_PATH == str(tmp_path / "vendas-teste.db")
    assert banco.DB_PATH != "vendas.db"


def test_init_db_normaliza_cadastros(banco):
    with database.conectar() as con:
        con.execute(
            "INSERT INTO clientes (nome, cpf, telefone, email, cidade) VALUES (?, ?, ?, ?, ?)",
            ("joao da silva", "11122233344", "11999998888", "TESTE@X.COM", "sao paulo"),
        )
        con.execute(
            "INSERT INTO produtos (nome, categoria, preco_custo, preco_venda, estoque) VALUES (?, ?, ?, ?, ?)",
            ("mouse gamer", "PERIFÉRICOS", 10.0, 20.0, 4),
        )

    database.init_db()

    with database.conectar() as con:
        cliente = con.execute(
            "SELECT * FROM clientes WHERE cpf = '11122233344'"
        ).fetchone()
        produto = con.execute(
            "SELECT * FROM produtos WHERE nome = 'Mouse gamer'"
        ).fetchone()

    assert cliente["nome"] == "Joao da Silva"
    assert cliente["telefone"] == "(11) 99999-8888"
    assert cliente["email"] == "teste@x.com"
    assert cliente["cidade"] == "Sao Paulo"
    assert produto["categoria"] == "Periféricos"


def test_exclusao_de_venda_remove_itens_em_cascata(banco):
    from src.models import cliente, produto, venda

    cliente_id = cliente.listar("Maria Silva")[0]["id"]
    produto_id = produto.listar("Mouse sem fio")[0]["id"]
    venda_id = venda.criar(
        cliente_id, None, "Pix", [{"produto_id": produto_id, "quantidade": 1}]
    )

    with database.conectar() as con:
        con.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))

    with database.conectar() as con:
        restantes = con.execute(
            "SELECT COUNT(*) FROM itens_venda WHERE venda_id = ?", (venda_id,)
        ).fetchone()[0]
    assert restantes == 0


def test_rollback_em_operacao_com_erro(banco):
    with pytest.raises(ValueError):
        with database.conectar() as con:
            con.execute(
                "INSERT INTO clientes (nome, cpf) VALUES (?, ?)",
                ("Cliente Temporario", "99988877766"),
            )
            raise ValueError("falha proposital")

    with database.conectar() as con:
        total = con.execute(
            "SELECT COUNT(*) FROM clientes WHERE cpf = '99988877766'"
        ).fetchone()[0]
    assert total == 0
