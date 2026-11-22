from datetime import date

import pytest

from src.utils.validacao import (
    formatar_cpf,
    formatar_data_hora,
    formatar_email,
    formatar_moeda,
    formatar_nome,
    formatar_telefone,
    formatar_titulo,
    normalizar_telefone,
    parse_data,
    parse_inteiro,
    parse_moeda,
    somente_digitos,
)


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("maria da silva", "Maria da Silva"),
        ("MARIA DA SILVA", "Maria da Silva"),
        ("  joão   VENDEDOR ", "João VENDEDOR"),
        ("ana-clara souza", "Ana-Clara Souza"),
        ("", ""),
        (None, ""),
    ],
)
def test_formatar_nome(entrada, esperado):
    assert formatar_nome(entrada) == esperado


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("mouse sem fio", "Mouse sem fio"),
        ("MOUSE SEM FIO", "Mouse sem fio"),
        ("  monitor 24\"  ", "Monitor 24\""),
        ("", ""),
    ],
)
def test_formatar_titulo(entrada, esperado):
    assert formatar_titulo(entrada) == esperado


def test_formatar_email():
    assert formatar_email("  TESTE@Email.COM ") == "teste@email.com"
    assert formatar_email(None) == ""


def test_somente_digitos():
    assert somente_digitos("123.456.789-01") == "12345678901"
    assert somente_digitos("(11) 98888-1111") == "11988881111"
    assert somente_digitos("") == ""


def test_formatar_cpf():
    assert formatar_cpf("12345678901") == "123.456.789-01"
    assert formatar_cpf("123") == "123"


def test_formatar_telefone():
    assert formatar_telefone("11988881111") == "(11) 98888-1111"
    assert formatar_telefone("1133334444") == "(11) 3333-4444"
    assert formatar_telefone("") == ""
    assert formatar_telefone(None) == ""


def test_normalizar_telefone():
    assert normalizar_telefone("(11) 98888-1111") == "(11) 98888-1111"
    assert normalizar_telefone("1133334444") == "(11) 3333-4444"
    assert normalizar_telefone("") == ""
    with pytest.raises(ValueError):
        normalizar_telefone("123")


def test_formatar_moeda():
    assert formatar_moeda(1234.5) == "R$ 1.234,50"
    assert formatar_moeda("59.9") == "R$ 59,90"
    assert formatar_moeda(None) == "R$ 0,00"


def test_parse_moeda():
    assert parse_moeda("R$ 1.234,50") == pytest.approx(1234.5)
    assert parse_moeda("1234.50") == pytest.approx(1234.5)
    with pytest.raises(ValueError):
        parse_moeda("")


def test_parse_inteiro():
    assert parse_inteiro(" 5 ") == 5
    with pytest.raises(ValueError):
        parse_inteiro("abc")
    with pytest.raises(ValueError):
        parse_inteiro("1.5")


def test_parse_data():
    assert parse_data("25/12/2024") == date(2024, 12, 25)
    with pytest.raises(ValueError):
        parse_data("2024-12-25")


def test_formatar_data_hora():
    assert formatar_data_hora("2024-01-02 03:04:05") == "02/01/2024 03:04"
    assert formatar_data_hora("2024-01-02") == "02/01/2024"
    assert formatar_data_hora("texto") == "texto"
