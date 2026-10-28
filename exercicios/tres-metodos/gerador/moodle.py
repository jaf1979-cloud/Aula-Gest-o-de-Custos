"""Gera o XML do Moodle (questões Cloze) a partir dos mesmos cálculos da página.
Na chave do Cloze o decimal é ponto (exigência do Moodle); o aluno digita com vírgula."""
import re
import sys
from gen import build, ANS

OUT = sys.argv[1]
CATEGORIA = "$course$/top/Comparação de Métodos de Custeio/Integral, ideal e margem de contribuição"
TOL = {"r": 0.01,   # R$ da Estrutura de Resultados (valores exatos)
       "p": 0.02,   # MC total % (2 casas)
       "cfu": 0.05,  # CF unitário
       "u": 0.10}   # custo total e PV; para valores grandes vale o mínimo de 0,05% do valor (czr)

EX = build()

ST = {
    "n": "display:block;padding:0 4px 2px;border-bottom:1px solid #333",
    "d": "display:block;padding:2px 4px 0",
    "fr": "display:inline-block;vertical-align:middle;text-align:center;margin:0 2px",
    "eq": "display:block;margin:10px 0;line-height:2",
    "lhs": "font-weight:bold;color:#0b2a63",
    "op": "color:#5a6878;margin:0 4px",
    "res": "background:#fff3c4;color:#3d2f00;padding:2px 8px;border-radius:4px;font-weight:bold;white-space:nowrap",
    "interp": "border-left:4px solid #0f9e93;background:#e2f4f2;padding:10px 14px;margin:14px 0",
    "tag": "font-weight:bold;text-transform:uppercase;font-size:12px;color:#0b7d72",
    "note": "border:1px dashed #b9c3cc;padding:8px 12px;color:#4a5866;font-size:14px;margin:10px 0",
    "prod": "font-weight:bold;font-size:17px;margin:16px 0 4px",
    "pill": "font-weight:bold;font-size:13px;padding:1px 8px;border-radius:4px",
    "cvp": "background:#dff2ef;color:#0b7d72", "cvv": "background:#fdeedf;color:#c25a00", "cf": "background:#efe8fa;color:#6a3fb5",
    "ok": "color:#1e7b3a;font-weight:bold", "bad": "color:#c62828;font-weight:bold",
    "sub": "display:inline-block;padding-left:1.2em;color:#4a5866", "muted": "color:#5a6878;font-size:14px",
    "tw": "overflow-x:auto;margin:10px 0",
    "r": "text-align:right;white-space:nowrap", "c": "text-align:center", "l": "",
}
TABLE = "border-collapse:collapse;margin:8px 0"
CELL = "border:1px solid #c9d2dc;padding:4px 8px"
TH = CELL + ";background:#eaf1f5;color:#0b2a63;text-align:left"


def inline(html):
    html = html.replace('<ul class="seta">', '<ul style="list-style:none;padding-left:0;margin:10px 0">')
    html = re.sub(r"<li>(?=[^<]*: <b>)", "<li>➔&nbsp; ", html)

    def cls(m):
        tag, names = m.group(1), m.group(2).split()
        st = "" if tag == "table" else ";".join(ST[n] for n in names if ST.get(n))
        base = {"table": TABLE, "td": CELL, "th": TH}.get(tag, "")
        style = ";".join(x for x in (base, st) if x)
        return f'<{tag} style="{style}"' if style else f"<{tag}"
    html = re.sub(r'<(\w+) class="?([\w ]+)"?', cls, html)
    html = re.sub(r"<table\b(?![^>]*style)", f'<table style="{TABLE}"', html)
    html = re.sub(r"<td\b(?![^>]*style)", f'<td style="{CELL}"', html)
    html = re.sub(r"<th\b(?![^>]*style)", f'<th style="{TH}"', html)
    html = re.sub(r"<h4>", '<h4 style="color:#0b2a63;margin:22px 0 8px;border-top:1px dashed #c9d2dc;padding-top:12px">', html)
    return html


def czr(v, tol):
    """tolerância relativa mínima de 0,05% do valor: absorve o arredondamento da MC total % em valores grandes"""
    return cz(v, max(tol, round(abs(v) * 0.0005, 2)))


def cz(v, tol):
    return "{1:NUMERICAL:=%.2f:%s}" % (round(v, 2) + 0.0, tol)


REGRAS = """<div style="border:2px solid #0b2a63;padding:10px 14px;margin:16px 0;background:#f3f6f8">
<b>RESPOSTAS</b><br>
NÃO UTILIZAR PONTO PARA MILHAR E USAR VÍRGULA PARA AS DECIMAIS NOS VALORES MONETÁRIOS (EX.: 100200,00)<br>
UTILIZAR 2 CASAS APÓS A VÍRGULA PARA VALORES MONETÁRIOS (EX.: 200,00) E PARA VALORES EM PERCENTUAL, SEM O SÍMBOLO % (EX.: 13,56)</div>"""


def tab(titulo, head, linhas):
    out = [f'<p style="margin:16px 0 4px;font-weight:bold;text-transform:uppercase">{titulo}</p>',
           f'<table style="{TABLE}"><thead><tr>' + "".join(f'<th style="{TH}">{h}</th>' for h in head) + "</tr></thead><tbody>"]
    for l in linhas:
        out.append("<tr>" + "".join(f'<td style="{CELL}{";font-weight:bold" if i == 0 else ""}">{x}</td>' for i, x in enumerate(l)) + "</tr>")
    return "".join(out) + "</tbody></table>"


def respostas(a):
    out = [tab("a) DRE sintético", ["Conta", "R$"], [[lab, "R$ " + cz(v, TOL["r"])] for lab, v in a["dre"]])]
    for key, tit in (("int", "b) Custeio por absorção integral"), ("ide", "c) Custeio por absorção ideal")):
        out.append(tab(tit, ["Item", "CF unit", "Custo total", "Preço"],
                       [[f"{p['nome']} · {p['desc']}", "R$ " + czr(p[key]["cfu"], TOL["cfu"]), "R$ " + czr(p[key]["ct"], TOL["u"]),
                         "R$ " + czr(p[key]["pvn"], TOL["u"])] for p in a["P"]]))
    out.append(tab("d) Custeio pela margem de contribuição", ["Item", "MC total %", "CF unit", "Custo total", "Preço"],
                   [[f"{p['nome']} · {p['desc']}", cz(p["mc"]["share"], TOL["p"]), "R$ " + czr(p["mc"]["cfu"], TOL["cfu"]),
                     "R$ " + czr(p["mc"]["ct"], TOL["u"]), "R$ " + czr(p["mc"]["pvn"], TOL["u"])] for p in a["P"]]))
    return "".join(out)


def cdata(s):
    assert "]]>" not in s
    return f"<![CDATA[{s}]]>"


qs = [f"""  <question type="category">
    <category><text>{CATEGORIA}</text></category>
  </question>"""]
total = 0
for e in EX:
    qtext = f"<h3>{e['ind']} · {e['empresa']}</h3>" + inline(e["enun"]) + REGRAS + respostas(ANS[e["n"]])
    n_sub = qtext.count("{1:NUMERICAL")
    assert n_sub == 5 + 10 * len(ANS[e["n"]]["P"])
    assert not re.search(r"\{(?!1:NUMERICAL:=-?\d+\.\d\d:[\d.]+\})", qtext.replace("{{", "")), "chave fora do padrão"
    total += n_sub
    fb = "<h3>Resolução passo a passo</h3>" + inline(e["sol"])
    assert "{" not in fb
    qs.append(f"""  <question type="cloze">
    <name><text>3M Ex. {e['n']} – {e['empresa'].replace(' Ltda.', '')} – {e['tit']}</text></name>
    <questiontext format="html"><text>{cdata(qtext)}</text></questiontext>
    <generalfeedback format="html"><text>{cdata(fb)}</text></generalfeedback>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber>custeio-3metodos-ex{e['n']}</idnumber>
  </question>""")
    print(f"Ex {e['n']}: {n_sub} lacunas")

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "\n".join(qs) + "\n</quiz>\n"
open(OUT, "w", encoding="utf-8").write(xml)
print("total", total)
