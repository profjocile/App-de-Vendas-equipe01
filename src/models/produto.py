from src.database import conectar
from src.utils.validacao import formatar_titulo


def listar(busca=""):
    termo = f"%{busca.strip()}%"
    with conectar() as con:
        return con.execute(
            "SELECT * FROM produtos WHERE nome LIKE ? OR categoria LIKE ? ORDER BY nome",
            (termo, termo),
        ).fetchall()


def obter(produto_id):
    with conectar() as con:
        return con.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()


def criar(nome, categoria, preco_custo, preco_venda, estoque):
    nome = formatar_titulo(nome)
    categoria = formatar_titulo(categoria)
    if not nome:
        raise ValueError("O nome do produto é obrigatório.")
    with conectar() as con:
        cursor = con.execute(
            "INSERT INTO produtos (nome, categoria, preco_custo, preco_venda, estoque) VALUES (?, ?, ?, ?, ?)",
            (nome, categoria, preco_custo, preco_venda, estoque),
        )
        return cursor.lastrowid


def atualizar(produto_id, nome, categoria, preco_custo, preco_venda, estoque):
    nome = formatar_titulo(nome)
    categoria = formatar_titulo(categoria)
    if not nome:
        raise ValueError("O nome do produto é obrigatório.")
    with conectar() as con:
        con.execute(
            "UPDATE produtos SET nome = ?, categoria = ?, preco_custo = ?, preco_venda = ?, estoque = ? WHERE id = ?",
            (nome, categoria, preco_custo, preco_venda, estoque, produto_id),
        )


def excluir(produto_id):
    with conectar() as con:
        itens = con.execute(
            "SELECT COUNT(*) FROM itens_venda WHERE produto_id = ?", (produto_id,)
        ).fetchone()[0]
        if itens:
            raise ValueError(
                "Este produto possui vendas registradas e não pode ser excluído."
            )
        con.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def listar_estoque_baixo(limite=5):
    with conectar() as con:
        return con.execute(
            "SELECT * FROM produtos WHERE estoque <= ? ORDER BY estoque ASC, nome",
            (limite,),
        ).fetchall()


def contar_estoque_baixo(limite=5):
    with conectar() as con:
        return con.execute(
            "SELECT COUNT(*) FROM produtos WHERE estoque <= ?", (limite,)
        ).fetchone()[0]


def total():
    with conectar() as con:
        return con.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
