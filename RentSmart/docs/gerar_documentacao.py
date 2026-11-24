"""Gera docs/fluxograma_rentsmart.png e docs/RentSmart_Documentacao.pdf.

Os valores dos exemplos são calculados pelas classes reais do projeto, para que a
documentação corresponda exatamente ao funcionamento do programa.
Uso (na raiz do projeto):  python docs/gerar_documentacao.py
"""
import os
import sys
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from cliente import Cliente
from imovel import Apartamento, Casa, Estudio
from orcamento import Orcamento
from relatorio import brl

AUTOR = "Davi Evangelista Dantas"          # edite aqui e rode o script de novo
CURSO = "Análise e Desenvolvimento de Sistemas · UniFECAF"
DISCIPLINA = "Algorithmic Thinking & Introduction to Object-Oriented Programming"
PNG = os.path.join(RAIZ, "docs", "fluxograma_rentsmart.png")
PDF = os.path.join(RAIZ, "docs", "RentSmart_Documentacao.pdf")

NAVY, NAVY2, SKY, SKY2, ERR = "#0b2447", "#19376d", "#a5d7e8", "#e8f4fa", "#b3261e"


# ----------------------------------------------------------------------------- fluxograma
def fluxograma(caminho=PNG):
    nos = [
        ("term", "Início", .7), ("proc", "Informar dados do cliente\n(nome, e-mail e telefone)", 1.0),
        ("dec", "Dados\nválidos?", 1.4), ("proc", "Escolher tipo de imóvel,\nquartos e vagas", 1.0),
        ("dec", "Quartos e vagas\ncompatíveis?", 1.4), ("proc", "Calcular aluguel-base e\nadicional de garagem\n(subtotal)", 1.3),
        ("dec", "Apartamento\nsem crianças?", 1.4), ("proc", "Aluguel mensal final =\nsubtotal − desconto", 1.0),
        ("proc", "Escolher parcelas da taxa\ncontratual (R$ 2.000,00)", 1.0), ("dec", "Parcelas\nde 1 a 5?", 1.4),
        ("proc", "Valor da parcela =\n2.000 ÷ nº de parcelas", 1.0),
        ("proc", "Gerar projeção de 12 meses\n(taxa separada do aluguel)\ne salvar no histórico", 1.3),
        ("proc", "Exibir resultado; gerar PDF,\nCSV ou imprimir", 1.0), ("term", "Fim", .7)]
    gap, topo = .38, .85
    altura = topo + sum(n[2] for n in nos) + gap * (len(nos) - 1) + .4
    fig, ax = plt.subplots(figsize=(6.4, altura / 2), dpi=300)
    ax.set_xlim(0, 12.8); ax.set_ylim(0, altura); ax.axis("off")
    X, XS = 4.3, 10.2                       # coluna principal e coluna lateral
    ax.text(6.4, altura - .35, "Fluxograma do RentSmart", ha="center", va="center", fontsize=10, fontweight="bold", color=NAVY)
    y, pos = altura - topo, []
    for k, t, h in nos:
        pos.append((y - h / 2, h)); y -= h + gap

    def caixa(cx, cy, w, h, texto, kind):
        if kind == "term":
            p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle=f"round,pad=0,rounding_size={h / 2}", fc=NAVY, ec=NAVY)
        elif kind == "dec":
            p = Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)], fc=SKY, ec=NAVY2, lw=1.2)
        elif kind == "err":
            p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=.12", fc="#fdecea", ec=ERR, lw=1.2)
        else:
            p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=.12", fc=SKY2, ec=NAVY2, lw=1.2)
        ax.add_patch(p)
        ax.text(cx, cy, texto, ha="center", va="center", fontsize=8.4, linespacing=1.25,
                color="white" if kind == "term" else (ERR if kind == "err" else NAVY), fontweight="bold" if kind == "term" else "normal")

    def seta(pts, rotulo=None, rpos=None, ha="center"):
        xs, ys = zip(*pts)
        ax.plot(xs[:-1], ys[:-1], color=NAVY, lw=1.1, solid_capstyle="round") if len(pts) > 2 else None
        ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.1, shrinkA=0, shrinkB=0))
        if rotulo:
            ax.text(*rpos, rotulo, fontsize=8, color=NAVY, fontweight="bold", ha=ha, va="center")

    W = {"term": 2.6, "proc": 4.5, "dec": 4.5}
    for (k, t, h), (cy, _) in zip(nos, pos):
        caixa(X, cy, W[k], h, t, k)
    # setas principais
    for i in range(len(nos) - 1):
        (k, _, h), (cy, _) = nos[i], pos[i]
        (_, _, h2), (cy2, _) = nos[i + 1], pos[i + 1]
        a, b = cy - h / 2, cy2 + h2 / 2
        rot = "Sim" if k == "dec" and i != 6 else ("Não (desconto = 0)" if i == 6 else None)
        seta([(X, a), (X, b)], rot, (X + .25, (a + b) / 2) if rot else None, ha="left")
    # decisões de erro (1, 3, 9) voltam para a etapa anterior
    for d, destino in ((2, 1), (4, 3), (9, 8)):
        cy, h = pos[d]; cyd, hd = pos[destino]
        caixa(XS, cy, 3.4, 1.0, "Exibir mensagem\nde erro", "err")
        seta([(X + W["dec"] / 2, cy), (XS - 1.7, cy)], "Não", ((X + W["dec"] / 2 + XS - 1.7) / 2, cy + .25))
        seta([(XS, cy + .5), (XS, cyd), (X + W["proc"] / 2, cyd)])
    # decisão do desconto (6): Sim -> desconto de 5%
    cy, h = pos[6]; cyn, hn = pos[7]
    caixa(XS, cy, 3.4, 1.0, "Desconto = 5% do\nsubtotal (apto)", "proc")
    seta([(X + W["dec"] / 2, cy), (XS - 1.7, cy)], "Sim", ((X + W["dec"] / 2 + XS - 1.7) / 2, cy + .25))
    seta([(XS, cy - .5), (XS, cyn), (X + W["proc"] / 2, cyn)])
    fig.savefig(caminho, bbox_inches="tight", pad_inches=.15, facecolor="white")
    plt.close(fig)
    return caminho


# ----------------------------------------------------------------------------- PDF
def pdf(caminho=PDF):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle)

    navy, sky2 = colors.HexColor(NAVY), colors.HexColor(SKY2)
    B = ParagraphStyle("B", fontName="Helvetica", fontSize=10.3, leading=14.8, alignment=TA_JUSTIFY, spaceAfter=6)
    H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=navy, spaceBefore=12, spaceAfter=7, keepWithNext=1)
    H2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=colors.HexColor(NAVY2), spaceBefore=8, spaceAfter=4, keepWithNext=1)
    C = ParagraphStyle("C", parent=B, fontSize=9, leading=12, alignment=0, spaceAfter=0)
    CB = ParagraphStyle("CB", parent=C, fontName="Helvetica-Bold", textColor=colors.white)
    BL = ParagraphStyle("BL", parent=B, leftIndent=14, bulletIndent=2, spaceAfter=3, alignment=0)
    CAP = ParagraphStyle("CAP", parent=B, fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#5b6b82"))
    COD = ParagraphStyle("COD", fontName="Courier", fontSize=8.6, leading=11, backColor=sky2, borderPadding=7, leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10)

    def P(t, s=B): return Paragraph(t, s)
    def bullets(itens): return [Paragraph(i, BL, bulletText="•") for i in itens]

    def tabela(linhas, larguras, zebra=True):
        data = [[Paragraph(c, CB) for c in linhas[0]]] + [[Paragraph(str(c), C) for c in r] for r in linhas[1:]]
        t = Table(data, colWidths=[w * cm for w in larguras], repeatRows=1)
        est = [("BACKGROUND", (0, 0), (-1, 0), navy), ("VALIGN", (0, 0), (-1, -1), "TOP"),
               ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#c9d8e6")),
               ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
        if zebra: est += [("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, sky2])]
        t.setStyle(TableStyle(est)); return t

    cli = Cliente("Maria da Silva", "maria@email.com", "(11) 91234-5678")
    def calc(im, n=1): return Orcamento(cli, im, n)
    ex = calc(Apartamento(2, 1, False), 3)
    n_testes = unittest.defaultTestLoader.discover(os.path.join(RAIZ, "tests")).countTestCases()

    S = []
    # capa
    S += [Spacer(1, 5 * cm), P("UniFECAF", ParagraphStyle("t0", parent=B, alignment=TA_CENTER, fontSize=12, textColor=colors.HexColor(NAVY2))),
          P("RentSmart", ParagraphStyle("t1", fontName="Helvetica-Bold", fontSize=40, leading=46, alignment=TA_CENTER, textColor=navy)),
          P("Sistema Inteligente de Orçamento de Locação", ParagraphStyle("t2", parent=B, alignment=TA_CENTER, fontSize=15, leading=20)),
          Spacer(1, .6 * cm), P("Documentação acadêmica do projeto", ParagraphStyle("t3", parent=B, alignment=TA_CENTER, fontSize=12)),
          Spacer(1, 5 * cm),
          P(f"<b>Disciplina:</b> {DISCIPLINA}", ParagraphStyle("t4", parent=B, alignment=TA_CENTER)),
          P(f"<b>Curso:</b> {CURSO}", ParagraphStyle("t5", parent=B, alignment=TA_CENTER)),
          P(f"<b>Aluno:</b> {AUTOR}", ParagraphStyle("t6", parent=B, alignment=TA_CENTER)),
          P("<b>Cliente fictício do trabalho:</b> R.M Imóveis", ParagraphStyle("t7", parent=B, alignment=TA_CENTER)),
          P("Novembro de 2026", ParagraphStyle("t8", parent=B, alignment=TA_CENTER)), PageBreak()]
    # 1
    S += [P("1. Análise do problema", H1),
          P("A imobiliária fictícia R.M Imóveis monta orçamentos de locação de casas, apartamentos e estúdios. Cada tipo de imóvel tem preço, regras de garagem e condições comerciais próprias, o que torna o cálculo manual lento e sujeito a erros, principalmente na aplicação do desconto e na separação entre o aluguel mensal e a taxa contratual."),
          P("O RentSmart resolve esse problema automatizando o orçamento: o atendente informa os dados do cliente e as características do imóvel, e o sistema valida as informações, aplica as regras comerciais, calcula o aluguel mensal e a taxa contratual parcelada e gera uma projeção financeira de 12 meses, exportável em CSV e PDF."),
          P("<b>Objetivo geral:</b> calcular orçamentos de locação de forma correta, padronizada e rastreável."),
          P("<b>Objetivos específicos:</b>"), *bullets([
              "aplicar corretamente as regras de preço, garagem e desconto de cada tipo de imóvel;",
              "manter a taxa contratual sempre separada do aluguel mensal;",
              "gerar a projeção de 12 meses e arquivos CSV e PDF para o cliente;",
              "guardar o histórico para consulta, filtro e exportação;",
              "organizar o código com Programação Orientada a Objetos."])]
    # 2
    S += [P("2. Regras de negócio", H1),
          tabela([["Imóvel", "Aluguel-base", "Garagem", "Desconto"],
                  ["Apartamento", "1 quarto: R$ 700,00<br/>2 quartos: R$ 900,00", "R$ 300,00 por vaga (no máximo 1 vaga)", "5% sobre aluguel-base + garagem quando o cliente não tem crianças"],
                  ["Casa", "1 quarto: R$ 900,00<br/>2 quartos: R$ 1.150,00", "R$ 300,00 por vaga (no máximo 1 vaga)", "Não se aplica"],
                  ["Estúdio", "R$ 1.200,00 (1 ambiente)", "Pacote de 2 vagas por R$ 250,00; cada vaga adicional custa R$ 60,00 (no máximo 6 vagas)", "Não se aplica"]], [2.6, 4.2, 5.4, 4.8]),
          Spacer(1, 8)] + bullets([
              "<b>Taxa contratual:</b> valor fixo de R$ 2.000,00, parcelável em 1 a 5 vezes. Nunca é somada ao aluguel mensal; aparece em coluna própria na projeção.",
              "<b>Aluguel mensal final</b> = (aluguel-base + garagem) − desconto.",
              "<b>Arredondamento:</b> valores com duas casas decimais; a diferença de centavos fica na última parcela da taxa (ex.: 3 parcelas = 666,67 + 666,67 + 666,66).",
              "<b>Estúdio:</b> como o pacote inicial já inclui duas vagas, o estúdio aceita 0 vagas ou 2 ou mais; 1 vaga isolada é recusada.",
              "<b>Validações:</b> campos obrigatórios, e-mail válido, quartos permitidos por tipo, vagas compatíveis, parcelas entre 1 e 5 e nenhum valor negativo."])
    # 3
    S += [P("3. Entradas, processamentos e saídas", H1),
          tabela([["Entradas", "Processamentos", "Saídas"],
                  ["Nome completo, e-mail e telefone<br/>Tipo do imóvel<br/>Quantidade de quartos<br/>Quantidade de vagas<br/>Presença de crianças (apartamento)<br/>Número de parcelas (1 a 5)",
                   "Validar os dados<br/>Obter o aluguel-base<br/>Calcular o adicional de garagem<br/>Calcular o desconto<br/>Calcular o aluguel mensal final<br/>Dividir a taxa contratual<br/>Montar a projeção de 12 meses<br/>Gravar o histórico",
                   "Resumo financeiro detalhado<br/>Tabela de projeção de 12 meses<br/>CSV da projeção e do histórico<br/>PDF do orçamento<br/>Impressão<br/>Histórico com busca e filtro"]], [5.4, 5.8, 5.8], zebra=False)]
    # 4 fluxograma
    S += [P("4. Fluxograma", H1),
          P("O fluxograma abaixo representa a sequência real executada pelo sistema. As decisões de validação devolvem o usuário à etapa anterior com uma mensagem de erro; a decisão do desconto separa o caso do apartamento sem crianças dos demais. O arquivo também está disponível em <font face='Courier'>docs/fluxograma_rentsmart.png</font>.", B)]
    from PIL import Image as PI
    w, h = PI.open(PNG).size
    altura = 23.2 * cm
    S += [PageBreak(), Image(PNG, width=altura * w / h, height=altura), P("Figura 1 - Fluxograma de funcionamento do RentSmart.", CAP)]
    # 5 e 6 classes
    S += [PageBreak(), P("5. Estrutura das classes", H1),
          P("O sistema é dividido em quatro responsabilidades, cada uma em seu arquivo Python, mais a camada web em <font face='Courier'>main.py</font>, que apenas recebe as requisições do Flask e delega o trabalho às classes."),
          Preformatted("""Cliente          valida e guarda os dados do cliente
Imovel (base)    regras comuns de um imóvel
  |-- Apartamento   R$ 300/vaga (máx. 1) + desconto de 5% sem crianças
  |-- Casa          R$ 300/vaga (máx. 1)
  |-- Estudio       pacote 2 vagas R$ 250 + R$ 60 por vaga extra
Orcamento        usa Cliente + Imovel: calcula valores e projeção
Relatorio        histórico (JSON), CSV e PDF
main.py          rotas Flask (interface web)""", COD),
          P("Relações: <b>Orcamento</b> é composto por um <b>Cliente</b> e um <b>Imovel</b> (composição); <b>Apartamento</b>, <b>Casa</b> e <b>Estudio</b> herdam de <b>Imovel</b> (herança); <b>Relatorio</b> recebe um <b>Orcamento</b> para gravar e exportar (dependência). Exceções de validação usam a classe <b>ValidacaoErro</b>, definida em <font face='Courier'>cliente.py</font>."),
          P("6. Atributos e métodos", H1),
          tabela([["Classe", "Atributos", "Métodos principais"],
                  ["Cliente<br/>(cliente.py)", "_nome, _email, _telefone (privados, com propriedades somente leitura)", "__init__ (valida nome, e-mail e telefone), para_dict()"],
                  ["Imovel<br/>(imovel.py)", "tipo, quartos_validos, precos (da classe); _quartos, _vagas, _criancas", "aluguel_base(), valor_vagas(), percentual_desconto(), _validar_vagas() (cada subclasse implementa o seu)"],
                  ["Apartamento<br/>Casa<br/>Estudio", "herdam os atributos; cada uma define tipo, quartos válidos e tabela de preços", "sobrescrevem _validar_vagas() e valor_vagas(); Apartamento também sobrescreve percentual_desconto()"],
                  ["Orcamento<br/>(orcamento.py)", "cliente, imovel, parcelas, criado_em, base, vagas, subtotal, pct, desconto, aluguel, taxa, valor_parcela", "__init__ (calcula tudo), projecao() (12 meses), para_dict()"],
                  ["Relatorio<br/>(relatorio.py)", "ARQ (caminho do histórico)", "carregar(), salvar(), buscar(), metricas(), csv_projecao(), salvar_csv_projecao(), csv_historico(), pdf()"]], [3.0, 6.4, 7.6])]
    # 7 pensamento algorítmico
    S += [P("7. Aplicação do pensamento algorítmico", H1),
          P("<b>Decomposição.</b> O problema foi dividido em partes menores e independentes: validar o cliente, escolher e validar o imóvel, calcular valores, parcelar a taxa, montar a projeção e exportar. Cada parte virou um método ou uma classe."),
          P("<b>Reconhecimento de padrões.</b> Casas, apartamentos e estúdios compartilham o mesmo padrão (aluguel-base, garagem, desconto), mudando só as regras de cada passo. Esse padrão comum virou a classe base Imovel."),
          P("<b>Abstração.</b> O Orcamento não precisa saber como cada imóvel calcula a garagem; ele só chama valor_vagas() e percentual_desconto(). Detalhes de interface (Flask, HTML) ficam fora do cálculo."),
          P("<b>Algoritmo.</b> A sequência de passos, com decisões e repetições, está descrita no pseudocódigo abaixo e no fluxograma da seção 4."),
          KeepTogether([Preformatted("""INÍCIO
  LER nome, e-mail, telefone
  SE dados inválidos ENTÃO exibir erro e repetir a leitura
  LER tipo, quartos, vagas
  SE quartos ou vagas incompatíveis com o tipo ENTÃO exibir erro e repetir
  aluguel_base  <- preço(tipo, quartos)
  garagem       <- valor_vagas(tipo, vagas)
  subtotal      <- aluguel_base + garagem
  SE tipo = Apartamento E sem crianças ENTÃO desconto <- 5% de subtotal
  SENÃO desconto <- 0
  aluguel_final <- subtotal - desconto
  LER parcelas
  SE parcelas < 1 OU parcelas > 5 ENTÃO exibir erro e repetir
  valor_parcela <- 2000 / parcelas
  PARA mes DE 1 ATÉ 12 FAÇA
     parcela <- (mes <= parcelas) ? valor_parcela : 0
     total   <- aluguel_final + parcela
  FIM PARA
  GRAVAR histórico; EXIBIR resultado; EXPORTAR CSV e PDF
FIM""", COD)]),
          P("O algoritmo usa <b>sequência</b> (cálculos em ordem), <b>seleção</b> (validações e desconto) e <b>repetição</b> (os 12 meses da projeção).")]
    # 8 POO
    S += [P("8. Justificativa da Programação Orientada a Objetos", H1),
          P("A POO foi escolhida porque o problema tem entidades claras (cliente, imóvel, orçamento, relatório) e porque as regras variam por tipo de imóvel:")] + bullets([
              "<b>Encapsulamento:</b> atributos privados (_nome, _quartos, _vagas) só são lidos por propriedades, e a validação acontece no construtor, de modo que um objeto inválido nunca existe.",
              "<b>Herança:</b> Apartamento, Casa e Estudio reaproveitam a estrutura de Imovel e mudam apenas o que é diferente.",
              "<b>Polimorfismo:</b> o Orcamento chama valor_vagas() e percentual_desconto() sem usar cadeias de if por tipo; adicionar um novo tipo exige criar uma classe, sem alterar o cálculo.",
              "<b>Separação de responsabilidades:</b> regras comerciais (imovel, orcamento), dados do cliente (cliente), persistência e exportação (relatorio) e interface web (main) ficam isoladas, o que facilita testar e manter.",
              "<b>Tratamento de exceções:</b> ValidacaoErro representa erros de regra de negócio, e as rotas Flask convertem em mensagens claras para o usuário."])
    # 9 exemplo real
    S += [KeepTogether([P("9. Exemplo de cálculo (executado pelo sistema)", H1),
          P(f"Apartamento de 2 quartos, 1 vaga de garagem, cliente sem crianças, taxa em 3 parcelas: aluguel-base {brl(ex.base)} + garagem {brl(ex.vagas)} = subtotal {brl(ex.subtotal)}; desconto de {ex.pct}% = {brl(ex.desconto)}; <b>aluguel mensal final {brl(ex.aluguel)}</b>. Taxa contratual de {brl(ex.taxa)} em 3 parcelas de {brl(ex.valor_parcela)} (a última de {brl(ex.projecao()[2]['parcela'])})."),
          tabela([["Mês", "Aluguel", "Parcela da taxa", "Total previsto"]] +
                 [[l["mes"], brl(l["aluguel"]), brl(l["parcela"]) if l["parcela"] else "-", brl(l["total"])] for l in ex.projecao()], [2, 4.5, 4.5, 4.5])])]
    # 10 testes
    cen = [("Apartamento de 1 quarto", calc(Apartamento(1, 0, True))), ("Apartamento de 2 quartos", calc(Apartamento(2, 0, True))),
           ("Casa de 1 quarto", calc(Casa(1, 0))), ("Casa de 2 quartos", calc(Casa(2, 0))),
           ("Estúdio com duas vagas", calc(Estudio(1, 2))), ("Estúdio com 4 vagas (2 adicionais)", calc(Estudio(1, 4))),
           ("Apartamento 2q + 1 vaga, sem crianças", calc(Apartamento(2, 1, False)))]
    S += [P("10. Testes automatizados", H1),
          P(f"O projeto possui {n_testes} testes em <font face='Courier'>tests/test_rentsmart.py</font> (biblioteca unittest, sem dependências extras). Resultados esperados dos principais cenários:"),
          tabela([["Cenário", "Aluguel mensal esperado"]] + [[n, brl(o.aluguel)] for n, o in cen], [10, 6]), Spacer(1, 8),
          tabela([["Parcelas da taxa", "Valor da parcela"]] + [[f"{n}x", brl(calc(Casa(1, 0), n).valor_parcela)] for n in range(1, 6)], [10, 6]), Spacer(1, 6),
          P("Também são testados o CSV (arquivo real com 12 meses), as validações (quartos, vagas, e-mail, parcelas) e o fluxo completo da aplicação Flask. Comando: <font face='Courier'>python -m unittest discover -s tests -v</font>.")]
    # 11 estrutura
    S += [P("11. Estrutura do projeto e execução", H1),
          KeepTogether([Preformatted("""rentsmart/
  main.py  cliente.py  imovel.py  orcamento.py  relatorio.py
  gerar_csv.py            gera o CSV da projeção (linha de comando)
  requirements.txt  README.md  .gitignore
  templates/  static/     interface web
  data/                   histórico (criado em uso)
  exemplos/               CSV de exemplo
  tests/                  testes automatizados
  docs/                   este PDF, fluxograma PNG e gerador""", COD)]),
          P("Para executar: <font face='Courier'>pip install -r requirements.txt</font> e depois <font face='Courier'>python main.py</font>; a aplicação abre em http://127.0.0.1:5000. Os detalhes estão no README.md."),
          P("12. Conclusão", H1),
          P("O RentSmart cumpre os requisitos propostos: aplica as regras comerciais corretamente, separa taxa e aluguel, gera projeção de 12 meses em CSV, mantém histórico e usa Programação Orientada a Objetos com testes automatizados. A estrutura permite incluir novos tipos de imóvel ou novas regras sem reescrever o cálculo existente.")]

    def rodape(c, d):
        c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#5b6b82"))
        if d.page > 1:
            c.drawString(2 * cm, 1.2 * cm, "RentSmart · R.M Imóveis · UniFECAF"); c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {d.page}")
        c.restoreState()

    doc = SimpleDocTemplate(caminho, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                            title="RentSmart - Documentação acadêmica", author=AUTOR, subject=DISCIPLINA)
    doc.build(S, onFirstPage=rodape, onLaterPages=rodape)
    return caminho


if __name__ == "__main__":
    print("PNG:", fluxograma()); print("PDF:", pdf())
