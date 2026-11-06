(function () {
  "use strict";

  var raiz = document.documentElement;

  function temaAtual() {
    return raiz.getAttribute("data-tema") || "claro";
  }

  function aplicarTema(tema) {
    raiz.setAttribute("data-tema", tema);
    try {
      localStorage.setItem("tema-vendas", tema);
    } catch (erro) {
      /* armazenamento indisponível */
    }
  }

  document
    .querySelectorAll("#btn-tema, [data-acao-tema]")
    .forEach(function (botao) {
      botao.addEventListener("click", function () {
        aplicarTema(temaAtual() === "claro" ? "escuro" : "claro");
      });
    });

  var corpo = document.body;
  var botaoMenu = document.getElementById("btn-menu");
  var botaoMenuFechar = document.getElementById("btn-menu-fechar");
  var overlayMenu = document.getElementById("menu-overlay");
  var sidebar = document.getElementById("sidebar");

  function menuEstaAberto() {
    return corpo.classList.contains("menu-aberto");
  }

  function abrirMenu() {
    corpo.classList.add("menu-aberto");
    if (overlayMenu) {
      overlayMenu.hidden = false;
    }
    if (botaoMenu) {
      botaoMenu.setAttribute("aria-expanded", "true");
    }
  }

  function fecharMenu() {
    corpo.classList.remove("menu-aberto");
    if (overlayMenu) {
      overlayMenu.hidden = true;
    }
    if (botaoMenu) {
      botaoMenu.setAttribute("aria-expanded", "false");
    }
  }

  if (botaoMenu) {
    botaoMenu.addEventListener("click", function () {
      if (menuEstaAberto()) {
        fecharMenu();
      } else {
        abrirMenu();
      }
    });
  }

  if (botaoMenuFechar) {
    botaoMenuFechar.addEventListener("click", fecharMenu);
  }

  if (overlayMenu) {
    overlayMenu.addEventListener("click", fecharMenu);
  }

  if (sidebar) {
    sidebar.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", fecharMenu);
    });
  }

  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape" && menuEstaAberto()) {
      fecharMenu();
    }
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth > 820 && menuEstaAberto()) {
      fecharMenu();
    }
  });

  document.querySelectorAll(".fechar-alerta").forEach(function (botao) {
    botao.addEventListener("click", function () {
      var alerta = botao.closest(".alerta");
      if (alerta) {
        alerta.remove();
      }
    });
  });

  document.querySelectorAll("form[data-confirmar]").forEach(function (formulario) {
    formulario.addEventListener("submit", function (evento) {
      if (!window.confirm(formulario.dataset.confirmar)) {
        evento.preventDefault();
      }
    });
  });

  var app = document.getElementById("venda-app");
  if (!app) {
    return;
  }

  var metaCsrf = document.querySelector('meta[name="csrf-token"]');
  var csrf = metaCsrf ? metaCsrf.getAttribute("content") : "";
  var seletorCliente = document.getElementById("cliente");
  var seletorPagamento = document.getElementById("pagamento");
  var seletorProduto = document.getElementById("produto");
  var campoQuantidade = document.getElementById("quantidade");
  var botaoAdicionar = document.getElementById("btn-adicionar");
  var botaoLimpar = document.getElementById("btn-limpar");
  var botaoFinalizar = document.getElementById("btn-finalizar");
  var corpoCarrinho = document.getElementById("carrinho-corpo");
  var totalVenda = document.getElementById("total-venda");
  var resumoCliente = document.getElementById("resumo-cliente");
  var resumoItens = document.getElementById("resumo-itens");
  var estoqueInfo = document.getElementById("estoque-info");
  var mensagemVenda = document.getElementById("mensagem-venda");
  var carrinho = [];

  var moeda = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

  function formatar(valor) {
    return moeda.format(Number(valor) || 0);
  }

  function mostrarMensagem(texto) {
    if (!mensagemVenda) {
      return;
    }
    mensagemVenda.textContent = texto;
    mensagemVenda.classList.remove("oculto");
  }

  function esconderMensagem() {
    if (!mensagemVenda) {
      return;
    }
    mensagemVenda.classList.add("oculto");
  }

  function produtoSelecionado() {
    if (!seletorProduto || !seletorProduto.value) {
      return null;
    }
    return seletorProduto.options[seletorProduto.selectedIndex];
  }

  function atualizarEstoque() {
    var opcao = produtoSelecionado();
    if (!opcao || !estoqueInfo) {
      if (estoqueInfo) {
        estoqueInfo.textContent = "";
      }
      return;
    }
    var estoque = Number(opcao.dataset.estoque) || 0;
    var preco = Number(opcao.dataset.preco) || 0;
    estoqueInfo.textContent =
      "Estoque disponível: " + estoque + " un. • Preço: " + formatar(preco);
    if (campoQuantidade) {
      campoQuantidade.max = String(Math.max(estoque, 1));
    }
  }

  function atualizarResumoCliente() {
    if (!resumoCliente || !seletorCliente) {
      return;
    }
    var opcao = seletorCliente.options[seletorCliente.selectedIndex];
    var nome = opcao && seletorCliente.value ? opcao.textContent : "—";
    resumoCliente.textContent = "Cliente: " + nome;
  }

  function linhaVazia() {
    var linha = document.createElement("tr");
    linha.id = "carrinho-vazio";
    var celula = document.createElement("td");
    celula.colSpan = 5;
    celula.className = "vazio";
    celula.textContent = "Carrinho vazio.";
    linha.appendChild(celula);
    return linha;
  }

  function linhaItem(item, indice) {
    var linha = document.createElement("tr");

    var nome = document.createElement("td");
    nome.textContent = item.nome;

    var quantidade = document.createElement("td");
    quantidade.className = "num";
    quantidade.textContent = String(item.quantidade);

    var preco = document.createElement("td");
    preco.className = "num";
    preco.textContent = formatar(item.preco);

    var subtotal = document.createElement("td");
    subtotal.className = "num";
    subtotal.textContent = formatar(item.preco * item.quantidade);

    var acoes = document.createElement("td");
    var remover = document.createElement("button");
    remover.type = "button";
    remover.className = "botao pequeno perigo";
    remover.textContent = "Remover";
    remover.addEventListener("click", function () {
      carrinho.splice(indice, 1);
      renderizar();
    });
    acoes.appendChild(remover);

    linha.appendChild(nome);
    linha.appendChild(quantidade);
    linha.appendChild(preco);
    linha.appendChild(subtotal);
    linha.appendChild(acoes);
    return linha;
  }

  function renderizar() {
    if (!corpoCarrinho) {
      return;
    }
    corpoCarrinho.innerHTML = "";
    if (!carrinho.length) {
      corpoCarrinho.appendChild(linhaVazia());
    } else {
      carrinho.forEach(function (item, indice) {
        corpoCarrinho.appendChild(linhaItem(item, indice));
      });
    }

    var total = carrinho.reduce(function (soma, item) {
      return soma + item.preco * item.quantidade;
    }, 0);
    var quantidadeTotal = carrinho.reduce(function (soma, item) {
      return soma + item.quantidade;
    }, 0);
    if (totalVenda) {
      totalVenda.textContent = formatar(total);
    }
    if (resumoItens) {
      resumoItens.textContent =
        "Itens: " + quantidadeTotal + " • Produtos: " + carrinho.length;
    }
  }

  if (seletorCliente) {
    seletorCliente.addEventListener("change", atualizarResumoCliente);
  }

  if (seletorProduto) {
    seletorProduto.addEventListener("change", function () {
      esconderMensagem();
      atualizarEstoque();
    });
  }

  if (botaoAdicionar) {
    botaoAdicionar.addEventListener("click", function () {
      esconderMensagem();
      var opcao = produtoSelecionado();
      if (!opcao) {
        mostrarMensagem("Selecione um produto.");
        return;
      }
      var quantidade = parseInt(campoQuantidade ? campoQuantidade.value : "1", 10);
      if (!quantidade || quantidade < 1) {
        mostrarMensagem("Informe uma quantidade válida.");
        return;
      }
      var estoque = Number(opcao.dataset.estoque) || 0;
      var existente = carrinho.find(function (item) {
        return item.id === Number(seletorProduto.value);
      });
      var quantidadeNoCarrinho = existente ? existente.quantidade : 0;
      if (quantidade + quantidadeNoCarrinho > estoque) {
        mostrarMensagem(
          "Estoque insuficiente. Disponível: " +
            estoque +
            " un. e já no carrinho: " +
            quantidadeNoCarrinho +
            " un."
        );
        return;
      }
      var preco = Number(opcao.dataset.preco) || 0;
      if (existente) {
        existente.quantidade += quantidade;
      } else {
        carrinho.push({
          id: Number(seletorProduto.value),
          nome: opcao.dataset.nome || opcao.textContent,
          preco: preco,
          quantidade: quantidade,
          estoque: estoque,
        });
      }
      if (campoQuantidade) {
        campoQuantidade.value = "1";
      }
      renderizar();
    });
  }

  if (botaoLimpar) {
    botaoLimpar.addEventListener("click", function () {
      carrinho = [];
      esconderMensagem();
      renderizar();
    });
  }

  if (botaoFinalizar) {
    botaoFinalizar.addEventListener("click", function () {
      esconderMensagem();
      if (!seletorCliente || !seletorCliente.value) {
        mostrarMensagem("Selecione um cliente.");
        return;
      }
      if (!carrinho.length) {
        mostrarMensagem("Adicione pelo menos um produto à venda.");
        return;
      }
      var conteudoOriginal = botaoFinalizar.innerHTML;
      botaoFinalizar.disabled = true;
      botaoFinalizar.textContent = "Finalizando...";

      var dados = {
        csrf: csrf,
        cliente_id: Number(seletorCliente.value),
        forma_pagamento: seletorPagamento ? seletorPagamento.value : "",
        itens: carrinho.map(function (item) {
          return {
            produto_id: item.id,
            quantidade: item.quantidade,
          };
        }),
      };

      fetch("/api/vendas", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrf,
        },
        body: JSON.stringify(dados),
      })
        .then(function (resposta) {
          if (resposta.status === 401) {
            window.location.href = "/login";
            throw new Error("Sessão expirada. Faça login novamente.");
          }
          return resposta
            .json()
            .catch(function () {
              return {};
            })
            .then(function (corpo) {
              if (!resposta.ok) {
                throw new Error(
                  corpo.erro || "Não foi possível registrar a venda."
                );
              }
              return corpo;
            });
        })
        .then(function (resultado) {
          window.location.href = "/historico/" + resultado.venda_id;
        })
        .catch(function (erro) {
          mostrarMensagem(erro.message);
          botaoFinalizar.disabled = false;
          botaoFinalizar.innerHTML = conteudoOriginal;
        });
    });
  }

  atualizarEstoque();
  atualizarResumoCliente();
  renderizar();
})();
