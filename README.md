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

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

São 101 testes, divididos em quatro arquivos: as regras do `Produto`, as do
`Estoque` com arquivos temporários, a interface de menu com o teclado simulado
e a identidade do produto no histórico. A suíte não toca nos seus
`produtos.json` e `historico.json` — cada teste trabalha num diretório próprio
criado pelo pytest.

O que mais importa ali é a regra que o projeto promete: a soma dos movimentos de
um produto tem que fechar com o saldo dele.

## O menu

```
---------CONTROLE DE PRODUTOS---------
1 - Cadastrar produtos
2 - Listar produtos
3 - Buscar produtos
4 - Entrada/Saída/Ajuste de estoque
5 - Mostrar valor total do estoque
6 - Excluir Produto
7 - Editar Produto
8 - Relatório do estoque
9 - Histórico de movimentações
0 - Sair
```

## Funcionalidades

**Cadastro e edição**
Cada produto guarda nome, preço, quantidade e categoria. O sistema recusa nome
vazio, nome já cadastrado, preço ou quantidade negativos e valores que não sejam
números tanto no cadastro quanto na edição. As regras ficam dentro do `Produto`,
então não há como criar ou editar um produto inválido por nenhum caminho.

Preço pode ser digitado do jeito brasileiro: `2,50` e `2.50` valem a mesma
coisa. Produto cadastrado sem categoria entra como "Sem categoria".

**Busca por parte do nome**
Com "Caneta Azul" e "Caneta Preta" cadastradas, buscar `caneta` retorna as duas.
Já as operações que alteram ou apagam exigem o nome exato, para não haver risco
de mexer no produto errado.

**Listagem ordenável**
Ordena por nome, preço, quantidade ou categoria.

**Entrada, saída e ajuste de estoque**
Em vez de informar o total final, você registra o movimento: chegaram 20, vendi 3.
Saídas maiores que o estoque disponível são recusadas.

Quando a contagem física discorda do sistema, o ajuste corrige o saldo e fica
registrado como tal, com a diferença aplicada:

```
29/09/2026 17:01 | Ajuste  |  -13 un | Arroz (ficou com 12)
```

**O histórico acompanha o produto, não o nome**
Cada produto tem um `id` gerado no cadastro, e é por ele que a movimentação
aponta. Renomear "Arroz" para "Arroz Branco" não desliga o produto do histórico
dele: a listagem passa a mostrar o nome novo também nos movimentos antigos.

O nome gravado em cada movimentação é o que o produto se chamava naquele
momento, e serve para quando o produto é excluído — aí o histórico continua
mostrando esse nome, marcado como excluído:

```
29/09/2026 17:01 | Entrada |    3 un | Mochila (excluído) (ficou com 3)
```

Arquivos gravados antes dessa mudança são migrados sozinhos na primeira
execução: os produtos ganham id e as movimentações são casadas pelo nome. O que
não casar com nenhum produto continua aparecendo pelo nome da época.

**A quantidade só muda por movimento**
Não existe caminho para alterar a quantidade sem deixar registro. O cadastro de
um produto com saldo inicial já entra como uma entrada, e o editar não mexe em
quantidade — só em nome, preço e categoria. Por isso vale a regra de que a soma
dos movimentos de um produto é igual ao saldo dele.

Na prática isso significa que o histórico pode ser usado para conferir o
estoque, o que antes não era verdade: existiam dois outros caminhos que
alteravam a quantidade em silêncio.

**Relatório**
Total de produtos, itens em estoque, valor total, produto mais caro, mais
barato, a quebra por categoria e o alerta de itens com menos de 5 unidades.

```
--------- RELATÓRIO DO ESTOQUE ---------
Produtos cadastrados: 3
Itens em estoque: 65
Valor total: R$ 574.70
Mais caro: Mochila (R$ 89.90)
Mais barato: caneta (R$ 2.50)

Por categoria:
  - Bolsas: 1 produto(s), 3 itens, R$ 269.70
  - Material: 2 produto(s), 62 itens, R$ 305.00

Estoque baixo (menos de 5 unidades):
  - Mochila: 3
```

**Histórico de movimentações**
Toda entrada e saída fica registrada com data e hora.

```
25/09/2026 16:33 | Entrada |   20 un | Caneta Azul (ficou com 30)
25/09/2026 16:33 | Saída   |    5 un | Caneta Azul (ficou com 25)
```

No arquivo a data é gravada em ISO (`2026-09-25T16:33`) e formatada só na hora
de exibir, para que mais tarde dê para ordenar e filtrar por período sem
precisar reinterpretar texto. Históricos gravados no formato antigo continuam
sendo exibidos normalmente.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `main.py` | todo o sistema |
| `tests/` | a suíte de testes |
| `produtos.json` | os produtos cadastrados |
| `historico.json` | as movimentações de estoque |

Os dois arquivos JSON são criados automaticamente na primeira execução. Se algum
deles estiver vazio, corrompido ou com um registro faltando campos, o programa
avisa e inicia com a lista vazia em vez de quebrar.

A gravação é feita primeiro num arquivo `.tmp` e só depois renomeada por cima do
original. Um erro no meio da escrita não deixa o `produtos.json` pela metade: ou
fica o conteúdo novo inteiro, ou o antigo intacto.

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

- Separar o `main.py` em módulos, quando o arquivo começar a incomodar
- Trocar o JSON por SQLite, como exercício de SQL — hoje o JSON dá conta do
  volume, então isso vale pelo aprendizado, não por necessidade

## Tecnologias

Python 3, biblioteca padrão apenas (`json`, `datetime`).
