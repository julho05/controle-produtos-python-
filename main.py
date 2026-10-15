import json
import os
from datetime import datetime

ESTOQUE_MINIMO = 5
SEM_CATEGORIA = 'Sem categoria'


def salvar_json(caminho, dados):
    temporario = f'{caminho}.tmp'

    with open(temporario, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    os.replace(temporario, caminho)


def carregar_json(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)

    except (FileNotFoundError, json.JSONDecodeError):
        return []


class Produto:
    def __init__(self, nome, preco, quantidade, categoria):
        self.nome = nome
        self.preco = preco
        self.categoria = categoria
        self._quantidade = self._validar_quantidade(quantidade)

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        valor = valor.strip()

        if valor == '':
            raise ValueError('O nome não pode estar vazio.')

        self._nome = valor

    @property
    def preco(self):
        return self._preco

    @preco.setter
    def preco(self, valor):
        if valor < 0:
            raise ValueError('O preço não pode ser negativo.')

        self._preco = valor

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, valor):
        self._categoria = valor.strip() or SEM_CATEGORIA

    @property
    def quantidade(self):
        return self._quantidade

    @staticmethod
    def _validar_quantidade(valor):
        if valor < 0:
            raise ValueError('A quantidade não pode ser negativa.')

        return valor

    def entrada(self, quantidade):
        if quantidade <= 0:
            raise ValueError('A quantidade precisa ser maior que zero.')

        self._quantidade += quantidade
        return quantidade

    def saida(self, quantidade):
        if quantidade <= 0:
            raise ValueError('A quantidade precisa ser maior que zero.')

        if quantidade > self._quantidade:
            raise ValueError(
                f'Estoque insuficiente! Disponível: {self._quantidade}')

        self._quantidade -= quantidade
        return quantidade

    def ajustar(self, novo_total):
        self._validar_quantidade(novo_total)

        diferenca = novo_total - self._quantidade
        self._quantidade = novo_total
        return diferenca

    def valor_total(self):
        return self.preco * self.quantidade

    def esta_em_falta(self):
        return self.quantidade < ESTOQUE_MINIMO

    def to_dict(self):
        return {
            'nome': self.nome,
            'preco': self.preco,
            'quantidade': self.quantidade,
            'categoria': self.categoria
        }

    @staticmethod
    def from_dict(dados):
        return Produto(
            dados['nome'],
            dados['preco'],
            dados['quantidade'],
            dados['categoria']
        )


class Estoque:
    def __init__(self, historico, arquivo='produtos.json'):
        self.historico = historico
        self.arquivo = arquivo
        self.produtos = self.carregar()

    def carregar(self):
        try:
            return [Produto.from_dict(item)
                    for item in carregar_json(self.arquivo)]

        except (KeyError, TypeError, ValueError, AttributeError):
            print(f'O arquivo {self.arquivo} está corrompido. '
                  'Iniciando com o estoque vazio.')
            return []

    def salvar(self):
        salvar_json(self.arquivo,
                    [produto.to_dict() for produto in self.produtos])

    def esta_vazio(self):
        return len(self.produtos) == 0

    def encontrar(self, nome):
        for produto in self.produtos:
            if produto.nome.lower() == nome.strip().lower():
                return produto
        return None

    def buscar(self, termo):
        termo = termo.strip().lower()
        return [produto for produto in self.produtos if termo in produto.nome.lower()]

    def adicionar(self, produto):
        self.produtos.append(produto)
        self.salvar()

        if produto.quantidade > 0:
            self.historico.registrar(Movimentacao(
                produto.nome, 'Entrada', produto.quantidade, produto.quantidade))

    def movimentar(self, produto, tipo, quantidade):
        if tipo == 'Entrada':
            registrado = produto.entrada(quantidade)
        elif tipo == 'Saída':
            registrado = produto.saida(quantidade)
        elif tipo == 'Ajuste':
            registrado = produto.ajustar(quantidade)
        else:
            raise ValueError(f'Tipo de movimentação desconhecido: {tipo}')

        self.salvar()
        self.historico.registrar(
            Movimentacao(produto.nome, tipo, registrado, produto.quantidade))

    def remover(self, produto):
        self.produtos.remove(produto)
        self.salvar()

    def ordenados_por(self, criterio):
        if criterio == 'preco':
            return sorted(self.produtos, key=lambda p: p.preco)

        if criterio == 'quantidade':
            return sorted(self.produtos, key=lambda p: p.quantidade)

        if criterio == 'categoria':
            return sorted(self.produtos,
                          key=lambda p: (p.categoria.lower(), p.nome.lower()))

        return sorted(self.produtos, key=lambda p: p.nome.lower())

    def por_categoria(self):
        agrupados = {}

        for produto in self.produtos:
            agrupados.setdefault(produto.categoria, []).append(produto)

        return dict(sorted(agrupados.items(), key=lambda item: item[0].lower()))

    def valor_total(self):
        return sum(produto.valor_total() for produto in self.produtos)

    def total_itens(self):
        return sum(produto.quantidade for produto in self.produtos)

    def mais_caro(self):
        return max(self.produtos, key=lambda p: p.preco)

    def mais_barato(self):
        return min(self.produtos, key=lambda p: p.preco)

    def em_falta(self):
        return [produto for produto in self.produtos if produto.esta_em_falta()]


class Movimentacao:
    def __init__(self, produto, tipo, quantidade, estoque_final, data=None):
        self.produto = produto
        self.tipo = tipo
        self.quantidade = quantidade
        self.estoque_final = estoque_final
        self.data = data or datetime.now().isoformat(timespec='minutes')

    def data_formatada(self):
        try:
            return datetime.fromisoformat(self.data).strftime('%d/%m/%Y %H:%M')
        except ValueError:
            return self.data

    def to_dict(self):
        return {
            'data': self.data,
            'produto': self.produto,
            'tipo': self.tipo,
            'quantidade': self.quantidade,
            'estoque_final': self.estoque_final
        }

    @staticmethod
    def from_dict(dados):
        return Movimentacao(
            dados['produto'],
            dados['tipo'],
            dados['quantidade'],
            dados['estoque_final'],
            dados['data']
        )


class Historico:
    def __init__(self, arquivo='historico.json'):
        self.arquivo = arquivo
        self.movimentacoes = self.carregar()

    def carregar(self):
        try:
            return [Movimentacao.from_dict(item)
                    for item in carregar_json(self.arquivo)]

        except (KeyError, TypeError):
            print(f'O arquivo {self.arquivo} está corrompido. '
                  'Iniciando com o histórico vazio.')
            return []

    def salvar(self):
        salvar_json(self.arquivo,
                    [movimentacao.to_dict() for movimentacao in self.movimentacoes])

    def esta_vazio(self):
        return len(self.movimentacoes) == 0

    def registrar(self, movimentacao):
        self.movimentacoes.append(movimentacao)
        self.salvar()


def ler_decimal(pergunta):
    texto = input(pergunta).strip().replace(',', '.')

    try:
        return float(texto)
    except ValueError:
        print('Esse valor precisa ser um número!!')
        return None


def ler_inteiro(pergunta):
    texto = input(pergunta).strip()

    try:
        return int(texto)
    except ValueError:
        print('Esse valor precisa ser um número inteiro!!')
        return None


def listar_historico(estoque):
    historico = estoque.historico

    if historico.esta_vazio():
        print('Nenhuma movimentação registrada.')
        return

    print('\n--------- HISTÓRICO DE MOVIMENTAÇÕES ---------')

    for movimentacao in historico.movimentacoes:
        print(f"{movimentacao.data_formatada()} | {movimentacao.tipo:7} | "
              f"{movimentacao.quantidade:4} un | {movimentacao.produto} "
              f"(ficou com {movimentacao.estoque_final})")


def exibir_produto(produto):
    print('------------------')
    print(f"Nome: {produto.nome}")
    print(f"Preco: R$ {produto.preco:.2f}")
    print(f"Quantidade: {produto.quantidade}")
    print(f"Categoria: {produto.categoria}")


def editar_produto(estoque):
    nome_busca = input('Digite o nome do produto que deseja editar: ')
    produto = estoque.encontrar(nome_busca)

    if produto is None:
        print('Produto Não Encontrado!!')
        return

    print('\n1 - Alterar nome')
    print('2 - Alterar preço')
    print('3 - Alterar categoria')

    opcao = input('Digite a sua opção para alteração: ')

    try:
        if opcao == '1':
            novo_nome = input('Digite o novo nome: ')
            existente = estoque.encontrar(novo_nome)

            if existente is not None and existente is not produto:
                print('Já existe um produto com esse nome.')
                return

            produto.nome = novo_nome
        elif opcao == '2':
            novo_preco = ler_decimal('Digite o novo preço: ')

            if novo_preco is None:
                return

            produto.preco = novo_preco
        elif opcao == '3':
            produto.categoria = input('Digite a nova categoria: ')
        else:
            print('Opção Invalida!!')
            return

    except ValueError as erro:
        print(erro)
        return

    estoque.salvar()
    print('Produto Atualizado Com Sucesso!!')


def cadastrar_produtos(estoque):
    nome = input('Nome do Produto: ')

    if estoque.encontrar(nome) is not None:
        print('Esse produto já está cadastrado')
        return

    preco = ler_decimal('Preço do Produto: ')

    if preco is None:
        return

    quantidade = ler_inteiro('Quantidade em estoque: ')

    if quantidade is None:
        return

    categoria = input('Categoria do Produto: ')

    try:
        estoque.adicionar(Produto(nome, preco, quantidade, categoria))
    except ValueError as erro:
        print(erro)
        return

    print('Produto Cadastrado Com Sucesso!!')


def listar_produtos(estoque):
    if estoque.esta_vazio():
        print('Nenhum produto cadastrado.')
        return

    print('\nOrdenar por:')
    print('1 - Nome')
    print('2 - Preço')
    print('3 - Quantidade')
    print('4 - Categoria')

    criterios = {'2': 'preco', '3': 'quantidade', '4': 'categoria'}

    opcao = input('Digite a sua opção (enter para nome): ')

    for produto in estoque.ordenados_por(criterios.get(opcao, 'nome')):
        exibir_produto(produto)


def buscar_produtos(estoque):
    termo = input('Digite o nome ou parte do nome do produto: ')

    if termo.strip() == '':
        print('Digite algum texto para buscar.')
        return

    encontrados = estoque.buscar(termo)

    if not encontrados:
        print('Produto Não Encontrado!!')
        return

    print(f'\n{len(encontrados)} produto(s) encontrado(s):')

    for produto in encontrados:
        exibir_produto(produto)


def movimentar_estoque(estoque):
    nome_buscar = input('Digite o nome do produto: ')
    produto = estoque.encontrar(nome_buscar)

    if produto is None:
        print('Produto Não Encontrado!!')
        return

    print(f"\nEstoque atual de {produto.nome}: {produto.quantidade}")
    print('1 - Entrada (chegou mercadoria)')
    print('2 - Saída (venda ou perda)')
    print('3 - Ajuste (corrigir o saldo depois de uma contagem)')

    tipos = {'1': 'Entrada', '2': 'Saída', '3': 'Ajuste'}

    opcao = input('Digite a sua opção: ')

    if opcao not in tipos:
        print('Opção Invalida!!')
        return

    if opcao == '3':
        pergunta = 'Quantidade contada em estoque: '
    else:
        pergunta = 'Quantidade: '

    quantidade = ler_inteiro(pergunta)

    if quantidade is None:
        return

    try:
        estoque.movimentar(produto, tipos[opcao], quantidade)
    except ValueError as erro:
        print(erro)
        return

    print(f"Movimentação registrada. Estoque atual: {produto.quantidade}")


def calcular_estoque(estoque):
    print(f'Valor total do estoque: R$ {estoque.valor_total():.2f}')


def relatorio_estoque(estoque):
    if estoque.esta_vazio():
        print('Nenhum produto cadastrado.')
        return

    mais_caro = estoque.mais_caro()
    mais_barato = estoque.mais_barato()
    estoque_baixo = estoque.em_falta()

    print('\n--------- RELATÓRIO DO ESTOQUE ---------')
    print(f'Produtos cadastrados: {len(estoque.produtos)}')
    print(f'Itens em estoque: {estoque.total_itens()}')
    print(f'Valor total: R$ {estoque.valor_total():.2f}')
    print(f"Mais caro: {mais_caro.nome} (R$ {mais_caro.preco:.2f})")
    print(f"Mais barato: {mais_barato.nome} (R$ {mais_barato.preco:.2f})")

    print('\nPor categoria:')
    for categoria, produtos in estoque.por_categoria().items():
        itens = sum(produto.quantidade for produto in produtos)
        valor = sum(produto.valor_total() for produto in produtos)
        print(f"  - {categoria}: {len(produtos)} produto(s), "
              f"{itens} itens, R$ {valor:.2f}")

    if not estoque_baixo:
        print('\nNenhum produto com estoque baixo.')
        return

    print(f'\nEstoque baixo (menos de {ESTOQUE_MINIMO} unidades):')
    for produto in estoque_baixo:
        print(f"  - {produto.nome}: {produto.quantidade}")


def excluir_produto(estoque):
    nome_buscar = input('Digite o nome do produto que deseja excluir: ')
    produto = estoque.encontrar(nome_buscar)

    if produto is None:
        print('Produto Não Encontrado!!')
        return

    estoque.remover(produto)

    print('Produto Excluido com Sucesso!!')


OPCOES = {
    '1': ('Cadastrar produtos', cadastrar_produtos),
    '2': ('Listar produtos', listar_produtos),
    '3': ('Buscar produtos', buscar_produtos),
    '4': ('Entrada/Saída/Ajuste de estoque', movimentar_estoque),
    '5': ('Mostrar valor total do estoque', calcular_estoque),
    '6': ('Excluir Produto', excluir_produto),
    '7': ('Editar Produto', editar_produto),
    '8': ('Relatório do estoque', relatorio_estoque),
    '9': ('Histórico de movimentações', listar_historico),
}


def main():
    historico = Historico()
    estoque = Estoque(historico)

    while True:
        print('---------CONTROLE DE PRODUTOS---------')

        for numero, (descricao, _) in OPCOES.items():
            print(f'{numero} - {descricao}')

        print('0 - Sair')

        opcao = input('Informe sua escolha: ')

        if opcao == '0':
            print('Sistema Encerrado.')
            break

        escolhida = OPCOES.get(opcao)

        if escolhida is None:
            print('Opção inválida! Escolha um número de 0 a 9.')
            continue

        escolhida[1](estoque)


if __name__ == '__main__':
    main()
