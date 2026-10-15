"""O histórico acompanha o produto pelo id, não pelo nome."""

import json

import pytest

import main
from main import Estoque, Historico, Produto


@pytest.fixture
def arquivos(tmp_path):
    return {
        'produtos': str(tmp_path / 'produtos.json'),
        'historico': str(tmp_path / 'historico.json'),
    }


@pytest.fixture
def estoque(arquivos):
    return Estoque(Historico(arquivos['historico']), arquivos['produtos'])


def abrir(caminho):
    with open(caminho, encoding='utf-8') as arquivo:
        return json.load(arquivo)


class TestIdDoProduto:
    def test_produto_nasce_com_id(self):
        assert Produto('Arroz', 5.0, 10, 'Comida').id

    def test_cada_produto_tem_um_id_diferente(self):
        um = Produto('Arroz', 5.0, 10, 'Comida')
        outro = Produto('Feijao', 9.0, 12, 'Comida')

        assert um.id != outro.id

    def test_o_id_sobrevive_ao_arquivo(self, arquivos, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        original = estoque.produtos[0].id

        recarregado = Estoque(Historico(arquivos['historico']),
                              arquivos['produtos'])

        assert recarregado.produtos[0].id == original

    def test_o_id_nao_muda_ao_renomear(self, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        produto = estoque.produtos[0]
        original = produto.id

        produto.nome = 'Arroz Branco'
        estoque.salvar()

        assert produto.id == original

    def test_encontrar_por_id(self, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        produto = estoque.produtos[0]

        assert estoque.encontrar_por_id(produto.id) is produto

    def test_encontrar_por_id_inexistente_devolve_none(self, estoque):
        assert estoque.encontrar_por_id('nao-existe') is None


class TestHistoricoLigadoAoProduto:
    def test_a_movimentacao_guarda_o_id_do_produto(self, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))

        assert estoque.historico.movimentacoes[0].produto_id == \
               estoque.produtos[0].id

    def test_renomear_nao_deixa_o_historico_orfao(self, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        produto = estoque.produtos[0]
        estoque.movimentar(produto, 'Saída', 4)

        produto.nome = 'Arroz Branco'
        estoque.salvar()

        movimentos = [m for m in estoque.historico.movimentacoes
                      if m.produto_id == produto.id]

        assert len(movimentos) == 2

    def test_a_soma_dos_movimentos_fecha_mesmo_depois_do_rename(self, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        produto = estoque.produtos[0]

        estoque.movimentar(produto, 'Entrada', 20)
        produto.nome = 'Arroz Branco'
        estoque.salvar()
        estoque.movimentar(produto, 'Saída', 5)

        soma = 0
        for movimentacao in estoque.historico.movimentacoes:
            if movimentacao.produto_id != produto.id:
                continue
            if movimentacao.tipo == 'Saída':
                soma -= movimentacao.quantidade
            else:
                soma += movimentacao.quantidade

        assert soma == produto.quantidade == 25

    def test_o_nome_gravado_e_o_da_hora_do_movimento(self, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        produto = estoque.produtos[0]

        produto.nome = 'Arroz Branco'
        estoque.salvar()
        estoque.movimentar(produto, 'Entrada', 5)

        nomes = [m.produto for m in estoque.historico.movimentacoes]

        assert nomes == ['Arroz', 'Arroz Branco']


class TestExibicaoDoHistorico:
    def test_mostra_o_nome_atual_depois_do_rename(self, estoque, capsys):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        produto = estoque.produtos[0]
        produto.nome = 'Arroz Branco'
        estoque.salvar()

        main.listar_historico(estoque)

        assert 'Arroz Branco' in capsys.readouterr().out

    def test_produto_excluido_aparece_com_o_nome_antigo(self, estoque, capsys):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        estoque.remover(estoque.produtos[0])

        main.listar_historico(estoque)
        saida = capsys.readouterr().out

        assert 'Arroz' in saida
        assert 'excluído' in saida


class TestMigracaoDosArquivosAntigos:
    def test_produto_sem_id_ganha_um_e_o_arquivo_e_regravado(self, arquivos):
        with open(arquivos['produtos'], 'w', encoding='utf-8') as arquivo:
            json.dump([{'nome': 'Arroz', 'preco': 5.0,
                        'quantidade': 10, 'categoria': 'Comida'}], arquivo)

        estoque = Estoque(Historico(arquivos['historico']),
                          arquivos['produtos'])

        assert estoque.produtos[0].id
        assert abrir(arquivos['produtos'])[0]['id'] == estoque.produtos[0].id

    def test_movimentacao_antiga_e_casada_pelo_nome(self, arquivos):
        with open(arquivos['produtos'], 'w', encoding='utf-8') as arquivo:
            json.dump([{'nome': 'Arroz', 'preco': 5.0,
                        'quantidade': 10, 'categoria': 'Comida'}], arquivo)

        with open(arquivos['historico'], 'w', encoding='utf-8') as arquivo:
            json.dump([{'data': '29/09/2026 17:01', 'produto': 'Arroz',
                        'tipo': 'Entrada', 'quantidade': 10,
                        'estoque_final': 10}], arquivo)

        estoque = Estoque(Historico(arquivos['historico']),
                          arquivos['produtos'])

        assert estoque.historico.movimentacoes[0].produto_id == \
               estoque.produtos[0].id
        assert abrir(arquivos['historico'])[0]['produto_id']

    def test_movimentacao_de_produto_que_nao_existe_mais_fica_sem_id(self, arquivos):
        with open(arquivos['historico'], 'w', encoding='utf-8') as arquivo:
            json.dump([{'data': '29/09/2026 17:01', 'produto': 'Sumido',
                        'tipo': 'Entrada', 'quantidade': 10,
                        'estoque_final': 10}], arquivo)

        estoque = Estoque(Historico(arquivos['historico']),
                          arquivos['produtos'])

        assert estoque.historico.movimentacoes[0].produto_id is None
        assert estoque.historico.movimentacoes[0].produto == 'Sumido'

    def test_arquivo_ja_migrado_nao_e_regravado(self, arquivos, estoque):
        estoque.adicionar(Produto('Arroz', 5.0, 10, 'Comida'))
        antes = abrir(arquivos['produtos'])

        Estoque(Historico(arquivos['historico']), arquivos['produtos'])

        assert abrir(arquivos['produtos']) == antes
