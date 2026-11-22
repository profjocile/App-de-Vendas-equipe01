import pytest

from src.models import usuario


def test_autenticar_admin(admin):
    assert admin is not None
    assert admin["login"] == "admin"
    assert admin["perfil"] == "admin"


def test_autenticar_vendedor(vendedor):
    assert vendedor is not None
    assert vendedor["perfil"] == "vendedor"


def test_autenticar_senha_errada(banco):
    assert usuario.autenticar("admin", "senha-errada") is None


def test_autenticar_login_inexistente(banco):
    assert usuario.autenticar("ninguem", "admin123") is None


def test_senha_armazenada_como_hash(banco):
    with banco.conectar() as con:
        registro = con.execute(
            "SELECT senha_hash FROM usuarios WHERE login = 'admin'"
        ).fetchone()
    assert "admin123" not in registro["senha_hash"]
    assert "$" in registro["senha_hash"]


def test_criar_usuario_formata_nome(banco):
    usuario_id = usuario.criar("  maria   vendedora ", "maria", "senha123", "vendedor")
    registro = usuario.obter(usuario_id)
    assert registro["nome"] == "Maria Vendedora"
    assert usuario.autenticar("maria", "senha123") is not None


def test_criar_usuario_login_duplicado(banco):
    with pytest.raises(ValueError, match="login"):
        usuario.criar("Outro Admin", "admin", "senha123", "vendedor")


def test_criar_usuario_perfil_invalido(banco):
    with pytest.raises(ValueError, match="Perfil"):
        usuario.criar("Fulano", "fulano", "senha123", "gerente")


def test_criar_usuario_senha_curta(banco):
    with pytest.raises(ValueError, match="6 caracteres"):
        usuario.criar("Fulano", "fulano", "123", "vendedor")


def test_criar_usuario_sem_nome(banco):
    with pytest.raises(ValueError, match="nome"):
        usuario.criar("   ", "fulano", "senha123", "vendedor")


def test_atualizar_usuario(banco, vendedor):
    usuario.atualizar(vendedor["id"], "joão da silva", "joao", "admin")
    registro = usuario.obter(vendedor["id"])
    assert registro["nome"] == "João da Silva"
    assert registro["login"] == "joao"
    assert registro["perfil"] == "admin"


def test_atualizar_usuario_login_duplicado(banco, vendedor):
    with pytest.raises(ValueError, match="login"):
        usuario.atualizar(vendedor["id"], "João", "admin", "vendedor")


def test_redefinir_senha(banco, vendedor):
    hash_antigo = usuario.obter(vendedor["id"])["senha_hash"]
    usuario.redefinir_senha(vendedor["id"], "novaSenha1")

    assert usuario.obter(vendedor["id"])["senha_hash"] != hash_antigo
    assert usuario.autenticar("vendedor", "vendedor123") is None
    assert usuario.autenticar("vendedor", "novaSenha1") is not None


def test_redefinir_senha_curta(banco, vendedor):
    with pytest.raises(ValueError):
        usuario.redefinir_senha(vendedor["id"], "123")


def test_nao_desativar_proprio_usuario(banco, admin):
    with pytest.raises(ValueError, match="próprio"):
        usuario.alternar_ativo(admin["id"], admin["id"])


def test_nao_desativar_ultimo_admin(banco, admin, vendedor):
    with pytest.raises(ValueError, match="administrador ativo"):
        usuario.alternar_ativo(admin["id"], vendedor["id"])


def test_desativar_e_reativar_vendedor(banco, admin, vendedor):
    novo_status = usuario.alternar_ativo(vendedor["id"], admin["id"])
    assert novo_status == 0
    assert usuario.autenticar("vendedor", "vendedor123") is None

    novo_status = usuario.alternar_ativo(vendedor["id"], admin["id"])
    assert novo_status == 1
    assert usuario.autenticar("vendedor", "vendedor123") is not None


def test_desativar_admin_quando_ha_outro_ativo(banco, admin, vendedor):
    usuario.criar("Segundo Admin", "admin2", "admin123", "admin")
    novo_status = usuario.alternar_ativo(admin["id"], vendedor["id"])
    assert novo_status == 0
    assert usuario.autenticar("admin", "admin123") is None


def test_listar_e_obter(banco):
    registros = usuario.listar()
    assert len(registros) == 2
    logins = {registro["login"] for registro in registros}
    assert logins == {"admin", "vendedor"}
    assert usuario.obter(999999) is None
