import pytest

from main import ESTOQUE_MINIMO, SEM_CATEGORIA, Produto


def novo_produto(quantidade=10, preco=5.0):
    return Produto('Arroz', preco, quantidade, 'Comida')


class TestCriacao:
    def test_guarda_os_dados_informados(self):
        produto = Produto('Arroz', 5.0, 10, 'Comida')

        assert produto.nome == 'Arroz'
        assert produto.preco == 5.0
        assert produto.quantidade == 10
        assert produto.categoria == 'Comida'

    def test_aceita_saldo_inicial_zerado(self):
        assert novo_produto(quantidade=0).quantidade == 0

    def test_tira_os_espacos_do_nome_e_da_categoria(self):
        produto = Produto('  Arroz  ', 5.0, 10, '  Comida  ')

        assert produto.nome == 'Arroz'
        assert produto.categoria == 'Comida'

    def test_categoria_em_branco_vira_sem_categoria(self):
        assert Produto('Arroz', 5.0, 10, '   ').categoria == SEM_CATEGORIA

    @pytest.mark.parametrize('nome', ['', '   '])
    def test_recusa_nome_vazio(self, nome):
        with pytest.raises(ValueError):
            Produto(nome, 5.0, 10, 'Comida')

    def test_recusa_preco_negativo(self):
        with pytest.raises(ValueError):
            Produto('Arroz', -0.01, 10, 'Comida')

    def test_recusa_quantidade_negativa(self):
        with pytest.raises(ValueError):
            Produto('Arroz', 5.0, -1, 'Comida')


class TestValidacaoNaEdicao:
    def test_recusa_renomear_para_vazio_e_mantem_o_nome(self):
        produto = novo_produto()

        with pytest.raises(ValueError):
            produto.nome = '   '

        assert produto.nome == 'Arroz'

    def test_recusa_preco_negativo_e_mantem_o_preco(self):
        produto = novo_produto(preco=5.0)

        with pytest.raises(ValueError):
            produto.preco = -1

        assert produto.preco == 5.0

    def test_nao_deixa_atribuir_quantidade_direto(self):
        produto = novo_produto()

        with pytest.raises(AttributeError):
            produto.quantidade = 999


class TestEntrada:
    def test_soma_ao_estoque_e_devolve_o_movimento(self):
        produto = novo_produto(quantidade=10)

        assert produto.entrada(20) == 20
        assert produto.quantidade == 30

    @pytest.mark.parametrize('quantidade', [0, -5])
    def test_recusa_quantidade_nao_positiva(self, quantidade):
        produto = novo_produto(quantidade=10)

        with pytest.raises(ValueError):
            produto.entrada(quantidade)

        assert produto.quantidade == 10


class TestSaida:
    def test_subtrai_do_estoque_e_devolve_o_movimento(self):
        produto = novo_produto(quantidade=10)

        assert produto.saida(4) == 4
        assert produto.quantidade == 6

    def test_permite_zerar_o_estoque(self):
        produto = novo_produto(quantidade=10)
        produto.saida(10)

        assert produto.quantidade == 0

    def test_recusa_saida_maior_que_o_estoque_sem_alterar_nada(self):
        produto = novo_produto(quantidade=10)

        with pytest.raises(ValueError):
            produto.saida(11)

        assert produto.quantidade == 10

    @pytest.mark.parametrize('quantidade', [0, -5])
    def test_recusa_quantidade_nao_positiva(self, quantidade):
        produto = novo_produto(quantidade=10)

        with pytest.raises(ValueError):
            produto.saida(quantidade)

        assert produto.quantidade == 10


class TestAjuste:
    def test_devolve_a_diferenca_negativa_quando_a_contagem_e_menor(self):
        produto = novo_produto(quantidade=25)

        assert produto.ajustar(12) == -13
        assert produto.quantidade == 12

    def test_devolve_a_diferenca_positiva_quando_a_contagem_e_maior(self):
        produto = novo_produto(quantidade=10)

        assert produto.ajustar(18) == 8
        assert produto.quantidade == 18

    def test_contagem_igual_ao_saldo_nao_mexe_em_nada(self):
        produto = novo_produto(quantidade=10)

        assert produto.ajustar(10) == 0
        assert produto.quantidade == 10

    def test_aceita_zerar_o_estoque(self):
        produto = novo_produto(quantidade=10)
        produto.ajustar(0)

        assert produto.quantidade == 0

    def test_recusa_total_negativo_sem_alterar_nada(self):
        produto = novo_produto(quantidade=10)

        with pytest.raises(ValueError):
            produto.ajustar(-1)

        assert produto.quantidade == 10


class TestCalculos:
    def test_valor_total_multiplica_preco_pela_quantidade(self):
        assert novo_produto(quantidade=10, preco=2.5).valor_total() == 25.0

    def test_valor_total_de_estoque_zerado_e_zero(self):
        assert novo_produto(quantidade=0).valor_total() == 0

    def test_esta_em_falta_logo_abaixo_do_minimo(self):
        assert novo_produto(quantidade=ESTOQUE_MINIMO - 1).esta_em_falta()

    def test_nao_esta_em_falta_exatamente_no_minimo(self):
        assert not novo_produto(quantidade=ESTOQUE_MINIMO).esta_em_falta()


class TestSerializacao:
    def test_to_dict_e_from_dict_preservam_o_produto(self):
        original = Produto('Arroz', 5.0, 10, 'Comida')
        copia = Produto.from_dict(original.to_dict())

        assert copia.to_dict() == original.to_dict()

    def test_from_dict_valida_os_dados_do_arquivo(self):
        dados = {'nome': 'Arroz', 'preco': -1,
                 'quantidade': 10, 'categoria': 'Comida'}

        with pytest.raises(ValueError):
            Produto.from_dict(dados)
