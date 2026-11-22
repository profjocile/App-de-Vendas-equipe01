import pytest

from src.utils.auth import ITERACOES, hash_senha, validar_senha, verificar_senha


def test_hash_nao_guarda_senha_em_texto_puro():
    senha = "minhaSenha123"
    hash_gerado = hash_senha(senha)
    assert senha not in hash_gerado
    assert "$" in hash_gerado


def test_hash_usa_salt_aleatorio():
    primeiro = hash_senha("senha123")
    segundo = hash_senha("senha123")
    assert primeiro != segundo
    assert verificar_senha("senha123", primeiro)
    assert verificar_senha("senha123", segundo)


def test_verificar_senha_correta():
    assert verificar_senha("admin123", hash_senha("admin123"))


def test_verificar_senha_incorreta():
    assert not verificar_senha("errada", hash_senha("admin123"))


@pytest.mark.parametrize("hash_invalido", ["", "sem-separador", "abc$xyz", None])
def test_verificar_hash_invalido_retorna_false(hash_invalido):
    assert verificar_senha("qualquer", hash_invalido) is False


def test_validar_senha_minima():
    validar_senha("123456")
    with pytest.raises(ValueError):
        validar_senha("12345")


def test_iteracoes_documentadas():
    assert ITERACOES == 100_000
