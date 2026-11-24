"""Persistência do histórico (JSON) e exportações CSV/PDF."""
import csv, io, json, os
from decimal import Decimal as D

ARQ = os.path.join(os.path.dirname(__file__), "data", "historico.json")


def brl(v):
    v = D(str(v))
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class Relatorio:
    @staticmethod
    def carregar():
        try:
            with open(ARQ, encoding="utf-8") as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def salvar(orc):
        dados = Relatorio.carregar()
        d = orc.para_dict(); d["id"] = len(dados) + 1
        dados.append(d)
        try:
            os.makedirs(os.path.dirname(ARQ), exist_ok=True)
            with open(ARQ, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=1)
        except OSError as e:
            raise RuntimeError(f"Não foi possível gravar o histórico: {e}")
        return d["id"]

    @staticmethod
    def buscar(busca="", tipo=""):
        return [o for o in reversed(Relatorio.carregar())
                if busca.lower() in o["nome"].lower() and (not tipo or o["tipo"].lower().replace("ú", "u") == tipo)]

    @staticmethod
    def metricas():
        d = Relatorio.carregar()
        media = sum(D(o["aluguel"]) for o in d) / len(d) if d else D("0")
        return len(d), media, list(reversed(d))[:5]

    @staticmethod
    def _escrever_projecao(orc, destino):
        """Escreve o CSV da projeção (separador ';' e vírgula decimal, padrão do Excel em português)."""
        w = csv.writer(destino, delimiter=";")
        w.writerow(["Mês", "Valor do aluguel", "Parcela da taxa contratual", "Total previsto"])
        for l in orc.projecao():
            w.writerow([l["mes"]] + [f"{l[k]:.2f}".replace(".", ",") for k in ("aluguel", "parcela", "total")])

    @staticmethod
    def csv_projecao(orc):
        """Devolve o CSV como texto, com BOM UTF-8 para abrir corretamente no Excel e no Google Planilhas."""
        buf = io.StringIO(); Relatorio._escrever_projecao(orc, buf)
        return "\ufeff" + buf.getvalue()

    @staticmethod
    def salvar_csv_projecao(orc, caminho):
        """Grava o arquivo CSV de 12 meses em disco e devolve o caminho."""
        try:
            pasta = os.path.dirname(os.path.abspath(caminho))
            os.makedirs(pasta, exist_ok=True)
            with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
                Relatorio._escrever_projecao(orc, f)
        except OSError as e:
            raise RuntimeError(f"Não foi possível gravar o CSV: {e}")
        return caminho

    @staticmethod
    def csv_historico(itens):
        buf = io.StringIO(); w = csv.writer(buf, delimiter=";")
        cols = ["id", "criado_em", "nome", "email", "telefone", "tipo", "quartos", "vagas", "aluguel", "taxa", "parcelas", "valor_parcela"]
        w.writerow(cols)
        for o in itens: w.writerow([str(o[c]).replace(".", ",") if c in ("aluguel", "taxa", "valor_parcela") else o[c] for c in cols])
        return "\ufeff" + buf.getvalue()

    @staticmethod
    def pdf(orc):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4); y = 800
        def linha(t, f="Helvetica", s=11):
            nonlocal y; c.setFont(f, s); c.drawString(50, y, t); y -= 20
        i = orc.imovel
        linha("RentSmart - R.M Imóveis", "Helvetica-Bold", 16); linha("Orçamento de locação  " + orc.criado_em); y -= 10
        linha(f"Cliente: {orc.cliente.nome} | {orc.cliente.email} | {orc.cliente.telefone}")
        linha(f"Imóvel: {i.tipo}, {i.quartos} quarto(s), {i.vagas} vaga(s)"); y -= 10
        linha(f"Aluguel-base: {brl(orc.base)}"); linha(f"Vagas de garagem: {brl(orc.vagas)}")
        linha(f"Desconto ({orc.pct}%): - {brl(orc.desconto)}")
        linha(f"Aluguel mensal final: {brl(orc.aluguel)}", "Helvetica-Bold"); y -= 10
        linha(f"Taxa contratual (separada do aluguel): {brl(orc.taxa)} em {orc.parcelas}x de {brl(orc.valor_parcela)}"); y -= 10
        linha("Projeção de 12 meses", "Helvetica-Bold")
        for l in orc.projecao():
            linha(f"Mês {l['mes']:>2}   aluguel {brl(l['aluguel'])}   parcela {brl(l['parcela'])}   total {brl(l['total'])}", s=10)
        c.save(); return buf.getvalue()
