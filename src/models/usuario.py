import sqlite3

from src.database import conectar
from src.utils.auth import hash_senha, validar_senha, verificar_senha
from src.utils.validacao import formatar_nome

PERFIS = ("admin", "vendedor")


def autenticar(login, senha):
    with conectar() as con:
        usuario = con.execute(
            "SELECT * FROM usuarios WHERE login = ?", (login.strip(),)
        ).fetchone()
    if usuario and usuario["ativo"] and verificar_senha(senha, usuario["senha_hash"]):
        return dict(usuario)
    return None


def listar():
    with conectar() as con:
        return con.execute("SELECT * FROM usuarios ORDER BY nome").fetchall()


def obter(usuario_id):
    with conectar() as con:
        return con.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()


def criar(nome, login, senha, perfil):
    nome = formatar_nome(nome)
    login = login.strip()
    if not nome:
        raise ValueError("O nome do usuário é obrigatório.")
    if not login:
        raise ValueError("O login é obrigatório.")
    if perfil not in PERFIS:
        raise ValueError("Perfil inválido.")
    validar_senha(senha)
    with conectar() as con:
        try:
            cursor = con.execute(
                "INSERT INTO usuarios (nome, login, senha_hash, perfil) VALUES (?, ?, ?, ?)",
                (nome, login, hash_senha(senha), perfil),
            )
        except sqlite3.IntegrityError:
            raise ValueError("Já existe um usuário com este login.")
        return cursor.lastrowid


def atualizar(usuario_id, nome, login, perfil):
    nome = formatar_nome(nome)
    login = login.strip()
    if not nome:
        raise ValueError("O nome do usuário é obrigatório.")
    if not login:
        raise ValueError("O login é obrigatório.")
    if perfil not in PERFIS:
        raise ValueError("Perfil inválido.")
    with conectar() as con:
        try:
            con.execute(
                "UPDATE usuarios SET nome = ?, login = ?, perfil = ? WHERE id = ?",
                (nome, login, perfil, usuario_id),
            )
        except sqlite3.IntegrityError:
            raise ValueError("Já existe um usuário com este login.")


def redefinir_senha(usuario_id, senha):
    validar_senha(senha)
    with conectar() as con:
        con.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (hash_senha(senha), usuario_id),
        )


def alternar_ativo(usuario_id, solicitante_id):
    with conectar() as con:
        usuario = con.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if usuario_id == solicitante_id and usuario["ativo"]:
            raise ValueError("Você não pode desativar o próprio usuário.")
        if usuario["ativo"] and usuario["perfil"] == "admin":
            admins = con.execute(
                "SELECT COUNT(*) FROM usuarios WHERE perfil = 'admin' AND ativo = 1"
            ).fetchone()[0]
            if admins <= 1:
                raise ValueError(
                    "É necessário manter pelo menos um administrador ativo."
                )
        novo_status = 0 if usuario["ativo"] else 1
        con.execute(
            "UPDATE usuarios SET ativo = ? WHERE id = ?", (novo_status, usuario_id)
        )
        return novo_status
