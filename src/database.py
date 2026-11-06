import os
import sqlite3
from contextlib import contextmanager

from src.utils.auth import hash_senha
from src.utils.validacao import (
    formatar_email,
    formatar_nome,
    formatar_telefone,
    formatar_titulo,
    somente_digitos,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("VENDAS_DB_PATH") or os.path.join(BASE_DIR, "vendas.db")


@contextmanager
def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def init_db():
    with conectar() as con:
        con.execute("PRAGMA journal_mode = WAL")
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                perfil TEXT NOT NULL DEFAULT 'vendedor',
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                telefone TEXT,
                email TEXT,
                cidade TEXT,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT,
                preco_custo REAL NOT NULL DEFAULT 0,
                preco_venda REAL NOT NULL DEFAULT 0,
                estoque INTEGER NOT NULL DEFAULT 0,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                usuario_id INTEGER,
                data_venda TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                forma_pagamento TEXT NOT NULL,
                total REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'concluida',
                FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS itens_venda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venda_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            );
            """
        )
    _seed()
    _normalizar_cadastros()


def _normalizar_cadastros():
    with conectar() as con:
        clientes = con.execute(
            "SELECT id, nome, cpf, telefone, email, cidade FROM clientes"
        ).fetchall()
        for registro in clientes:
            nome = formatar_nome(registro["nome"])
            cpf = somente_digitos(registro["cpf"])
            telefone = formatar_telefone(registro["telefone"] or "")
            email = formatar_email(registro["email"] or "")
            cidade = formatar_nome(registro["cidade"] or "")
            if (
                nome,
                cpf,
                telefone,
                email,
                cidade,
            ) != (
                registro["nome"],
                registro["cpf"],
                registro["telefone"],
                registro["email"],
                registro["cidade"],
            ):
                con.execute(
                    "UPDATE clientes SET nome = ?, cpf = ?, telefone = ?, email = ?, cidade = ? WHERE id = ?",
                    (nome, cpf, telefone, email, cidade, registro["id"]),
                )

        produtos = con.execute(
            "SELECT id, nome, categoria FROM produtos"
        ).fetchall()
        for registro in produtos:
            nome = formatar_titulo(registro["nome"])
            categoria = formatar_titulo(registro["categoria"] or "")
            if (nome, categoria) != (registro["nome"], registro["categoria"]):
                con.execute(
                    "UPDATE produtos SET nome = ?, categoria = ? WHERE id = ?",
                    (nome, categoria, registro["id"]),
                )

        usuarios = con.execute("SELECT id, nome FROM usuarios").fetchall()
        for registro in usuarios:
            nome = formatar_nome(registro["nome"])
            if nome != registro["nome"]:
                con.execute(
                    "UPDATE usuarios SET nome = ? WHERE id = ?",
                    (nome, registro["id"]),
                )


def _seed():
    with conectar() as con:
        if con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO usuarios (nome, login, senha_hash, perfil) VALUES (?, ?, ?, ?)",
                [
                    ("Administrador do Sistema", "admin", hash_senha("admin123"), "admin"),
                    ("João Vendedor", "vendedor", hash_senha("vendedor123"), "vendedor"),
                ],
            )

        if con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO clientes (nome, cpf, telefone, email, cidade) VALUES (?, ?, ?, ?, ?)",
                [
                    ("Maria Silva", "12345678901", "(11) 98888-1111", "maria@email.com", "São Paulo"),
                    ("Carlos Souza", "98765432100", "(21) 97777-2222", "carlos@email.com", "Rio de Janeiro"),
                    ("Ana Oliveira", "45678912300", "(31) 96666-3333", "ana@email.com", "Belo Horizonte"),
                ],
            )

        if con.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO produtos (nome, categoria, preco_custo, preco_venda, estoque) VALUES (?, ?, ?, ?, ?)",
                [
                    ("Mouse sem fio", "Periféricos", 25.00, 59.90, 15),
                    ("Teclado mecânico", "Periféricos", 150.00, 299.90, 8),
                    ('Monitor 24"', "Monitores", 550.00, 899.00, 3),
                    ("Headset gamer", "Áudio", 80.00, 189.90, 10),
                    ("Webcam HD", "Periféricos", 90.00, 159.90, 2),
                ],
            )
