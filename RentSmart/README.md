# RentSmart · Sistema Inteligente de Orçamento de Locação

Aplicação web em Python (Flask) para a imobiliária fictícia **R.M Imóveis**, desenvolvida como trabalho acadêmico da **UniFECAF** na disciplina *Algorithmic Thinking & Introduction to Object-Oriented Programming*.

O sistema automatiza orçamentos de locação de apartamentos, casas e estúdios: aplica as regras comerciais, calcula o aluguel mensal e a taxa contratual parcelada, e gera uma projeção financeira de 12 meses (tela, CSV e PDF).

## Tecnologias

- Python 3.10 ou superior
- Flask (interface web e rotas)
- ReportLab (PDF do orçamento)
- HTML, CSS e JavaScript (somente para a navegação entre as etapas do formulário; todos os cálculos ficam no Python)
- unittest (testes automatizados, biblioteca padrão)

## Estrutura de pastas

```
rentsmart/
├── main.py              # rotas Flask (interface web)
├── cliente.py           # classe Cliente e exceção ValidacaoErro
├── imovel.py            # classe Imovel e subclasses Apartamento, Casa, Estudio
├── orcamento.py         # classe Orcamento (cálculos e projeção de 12 meses)
├── relatorio.py         # classe Relatorio (histórico, CSV e PDF)
├── iniciar.bat / iniciar.sh   # inicia o sistema com um clique
├── gerar_csv.py         # gera o CSV da projeção pela linha de comando
├── requirements.txt     # dependências
├── templates/           # páginas HTML (Jinja2)
├── static/              # CSS
├── data/                # histórico de orçamentos (criado durante o uso)
├── exemplos/            # CSV de exemplo da projeção de 12 meses
├── tests/               # testes automatizados
└── docs/                # documentação em PDF, fluxograma PNG e script gerador
```

## Como instalar as dependências

```bash
python -m venv venv
# Windows:      venv\Scripts\activate
# Linux / Mac:  source venv/bin/activate
pip install -r requirements.txt
```

## Como executar

**Sem VS Code (um clique):** no Windows, dê dois cliques em `iniciar.bat`; no Linux/Mac, rode `bash iniciar.sh`. O script cria o ambiente virtual, instala as dependências, sobe o Flask e abre o navegador em http://127.0.0.1:5000. Requer Python 3.10+ instalado. Para encerrar, feche a janela ou pressione Ctrl+C.

**Pelo terminal ou VS Code:**

```bash
python main.py
```

Abra http://127.0.0.1:5000 no navegador. No VS Code, abra a pasta do projeto, selecione o interpretador do `venv` e execute `main.py`.

## Como gerar o CSV

**Pela interface:** crie um orçamento em *Novo orçamento* e clique em **Exportar CSV** na página de resultado (projeção de 12 meses) ou em **Exportar CSV** no Histórico (lista de orçamentos).

**Pela linha de comando:**

```bash
python gerar_csv.py                                   # exemplo padrão em exports/projecao_12_meses.csv
python gerar_csv.py --tipo apartamento --quartos 2 --vagas 1 --sem-criancas --parcelas 3 --saida exports/meu_orcamento.csv
python gerar_csv.py --tipo estudio --vagas 4 --parcelas 5
python gerar_csv.py --help
```

O arquivo tem as colunas *Mês, Valor do aluguel, Parcela da taxa contratual, Total previsto*, usa `;` como separador e vírgula decimal, com BOM UTF-8, para abrir direto no Excel e no Google Planilhas em português. Um exemplo pronto está em `exemplos/projecao_12_meses_exemplo.csv`.

## Testes

```bash
python -m unittest discover -s tests -v
```

Cobrem apartamento de 1 e 2 quartos, casa de 1 e 2 quartos, estúdio com duas vagas e com vagas adicionais, desconto de 5% do apartamento sem crianças, parcelamento da taxa de 1 a 5 vezes, validações, geração do CSV e o fluxo completo da aplicação Flask.

## Regras de negócio

| Imóvel | Aluguel-base | Garagem | Desconto |
|---|---|---|---|
| Apartamento | 1 quarto R$ 700,00 · 2 quartos R$ 900,00 | R$ 300,00 por vaga (máx. 1) | 5% sobre aluguel + adicionais, se o cliente não tem crianças |
| Casa | 1 quarto R$ 900,00 · 2 quartos R$ 1.150,00 | R$ 300,00 por vaga (máx. 1) | não há |
| Estúdio | R$ 1.200,00 | pacote de 2 vagas R$ 250,00; vaga adicional R$ 60,00 (máx. 6) | não há |

A taxa contratual é fixa (R$ 2.000,00), parcelável em 1 a 5 vezes e **nunca é somada ao aluguel mensal**. Na projeção, a diferença de centavos fica na última parcela.

## Documentação acadêmica

- `docs/RentSmart_Documentacao.pdf`: análise do problema, regras, entradas/processamentos/saídas, fluxograma, classes, atributos e métodos, pensamento algorítmico e justificativa da POO.
- `docs/fluxograma_rentsmart.png`: fluxograma do sistema.
- Para regenerar ambos (por exemplo, após alterar o nome do autor em `docs/gerar_documentacao.py`): `pip install matplotlib pillow` e `python docs/gerar_documentacao.py`.

## Publicar no GitHub

```bash
git init
git add .
git commit -m "RentSmart: sistema de orçamento de locação"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/rentsmart.git
git push -u origin main
```
