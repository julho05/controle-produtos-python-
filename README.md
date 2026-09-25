# Sistema de Controle de Produtos

Sistema de controle de estoque em linha de comando, feito em Python puro, sem
bibliotecas externas. Os dados ficam em arquivos JSON e sobrevivem entre as
execuções.

Projeto desenvolvido durante meus estudos de Python, evoluído de forma
incremental através de pull requests.

## Como executar

Requer Python 3.6 ou superior (desenvolvido na 3.13).

```bash
git clone https://github.com/julho05/controle-produtos-python-.git
cd controle-produtos-python-
python main.py
```

Não há dependências para instalar.

## O menu

```
---------CONTROLE DE PRODUTOS---------
1 - Cadastrar produtos
2 - Listar produtos
3 - Buscar produtos
4 - Atualizar quantidade
5 - Mostrar valor total do estoque
6 - Excluir Produto
7 - Editar Produto
8 - Entrada/Saída de estoque
9 - Relatório do estoque
10 - Histórico de movimentações
0 - Sair
```

## Funcionalidades

**Cadastro e edição**
Cada produto guarda nome, preço, quantidade e categoria. O sistema recusa nome
vazio, nome já cadastrado, preço ou quantidade negativos e valores que não sejam
números tanto no cadastro quanto na edição.

**Busca por parte do nome**
Com "Caneta Azul" e "Caneta Preta" cadastradas, buscar `caneta` retorna as duas.
Já as operações que alteram ou apagam exigem o nome exato, para não haver risco
de mexer no produto errado.

**Listagem ordenável**
Ordena por nome, preço ou quantidade.

**Entrada e saída de estoque**
Em vez de informar o total final, você registra o movimento: chegaram 20, vendi 3.
Saídas maiores que o estoque disponível são recusadas.

**Relatório**
Total de produtos, itens em estoque, valor total, produto mais caro, mais barato
e alerta de itens com menos de 5 unidades.

```
--------- RELATÓRIO DO ESTOQUE ---------
Produtos cadastrados: 3
Itens em estoque: 65
Valor total: R$ 574.70
Mais caro: Mochila (R$ 89.90)
Mais barato: caneta (R$ 2.50)

Estoque baixo (menos de 5 unidades):
  - Mochila: 3
```

**Histórico de movimentações**
Toda entrada e saída fica registrada com data e hora.

```
25/09/2026 16:33 | Entrada |   20 un | Caneta Azul (ficou com 30)
25/09/2026 16:33 | Saída   |    5 un | Caneta Azul (ficou com 25)
```

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `main.py` | todo o sistema |
| `produtos.json` | os produtos cadastrados |
| `historico.json` | as movimentações de estoque |

Os dois arquivos JSON são criados automaticamente na primeira execução. Se algum
deles estiver corrompido ou vazio, o programa inicia com a lista vazia em vez de
quebrar.

## O que este projeto me ensinou

O código começou com todas as funções repetindo o mesmo laço de busca, e vários
bugs que só apareciam no segundo produto da lista. A evolução foi feita em pull
requests pequenos, um assunto por vez:

- Extrair `encontrar_produto` e `exibir_produto` eliminou código duplicado que
  estava espalhado por cinco funções e era justamente aí que os bugs se
  multiplicavam, porque corrigir um lugar não corrigia os outros quatro.
- Tratar entradas inválidas com `try/except` fez o programa parar de fechar na
  cara do usuário.
- Separar a busca parcial da busca exata evitou que excluir "caneta" apagasse a
  "Caneta Azul" sem avisar.

## Próximos passos

- Reorganizar em classes (`Produto` e `Estoque`)
- Testes automatizados com pytest
- Trocar o JSON por SQLite

## Tecnologias

Python 3, biblioteca padrão apenas (`json`, `datetime`).
