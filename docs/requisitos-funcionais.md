# Requisitos Funcionais — Sistema de Vendas

**Projeto:** Projeto Integrador · **Stack:** Python 3.10+, Tkinter, SQLite, pytest · **Arquitetura:** MVC simplificado (`models`, `views`, `utils`).

## 1. Visão geral
- **Objetivo:** controlar produtos, clientes, vendas, estoque, usuários e relatórios em pequenos comércios.
- **Atores:** Administrador (acesso total), Vendedor (operações do dia a dia) e Sistema (validações, permissões, cálculos e transações).
- **Persistência:** `vendas.db` criado automaticamente; seed com 2 usuários, 3 clientes e 5 produtos.
- **Prioridades:** Essencial, Alta, Média.

## 2. Requisitos Funcionais

| ID | Requisito | Descrição e critérios de aceitação | Prioridade |
|----|-----------|------------------------------------|------------|
| RF-01 | Autenticação e sessão | Login obrigatório; bloqueia credenciais inválidas e usuário inativo; senha em hash PBKDF2+salt; sessão em memória; botão Sair encerra. | Essencial |
| RF-02 | Usuários | Admin lista, cadastra, edita, ativa/desativa e redefine senha; login único; senha ≥ 6; não desativa a si nem o último admin ativo; não rebaixa o próprio perfil. | Essencial |
| RF-03 | Produtos | CRUD com busca por nome/categoria; nome obrigatório; nome e categoria padronizados; estoque baixo ≤ 5; exclusão bloqueada se houver vendas. | Essencial |
| RF-04 | Clientes | CRUD com busca por nome/CPF; nome obrigatório; CPF com 11 dígitos e único; telefone DDD+8/9 dígitos e único; nome/cidade padronizados e e-mail minúsculo; exclusão bloqueada se houver vendas. | Essencial |
| RF-05 | Registro de vendas | Cliente + vários itens; subtotal e total automáticos; formas Dinheiro/Cartão/Pix; baixa de estoque; bloqueia quantidade > estoque; venda, itens e baixa na mesma transação. | Essencial |
| RF-06 | Histórico | Lista com filtros por período/status; detalhes com itens e totais; cancelamento (admin) devolve estoque; venda cancelada não pode ser recancelada. | Essencial |
| RF-07 | Relatórios | Filtro por período; quantidade, total e ticket médio; top produtos; por forma de pagamento; CSV `;`/`utf-8-sig`; abertura no Excel. | Alta |
| RF-08 | Dashboard | Vendas do dia (quantidade/valor), totais de produtos e clientes, estoque baixo e últimas 5 vendas. | Alta |
| RF-09 | Permissões | Admin: tudo. Vendedor: dashboard, produtos/clientes (sem excluir), vendas e histórico; sem cancelar, relatórios ou usuários. | Essencial |
| RF-10 | Aparência | Temas claro/escuro; preferência salva em `config.json` (desktop) e `localStorage` (web). | Média |
| RF-11 | Versão web | Interface local via `http.server` no mesmo banco; sessão, cookie HttpOnly, CSRF e `POST /api/vendas`; variáveis `VENDAS_WEB_HOST/PORT` e `VENDAS_DB_PATH`. | Média |
| RF-12 | Persistência | `init_db()` idempotente cria tabelas, seed e normaliza cadastros; FKs ativas; itens em cascata ao excluir venda. | Essencial |

## 3. Regras de Negócio

| ID | Regra |
|----|-------|
| RN-01 | Usuário inativo não autentica; senhas usam PBKDF2-SHA256 (100.000 iterações) + salt; mínimo 6 caracteres. |
| RN-02 | Login único; perfis `admin`/`vendedor`; sempre pelo menos um admin ativo; ninguém desativa a própria conta. |
| RN-03 | Nome do produto é obrigatório; nome/categoria com inicial maiúscula e siglas preservadas; estoque baixo ≤ 5. |
| RN-04 | Produto ou cliente com vendas registradas não pode ser excluído. |
| RN-05 | Cliente: nome obrigatório; CPF com 11 dígitos, sem pontuação e único; telefone único e válido; e-mail minúsculo. |
| RN-06 | Venda exige cliente válido e ao menos um item; quantidade > 0 e ≤ estoque; forma de pagamento válida. |
| RN-07 | Preço unitário = preço de venda no momento; subtotal = preço × quantidade; total = soma dos subtotais (2 casas). |
| RN-08 | Venda + itens + baixa de estoque são transacionais; cancelamento devolve estoque e grava `cancelada` na mesma transação. |
| RN-09 | Venda cancelada não pode ser cancelada de novo e não entra no resumo, top produtos nem formas de pagamento. |
| RN-10 | Relatórios usam apenas vendas `concluida`; ticket médio = total ÷ quantidade (0 se vazio); CSV exporta canceladas com status. |
| RN-11 | FKs ativas (`PRAGMA foreign_keys = ON`); `busy_timeout` 5000; rollback automático em exceções; seed só quando tabela vazia. |

## 4. Modelo de Dados (SQLite)

| Tabela | Campos principais | Restrições |
|--------|-------------------|------------|
| `usuarios` | id, nome, login, senha_hash, perfil, ativo, criado_em | login UNIQUE; perfil padrão `vendedor` |
| `clientes` | id, nome, cpf, telefone, email, cidade, criado_em | cpf UNIQUE; nome NOT NULL |
| `produtos` | id, nome, categoria, preco_custo, preco_venda, estoque, criado_em | nome NOT NULL; preços/estoque padrão 0 |
| `vendas` | id, cliente_id, usuario_id, data_venda, forma_pagamento, total, status | FK cliente; FK usuário ON DELETE SET NULL |
| `itens_venda` | id, venda_id, produto_id, quantidade, preco_unitario, subtotal | FK venda ON DELETE CASCADE; FK produto |

## 5. Testes

- **Automatizados (pytest):** `test/test_auth.py`, `test_validacao.py`, `test_database.py`, `test_usuarios.py`, `test_produtos.py`, `test_clientes.py`, `test_vendas.py`, `test_relatorios.py`, `test_sessao.py`.
- **Cobertura:** hash/salt, validações e formatação, criação de tabelas/seed/rollback/cascata, autenticação e permissões, CRUD com duplicidades e bloqueios, cálculo/baixa/devolução de estoque, filtros, cancelamento, relatórios e CSV.
- **Isolamento:** cada teste usa banco temporário via `VENDAS_DB_PATH`/`tmp_path`; o `vendas.db` real não é alterado.
- **Execução:** `python -m pip install -r requirements-dev.txt` e `python -m pytest` (110 testes).
- **Aceitação manual:** abrir sistema, login inválido, CRUD, venda com 2 itens, estoque insuficiente, cancelamento, CSV, temas, perfil vendedor, versão web e persistência após reabrir.

## 6. Critérios de Aceitação Gerais
- [ ] Sistema abre com `python main.py`; login obrigatório e usuário inativo bloqueado.
- [ ] Senhas apenas em hash; menus e ações respeitam o perfil.
- [ ] CRUD de produtos/clientes funcional e padronizado.
- [ ] Venda calcula total, reduz estoque e é bloqueada sem saldo; cancelamento devolve.
- [ ] Relatório por período gera CSV; dashboard atualizado.
- [ ] Tema persiste; dados persistem após reabrir.
