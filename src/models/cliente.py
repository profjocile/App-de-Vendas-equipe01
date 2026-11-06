import sqlite3

from src.database import conectar
from src.utils.validacao import (
    formatar_email,
    formatar_nome,
    normalizar_telefone,
    somente_digitos,
)


def listar(busca=""):
    busca = busca.strip()
    termo = f"%{busca}%"
    digitos = somente_digitos(busca)
    with conectar() as con:
        if digitos:
            return con.execute(
                "SELECT * FROM clientes WHERE nome LIKE ? OR cpf LIKE ? ORDER BY nome",
                (termo, f"%{digitos}%"),
            ).fetchall()
        return con.execute(
            "SELECT * FROM clientes WHERE nome LIKE ? ORDER BY nome",
            (termo,),
        ).fetchall()


def obter(cliente_id):
    with conectar() as con:
        return con.execute(
            "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()


def criar(nome, cpf, telefone="", email="", cidade=""):
    nome = formatar_nome(nome)
    cpf = somente_digitos(cpf)
    telefone = normalizar_telefone(telefone)
    email = formatar_email(email)
    cidade = formatar_nome(cidade)
    if not nome:
        raise ValueError("O nome do cliente é obrigatório.")
    if len(cpf) != 11:
        raise ValueError("O CPF deve conter 11 dígitos.")
    with conectar() as con:
        if telefone:
            existente = con.execute(
                "SELECT id, nome FROM clientes WHERE telefone = ?", (telefone,)
            ).fetchone()
            if existente:
                raise ValueError(
                    f"Já existe um cliente cadastrado com este telefone ({existente['nome']})."
                )
        try:
            cursor = con.execute(
                "INSERT INTO clientes (nome, cpf, telefone, email, cidade) VALUES (?, ?, ?, ?, ?)",
                (nome, cpf, telefone, email, cidade),
            )
        except sqlite3.IntegrityError:
            raise ValueError("Já existe um cliente cadastrado com este CPF.")
        return cursor.lastrowid


def atualizar(cliente_id, nome, cpf, telefone="", email="", cidade=""):
    nome = formatar_nome(nome)
    cpf = somente_digitos(cpf)
    telefone = normalizar_telefone(telefone)
    email = formatar_email(email)
    cidade = formatar_nome(cidade)
    if not nome:
        raise ValueError("O nome do cliente é obrigatório.")
    if len(cpf) != 11:
        raise ValueError("O CPF deve conter 11 dígitos.")
    with conectar() as con:
        if telefone:
            existente = con.execute(
                "SELECT id, nome FROM clientes WHERE telefone = ? AND id != ?",
                (telefone, cliente_id),
            ).fetchone()
            if existente:
                raise ValueError(
                    f"Já existe outro cliente cadastrado com este telefone ({existente['nome']})."
                )
        try:
            con.execute(
                "UPDATE clientes SET nome = ?, cpf = ?, telefone = ?, email = ?, cidade = ? WHERE id = ?",
                (nome, cpf, telefone, email, cidade, cliente_id),
            )
        except sqlite3.IntegrityError:
            raise ValueError("Já existe um cliente cadastrado com este CPF.")


def excluir(cliente_id):
    with conectar() as con:
        vendas = con.execute(
            "SELECT COUNT(*) FROM vendas WHERE cliente_id = ?", (cliente_id,)
        ).fetchone()[0]
        if vendas:
            raise ValueError(
                "Este cliente possui vendas registradas e não pode ser excluído."
            )
        con.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))


def total():
    with conectar() as con:
        return con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
