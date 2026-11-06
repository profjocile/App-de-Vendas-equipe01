import csv
import os

from src.database import conectar
from src.models import venda
from src.utils.validacao import formatar_data_hora


def resumo(data_ini, data_fim):
    with conectar() as con:
        linha = con.execute(
            """SELECT COUNT(*) AS quantidade, COALESCE(SUM(total), 0) AS total
               FROM vendas
               WHERE status = 'concluida' AND date(data_venda) BETWEEN ? AND ?""",
            (data_ini, data_fim),
        ).fetchone()
    quantidade = linha["quantidade"]
    total = linha["total"] or 0
    return {
        "quantidade": quantidade,
        "total": total,
        "ticket_medio": (total / quantidade) if quantidade else 0,
    }


def top_produtos(data_ini, data_fim, limite=10):
    with conectar() as con:
        return con.execute(
            """SELECT p.nome, SUM(i.quantidade) AS quantidade, SUM(i.subtotal) AS total
               FROM itens_venda i
               JOIN vendas v ON v.id = i.venda_id
               JOIN produtos p ON p.id = i.produto_id
               WHERE v.status = 'concluida' AND date(v.data_venda) BETWEEN ? AND ?
               GROUP BY p.id
               ORDER BY quantidade DESC, total DESC
               LIMIT ?""",
            (data_ini, data_fim, limite),
        ).fetchall()


def por_forma_pagamento(data_ini, data_fim):
    with conectar() as con:
        return con.execute(
            """SELECT forma_pagamento, COUNT(*) AS quantidade, SUM(total) AS total
               FROM vendas
               WHERE status = 'concluida' AND date(data_venda) BETWEEN ? AND ?
               GROUP BY forma_pagamento
               ORDER BY total DESC""",
            (data_ini, data_fim),
        ).fetchall()


def exportar_csv(caminho, data_ini, data_fim):
    vendas = venda.listar(data_ini, data_fim)
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(
            ["ID", "Data", "Cliente", "Vendedor", "Forma de pagamento", "Status", "Total"]
        )
        for registro in vendas:
            escritor.writerow(
                [
                    registro["id"],
                    formatar_data_hora(registro["data_venda"]),
                    registro["cliente_nome"],
                    registro["vendedor_nome"],
                    registro["forma_pagamento"],
                    "Concluída" if registro["status"] == "concluida" else "Cancelada",
                    f"{registro['total']:.2f}".replace(".", ","),
                ]
            )
    return len(vendas)
