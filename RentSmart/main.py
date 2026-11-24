"""RentSmart - aplicação Flask. Todos os cálculos ficam no backend Python."""
import os
try:
    from flask import Flask, render_template, request, Response, redirect, url_for
except ImportError:
    raise SystemExit("Flask não está instalado. Ative o ambiente virtual e rode: pip install -r requirements.txt")
from cliente import Cliente, ValidacaoErro
from imovel import TIPOS
from orcamento import Orcamento
from relatorio import Relatorio, brl

app = Flask(__name__)
app.jinja_env.filters["brl"] = brl
_cache = {}  # orçamentos recém-criados (para PDF/CSV da página de resultado)


def _inteiro(valor, campo):
    try: return int(valor)
    except (TypeError, ValueError): raise ValidacaoErro(f"O campo {campo} deve ser um número inteiro.")


def montar(form):
    cliente = Cliente(form.get("nome"), form.get("email"), form.get("telefone"))
    cls = TIPOS.get(form.get("tipo"))
    if cls is None: raise ValidacaoErro("Escolha um tipo de imóvel.")
    quartos = _inteiro(form.get("quartos", 1), "quartos")
    vagas = _inteiro(form.get("vagas", 0), "vagas")
    criancas = form.get("criancas", "sim") == "sim"
    return Orcamento(cliente, cls(quartos, vagas, criancas), _inteiro(form.get("parcelas", 1), "parcelas"))


@app.route("/")
def dashboard():
    total, media, ultimos = Relatorio.metricas()
    return render_template("dashboard.html", total=total, media=media, ultimos=ultimos)


@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        try:
            orc = montar(request.form)
            oid = Relatorio.salvar(orc); _cache[oid] = orc
            return redirect(url_for("resultado", oid=oid))
        except (ValidacaoErro, RuntimeError) as e:
            return render_template("novo.html", erro=str(e), f=request.form), 400
    return render_template("novo.html", erro=None, f={})


def _orc(oid):
    if oid in _cache: return _cache[oid]
    d = next((o for o in Relatorio.carregar() if o["id"] == oid), None)
    if d is None: return None
    f = {"nome": d["nome"], "email": d["email"], "telefone": d["telefone"], "tipo": d["tipo"].lower().replace("ú", "u"),
         "quartos": d["quartos"], "vagas": d["vagas"], "criancas": "sim" if d["criancas"] else "nao", "parcelas": d["parcelas"]}
    _cache[oid] = montar(f); return _cache[oid]


@app.route("/orcamento/<int:oid>")
def resultado(oid):
    orc = _orc(oid)
    return render_template("resultado.html", o=orc, oid=oid, proj=orc.projecao()) if orc else ("Orçamento não encontrado.", 404)


@app.route("/orcamento/<int:oid>/projecao.csv")
def csv_projecao(oid):
    return Response(Relatorio.csv_projecao(_orc(oid)), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename=projecao_12_meses_{oid}.csv"})


@app.route("/orcamento/<int:oid>/orcamento.pdf")
def pdf(oid):
    return Response(Relatorio.pdf(_orc(oid)), mimetype="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=orcamento_{oid}.pdf"})


@app.route("/historico")
def historico():
    busca, tipo = request.args.get("q", ""), request.args.get("tipo", "")
    return render_template("historico.html", itens=Relatorio.buscar(busca, tipo), q=busca, tipo=tipo)


@app.route("/historico.csv")
def csv_historico():
    itens = Relatorio.buscar(request.args.get("q", ""), request.args.get("tipo", ""))
    return Response(Relatorio.csv_historico(itens), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=historico_orcamentos.csv"})


@app.route("/documentacao")
def documentacao():
    return render_template("docs.html")


if __name__ == "__main__":
    import threading
    import webbrowser
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"), exist_ok=True)
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":  # abre o navegador uma única vez
        threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=True)
