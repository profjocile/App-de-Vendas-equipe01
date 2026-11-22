# Sistema de Vendas — Projeto Integrador

Aplicativo desktop de vendas desenvolvido em **Python** com interface **Tkinter** e banco de dados **SQLite**. O sistema possui autenticação, controle de permissões, cadastro de produtos e clientes, registro de vendas, controle de estoque, histórico, relatórios e exportação em CSV. A interface oferece temas claro e escuro, e os cadastros são padronizados automaticamente.

## Requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa (usa apenas a biblioteca padrão)

## Como executar

```powershell
python main.py
```

Na primeira execução, o banco `vendas.db` é criado automaticamente com dados de exemplo.

## Versão web (opcional)

O sistema também possui uma versão web local, feita apenas com a biblioteca padrão do Python e usando o mesmo banco `vendas.db`.

- Pelo aplicativo desktop: clique em **Versão Web** no rodapé do menu lateral. O servidor é iniciado automaticamente e o navegador é aberto.
- Manualmente: execute `python -m web.server` e acesse `http://127.0.0.1:8765`.
- Os logins e senhas são os mesmos da versão desktop.
- Para usar outra porta ou host, defina `VENDAS_WEB_PORT` e `VENDAS_WEB_HOST` antes de iniciar.
- Para usar outro arquivo de banco, defina `VENDAS_DB_PATH`.

A interface web oferece dashboard, produtos, clientes, nova venda, histórico, relatórios, usuários, temas claro/escuro e exportação CSV.

## Acessos padrão

| Perfil | Login | Senha |
|--------|-------|-------|
| Administrador | `admin` | `admin123` |
| Vendedor | `vendedor` | `vendedor123` |

> Recomenda-se trocar as senhas na tela **Usuários** após o primeiro acesso.

## Aparência

O sistema inicia no tema claro. Use o item **Tema escuro** / **Tema claro** no rodapé do menu lateral (ou o botão com ícone de Sol/Lua na tela de login) para alternar. A escolha fica salva em `config.json` na raiz do projeto.

## Funcionalidades

- **Interface moderna**: temas claro e escuro, paleta índigo/slate, botões arredondados, cards com novos ícones vetoriais, notificações toast com toque sonoro suave e login em painel duplo
- **Padronização de cadastros**: nomes com iniciais maiúsculas, CPF e telefone formatados e validados contra duplicidade, e-mail em minúsculas
- **Login e sessão** com senhas protegidas por hash PBKDF2 + salt
- **Permissões por perfil**: administrador acessa tudo; vendedor não exclui registros, não cancela vendas e não acessa relatórios/usuários
- **Produtos**: CRUD com busca, preços, estoque e alerta de estoque baixo
- **Clientes**: CRUD com busca e validação de CPF e telefone único
- **Nova venda**: carrinho com múltiplos itens, cálculo automático, baixa de estoque e formas de pagamento
- **Histórico**: filtros por período/status, detalhes e cancelamento (com devolução ao estoque)
- **Relatórios**: total vendido, ticket médio, produtos mais vendidos, formas de pagamento, exportação CSV e abertura no Excel instalado (ou Excel Online, se não houver Excel no computador)
- **Usuários**: cadastro, edição, ativação/desativação e redefinição de senha
- **Versão web local**: interface completa no navegador usando o mesmo banco, com sessão, CSRF, tema claro/escuro e venda via API
- **Dashboard**: indicadores do dia com ícones ilustrativos, últimas vendas e produtos com estoque baixo

## Estrutura do projeto

```
projeto-integrador-vendas/
├── main.py
├── guia.md
├── vendas.db            # criado automaticamente
├── config.json          # preferência de tema (criado ao alternar)
├── exports/             # relatórios CSV
└── src/
    ├── database.py      # conexão, tabelas e seed
    ├── sessao.py        # usuário logado
    ├── models/          # regras de negócio e acesso ao banco
    ├── views/           # telas Tkinter
    └── utils/           # autenticação, validação e componentes de UI
```

A versão web fica no pacote `web/` (`server.py`, `pages.py`, `ui.py` e `static/`) e o lançador usado pelo botão desktop está em `src/utils/webapp.py`.

## Resetar o banco de dados

Feche o sistema, apague o arquivo `vendas.db` e execute novamente `python main.py`. O banco será recriado com os dados de exemplo.

## Solução de problemas

- **`python` não reconhecido**: instale o Python marcando a opção "Add Python to PATH".
- **Tkinter não encontrado**: no Windows, o Tkinter já vem com o instalador oficial do Python. No Linux, instale o pacote `python3-tk`.
- **Erro ao abrir o banco**: verifique se você tem permissão de escrita na pasta do projeto.

## Documentação completa

O planejamento, modelo de banco, regras de negócio e roteiro de apresentação estão em [`guia.md`](guia.md).

A documentação de requisitos está em [`docs/requisitos-funcionais.md`](docs/requisitos-funcionais.md) — requisitos, regras de negócio, modelo de dados, testes e critérios de aceitação.

## Testes

A suíte automatizada fica em [`test/`](test) e usa **pytest** com banco temporário isolado:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```
