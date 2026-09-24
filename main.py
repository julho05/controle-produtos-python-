import json

def carregar_produtos():
    try:
        with open('produtos.json', 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)

    except FileNotFoundError:
        return[]

produtos = carregar_produtos()

def salvar_produtos():
    with open('produtos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)



def editar_produto():
    nome_busca = input('Digite o nome do produto que deseja editar: ').strip().lower()

    for produto in produtos:
        if produto['nome'].lower() == nome_busca:

            print('\n1 - Alterar nome')
            print('2 - Alterar preço')
            print('3 - Alterar quantidade')
            print('4 - Alterar categoria')

            opcao = input('Digite a sua opção para alteração: ')

            if opcao == '1':
                novo_nome = input('Digite o novo nome: ').lower()
                produto['nome'] = novo_nome
            elif opcao == '2':
                novo_preco = float(input('Digite o novo preço: '))
                produto['preco'] = novo_preco
            elif opcao == '3':
                nova_quantidade = int(input('Digite a nova quantidade: '))
                produto['quantidade'] = nova_quantidade
            elif opcao == '4':
                nova_categoria = input('Digite a nova categoria: ')
                produto['categoria'] = nova_categoria
            else:
                print('Opção Invalida!!')
                return

        salvar_produtos()
        print('Produto Atualizado Com Sucesso!!')
        return

    print('Produto Não Encontrado!!')


def cadastrar_produtos():
    nome = input('Nome do Produto: ').strip()

    if nome == '':
        print("O nome não pode está vazio")
        return

    for produto in produtos:
        if produto['nome'].lower() == nome.lower():
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
    for produto in produtos:
        print('------------------')
        print('Nome: ',produto['nome'])
        print('Preco: ',produto['preco'])
        print('Quantidade: ',produto['quantidade'])
        print('Categoria: ',produto['categoria'])


def buscar_produtos():
    nome_buscar = input('Digite o nome do produto: ').lower()

    for produto in produtos:
        if produto['nome'].lower() == nome_buscar:
            print('------------------')
            print('Nome: ',produto['nome'])
            print('Preco: ',produto['preco'])
            print('Quantidade: ',produto['quantidade'])
            print('Categoria: ',produto['categoria'])
            return
    print('Produto Não Encontrado!!')


def atualizar_quantidade ():
    nome_buscar = input('Digite o nome do produto').lower()

    for produto in produtos:
        if produto['nome'].lower() == nome_buscar:
            nova_quantidade = int(input('Digite a nova quantidade: '))
            produto['quantidade'] = nova_quantidade

            print('Quantidade atualizada com sucesso!!')
            return

        salvar_produtos()

    print('Produto Não Encontrado!!')


def calcular_estoque():
    total = 0

    for produto in produtos:
        valor_produto = produto['preco'] * produto['quantidade']
        total = total + valor_produto

    print(f'Valor total do estoque: R$ {total:.2f}')


def excluir_produto():
    nome_buscar = input('Digite o nome do produto que deseja excluir: ').lower()

    for produto in produtos:
        if produto['nome'].lower() == nome_buscar:
            produtos.remove(produto)

            print('Produto Excluido com Sucesso!!')
            return

    salvar_produtos()

    print('Produto Não Encontrado!!')


while True:
    print('---------CONTROLE DE PRODUTOS---------')
    print('1 - Cadastrar produtos')
    print('2 - Listar produtos')
    print('3 - Buscar produtos')
    print('4 - Atualizar quantidade')
    print('5 - Mostrar valor total do estoque')
    print('6 - Excluir Produto')
    print('7 - Editar Produto')
    print('8 - Sair')

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
        print('Sistema Encerrado.')
        break

