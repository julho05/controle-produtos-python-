import pytest

import main
from main import Estoque, Historico, Produto


@pytest.fixture
def estoque(tmp_path):
    return Estoque(Historico(str(tmp_path / 'historico.json')),
                   str(tmp_path / 'produtos.json'))


@pytest.fixture
def digitar(monkeypatch):
    """Responde cada input() com a próxima resposta da lista."""

    def configurar(*respostas):
        pendentes = iter(respostas)
        monkeypatch.setattr('builtins.input', lambda _='': next(pendentes))

    return configurar


class TestLeituraDeNumeros:
    def test_le_decimal_com_ponto(self, digitar):
        digitar('2.50')

        assert main.ler_decimal('') == 2.5

    def test_le_decimal_com_virgula(self, digitar):
        digitar('2,50')

        assert main.ler_decimal('') == 2.5

    def test_decimal_invalido_devolve_none(self, digitar, capsys):
        digitar('abc')

        assert main.ler_decimal('') is None
        assert 'número' in capsys.readouterr().out

    def test_le_inteiro_com_espacos(self, digitar):
        digitar('  20  ')

        assert main.ler_inteiro('') == 20

    def test_inteiro_quebrado_devolve_none(self, digitar):
        digitar('2.5')

        assert main.ler_inteiro('') is None


class TestEditarProduto:
    def test_renomear_mudando_so_a_caixa(self, estoque, digitar):
        estoque.adicionar(Produto('arroz', 5.0, 10, 'Comida'))
        digitar('arroz', '1', 'Arroz')

        main.editar_produto(estoque)

        assert estoque.produtos[0].nome == 'Arroz'

    def test_renomear_para_o_nome_de_outro_produto_e_recusado(self, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        estoque.adicionar(Produto('Feijao', 9.0, 12, 'Comida'))
        digitar('Feijao', '1', 'arroz')

        main.editar_produto(estoque)

        assert estoque.encontrar('Feijao').nome == 'Feijao'

    def test_renomear_para_vazio_e_recusado(self, estoque, digitar, capsys):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('Arroz', '1', '   ')

        main.editar_produto(estoque)

        assert estoque.produtos[0].nome == 'Arroz'
        assert 'vazio' in capsys.readouterr().out

    def test_alterar_preco_aceita_virgula(self, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('Arroz', '2', '7,25')

        main.editar_produto(estoque)

        assert estoque.produtos[0].preco == 7.25

    def test_preco_negativo_e_recusado(self, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('Arroz', '2', '-1')

        main.editar_produto(estoque)

        assert estoque.produtos[0].preco == 5.0

    def test_edicao_nao_mexe_na_quantidade(self, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('Arroz', '2', '7.00')

        main.editar_produto(estoque)

        assert estoque.produtos[0].quantidade == 10
        assert len(estoque.historico.movimentacoes) == 1

    def test_a_alteracao_vai_para_o_arquivo(self, tmp_path, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('Arroz', '3', 'Mantimentos')

        main.editar_produto(estoque)
        recarregado = Estoque(Historico(str(tmp_path / 'historico.json')),
                              str(tmp_path / 'produtos.json'))

        assert recarregado.produtos[0].categoria == 'Mantimentos'


class TestCadastrarProduto:
    def test_cadastra_com_preco_em_virgula(self, estoque, digitar):
        digitar('Caneta Azul', '2,50', '30', 'Material')

        main.cadastrar_produtos(estoque)

        produto = estoque.encontrar('Caneta Azul')

        assert produto.preco == 2.5
        assert produto.quantidade == 30

    def test_nome_repetido_e_recusado(self, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('  arroz  ')

        main.cadastrar_produtos(estoque)

        assert len(estoque.produtos) == 1

    def test_nome_vazio_e_recusado(self, estoque, digitar):
        digitar('   ', '5.00', '10', 'Comida')

        main.cadastrar_produtos(estoque)

        assert estoque.esta_vazio()

    def test_quantidade_negativa_e_recusada(self, estoque, digitar):
        digitar('Arroz', '5.00', '-1', 'Comida')

        main.cadastrar_produtos(estoque)

        assert estoque.esta_vazio()


class TestMovimentarEstoque:
    def test_entrada_pelo_menu(self, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('Arroz', '1', '20')

        main.movimentar_estoque(estoque)

        assert estoque.produtos[0].quantidade == 30

    def test_ajuste_pelo_menu_registra_a_diferenca(self, estoque, digitar):
        estoque.adicionar(Produto('Arroz', 5.0, 25, 'Comida'))
        digitar('Arroz', '3', '12')

        main.movimentar_estoque(estoque)

        ultimo = estoque.historico.movimentacoes[-1]

        assert estoque.produtos[0].quantidade == 12
        assert ultimo.tipo == 'Ajuste'
        assert ultimo.quantidade == -13

    def test_saida_maior_que_o_estoque_avisa_e_nao_altera(self, estoque, digitar, capsys):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        digitar('Arroz', '2', '11')

        main.movimentar_estoque(estoque)

        assert estoque.produtos[0].quantidade == 10
        assert 'Estoque insuficiente' in capsys.readouterr().out

    def test_produto_inexistente_avisa(self, estoque, digitar, capsys):
        digitar('Mochila')

        main.movimentar_estoque(estoque)

        assert 'Não Encontrado' in capsys.readouterr().out


class TestMenu:
    def test_toda_opcao_do_menu_tem_descricao_e_acao(self):
        for numero, (descricao, acao) in main.OPCOES.items():
            assert numero.isdigit()
            assert descricao
            assert callable(acao)

    def test_as_acoes_do_menu_recebem_o_estoque(self, estoque, digitar):
        digitar(*([''] * 20))

        for _, acao in main.OPCOES.values():
            acao(estoque)
