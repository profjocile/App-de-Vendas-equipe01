"""Configuração compartilhada da suíte de testes.

O banco de produção (`vendas.db`) nunca é tocado: cada teste recebe um arquivo
SQLite temporário e isolado.
"""

import os
import tempfile

import pytest

_TMP_DIR = tempfile.mkdtemp(prefix="vendas-testes-")
os.environ["VENDAS_DB_PATH"] = os.path.join(_TMP_DIR, "vendas-testes.db")

from src import database  # noqa: E402


@pytest.fixture
def banco(tmp_path, monkeypatch):
    """Cria um banco novo (com seed) para cada teste."""
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "vendas-teste.db"))
    database.init_db()
    return database


@pytest.fixture
def cliente_id(banco):
    from src.models import cliente

    return cliente.listar("Maria Silva")[0]["id"]


@pytest.fixture
def produto_id(banco):
    from src.models import produto

    return produto.listar("Mouse sem fio")[0]["id"]


@pytest.fixture
def admin(banco):
    from src.models import usuario

    return usuario.autenticar("admin", "admin123")


@pytest.fixture
def vendedor(banco):
    from src.models import usuario

    return usuario.autenticar("vendedor", "vendedor123")
