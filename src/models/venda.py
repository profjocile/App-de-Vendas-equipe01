FORMAS_PAGAMENTO = ("Dinheiro", "Cartão", "Pix")


def criar(cliente_id, usuario_id, forma_pagamento, itens):
    if not cliente_id:
        raise ValueError("Selecione um cliente.")
    if not itens:
        raise ValueError("Adicione pelo menos um item à venda.")
    if forma_pagamento not in FORMAS_PAGAMENTO:
        raise ValueError("Forma de pagamento inválida.")

    from src.database import conectar

    with conectar() as con:
        cliente = con.execute(
            "SELECT id FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()
        if not cliente:
            raise ValueError("Cliente não encontrado.")

        detalhes = []
        total = 0.0
        for item in itens:
            produto = con.execute(
                "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            if not produto:
                raise ValueError("Produto não encontrado.")
            quantidade = int(item["quantidade"])
            if quantidade <= 0:
                raise ValueError("Quantidade inválida.")
            if quantidade > produto["estoque"]:
                raise ValueError(
                    f"Estoque insuficiente para '{produto['nome']}' "
                    f"(disponível: {produto['estoque']})."
                )
            preco = produto["preco_venda"]
            subtotal = round(preco * quantidade, 2)
            total += subtotal
            detalhes.append((produto["id"], quantidade, preco, subtotal))

        total = round(total, 2)
        cursor = con.execute(
            """INSERT INTO vendas (cliente_id, usuario_id, forma_pagamento, total, status)
               VALUES (?, ?, ?, ?, 'concluida')""",
            (cliente_id, usuario_id, forma_pagamento, total),
        )
        venda_id = cursor.lastrowid

        for produto_id, quantidade, preco, subtotal in detalhes:
            con.execute(
                """INSERT INTO itens_venda
                   (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                   VALUES (?, ?, ?, ?, ?)""",
                (venda_id, produto_id, quantidade, preco, subtotal),
            )
            con.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (quantidade, produto_id),
            )
        return venda_id


def listar(data_ini=None, data_fim=None, status=None):
    from src.database import conectar

    sql = """
        SELECT v.*, c.nome AS cliente_nome, COALESCE(u.nome, '—') AS vendedor_nome
        FROM vendas v
        JOIN clientes c ON c.id = v.cliente_id
        LEFT JOIN usuarios u ON u.id = v.usuario_id
        WHERE 1 = 1
    """
    parametros = []
    if data_ini:
        sql += " AND date(v.data_venda) >= ?"
        parametros.append(data_ini)
    if data_fim:
        sql += " AND date(v.data_venda) <= ?"
        parametros.append(data_fim)
    if status:
        sql += " AND v.status = ?"
        parametros.append(status)
    sql += " ORDER BY v.data_venda DESC, v.id DESC"

    with conectar() as con:
        return con.execute(sql, parametros).fetchall()


def detalhes(venda_id):
    from src.database import conectar

    with conectar() as con:
        venda = con.execute(
            """SELECT v.*, c.nome AS cliente_nome, c.cpf AS cliente_cpf,
                      COALESCE(u.nome, '—') AS vendedor_nome
               FROM vendas v
               JOIN clientes c ON c.id = v.cliente_id
               LEFT JOIN usuarios u ON u.id = v.usuario_id
               WHERE v.id = ?""",
            (venda_id,),
        ).fetchone()
        itens = con.execute(
            """SELECT i.*, p.nome AS produto_nome
               FROM itens_venda i
               JOIN produtos p ON p.id = i.produto_id
               WHERE i.venda_id = ?
               ORDER BY i.id""",
            (venda_id,),
        ).fetchall()
    return venda, itens


def cancelar(venda_id):
    from src.database import conectar

    with conectar() as con:
        venda = con.execute(
            "SELECT * FROM vendas WHERE id = ?", (venda_id,)
        ).fetchone()
        if not venda:
            raise ValueError("Venda não encontrada.")
        if venda["status"] == "cancelada":
            raise ValueError("Esta venda já está cancelada.")

        itens = con.execute(
            "SELECT * FROM itens_venda WHERE venda_id = ?", (venda_id,)
        ).fetchall()
        for item in itens:
            con.execute(
                "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        con.execute(
            "UPDATE vendas SET status = 'cancelada' WHERE id = ?", (venda_id,)
        )


def ultimas(limite=5):
    from src.database import conectar

    with conectar() as con:
        return con.execute(
            """SELECT v.*, c.nome AS cliente_nome
               FROM vendas v
               JOIN clientes c ON c.id = v.cliente_id
               ORDER BY v.data_venda DESC, v.id DESC
               LIMIT ?""",
            (limite,),
        ).fetchall()


def resumo_dia():
    from src.database import conectar

    with conectar() as con:
        linha = con.execute(
            """SELECT COUNT(*) AS quantidade, COALESCE(SUM(total), 0) AS total
               FROM vendas
               WHERE status = 'concluida' AND date(data_venda) = date('now', 'localtime')"""
        ).fetchone()
    return {"quantidade": linha["quantidade"], "total": linha["total"]}
