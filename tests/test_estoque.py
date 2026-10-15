import json

import pytest

import main
from main import Estoque, Historico, Movimentacao, Produto


@pytest.fixture
def arquivos(tmp_path):
    return {
        'produtos': str(tmp_path / 'produtos.json'),
        'historico': str(tmp_path / 'historico.json'),
    }


@pytest.fixture
def estoque(arquivos):
    return Estoque(Historico(arquivos['historico']), arquivos['produtos'])


def arroz(quantidade=10):
    return Produto('Arroz', 5.0, quantidade, 'Comida')


class TestRegraDoSaldo:
    """A soma dos movimentos de um produto fecha com o saldo dele."""

    def test_cadastro_com_saldo_inicial_entra_como_entrada(self, estoque):
        estoque.adicionar(arroz(10))

        movimentacoes = estoque.historico.movimentacoes

        assert len(movimentacoes) == 1
        assert movimentacoes[0].tipo == 'Entrada'
        assert movimentacoes[0].quantidade == 10
        assert movimentacoes[0].estoque_final == 10

    def test_cadastro_zerado_nao_gera_movimento(self, estoque):
        estoque.adicionar(arroz(0))

        assert estoque.historico.esta_vazio()

    def test_a_soma_dos_movimentos_bate_com_o_saldo(self, estoque):
        estoque.adicionar(arroz(10))
        produto = estoque.encontrar('Arroz')

        estoque.movimentar(produto, 'Entrada', 20)
        estoque.movimentar(produto, 'Saída', 5)
        estoque.movimentar(produto, 'Ajuste', 12)

        soma = 0
        for movimentacao in estoque.historico.movimentacoes:
            if movimentacao.tipo == 'Saída':
                soma -= movimentacao.quantidade
            else:
                soma += movimentacao.quantidade

        assert soma == produto.quantidade == 12

    def test_cada_movimento_guarda_o_saldo_de_depois(self, estoque):
        estoque.adicionar(arroz(10))
        produto = estoque.encontrar('Arroz')

        estoque.movimentar(produto, 'Entrada', 20)
        estoque.movimentar(produto, 'Saída', 5)

        finais = [m.estoque_final for m in estoque.historico.movimentacoes]

        assert finais == [10, 30, 25]

    def test_saida_maior_que_o_estoque_nao_gera_movimento(self, estoque):
        estoque.adicionar(arroz(10))
        produto = estoque.encontrar('Arroz')

        with pytest.raises(ValueError):
            estoque.movimentar(produto, 'Saída', 11)

        assert produto.quantidade == 10
        assert len(estoque.historico.movimentacoes) == 1

    def test_tipo_desconhecido_levanta_erro_e_nao_mexe_no_estoque(self, estoque):
        estoque.adicionar(arroz(10))
        produto = estoque.encontrar('Arroz')

        with pytest.raises(ValueError):
            estoque.movimentar(produto, 'Saida', 3)

        assert produto.quantidade == 10
        assert len(estoque.historico.movimentacoes) == 1


class TestPersistencia:
    def test_salvar_e_recarregar_preserva_os_produtos(self, arquivos, estoque):
        estoque.adicionar(arroz(10))
        estoque.adicionar(Produto('Mochila', 89.9, 3, 'Bolsas'))

        recarregado = Estoque(Historico(arquivos['historico']),
                              arquivos['produtos'])

        assert [p.to_dict() for p in recarregado.produtos] == \
               [p.to_dict() for p in estoque.produtos]

    def test_salvar_e_recarregar_preserva_o_historico(self, arquivos, estoque):
        estoque.adicionar(arroz(10))
        estoque.movimentar(estoque.encontrar('Arroz'), 'Saída', 4)

        recarregado = Historico(arquivos['historico'])

        assert [m.to_dict() for m in recarregado.movimentacoes] == \
               [m.to_dict() for m in estoque.historico.movimentacoes]

    def test_arquivo_inexistente_comeca_vazio(self, estoque):
        assert estoque.esta_vazio()
        assert estoque.historico.esta_vazio()

    def test_arquivo_vazio_comeca_vazio(self, arquivos):
        open(arquivos['produtos'], 'w').close()

        assert Estoque(Historico(arquivos['historico']),
                       arquivos['produtos']).esta_vazio()

    def test_json_invalido_comeca_vazio(self, arquivos):
        with open(arquivos['produtos'], 'w', encoding='utf-8') as arquivo:
            arquivo.write('{{{ nao e json')

        assert Estoque(Historico(arquivos['historico']),
                       arquivos['produtos']).esta_vazio()

    def test_registro_sem_os_campos_esperados_comeca_vazio(self, arquivos):
        with open(arquivos['produtos'], 'w', encoding='utf-8') as arquivo:
            json.dump([{'nome': 'Arroz'}], arquivo)

        assert Estoque(Historico(arquivos['historico']),
                       arquivos['produtos']).esta_vazio()

    def test_registro_com_valor_invalido_comeca_vazio(self, arquivos):
        with open(arquivos['produtos'], 'w', encoding='utf-8') as arquivo:
            json.dump([{'nome': 'Arroz', 'preco': -1,
                        'quantidade': 10, 'categoria': 'Comida'}], arquivo)

        assert Estoque(Historico(arquivos['historico']),
                       arquivos['produtos']).esta_vazio()

    def test_a_gravacao_nao_deixa_arquivo_temporario(self, tmp_path, estoque):
        estoque.adicionar(arroz(10))

        assert list(tmp_path.glob('*.tmp')) == []

    def test_falha_no_meio_da_gravacao_preserva_o_arquivo(self, arquivos,
                                                          estoque, monkeypatch):
        estoque.adicionar(arroz(10))

        with open(arquivos['produtos'], encoding='utf-8') as arquivo:
            antes = arquivo.read()

        def disco_cheio(*args, **kwargs):
            raise OSError('disco cheio')

        monkeypatch.setattr(main.json, 'dump', disco_cheio)

        with pytest.raises(OSError):
            estoque.adicionar(Produto('Mochila', 89.9, 3, 'Bolsas'))

        monkeypatch.undo()

        with open(arquivos['produtos'], encoding='utf-8') as arquivo:
            assert arquivo.read() == antes


class TestBusca:
    def test_encontrar_ignora_caixa_e_espacos(self, estoque):
        estoque.adicionar(arroz(10))

        assert estoque.encontrar('  arroz  ') is estoque.produtos[0]

    def test_encontrar_exige_o_nome_inteiro(self, estoque):
        estoque.adicionar(Produto('Caneta Azul', 2.5, 10, 'Material'))

        assert estoque.encontrar('caneta') is None

    def test_buscar_aceita_parte_do_nome(self, estoque):
        estoque.adicionar(Produto('Caneta Azul', 2.5, 10, 'Material'))
        estoque.adicionar(Produto('Caneta Preta', 2.5, 10, 'Material'))
        estoque.adicionar(arroz(10))

        encontrados = estoque.buscar('caneta')

        assert [p.nome for p in encontrados] == ['Caneta Azul', 'Caneta Preta']

    def test_buscar_sem_resultado_devolve_lista_vazia(self, estoque):
        estoque.adicionar(arroz(10))

        assert estoque.buscar('mochila') == []


class TestRelatorios:
    @pytest.fixture
    def estoque_cheio(self, estoque):
        estoque.adicionar(Produto('Caneta', 2.5, 50, 'Material'))
        estoque.adicionar(Produto('Mochila', 89.9, 3, 'Bolsas'))
        estoque.adicionar(Produto('Arroz', 5.0, 12, 'Comida'))
        return estoque

    def test_valor_total_soma_todos_os_produtos(self, estoque_cheio):
        assert estoque_cheio.valor_total() == pytest.approx(454.7)

    def test_total_itens_soma_as_quantidades(self, estoque_cheio):
        assert estoque_cheio.total_itens() == 65

    def test_mais_caro_e_mais_barato(self, estoque_cheio):
        assert estoque_cheio.mais_caro().nome == 'Mochila'
        assert estoque_cheio.mais_barato().nome == 'Caneta'

    def test_em_falta_lista_so_quem_esta_abaixo_do_minimo(self, estoque_cheio):
        assert [p.nome for p in estoque_cheio.em_falta()] == ['Mochila']

    def test_por_categoria_agrupa_em_ordem_alfabetica(self, estoque_cheio):
        agrupados = estoque_cheio.por_categoria()

        assert list(agrupados) == ['Bolsas', 'Comida', 'Material']
        assert [p.nome for p in agrupados['Bolsas']] == ['Mochila']

    def test_ordenados_por_preco(self, estoque_cheio):
        nomes = [p.nome for p in estoque_cheio.ordenados_por('preco')]

        assert nomes == ['Caneta', 'Arroz', 'Mochila']

    def test_ordenados_por_quantidade(self, estoque_cheio):
        nomes = [p.nome for p in estoque_cheio.ordenados_por('quantidade')]

        assert nomes == ['Mochila', 'Arroz', 'Caneta']

    def test_ordenados_por_nome_ignora_a_caixa(self, estoque):
        estoque.adicionar(Produto('banana', 1.0, 1, 'Comida'))
        estoque.adicionar(Produto('Abacate', 1.0, 1, 'Comida'))

        nomes = [p.nome for p in estoque.ordenados_por('nome')]

        assert nomes == ['Abacate', 'banana']

    def test_ordenados_por_categoria_desempata_pelo_nome(self, estoque_cheio):
        estoque_cheio.adicionar(Produto('Caderno', 15.0, 5, 'Material'))

        nomes = [p.nome for p in estoque_cheio.ordenados_por('categoria')]

        assert nomes == ['Mochila', 'Arroz', 'Caderno', 'Caneta']


class TestRemocao:
    def test_remover_tira_do_estoque_e_do_arquivo(self, arquivos, estoque):
        estoque.adicionar(arroz(10))
        estoque.remover(estoque.encontrar('Arroz'))

        recarregado = Estoque(Historico(arquivos['historico']),
                              arquivos['produtos'])

        assert estoque.esta_vazio()
        assert recarregado.esta_vazio()

    def test_remover_nao_apaga_o_historico(self, estoque):
        estoque.adicionar(arroz(10))
        estoque.remover(estoque.encontrar('Arroz'))

        assert len(estoque.historico.movimentacoes) == 1


class TestDataDaMovimentacao:
    def test_grava_em_iso_e_exibe_formatado(self):
        movimentacao = Movimentacao('Arroz', 'Entrada', 5, 5,
                                    '2026-09-25T16:33')

        assert movimentacao.to_dict()['data'] == '2026-09-25T16:33'
        assert movimentacao.data_formatada() == '25/09/2026 16:33'

    def test_historico_no_formato_antigo_continua_legivel(self):
        movimentacao = Movimentacao('Arroz', 'Entrada', 5, 5,
                                    '29/09/2026 17:01')

        assert movimentacao.data_formatada() == '29/09/2026 17:01'

    def test_data_nova_sai_em_iso(self):
        movimentacao = Movimentacao('Arroz', 'Entrada', 5, 5)

        assert 'T' in movimentacao.data
        assert len(movimentacao.data_formatada()) == len('25/09/2026 16:33')
