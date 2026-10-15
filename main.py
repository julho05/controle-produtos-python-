import json
from datetime import datetime


class Produto:
    def __init__(self, nome, preco, quantidade, categoria):
        self.nome = nome
        self.preco = preco
        self._quantidade = quantidade
        self.categoria = categoria

    @property
    def quantidade(self):
        return self._quantidade

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
        if novo_total < 0:
            raise ValueError('A quantidade não pode ser negativa.')

        diferenca = novo_total - self._quantidade
        self._quantidade = novo_total
        return diferenca

    def valor_total(self):
        return self.preco * self.quantidade

    def esta_em_falta(self):
        return self.quantidade < 5

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
            with open(self.arquivo, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)

        except (FileNotFoundError, json.JSONDecodeError):
            return []

        return [Produto.from_dict(item) for item in dados]

    def salvar(self):
        with open(self.arquivo, 'w', encoding='utf-8') as arquivo:
            json.dump([produto.to_dict() for produto in self.produtos], arquivo,
                      ensure_ascii=False, indent=4)

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
        else:
            registrado = produto.ajustar(quantidade)

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

        return sorted(self.produtos, key=lambda p: p.nome.lower())

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
        self.data = data or datetime.now().strftime('%d/%m/%Y %H:%M')

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
            with open(self.arquivo, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)

        except (FileNotFoundError, json.JSONDecodeError):
            return []

        return [Movimentacao.from_dict(item) for item in dados]

    def salvar(self):
        with open(self.arquivo, 'w', encoding='utf-8') as arquivo:
            json.dump([movimentacao.to_dict() for movimentacao in self.movimentacoes],
                      arquivo, ensure_ascii=False, indent=4)

    def esta_vazio(self):
        return len(self.movimentacoes) == 0

    def registrar(self, movimentacao):
        self.movimentacoes.append(movimentacao)
        self.salvar()


def listar_historico(historico):
    if historico.esta_vazio():
        print('Nenhuma movimentação registrada.')
        return

    print('\n--------- HISTÓRICO DE MOVIMENTAÇÕES ---------')

    for movimentacao in historico.movimentacoes:
        print(f"{movimentacao.data} | {movimentacao.tipo:7} | "
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

    if opcao == '1':
        novo_nome = input('Digite o novo nome: ').strip()

        if novo_nome == '':
            print('O nome não pode estar vazio.')
            return

        if estoque.encontrar(novo_nome) is not None:
            print('Já existe um produto com esse nome.')
            return

        produto.nome = novo_nome
    elif opcao == '2':
        try:
            novo_preco = float(input('Digite o novo preço: '))
        except ValueError:
            print('O preço precisa ser um número!!')
            return

        if novo_preco < 0:
            print('O preço não pode ser negativo.')
            return

        produto.preco = novo_preco
    elif opcao == '3':
        produto.categoria = input('Digite a nova categoria: ').strip()
    else:
        print('Opção Invalida!!')
        return

    estoque.salvar()
    print('Produto Atualizado Com Sucesso!!')


def cadastrar_produtos(estoque):
    nome = input('Nome do Produto: ').strip()

    if nome == '':
        print("O nome não pode está vazio")
        return

    if estoque.encontrar(nome) is not None:
        print('Esse produto já está cadastrado')
        return

    try:
        preco = float(input('Preço do Produto: '))
        quantidade = int(input('Quantidade em estoque: '))
    except ValueError:
        print('Preço e quantidade precisam ser números!!')
        return

    if preco < 0:
        print('O preco não pode ser negativo.')
        return


    if quantidade < 0:
        print('A quantidade não pode ser negativa.')
        return

    categoria = input('Categoria do Produto: ').strip()

    estoque.adicionar(Produto(nome, preco, quantidade, categoria))

    print('Produto Cadastrado Com Sucesso!!')

def listar_produtos(estoque):
    if estoque.esta_vazio():
        print('Nenhum produto cadastrado.')
        return

    print('\nOrdenar por:')
    print('1 - Nome')
    print('2 - Preço')
    print('3 - Quantidade')

    opcao = input('Digite a sua opção (enter para nome): ')

    if opcao == '2':
        ordenados = estoque.ordenados_por('preco')
    elif opcao == '3':
        ordenados = estoque.ordenados_por('quantidade')
    else:
        ordenados = estoque.ordenados_por('nome')

    for produto in ordenados:
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

    try:
        quantidade = int(input(pergunta))
    except ValueError:
        print('A quantidade precisa ser um número!!')
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

    if not estoque_baixo:
        print('\nNenhum produto com estoque baixo.')
        return

    print(f'\nEstoque baixo (menos de 5 unidades):')
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


def main():
    historico = Historico()
    estoque = Estoque(historico)

    while True:
        print('---------CONTROLE DE PRODUTOS---------')
        print('1 - Cadastrar produtos')
        print('2 - Listar produtos')
        print('3 - Buscar produtos')
        print('4 - Entrada/Saída/Ajuste de estoque')
        print('5 - Mostrar valor total do estoque')
        print('6 - Excluir Produto')
        print('7 - Editar Produto')
        print('8 - Relatório do estoque')
        print('9 - Histórico de movimentações')
        print('0 - Sair')

        opcao = input('Informe sua escolha: ')

        if opcao == '1':
            cadastrar_produtos(estoque)
        elif opcao == '2':
            listar_produtos(estoque)
        elif opcao == '3':
            buscar_produtos(estoque)
        elif opcao == '4':
            movimentar_estoque(estoque)
        elif opcao == '5':
            calcular_estoque(estoque)
        elif opcao == '6':
            excluir_produto(estoque)
        elif opcao == '7':
            editar_produto(estoque)
        elif opcao == '8':
            relatorio_estoque(estoque)
        elif opcao == '9':
            listar_historico(historico)
        elif opcao == '0':
            print('Sistema Encerrado.')
            break
        else:
            print('Opção inválida! Escolha um número de 0 a 9.')


if __name__ == '__main__':
    main()
