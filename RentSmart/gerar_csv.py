"""Gera o arquivo CSV com a projeção de 12 meses pela linha de comando.

Exemplos:
    python gerar_csv.py
    python gerar_csv.py --tipo estudio --vagas 4 --parcelas 5 --saida exports/estudio.csv
    python gerar_csv.py --tipo apartamento --quartos 2 --vagas 1 --sem-criancas --parcelas 3
"""
import argparse
import sys

from cliente import Cliente, ValidacaoErro
from imovel import TIPOS
from orcamento import Orcamento
from relatorio import Relatorio


def main(argv=None):
    p = argparse.ArgumentParser(description="Gera o CSV da projeção financeira de 12 meses do RentSmart.")
    p.add_argument("--tipo", choices=sorted(TIPOS), default="apartamento")
    p.add_argument("--quartos", type=int, default=1)
    p.add_argument("--vagas", type=int, default=0)
    p.add_argument("--sem-criancas", action="store_true", help="cliente sem crianças (desconto de 5% só em apartamento)")
    p.add_argument("--parcelas", type=int, default=1, help="parcelas da taxa contratual (1 a 5)")
    p.add_argument("--nome", default="Cliente Exemplo")
    p.add_argument("--email", default="cliente@exemplo.com")
    p.add_argument("--telefone", default="(11) 91234-5678")
    p.add_argument("--saida", default="exports/projecao_12_meses.csv")
    a = p.parse_args(argv)
    try:
        orc = Orcamento(Cliente(a.nome, a.email, a.telefone),
                        TIPOS[a.tipo](a.quartos, a.vagas, not a.sem_criancas), a.parcelas)
        caminho = Relatorio.salvar_csv_projecao(orc, a.saida)
    except (ValidacaoErro, RuntimeError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    print(f"CSV gerado: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
