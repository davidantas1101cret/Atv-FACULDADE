"""Classes de imóveis (herança + polimorfismo). Valores em Decimal."""
from decimal import Decimal as D
from cliente import ValidacaoErro


class Imovel:
    tipo = "Imóvel"
    quartos_validos = ()
    precos = {}

    def __init__(self, quartos, vagas=0, tem_criancas=True):
        if quartos not in self.quartos_validos:
            raise ValidacaoErro(f"{self.tipo}: quantidade de quartos inválida. Opções: {', '.join(map(str, self.quartos_validos))}.")
        if not isinstance(vagas, int) or vagas < 0:
            raise ValidacaoErro("A quantidade de vagas não pode ser negativa.")
        self._quartos, self._vagas, self._criancas = quartos, vagas, tem_criancas
        self._validar_vagas()

    def _validar_vagas(self): raise NotImplementedError
    def aluguel_base(self): return self.precos[self._quartos]
    def valor_vagas(self): raise NotImplementedError
    def percentual_desconto(self): return D("0")

    @property
    def quartos(self): return self._quartos
    @property
    def vagas(self): return self._vagas
    @property
    def tem_criancas(self): return self._criancas


class Apartamento(Imovel):
    tipo = "Apartamento"
    quartos_validos = (1, 2)
    precos = {1: D("700"), 2: D("900")}

    def _validar_vagas(self):
        if self._vagas > 1: raise ValidacaoErro("Apartamento permite no máximo 1 vaga de garagem.")
    def valor_vagas(self): return D("300") * self._vagas
    def percentual_desconto(self): return D("0") if self._criancas else D("5")


class Casa(Imovel):
    tipo = "Casa"
    quartos_validos = (1, 2)
    precos = {1: D("900"), 2: D("1150")}

    def _validar_vagas(self):
        if self._vagas > 1: raise ValidacaoErro("Casa permite no máximo 1 vaga de garagem.")
    def valor_vagas(self): return D("300") * self._vagas


class Estudio(Imovel):
    tipo = "Estúdio"
    quartos_validos = (1,)
    precos = {1: D("1200")}

    def _validar_vagas(self):
        if self._vagas == 1: raise ValidacaoErro("Estúdio contrata o pacote de 2 vagas (ou nenhuma). Escolha 0 ou 2 ou mais.")
        if self._vagas > 6: raise ValidacaoErro("Estúdio permite no máximo 6 vagas.")
    def valor_vagas(self):
        if self._vagas == 0: return D("0")
        return D("250") + D("60") * (self._vagas - 2)


TIPOS = {"apartamento": Apartamento, "casa": Casa, "estudio": Estudio}
