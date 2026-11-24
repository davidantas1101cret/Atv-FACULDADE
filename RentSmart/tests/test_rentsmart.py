"""Testes automatizados do RentSmart (unittest, sem dependências extras).

Executar na raiz do projeto:  python -m unittest discover -s tests -v
"""
import csv
import os
import sys
import tempfile
import unittest
from decimal import Decimal as D

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import relatorio
from cliente import Cliente, ValidacaoErro
from imovel import Apartamento, Casa, Estudio
from orcamento import Orcamento
from relatorio import Relatorio
import gerar_csv


def cliente():
    return Cliente("Maria da Silva", "maria@email.com", "(11) 91234-5678")


def orc(imovel, parcelas=1):
    return Orcamento(cliente(), imovel, parcelas)


class TestImoveis(unittest.TestCase):
    def test_apartamento_1_quarto(self):
        o = orc(Apartamento(1, 0, True))
        self.assertEqual(o.base, D("700")); self.assertEqual(o.aluguel, D("700.00"))

    def test_apartamento_2_quartos(self):
        o = orc(Apartamento(2, 0, True))
        self.assertEqual(o.base, D("900")); self.assertEqual(o.aluguel, D("900.00"))

    def test_apartamento_com_vaga(self):
        o = orc(Apartamento(2, 1, True))
        self.assertEqual(o.vagas, D("300")); self.assertEqual(o.aluguel, D("1200.00"))

    def test_casa_1_quarto(self):
        self.assertEqual(orc(Casa(1, 0)).aluguel, D("900.00"))

    def test_casa_2_quartos(self):
        self.assertEqual(orc(Casa(2, 0)).aluguel, D("1150.00"))

    def test_casa_com_vaga(self):
        self.assertEqual(orc(Casa(2, 1)).aluguel, D("1450.00"))

    def test_estudio_duas_vagas(self):
        o = orc(Estudio(1, 2))
        self.assertEqual(o.vagas, D("250")); self.assertEqual(o.aluguel, D("1450.00"))

    def test_estudio_vagas_adicionais(self):
        # pacote de 2 vagas (R$ 250) + 2 vagas extras (2 x R$ 60)
        o = orc(Estudio(1, 4))
        self.assertEqual(o.vagas, D("370")); self.assertEqual(o.aluguel, D("1570.00"))

    def test_estudio_sem_vaga(self):
        self.assertEqual(orc(Estudio(1, 0)).aluguel, D("1200.00"))


class TestDesconto(unittest.TestCase):
    def test_apartamento_sem_criancas_tem_5_por_cento(self):
        o = orc(Apartamento(2, 1, False))  # (900 + 300) = 1200 -> 5% = 60
        self.assertEqual(o.subtotal, D("1200")); self.assertEqual(o.desconto, D("60.00"))
        self.assertEqual(o.aluguel, D("1140.00"))

    def test_apartamento_1_quarto_sem_criancas_sem_vaga(self):
        o = orc(Apartamento(1, 0, False))
        self.assertEqual(o.desconto, D("35.00")); self.assertEqual(o.aluguel, D("665.00"))

    def test_apartamento_com_criancas_nao_tem_desconto(self):
        self.assertEqual(orc(Apartamento(2, 1, True)).desconto, D("0.00"))

    def test_casa_e_estudio_nunca_tem_desconto(self):
        self.assertEqual(orc(Casa(2, 1, False)).desconto, D("0.00"))
        self.assertEqual(orc(Estudio(1, 2, False)).desconto, D("0.00"))


class TestParcelamento(unittest.TestCase):
    ESPERADO = {1: D("2000.00"), 2: D("1000.00"), 3: D("666.67"), 4: D("500.00"), 5: D("400.00")}

    def test_parcelas_de_1_a_5(self):
        for n, valor in self.ESPERADO.items():
            with self.subTest(parcelas=n):
                o = orc(Casa(1, 0), n)
                self.assertEqual(o.taxa, D("2000.00"))
                self.assertEqual(o.valor_parcela, valor)

    def test_projecao_soma_exatamente_a_taxa(self):
        for n in range(1, 6):
            with self.subTest(parcelas=n):
                proj = orc(Casa(1, 0), n).projecao()
                self.assertEqual(sum(l["parcela"] for l in proj), D("2000.00"))
                self.assertEqual(sum(1 for l in proj if l["parcela"] > 0), n)

    def test_taxa_fica_separada_do_aluguel(self):
        o = orc(Apartamento(2, 1, False), 4)
        for l in o.projecao():
            self.assertEqual(l["aluguel"], o.aluguel)
            self.assertEqual(l["total"], l["aluguel"] + l["parcela"])

    def test_projecao_tem_12_meses(self):
        self.assertEqual([l["mes"] for l in orc(Casa(1, 0)).projecao()], list(range(1, 13)))


class TestValidacoes(unittest.TestCase):
    def test_parcelas_fora_do_intervalo(self):
        for n in (0, 6, -1):
            with self.subTest(parcelas=n), self.assertRaises(ValidacaoErro):
                orc(Casa(1, 0), n)

    def test_quartos_invalidos(self):
        for cls, q in ((Apartamento, 3), (Casa, 0), (Estudio, 2)):
            with self.subTest(tipo=cls.__name__), self.assertRaises(ValidacaoErro):
                cls(q, 0)

    def test_vagas_negativas(self):
        with self.assertRaises(ValidacaoErro):
            Casa(1, -1)

    def test_vagas_incompativeis(self):
        with self.assertRaises(ValidacaoErro): Apartamento(1, 2)
        with self.assertRaises(ValidacaoErro): Casa(1, 2)
        with self.assertRaises(ValidacaoErro): Estudio(1, 1)
        with self.assertRaises(ValidacaoErro): Estudio(1, 7)

    def test_cliente_invalido(self):
        for args in (("Maria", "a@b.com", "11912345678"), ("Maria Silva", "email-invalido", "11912345678"),
                     ("Maria Silva", "a@b.com", "123"), ("", "", "")):
            with self.subTest(args=args), self.assertRaises(ValidacaoErro):
                Cliente(*args)


class TestCSV(unittest.TestCase):
    def test_arquivo_csv_real_com_12_meses(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "sub", "projecao.csv")
            Relatorio.salvar_csv_projecao(orc(Apartamento(2, 1, False), 3), caminho)
            self.assertTrue(os.path.isfile(caminho))
            with open(caminho, "rb") as f:
                self.assertTrue(f.read(3) == b"\xef\xbb\xbf")  # BOM para o Excel
            with open(caminho, newline="", encoding="utf-8-sig") as f:
                linhas = list(csv.reader(f, delimiter=";"))
            self.assertEqual(linhas[0], ["Mês", "Valor do aluguel", "Parcela da taxa contratual", "Total previsto"])
            self.assertEqual(len(linhas), 13)
            self.assertEqual(linhas[1], ["1", "1140,00", "666,67", "1806,67"])
            self.assertEqual(linhas[3], ["3", "1140,00", "666,66", "1806,66"])
            self.assertEqual(linhas[4], ["4", "1140,00", "0,00", "1140,00"])

    def test_script_gerar_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = os.path.join(pasta, "x.csv")
            self.assertEqual(gerar_csv.main(["--tipo", "estudio", "--vagas", "4", "--parcelas", "5", "--saida", destino]), 0)
            self.assertTrue(os.path.getsize(destino) > 0)
            self.assertEqual(gerar_csv.main(["--parcelas", "9", "--saida", destino]), 1)


try:
    import flask  # noqa: F401
    TEM_FLASK = True
except ImportError:
    TEM_FLASK = False


@unittest.skipUnless(TEM_FLASK, "Flask não instalado: rode pip install -r requirements.txt")
class TestAplicacaoFlask(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.arq_original = relatorio.ARQ
        relatorio.ARQ = os.path.join(self.tmp.name, "historico.json")
        import main
        main._cache.clear()
        self.c = main.app.test_client()

    def tearDown(self):
        relatorio.ARQ = self.arq_original
        self.tmp.cleanup()

    DADOS = dict(nome="Ana Souza", email="ana@email.com", telefone="11912345678", tipo="apartamento",
                 quartos=2, vagas=1, criancas="nao", parcelas=3)

    def test_fluxo_completo(self):
        r = self.c.post("/novo", data=self.DADOS, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn("1.140,00", r.data.decode())
        csv_r = self.c.get("/orcamento/1/projecao.csv")
        self.assertIn("text/csv", csv_r.content_type)
        self.assertEqual(len(csv_r.data.decode("utf-8-sig").strip().splitlines()), 13)
        self.assertTrue(self.c.get("/orcamento/1/orcamento.pdf").data.startswith(b"%PDF"))
        self.assertIn("Ana Souza", self.c.get("/historico?q=ana").data.decode())
        self.assertNotIn("Ana Souza", self.c.get("/historico?tipo=casa").data.decode())
        for rota in ("/", "/novo", "/documentacao", "/historico.csv"):
            self.assertEqual(self.c.get(rota).status_code, 200)

    def test_entrada_invalida_retorna_erro(self):
        r = self.c.post("/novo", data={**self.DADOS, "parcelas": 9})
        self.assertEqual(r.status_code, 400)
        self.assertIn("1 a 5", r.data.decode())
        self.assertEqual(self.c.get("/orcamento/99").status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
