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
números tanto no cadastro quanto na edição.

**Busca por parte do nome**
Com "Caneta Azul" e "Caneta Preta" cadastradas, buscar `caneta` retorna as duas.
Já as operações que alteram ou apagam exigem o nome exato, para não haver risco
de mexer no produto errado.

**Listagem ordenável**
Ordena por nome, preço ou quantidade.

**Entrada, saída e ajuste de estoque**
Em vez de informar o total final, você registra o movimento: chegaram 20, vendi 3.
Saídas maiores que o estoque disponível são recusadas.

Quando a contagem física discorda do sistema, o ajuste corrige o saldo e fica
registrado como tal, com a diferença aplicada:

```
29/09/2026 17:01 | Ajuste  |  -13 un | Arroz (ficou com 12)
```

**A quantidade só muda por movimento**
Não existe caminho para alterar a quantidade sem deixar registro. O cadastro de
um produto com saldo inicial já entra como uma entrada, e o editar não mexe em
quantidade — só em nome, preço e categoria. Por isso vale a regra de que a soma
dos movimentos de um produto é igual ao saldo dele.

Na prática isso significa que o histórico pode ser usado para conferir o
estoque, o que antes não era verdade: existiam dois outros caminhos que
alteravam a quantidade em silêncio.

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

- Impedir que renomear um produto deixe o histórico dele órfão
- Mover as validações de preço e quantidade para dentro do `Produto`, hoje
  duplicadas entre o cadastro e a edição
- Testes automatizados com pytest, começando pela regra de que a soma dos
  movimentos fecha com o saldo
- Separar o `main.py` em módulos, quando o arquivo começar a incomodar
- Trocar o JSON por SQLite, como exercício de SQL — hoje o JSON dá conta do
  volume, então isso vale pelo aprendizado, não por necessidade

## Tecnologias

Python 3, biblioteca padrão apenas (`json`, `datetime`).
