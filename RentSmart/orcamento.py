"""Classe Orcamento: aplica as regras comerciais e gera a projeção de 12 meses."""
from datetime import datetime
from decimal import Decimal as D, ROUND_HALF_UP
from cliente import ValidacaoErro

TAXA_CONTRATUAL = D("2000.00")


def _q(v): return v.quantize(D("0.01"), ROUND_HALF_UP)


class Orcamento:
    def __init__(self, cliente, imovel, parcelas):
        if not isinstance(parcelas, int) or not 1 <= parcelas <= 5:
            raise ValidacaoErro("O parcelamento da taxa contratual deve ser de 1 a 5 vezes.")
        self.cliente, self.imovel, self.parcelas = cliente, imovel, parcelas
        self.criado_em = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.base = imovel.aluguel_base()
        self.vagas = imovel.valor_vagas()
        self.subtotal = self.base + self.vagas
        self.pct = imovel.percentual_desconto()
        self.desconto = _q(self.subtotal * self.pct / 100)
        self.aluguel = _q(self.subtotal - self.desconto)
        self.taxa = TAXA_CONTRATUAL
        self.valor_parcela = _q(self.taxa / parcelas)

    def projecao(self):
        """12 meses. Taxa fica em colunas separadas do aluguel; ajusta centavos na última parcela."""
        linhas, restante = [], self.taxa
        for mes in range(1, 13):
            p = D("0")
            if mes <= self.parcelas:
                p = restante if mes == self.parcelas else self.valor_parcela
                restante -= p
            linhas.append({"mes": mes, "aluguel": self.aluguel, "parcela": p, "total": self.aluguel + p})
        return linhas

    def para_dict(self):
        i = self.imovel
        return {"criado_em": self.criado_em, **self.cliente.para_dict(), "tipo": i.tipo, "quartos": i.quartos,
                "vagas": i.vagas, "criancas": i.tem_criancas, "base": str(self.base), "valor_vagas": str(self.vagas),
                "pct": str(self.pct), "desconto": str(self.desconto), "aluguel": str(self.aluguel),
                "taxa": str(self.taxa), "parcelas": self.parcelas, "valor_parcela": str(self.valor_parcela)}
