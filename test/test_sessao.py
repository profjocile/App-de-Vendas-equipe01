import pytest

from src.sessao import Sessao


@pytest.fixture(autouse=True)
def limpar_sessao():
    Sessao.encerrar()
    yield
    Sessao.encerrar()


def test_sessao_inicialmente_vazia():
    assert Sessao.usuario() is None
    assert Sessao.e_admin() is False


def test_iniciar_e_encerrar_sessao():
    Sessao.iniciar({"id": 1, "nome": "Administrador", "perfil": "admin"})
    assert Sessao.usuario()["nome"] == "Administrador"
    assert Sessao.e_admin() is True

    Sessao.encerrar()
    assert Sessao.usuario() is None
    assert Sessao.e_admin() is False


def test_sessao_de_vendedor_nao_e_admin():
    Sessao.iniciar({"id": 2, "nome": "João Vendedor", "perfil": "vendedor"})
    assert Sessao.e_admin() is False


def test_sessao_copia_dados_do_usuario():
    dados = {"id": 1, "nome": "Admin", "perfil": "admin"}
    Sessao.iniciar(dados)
    dados["nome"] = "Alterado"

    assert Sessao.usuario()["nome"] == "Admin"
