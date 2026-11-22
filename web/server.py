import hmac
import json
import mimetypes
import os
import re
import secrets
import sys
import tempfile
import threading
import time
import traceback
from datetime import date, datetime
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import init_db
from src.models import cliente, produto, relatorio, usuario, venda
from src.utils.validacao import (
    formatar_moeda,
    parse_inteiro,
    parse_moeda,
)
from web import pages, ui
from web.config import HOST, PORT, URL

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
SESSAO_TTL = 8 * 60 * 60
COOKIE = "vendas_sessao"

SESSOES = {}
SESSOES_LOCK = threading.RLock()
REQUISICOES = 0


def _novo_token():
    return secrets.token_urlsafe(32)


def _dados_usuario(registro):
    campos = ("id", "nome", "login", "perfil", "ativo")
    return {campo: registro[campo] for campo in campos}


def _limpar_sessoes():
    agora = time.time()
    with SESSOES_LOCK:
        expiradas = [
            token
            for token, sessao in SESSOES.items()
            if agora - sessao.get("ultimo", agora) > SESSAO_TTL
        ]
        for token in expiradas:
            SESSOES.pop(token, None)


def _normalizar_periodo(data_ini, data_fim):
    def converter(valor):
        if not valor:
            return None
        return datetime.strptime(valor, "%Y-%m-%d").date().isoformat()

    data_ini = converter(data_ini)
    data_fim = converter(data_fim)
    if data_ini and data_fim and data_ini > data_fim:
        raise ValueError("A data inicial não pode ser maior que a final.")
    return data_ini, data_fim


def _periodo_padrao():
    hoje = date.today()
    return hoje.replace(day=1).isoformat(), hoje.isoformat()


def _inteiro(valor, campo="registro"):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        raise ValueError(f"O campo {campo} é inválido.")


def _inteiro_opcional(valor):
    if not valor:
        return None
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


class ServidorWeb(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class Aplicacao(BaseHTTPRequestHandler):
    server_version = "SistemaVendasWeb/1.0"

    def do_GET(self):
        self._despachar("GET")

    def do_HEAD(self):
        self._despachar("GET")

    def do_POST(self):
        self._despachar("POST")

    def log_message(self, formato, *args):
        print("[web] " + (formato % args))

    def _despachar(self, metodo):
        global REQUISICOES
        REQUISICOES += 1
        if REQUISICOES % 100 == 0:
            _limpar_sessoes()
        self._resposta_enviada = False
        self._nova_sessao = False
        self._remover_cookie = False
        caminho = urlparse(self.path).path
        try:
            self._preparar_sessao()
            for metodo_rota, padrao, funcao in ROTAS:
                if metodo_rota != metodo:
                    continue
                encontrado = re.match(padrao, caminho)
                if encontrado:
                    funcao(self, **encontrado.groupdict())
                    return
            self._erro(404, "Página não encontrada")
        except ConnectionResetError:
            return
        except Exception:
            traceback.print_exc()
            if not self._resposta_enviada:
                self._erro(500, "Erro interno no servidor")

    def _preparar_sessao(self):
        self._nova_sessao = False
        self._remover_cookie = False

        token = None
        cabecalho_cookie = self.headers.get("Cookie", "")
        if cabecalho_cookie:
            cookie = SimpleCookie()
            try:
                cookie.load(cabecalho_cookie)
                if COOKIE in cookie:
                    token = cookie[COOKIE].value
            except CookieError:
                token = None

        with SESSOES_LOCK:
            sessao = SESSOES.get(token) if token else None
            if sessao:
                self.sessao_id = token
                self.sessao = sessao
                sessao["ultimo"] = time.time()
            else:
                self.sessao_id = _novo_token()
                self.sessao = {
                    "usuario": None,
                    "csrf": secrets.token_urlsafe(24),
                    "flash": [],
                    "ultimo": time.time(),
                }
                SESSOES[self.sessao_id] = self.sessao
                self._nova_sessao = True

        dados = self.sessao.get("usuario")
        if not dados:
            return
        registro = usuario.obter(dados["id"])
        with SESSOES_LOCK:
            if not registro or not registro["ativo"]:
                self.sessao["usuario"] = None
            else:
                self.sessao["usuario"] = _dados_usuario(registro)

    def _enviar(self, status, tipo, corpo, cabecalhos=None):
        if isinstance(corpo, str):
            corpo = corpo.encode("utf-8")
        self._resposta_enviada = True
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Cache-Control", "no-store")
        if self._nova_sessao:
            self.send_header(
                "Set-Cookie",
                f"{COOKIE}={self.sessao_id}; Path=/; HttpOnly; SameSite=Lax; "
                f"Max-Age={SESSAO_TTL}",
            )
        if self._remover_cookie:
            self.send_header(
                "Set-Cookie",
                f"{COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0",
            )
        for chave, valor in (cabecalhos or {}).items():
            self.send_header(chave, valor)
        self.end_headers()
        if self.command != "HEAD" and corpo:
            self.wfile.write(corpo)

    def _html(self, conteudo, status=200):
        self._enviar(status, "text/html; charset=utf-8", conteudo)

    def _json(self, dados, status=200):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self._enviar(status, "application/json; charset=utf-8", corpo)

    def _redirecionar(self, destino):
        self._enviar(303, "text/html; charset=utf-8", "", {"Location": destino})

    def _arquivo(self, conteudo, nome_arquivo, tipo):
        nome = quote(nome_arquivo)
        self._enviar(
            200,
            tipo,
            conteudo,
            {
                "Content-Disposition": (
                    f"attachment; filename=\"{nome_arquivo}\"; "
                    f"filename*=UTF-8''{nome}"
                )
            },
        )

    def _csv(self, conteudo, nome_arquivo):
        self._arquivo(conteudo, nome_arquivo, "text/csv; charset=utf-8")

    def _xlsx(self, conteudo, nome_arquivo):
        self._arquivo(
            conteudo,
            nome_arquivo,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def _erro(self, codigo, mensagem):
        if self._resposta_enviada:
            return
        self._html(ui.pagina_erro(codigo, mensagem), codigo)

    def _query(self):
        return {
            chave: valores[0]
            for chave, valores in parse_qs(
                urlparse(self.path).query, keep_blank_values=True
            ).items()
        }

    def _ler_form(self):
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            tamanho = 0
        if tamanho < 0:
            tamanho = 0
        if tamanho > 1_000_000:
            raise ValueError("Requisição muito grande.")
        corpo = self.rfile.read(tamanho).decode("utf-8", "replace")
        dados = parse_qs(corpo, keep_blank_values=True)
        return {chave: valores[0] for chave, valores in dados.items()}

    def _ler_json(self):
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            tamanho = 0
        if tamanho < 0:
            tamanho = 0
        if tamanho > 1_000_000:
            raise ValueError("Requisição muito grande.")
        corpo = self.rfile.read(tamanho).decode("utf-8")
        if not corpo:
            return {}
        try:
            return json.loads(corpo)
        except json.JSONDecodeError:
            raise ValueError("Dados JSON inválidos.")

    def _csrf_valido(self, dados=None):
        token = ""
        if isinstance(dados, dict):
            token = str(dados.get("csrf") or "")
        if not token:
            token = str(self.headers.get("X-CSRF-Token") or "")
        return bool(token) and hmac.compare_digest(
            token, str(self.sessao.get("csrf", ""))
        )

    def _validar_csrf(self, dados=None):
        if self._csrf_valido(dados):
            return True
        self._erro(403, "Sessão expirada. Atualize a página e tente novamente.")
        return False

    def _flash(self, tipo, mensagem):
        with SESSOES_LOCK:
            self.sessao.setdefault("flash", []).append((tipo, mensagem))

    def _pegar_flash(self):
        with SESSOES_LOCK:
            mensagens = list(self.sessao.get("flash", []))
            self.sessao["flash"] = []
        return mensagens

    def _contexto(self):
        return {
            "usuario": self.sessao.get("usuario"),
            "csrf": self.sessao["csrf"],
            "flash": self._pegar_flash(),
        }

    def _render(self, funcao, *args, **kwargs):
        self._html(funcao(self._contexto(), *args, **kwargs))

    def _exigir_login(self):
        usuario_atual = self.sessao.get("usuario")
        if not usuario_atual:
            self._flash("aviso", "Faça login para continuar.")
            self._redirecionar("/login")
            return None
        return usuario_atual

    def _exigir_admin(self):
        usuario_atual = self._exigir_login()
        if not usuario_atual:
            return None
        if usuario_atual.get("perfil") != "admin":
            self._flash("erro", "Acesso restrito a administradores.")
            self._redirecionar("/dashboard")
            return None
        return usuario_atual

    def _usuario_api(self):
        usuario_atual = self.sessao.get("usuario")
        if not usuario_atual:
            self._json({"erro": "Sessão expirada. Faça login novamente."}, 401)
            return None
        return usuario_atual

    def _rotacionar_sessao(self, registro):
        antigo = self.sessao_id
        novo = _novo_token()
        with SESSOES_LOCK:
            SESSOES.pop(antigo, None)
            self.sessao_id = novo
            self.sessao = {
                "usuario": _dados_usuario(registro),
                "csrf": secrets.token_urlsafe(24),
                "flash": [],
                "ultimo": time.time(),
            }
            SESSOES[novo] = self.sessao
        self._nova_sessao = True

    def inicio(self):
        if self.sessao.get("usuario"):
            self._redirecionar("/dashboard")
        else:
            self._redirecionar("/login")

    def health(self):
        self._enviar(200, "text/plain; charset=utf-8", "ok")

    def favicon(self):
        self._enviar(204, "image/x-icon", b"")

    def estatico(self, arquivo):
        caminho = os.path.normpath(os.path.join(STATIC_DIR, arquivo))
        if not caminho.startswith(STATIC_DIR + os.sep) or not os.path.isfile(caminho):
            self._erro(404, "Arquivo não encontrado")
            return
        tipo = mimetypes.guess_type(caminho)[0] or "application/octet-stream"
        with open(caminho, "rb") as arquivo_aberto:
            conteudo = arquivo_aberto.read()
        self._enviar(200, tipo, conteudo)

    def login_get(self):
        if self.sessao.get("usuario"):
            self._redirecionar("/dashboard")
            return
        self._html(ui.pagina_login(self.sessao["csrf"]))

    def login_post(self):
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        login = (form.get("login") or "").strip()
        senha = form.get("senha") or ""
        if not login or not senha:
            self._html(ui.pagina_login(self.sessao["csrf"], "Informe login e senha."))
            return
        registro = usuario.autenticar(login, senha)
        if not registro:
            self._html(
                ui.pagina_login(
                    self.sessao["csrf"],
                    "Login ou senha inválidos, ou usuário inativo.",
                )
            )
            return
        self._rotacionar_sessao(registro)
        self._flash("sucesso", f"Bem-vindo(a), {registro['nome']}!")
        self._redirecionar("/dashboard")

    def logout(self):
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        with SESSOES_LOCK:
            SESSOES.pop(self.sessao_id, None)
        self._remover_cookie = True
        self._redirecionar("/login")

    def dashboard(self):
        if not self._exigir_login():
            return
        self._render(pages.pagina_dashboard)

    def produtos_get(self):
        if not self._exigir_login():
            return
        query = self._query()
        edit_id = _inteiro_opcional(query.get("edit"))
        self._render(
            pages.pagina_produtos,
            q=query.get("q", ""),
            novo=query.get("novo") == "1",
            edit_id=edit_id,
        )

    def produtos_salvar(self):
        if not self._exigir_login():
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        id_registro = (form.get("id") or "").strip()
        destino = "/produtos"
        try:
            nome = form.get("nome") or ""
            categoria = form.get("categoria") or ""
            preco_custo = parse_moeda(form.get("preco_custo") or "0")
            preco_venda = parse_moeda(form.get("preco_venda") or "0")
            estoque = parse_inteiro(form.get("estoque") or "0", "estoque")
            if preco_custo < 0 or preco_venda < 0:
                raise ValueError("Os preços não podem ser negativos.")
            if estoque < 0:
                raise ValueError("O estoque não pode ser negativo.")
            if id_registro:
                destino = f"/produtos?edit={id_registro}"
                produto.atualizar(
                    _inteiro(id_registro),
                    nome,
                    categoria,
                    preco_custo,
                    preco_venda,
                    estoque,
                )
                self._flash("sucesso", f"Produto '{nome}' atualizado com sucesso.")
            else:
                destino = "/produtos?novo=1"
                produto.criar(nome, categoria, preco_custo, preco_venda, estoque)
                self._flash("sucesso", f"Produto '{nome}' cadastrado com sucesso.")
        except ValueError as erro:
            self._flash("erro", str(erro))
            self._redirecionar(destino)
            return
        self._redirecionar("/produtos")

    def produtos_excluir(self):
        if not self._exigir_admin():
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        try:
            produto_id = _inteiro(form.get("id"))
            registro = produto.obter(produto_id)
            produto.excluir(produto_id)
            nome = registro["nome"] if registro else f"#{produto_id}"
            self._flash("sucesso", f"Produto '{nome}' excluído com sucesso.")
        except ValueError as erro:
            self._flash("erro", str(erro))
        self._redirecionar("/produtos")

    def clientes_get(self):
        if not self._exigir_login():
            return
        query = self._query()
        edit_id = _inteiro_opcional(query.get("edit"))
        self._render(
            pages.pagina_clientes,
            q=query.get("q", ""),
            novo=query.get("novo") == "1",
            edit_id=edit_id,
        )

    def clientes_salvar(self):
        if not self._exigir_login():
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        id_registro = (form.get("id") or "").strip()
        destino = "/clientes"
        try:
            nome = form.get("nome") or ""
            cpf = form.get("cpf") or ""
            telefone = form.get("telefone") or ""
            email = form.get("email") or ""
            cidade = form.get("cidade") or ""
            if id_registro:
                destino = f"/clientes?edit={id_registro}"
                cliente.atualizar(
                    _inteiro(id_registro), nome, cpf, telefone, email, cidade
                )
                self._flash("sucesso", f"Cliente '{nome}' atualizado com sucesso.")
            else:
                destino = "/clientes?novo=1"
                cliente.criar(nome, cpf, telefone, email, cidade)
                self._flash("sucesso", f"Cliente '{nome}' cadastrado com sucesso.")
        except ValueError as erro:
            self._flash("erro", str(erro))
            self._redirecionar(destino)
            return
        self._redirecionar("/clientes")

    def clientes_excluir(self):
        if not self._exigir_admin():
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        try:
            cliente_id = _inteiro(form.get("id"))
            registro = cliente.obter(cliente_id)
            cliente.excluir(cliente_id)
            nome = registro["nome"] if registro else f"#{cliente_id}"
            self._flash("sucesso", f"Cliente '{nome}' excluído com sucesso.")
        except ValueError as erro:
            self._flash("erro", str(erro))
        self._redirecionar("/clientes")

    def vendas_get(self):
        if not self._exigir_login():
            return
        self._render(pages.pagina_vendas)

    def api_vendas(self):
        usuario_atual = self._usuario_api()
        if not usuario_atual:
            return
        try:
            dados = self._ler_json()
        except ValueError as erro:
            self._json({"erro": str(erro)}, 400)
            return
        if not isinstance(dados, dict):
            self._json({"erro": "Dados da venda inválidos."}, 400)
            return
        if not self._csrf_valido(dados):
            self._json({"erro": "Sessão expirada. Atualize a página."}, 403)
            return
        try:
            if not dados.get("cliente_id"):
                raise ValueError("Selecione um cliente.")
            cliente_id = _inteiro(dados.get("cliente_id"), "cliente")
            forma_pagamento = str(dados.get("forma_pagamento") or "")
            itens = []
            for item in dados.get("itens") or []:
                if not isinstance(item, dict):
                    raise ValueError("Item da venda inválido.")
                itens.append(
                    {
                        "produto_id": _inteiro(item.get("produto_id"), "produto"),
                        "quantidade": _inteiro(item.get("quantidade"), "quantidade"),
                    }
                )
            venda_id = venda.criar(
                cliente_id,
                usuario_atual["id"],
                forma_pagamento,
                itens,
            )
            registro, _ = venda.detalhes(venda_id)
            total = registro["total"] if registro else 0
            self._flash(
                "sucesso",
                f"Venda #{venda_id} registrada com sucesso! Total: "
                f"{formatar_moeda(total)}",
            )
            self._json({"ok": True, "venda_id": venda_id, "total": total})
        except (ValueError, TypeError, KeyError) as erro:
            self._json({"erro": str(erro) or "Dados da venda inválidos."}, 400)

    def historico_get(self):
        if not self._exigir_login():
            return
        query = self._query()
        status = query.get("status") or None
        if status not in (None, "concluida", "cancelada"):
            status = None
        erro = None
        try:
            data_ini, data_fim = _normalizar_periodo(
                query.get("data_ini"), query.get("data_fim")
            )
        except ValueError as exc:
            erro = str(exc)
            data_ini, data_fim = None, None
        self._render(
            pages.pagina_historico,
            data_ini=data_ini,
            data_fim=data_fim,
            status=status,
            erro=erro,
        )

    def historico_detalhes(self, venda_id):
        if not self._exigir_login():
            return
        self._render(pages.pagina_detalhes_venda, _inteiro(venda_id))

    def historico_cancelar(self, venda_id):
        if not self._exigir_admin():
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        try:
            venda.cancelar(_inteiro(venda_id))
            self._flash(
                "sucesso",
                f"A venda #{venda_id} foi cancelada e o estoque foi devolvido.",
            )
        except ValueError as erro:
            self._flash("erro", str(erro))
        self._redirecionar("/historico")

    def relatorios_get(self):
        if not self._exigir_admin():
            return
        query = self._query()
        padrao_ini, padrao_fim = _periodo_padrao()
        data_ini = query.get("data_ini") or padrao_ini
        data_fim = query.get("data_fim") or padrao_fim
        erro = None
        try:
            data_ini, data_fim = _normalizar_periodo(data_ini, data_fim)
        except ValueError as exc:
            erro = str(exc)
            data_ini, data_fim = padrao_ini, padrao_fim
        self._render(
            pages.pagina_relatorios,
            data_ini,
            data_fim,
            erro,
        )

    def relatorios_exportar(self):
        if not self._exigir_admin():
            return
        query = self._query()
        padrao_ini, padrao_fim = _periodo_padrao()
        try:
            data_ini, data_fim = _normalizar_periodo(
                query.get("data_ini") or padrao_ini,
                query.get("data_fim") or padrao_fim,
            )
        except ValueError as erro:
            self._flash("erro", str(erro))
            self._redirecionar("/relatorios")
            return
        nome = f"relatorio_vendas_{data_ini}_{data_fim}.csv"
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, nome)
            try:
                relatorio.exportar_csv(caminho, data_ini, data_fim)
                with open(caminho, "rb") as arquivo:
                    conteudo = arquivo.read()
            except OSError as erro:
                self._flash("erro", f"Não foi possível gerar o CSV: {erro}")
                self._redirecionar("/relatorios")
                return
        self._csv(conteudo, nome)

    def relatorios_exportar_excel(self):
        if not self._exigir_admin():
            return
        query = self._query()
        padrao_ini, padrao_fim = _periodo_padrao()
        try:
            data_ini, data_fim = _normalizar_periodo(
                query.get("data_ini") or padrao_ini,
                query.get("data_fim") or padrao_fim,
            )
        except ValueError as erro:
            self._flash("erro", str(erro))
            self._redirecionar("/relatorios")
            return
        nome = f"relatorio_vendas_{data_ini}_{data_fim}.xlsx"
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, nome)
            try:
                relatorio.exportar_excel(caminho, data_ini, data_fim)
                with open(caminho, "rb") as arquivo:
                    conteudo = arquivo.read()
            except OSError as erro:
                self._flash("erro", f"Não foi possível gerar a planilha: {erro}")
                self._redirecionar("/relatorios")
                return
        self._xlsx(conteudo, nome)

    def usuarios_get(self):
        if not self._exigir_admin():
            return
        query = self._query()
        self._render(
            pages.pagina_usuarios,
            novo=query.get("novo") == "1",
            edit_id=_inteiro_opcional(query.get("edit")),
            senha_id=_inteiro_opcional(query.get("senha")),
        )

    def usuarios_salvar(self):
        usuario_atual = self._exigir_admin()
        if not usuario_atual:
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        id_registro = (form.get("id") or "").strip()
        destino = "/usuarios"
        try:
            nome = form.get("nome") or ""
            login = form.get("login") or ""
            perfil = form.get("perfil") or ""
            if perfil not in usuario.PERFIS:
                raise ValueError("Selecione um perfil válido.")
            if id_registro:
                usuario_id = _inteiro(id_registro)
                destino = f"/usuarios?edit={usuario_id}"
                registro = usuario.obter(usuario_id)
                if not registro:
                    raise ValueError("Usuário não encontrado.")
                if usuario_id == usuario_atual["id"]:
                    perfil = registro["perfil"]
                if registro["perfil"] == "admin" and perfil != "admin":
                    admins_ativos = sum(
                        1
                        for item in usuario.listar()
                        if item["perfil"] == "admin" and item["ativo"]
                    )
                    if admins_ativos <= 1:
                        raise ValueError(
                            "É necessário manter pelo menos um administrador ativo."
                        )
                usuario.atualizar(usuario_id, nome, login, perfil)
                self._flash("sucesso", f"Usuário '{nome}' atualizado com sucesso.")
            else:
                destino = "/usuarios?novo=1"
                usuario.criar(nome, login, form.get("senha") or "", perfil)
                self._flash("sucesso", f"Usuário '{nome}' cadastrado com sucesso.")
        except ValueError as erro:
            self._flash("erro", str(erro))
            self._redirecionar(destino)
            return
        self._redirecionar("/usuarios")

    def usuarios_senha(self):
        if not self._exigir_admin():
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        try:
            usuario_id = _inteiro(form.get("id"))
            senha = form.get("senha") or ""
            confirmar = form.get("confirmar") or ""
            if senha != confirmar:
                raise ValueError("A confirmação de senha não confere.")
            if not usuario.obter(usuario_id):
                raise ValueError("Usuário não encontrado.")
            usuario.redefinir_senha(usuario_id, senha)
            self._flash("sucesso", "A senha foi redefinida com sucesso.")
        except ValueError as erro:
            self._flash("erro", str(erro))
        self._redirecionar("/usuarios")

    def usuarios_alternar(self):
        usuario_atual = self._exigir_admin()
        if not usuario_atual:
            return
        form = self._ler_form()
        if not self._validar_csrf(form):
            return
        try:
            usuario_id = _inteiro(form.get("id"))
            registro = usuario.obter(usuario_id)
            usuario.alternar_ativo(usuario_id, usuario_atual["id"])
            estado = "ativado" if registro and not registro["ativo"] else "desativado"
            nome = registro["nome"] if registro else f"#{usuario_id}"
            self._flash("sucesso", f"Usuário '{nome}' {estado} com sucesso.")
        except ValueError as erro:
            self._flash("erro", str(erro))
        self._redirecionar("/usuarios")


ROTAS = [
    ("GET", r"^/$", Aplicacao.inicio),
    ("GET", r"^/health$", Aplicacao.health),
    ("GET", r"^/favicon.ico$", Aplicacao.favicon),
    ("GET", r"^/login$", Aplicacao.login_get),
    ("POST", r"^/login$", Aplicacao.login_post),
    ("POST", r"^/logout$", Aplicacao.logout),
    ("GET", r"^/dashboard$", Aplicacao.dashboard),
    ("GET", r"^/produtos$", Aplicacao.produtos_get),
    ("POST", r"^/produtos/salvar$", Aplicacao.produtos_salvar),
    ("POST", r"^/produtos/excluir$", Aplicacao.produtos_excluir),
    ("GET", r"^/clientes$", Aplicacao.clientes_get),
    ("POST", r"^/clientes/salvar$", Aplicacao.clientes_salvar),
    ("POST", r"^/clientes/excluir$", Aplicacao.clientes_excluir),
    ("GET", r"^/vendas$", Aplicacao.vendas_get),
    ("POST", r"^/api/vendas$", Aplicacao.api_vendas),
    ("GET", r"^/historico$", Aplicacao.historico_get),
    ("GET", r"^/historico/(?P<venda_id>\d+)$", Aplicacao.historico_detalhes),
    ("POST", r"^/historico/(?P<venda_id>\d+)/cancelar$", Aplicacao.historico_cancelar),
    ("GET", r"^/relatorios$", Aplicacao.relatorios_get),
    ("GET", r"^/relatorios/exportar$", Aplicacao.relatorios_exportar),
    (
        "GET",
        r"^/relatorios/exportar-excel$",
        Aplicacao.relatorios_exportar_excel,
    ),
    ("GET", r"^/usuarios$", Aplicacao.usuarios_get),
    ("POST", r"^/usuarios/salvar$", Aplicacao.usuarios_salvar),
    ("POST", r"^/usuarios/senha$", Aplicacao.usuarios_senha),
    ("POST", r"^/usuarios/alternar$", Aplicacao.usuarios_alternar),
    ("GET", r"^/static/(?P<arquivo>.+)$", Aplicacao.estatico),
]


def main():
    init_db()
    try:
        servidor = ServidorWeb((HOST, PORT), Aplicacao)
    except OSError as erro:
        print(f"Não foi possível iniciar o servidor em {URL}: {erro}")
        raise SystemExit(1)
    print(f"Versão web disponível em {URL}")
    print("Pressione Ctrl+C para encerrar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor web...")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
