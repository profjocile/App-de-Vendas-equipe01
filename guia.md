# Guia do Projeto Integrador — App de Vendas

## 1. Visão geral

Aplicativo desktop de vendas feito em **Python**, com interface gráfica em **Tkinter** (biblioteca nativa, sem instalação extra) e banco de dados **SQLite** (arquivo local, sem servidor). O sistema permite cadastrar produtos e clientes, registrar vendas com múltiplos itens, controlar estoque, consultar relatórios e gerenciar usuários com autenticação e permissões por perfil.

**Público-alvo:** pequenos comércios que precisam de um controle básico de vendas.

## 2. Tecnologias escolhidas

| Item | Tecnologia | Motivo |
|------|-----------|--------|
| Linguagem | Python 3.10+ | Simples, exigida pelo projeto |
| Interface | Tkinter + ttk | Nativa do Python, sem dependências externas |
| Banco de dados | SQLite (módulo `sqlite3`) | Arquivo único, zero configuração |
| Segurança | `hashlib` (PBKDF2 + salt) | Senhas nunca são gravadas em texto puro |
| Relatórios | Exportação para CSV | Abre no Excel, sem bibliotecas extras |
| Arquitetura | MVC simplificado (models, views, controllers) | Organização sem complexidade |

> Não é necessário instalar nada além do Python. Sem ORM, sem frameworks web, sem Docker.

## 3. Funcionalidades

### 3.1 Autenticação e usuários
- Tela de login exibida antes do sistema; sem login válido não há acesso
- Senhas armazenadas com hash **PBKDF2 + salt** (nunca em texto puro)
- Dois perfis: **Administrador** e **Vendedor**
- Administrador gerencia usuários: cadastrar, editar, ativar/desativar e redefinir senha
- Não é possível desativar o próprio usuário nem o último administrador ativo
- Botão **Sair** encerra a sessão e volta para a tela de login
- Sessão mantida apenas em memória (fechou o programa, precisa logar de novo)

### 3.2 Produtos
- Cadastrar, editar, listar e excluir produtos
- Campos: código (automático), nome, categoria, preço de custo, preço de venda, quantidade em estoque
- Busca por nome ou categoria
- Alerta visual para produtos com estoque baixo (≤ 5 unidades)
- Nomes e categorias padronizados automaticamente (primeira letra maiúscula, siglas preservadas)

### 3.3 Clientes
- Cadastrar, editar, listar e excluir clientes
- Campos: código (automático), nome, CPF, telefone, e-mail, cidade
- Busca por nome ou CPF
- Validação: nome obrigatório, CPF com 11 dígitos e sem duplicidade, telefone único por cliente
- Nome padronizado com iniciais maiúsculas (ex.: `maria da silva` → `Maria da Silva`)
- CPF armazenado apenas com dígitos e exibido como `000.000.000-00`
- Telefone validado (DDD + 8 ou 9 dígitos), sem duplicidade e exibido como `(11) 98888-1111`
- E-mail salvo em minúsculas e cidade padronizada

### 3.4 Vendas
- Nova venda: selecionar cliente, adicionar vários produtos com quantidade
- Cálculo automático do subtotal por item e do total da venda
- Baixa automática no estoque ao finalizar
- Bloqueio de venda com quantidade maior que o estoque
- Cancelamento de venda com devolução dos itens ao estoque
- Formas de pagamento: Dinheiro, Cartão, Pix
- Registro do vendedor responsável por cada venda

### 3.5 Histórico
- Lista de todas as vendas com filtro por período e status
- Detalhes da venda com itens, quantidades, preços e totais
- Cancelamento de venda (somente Administrador)

### 3.6 Relatórios
- Vendas por período (data inicial e final)
- Total vendido, quantidade de vendas e ticket médio
- Produtos mais vendidos
- Vendas por forma de pagamento
- Exportação do relatório para CSV
- Abertura no Excel instalado (com fallback para o Excel Online)

### 3.7 Dashboard (tela inicial)
- Vendas do dia (quantidade e valor)
- Número de produtos e clientes cadastrados
- Produtos com estoque baixo
- Últimas 5 vendas

### 3.8 Permissões por perfil

| Funcionalidade | Administrador | Vendedor |
|----------------|:-------------:|:--------:|
| Dashboard | Sim | Sim |
| Cadastrar/editar produtos | Sim | Sim |
| Excluir produtos | Sim | Não |
| Cadastrar/editar clientes | Sim | Sim |
| Excluir clientes | Sim | Não |
| Registrar vendas | Sim | Sim |
| Histórico de vendas | Sim | Sim |
| Cancelar vendas | Sim | Não |
| Relatórios | Sim | Não |
| Gerenciar usuários | Sim | Não |

### 3.9 Aparência
- Alternância entre **tema claro** e **tema escuro** no rodapé do menu lateral e na tela de login (com botão de ícone de sol para modo branco e lua para modo escuro)
- A preferência é salva em `config.json` e aplicada na próxima abertura
- Notificações modernas estilo *toast* com aviso sonoro suave e discreto no lugar de popups invasivos
- Cores, tabelas, formulários e mensagens se adaptam ao tema escolhido

### 3.10 Versão web

- Versão web local com as mesmas regras de negócio e o mesmo banco SQLite da versão desktop
- Implementada apenas com a biblioteca padrão (`http.server`), sem Flask, Django ou Jinja
- Acesso pelo botão **Versão Web** no rodapé do menu lateral ou por `python -m web.server`
- Endereço padrão: `http://127.0.0.1:8765`
- Autenticação própria por sessão em memória, cookie `HttpOnly` e proteção CSRF em formulários e na API de vendas
- Telas de dashboard, produtos, clientes, nova venda, histórico, detalhes, relatórios e usuários
- Nova venda via JavaScript com carrinho, validação de estoque e `POST /api/vendas`
- Temas claro/escuro no navegador (preferência salva em `localStorage`)
- Relatórios com download de CSV gerado no servidor
- Configuração por variáveis de ambiente: `VENDAS_WEB_HOST`, `VENDAS_WEB_PORT` e `VENDAS_DB_PATH`

## 4. Modelo de banco de dados (SQLite)

Banco criado automaticamente na primeira execução (`vendas.db`).

### Tabela `usuarios`
| Campo | Tipo | Observação |
|-------|------|-----------|
| id | INTEGER | PK, autoincremento |
| nome | TEXT | Obrigatório |
| login | TEXT | Obrigatório, único |
| senha_hash | TEXT | PBKDF2 + salt (nunca texto puro) |
| perfil | TEXT | `admin` ou `vendedor` |
| ativo | INTEGER | 1 = ativo, 0 = inativo |
| criado_em | TEXT | Data/hora automática |

### Tabela `clientes`
| Campo | Tipo | Observação |
|-------|------|-----------|
| id | INTEGER | PK, autoincremento |
| nome | TEXT | Obrigatório |
| cpf | TEXT | Obrigatório, único |
| telefone | TEXT | Opcional |
| email | TEXT | Opcional |
| cidade | TEXT | Opcional |
| criado_em | TEXT | Data/hora automática |

### Tabela `produtos`
| Campo | Tipo | Observação |
|-------|------|-----------|
| id | INTEGER | PK, autoincremento |
| nome | TEXT | Obrigatório |
| categoria | TEXT | Opcional |
| preco_custo | REAL | ≥ 0 |
| preco_venda | REAL | ≥ 0 |
| estoque | INTEGER | ≥ 0 |
| criado_em | TEXT | Data/hora automática |

### Tabela `vendas`
| Campo | Tipo | Observação |
|-------|------|-----------|
| id | INTEGER | PK, autoincremento |
| cliente_id | INTEGER | FK → clientes.id |
| usuario_id | INTEGER | FK → usuarios.id (vendedor responsável) |
| data_venda | TEXT | Data/hora |
| forma_pagamento | TEXT | Dinheiro / Cartão / Pix |
| total | REAL | Soma dos itens |
| status | TEXT | `concluida` ou `cancelada` |

### Tabela `itens_venda`
| Campo | Tipo | Observação |
|-------|------|-----------|
| id | INTEGER | PK, autoincremento |
| venda_id | INTEGER | FK → vendas.id (exclusão em cascata) |
| produto_id | INTEGER | FK → produtos.id |
| quantidade | INTEGER | > 0 |
| preco_unitario | REAL | Preço no momento da venda |
| subtotal | REAL | quantidade × preço unitário |

**Regras de integridade:**
- Chaves estrangeiras ativadas (`PRAGMA foreign_keys = ON`)
- Exclusão de cliente/produto com vendas vinculadas é bloqueada
- Toda venda é gravada em transação (venda + itens + baixa de estoque juntos)
- Cancelamento também é transacional (status + devolução de estoque)

## 5. Estrutura de pastas

```
projeto-integrador-vendas/
├── main.py                  # Ponto de entrada (login → sistema)
├── guia.md                  # Este guia
├── README.md                # Instruções de uso
├── requirements.txt         # Sem dependências externas (apenas documentação)
├── vendas.db                # Banco (criado automaticamente)
├── config.json              # Preferência de tema (criado ao alternar)
├── exports/                 # Relatórios CSV gerados
└── src/
    ├── __init__.py
    ├── database.py          # Conexão, criação das tabelas, seed inicial
    ├── sessao.py            # Usuário logado em memória
    ├── models/
    │   ├── __init__.py
    │   ├── usuario.py       # Autenticação e CRUD de usuários
    │   ├── cliente.py       # CRUD de clientes
    │   ├── produto.py       # CRUD de produtos
    │   ├── venda.py         # Registro/cancelamento de vendas
    │   └── relatorio.py     # Consultas de relatório e exportação CSV
    ├── views/
    │   ├── __init__.py
    │   ├── app.py           # Janela principal + menu lateral + navegação
    │   ├── tela_login.py    # Tela de autenticação
    │   ├── tela_dashboard.py
    │   ├── tela_produtos.py
    │   ├── tela_clientes.py
    │   ├── tela_vendas.py
    │   ├── tela_historico.py
    │   ├── tela_relatorios.py
    │   └── tela_usuarios.py # Gestão de usuários (somente admin)
    └── utils/
        ├── __init__.py
        ├── auth.py          # Hash e verificação de senha (PBKDF2)
        ├── ui.py            # Cores, estilos e componentes reutilizáveis
        └── validacao.py     # Validações e formatação (moeda, data, números)
```

A versão web fica no pacote `web/` (`server.py`, `pages.py`, `ui.py`, `config.py` e `static/`). O lançador acionado pelo botão desktop está em `src/utils/webapp.py`.

## 6. Telas do sistema

1. **Login** — autenticação com login e senha; mensagem de erro e acesso de demonstração
2. **Dashboard** — cards com indicadores, últimas vendas e estoque baixo
3. **Produtos** — tabela com busca, formulário de cadastro/edição e exclusão (admin)
4. **Clientes** — tabela com busca, formulário de cadastro/edição e exclusão (admin)
5. **Nova Venda** — seleção de cliente, carrinho de itens, total e finalização
6. **Histórico** — vendas com filtro por data/status, detalhes e cancelamento (admin)
7. **Relatórios** — filtro por período, resumo, top produtos, formas de pagamento e CSV (admin)
8. **Usuários** — cadastro, edição, ativação/desativação e redefinição de senha (admin)

Navegação por menu lateral fixo na janela principal, com nome e perfil do usuário logado. Itens restritos aparecem apenas para administradores.

**Identidade visual:** temas claro e escuro com paleta índigo/slate, menu lateral escuro com item ativo em destaque, botões arredondados, cards com ícones, tabelas com linhas zebradas e tela de login em painel duplo (marca + formulário). O tema pode ser alternado no rodapé do menu lateral ou na tela de login.

## 7. Regras de negócio principais

**Autenticação:**
- Login único e senha mínima de 6 caracteres
- Usuário inativo não consegue entrar
- Senhas armazenadas com PBKDF2 (100.000 iterações) + salt aleatório
- Não é possível desativar a própria conta
- Sempre deve existir pelo menos um administrador ativo
- Administrador não altera o próprio perfil pela tela de usuários

**Vendas e estoque:**
- Preço de venda não pode ser menor que zero; estoque não pode ser negativo
- Não é possível vender quantidade superior ao estoque disponível
- Ao finalizar venda: subtrai estoque e grava venda + itens na mesma transação
- Ao cancelar venda: status muda para `cancelada` e estoque é devolvido
- CPF único por cliente (validação de duplicidade)
- Telefone único por cliente (validação contra duplicidade de número)
- Exclusão bloqueada quando existem vendas vinculadas
- Valores monetários exibidos no formato `R$ 0,00`
- Nomes, produtos, categorias, cidades e e-mails são padronizados ao salvar
- CPF é armazenado sem pontuação e telefone é validado, formatado e verificado

## 8. Dados iniciais (seed)

Na primeira execução, o sistema cria automaticamente:

| Usuário | Login | Senha | Perfil |
|---------|-------|-------|--------|
| Administrador do Sistema | `admin` | `admin123` | admin |
| João Vendedor | `vendedor` | `vendedor123` | vendedor |

Também são criados:
- 3 clientes de exemplo
- 5 produtos de exemplo (com estoques variados, incluindo 2 com estoque baixo)
- Nenhuma venda inicial

> Em produção, as senhas padrão devem ser trocadas pelo administrador.

## 9. Etapas de desenvolvimento

1. Estrutura do projeto, conexão com o banco e seed (`database.py`)
2. Utilitários: hash de senha, validações e componentes de interface
3. Models: usuários, clientes, produtos, vendas e relatórios
4. Tela de login + sessão
5. Janela principal com menu lateral, permissões e navegação
6. Tela de produtos (CRUD completo)
7. Tela de clientes (CRUD completo)
8. Tela de nova venda (carrinho + baixa de estoque)
9. Tela de histórico (detalhes + cancelamento)
10. Tela de relatórios (filtros + CSV)
11. Tela de usuários (gestão + redefinição de senha)
12. Dashboard
13. README, revisão final e testes manuais

## 10. Como executar

```powershell
python main.py
```

Requisitos: Python 3.10 ou superior. Nenhuma instalação adicional.

## 11. Roteiro sugerido de apresentação

1. **Abertura** — explicar o problema (controle manual de vendas) e a solução proposta
2. **Login** — entrar como `admin` e mostrar que o sistema bloqueia acesso sem credenciais
3. **Dashboard** — apresentar os indicadores
4. **Produtos** — cadastrar um produto novo e mostrar alerta de estoque baixo
5. **Clientes** — cadastrar um cliente e destacar validação de CPF duplicado
6. **Nova Venda** — montar uma venda com 2 itens, mostrar cálculo do total e finalização
7. **Estoque** — voltar em Produtos e mostrar a baixa automática
8. **Histórico** — abrir detalhes da venda e cancelar (estoque volta)
9. **Relatórios** — gerar relatório do mês e exportar o CSV
10. **Usuários** — mostrar a tela de gestão e explicar os perfis
11. **Permissões** — sair, entrar como `vendedor` e mostrar menus e botões restritos
12. **Encerramento** — arquitetura (MVC), SQLite, segurança das senhas e trabalhos futuros

## 12. O que fica de fora (escopo)

Para manter o projeto simples e adequado ao curso:
- Impressão de cupom fiscal
- Integração com leitor de código de barras
- Controle de fornecedores e compras
- Recuperação de senha por e-mail
- Múltiplos usuários simultâneos ou acesso em rede
- Backup automático do banco

Esses itens podem ser listados como **trabalhos futuros** na apresentação.

## 13. Critérios de aceitação

- [ ] O sistema abre sem erros com `python main.py`
- [ ] Login obrigatório; credenciais inválidas ou usuário inativo são bloqueados
- [ ] Senhas gravadas apenas como hash no banco
- [ ] Menu e ações respeitam o perfil (admin/vendedor)
- [ ] CRUD de produtos e clientes funcional
- [ ] Venda com múltiplos itens calcula total corretamente
- [ ] Estoque é reduzido ao vender e devolvido ao cancelar
- [ ] Venda bloqueada quando estoque é insuficiente
- [ ] Relatório por período gera CSV corretamente
- [ ] Gestão de usuários funcional (criar, editar, ativar/desativar, redefinir senha)
- [ ] Dashboard exibe indicadores atualizados
- [ ] Alternância entre tema claro e escuro funciona e é mantida ao reabrir
- [ ] Nomes, CPF e telefones são padronizados nos cadastros
- [ ] Dados persistem ao fechar e reabrir o programa
