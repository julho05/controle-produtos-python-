import json

def carregar_produtos():
    try:
        with open('produtos.json', 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)

    except (FileNotFoundError, json.JSONDecodeError):
        return []

produtos = carregar_produtos()

def salvar_produtos():
    with open('produtos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


def encontrar_produto(nome):
    for produto in produtos:
        if produto['nome'].lower() == nome.strip().lower():
            return produto
    return None


def buscar_por_nome(termo):
    termo = termo.strip().lower()
    return [produto for produto in produtos if termo in produto['nome'].lower()]


def exibir_produto(produto):
    print('------------------')
    print(f"Nome: {produto['nome']}")
    print(f"Preco: R$ {produto['preco']:.2f}")
    print(f"Quantidade: {produto['quantidade']}")
    print(f"Categoria: {produto['categoria']}")


def editar_produto():
    nome_busca = input('Digite o nome do produto que deseja editar: ')
    produto = encontrar_produto(nome_busca)

    if produto is None:
        print('Produto Não Encontrado!!')
        return

    print('\n1 - Alterar nome')
    print('2 - Alterar preço')
    print('3 - Alterar quantidade')
    print('4 - Alterar categoria')

    opcao = input('Digite a sua opção para alteração: ')

    if opcao == '1':
        novo_nome = input('Digite o novo nome: ').strip()

        if novo_nome == '':
            print('O nome não pode estar vazio.')
            return

        if encontrar_produto(novo_nome) is not None:
            print('Já existe um produto com esse nome.')
            return

        produto['nome'] = novo_nome
    elif opcao == '2':
        try:
            novo_preco = float(input('Digite o novo preço: '))
        except ValueError:
            print('O preço precisa ser um número!!')
            return

        if novo_preco < 0:
            print('O preço não pode ser negativo.')
            return

        produto['preco'] = novo_preco
    elif opcao == '3':
        try:
            nova_quantidade = int(input('Digite a nova quantidade: '))
        except ValueError:
            print('A quantidade precisa ser um número!!')
            return

        if nova_quantidade < 0:
            print('A quantidade não pode ser negativa.')
            return

        produto['quantidade'] = nova_quantidade
    elif opcao == '4':
        produto['categoria'] = input('Digite a nova categoria: ').strip()
    else:
        print('Opção Invalida!!')
        return

    salvar_produtos()
    print('Produto Atualizado Com Sucesso!!')


def cadastrar_produtos():
    nome = input('Nome do Produto: ').strip()

    if nome == '':
        print("O nome não pode está vazio")
        return

    if encontrar_produto(nome) is not None:
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

    produto = {
        'nome' : nome,
        'preco' : preco,
        'quantidade' : quantidade,
        'categoria' : categoria
    }
        
    produtos.append(produto)

    salvar_produtos()

    print('Produto Cadastrado Com Sucesso!!')

def listar_produtos():
    if not produtos:
        print('Nenhum produto cadastrado.')
        return

    print('\nOrdenar por:')
    print('1 - Nome')
    print('2 - Preço')
    print('3 - Quantidade')

    opcao = input('Digite a sua opção (enter para nome): ')

    if opcao == '2':
        ordenados = sorted(produtos, key=lambda p: p['preco'])
    elif opcao == '3':
        ordenados = sorted(produtos, key=lambda p: p['quantidade'])
    else:
        ordenados = sorted(produtos, key=lambda p: p['nome'].lower())

    for produto in ordenados:
        exibir_produto(produto)


def buscar_produtos():
    termo = input('Digite o nome ou parte do nome do produto: ')

    if termo.strip() == '':
        print('Digite algum texto para buscar.')
        return

    encontrados = buscar_por_nome(termo)

    if not encontrados:
        print('Produto Não Encontrado!!')
        return

    print(f'\n{len(encontrados)} produto(s) encontrado(s):')

    for produto in encontrados:
        exibir_produto(produto)


def atualizar_quantidade():
    nome_buscar = input('Digite o nome do produto: ')
    produto = encontrar_produto(nome_buscar)

    if produto is None:
        print('Produto Não Encontrado!!')
        return

    try:
        nova_quantidade = int(input('Digite a nova quantidade: '))
    except ValueError:
        print('A quantidade precisa ser um número!!')
        return

    if nova_quantidade < 0:
        print('A quantidade não pode ser negativa.')
        return

    produto['quantidade'] = nova_quantidade

    salvar_produtos()
    print('Quantidade atualizada com sucesso!!')


def movimentar_estoque():
    nome_buscar = input('Digite o nome do produto: ')
    produto = encontrar_produto(nome_buscar)

    if produto is None:
        print('Produto Não Encontrado!!')
        return

    print(f"\nEstoque atual de {produto['nome']}: {produto['quantidade']}")
    print('1 - Entrada (chegou mercadoria)')
    print('2 - Saída (venda ou perda)')

    opcao = input('Digite a sua opção: ')

    if opcao != '1' and opcao != '2':
        print('Opção Invalida!!')
        return

    try:
        quantidade = int(input('Quantidade: '))
    except ValueError:
        print('A quantidade precisa ser um número!!')
        return

    if quantidade <= 0:
        print('A quantidade precisa ser maior que zero.')
        return

    if opcao == '1':
        produto['quantidade'] += quantidade
    else:
        if quantidade > produto['quantidade']:
            print(f"Estoque insuficiente! Disponível: {produto['quantidade']}")
            return

        produto['quantidade'] -= quantidade

    salvar_produtos()
    print(f"Movimentação registrada. Estoque atual: {produto['quantidade']}")


def calcular_estoque():
    total = 0

    for produto in produtos:
        valor_produto = produto['preco'] * produto['quantidade']
        total = total + valor_produto

    print(f'Valor total do estoque: R$ {total:.2f}')


def relatorio_estoque():
    if not produtos:
        print('Nenhum produto cadastrado.')
        return

    total_itens = sum(produto['quantidade'] for produto in produtos)
    valor_total = sum(produto['preco'] * produto['quantidade'] for produto in produtos)
    mais_caro = max(produtos, key=lambda p: p['preco'])
    mais_barato = min(produtos, key=lambda p: p['preco'])
    estoque_baixo = [produto for produto in produtos if produto['quantidade'] < 5]

    print('\n--------- RELATÓRIO DO ESTOQUE ---------')
    print(f'Produtos cadastrados: {len(produtos)}')
    print(f'Itens em estoque: {total_itens}')
    print(f'Valor total: R$ {valor_total:.2f}')
    print(f"Mais caro: {mais_caro['nome']} (R$ {mais_caro['preco']:.2f})")
    print(f"Mais barato: {mais_barato['nome']} (R$ {mais_barato['preco']:.2f})")

    if not estoque_baixo:
        print('\nNenhum produto com estoque baixo.')
        return

    print(f'\nEstoque baixo (menos de 5 unidades):')
    for produto in estoque_baixo:
        print(f"  - {produto['nome']}: {produto['quantidade']}")


def excluir_produto():
    nome_buscar = input('Digite o nome do produto que deseja excluir: ')
    produto = encontrar_produto(nome_buscar)

    if produto is None:
        print('Produto Não Encontrado!!')
        return

    produtos.remove(produto)

    salvar_produtos()
    print('Produto Excluido com Sucesso!!')


while True:
    print('---------CONTROLE DE PRODUTOS---------')
    print('1 - Cadastrar produtos')
    print('2 - Listar produtos')
    print('3 - Buscar produtos')
    print('4 - Atualizar quantidade')
    print('5 - Mostrar valor total do estoque')
    print('6 - Excluir Produto')
    print('7 - Editar Produto')
    print('8 - Entrada/Saída de estoque')
    print('9 - Relatório do estoque')
    print('0 - Sair')

    opcao = input('Informe sua escolha: ')

    if opcao == '1':
        cadastrar_produtos()
    elif opcao == '2':
        listar_produtos()
    elif opcao == '3':
        buscar_produtos()
    elif opcao == '4':
        atualizar_quantidade()
    elif opcao == '5':
        calcular_estoque()
    elif opcao == '6':
        excluir_produto()
    elif opcao == '7':
        editar_produto()
    elif opcao == '8':
        movimentar_estoque()
    elif opcao == '9':
        relatorio_estoque()
    elif opcao == '0':
        print('Sistema Encerrado.')
        break
    else:
        print('Opção inválida! Escolha um número de 0 a 9.')

