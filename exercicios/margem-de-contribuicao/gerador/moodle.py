"""Gera o XML do Moodle (questões Cloze) a partir dos mesmos cálculos da página.
Na chave do Cloze o decimal é ponto (exigência do Moodle); o aluno digita com vírgula."""
import re
import sys
from gen import build, ANS

OUT = sys.argv[1]
CATEGORIA = "$course$/top/Custeio pela Margem de Contribuição/Exercícios práticos"
TOL = {"r": 0.01,   # R$ da Estrutura de Resultados (valores exatos)
       "p": 0.02,   # MC total % (2 casas)
       "cfu": 0.05,  # CF unitário
       "u": 0.10}   # custo total e PV: aceita quem arredonda os passos intermediários

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


def cz(v, tol):
    return "{1:NUMERICAL:=%.2f:%s}" % (round(v, 2) + 0.0, tol)


REGRAS = """<div style="border:2px solid #0b2a63;padding:10px 14px;margin:16px 0;background:#f3f6f8">
<b>RESPOSTAS</b><br>
NÃO UTILIZAR PONTO NO MILHAR (EX.: 1000)<br>
USAR 2 CASAS APÓS A VÍRGULA PARA VALORES FINANCEIROS (EX.: 1000,00)<br>
NOS VALORES PERCENTUAIS UTILIZAR 2 CASAS APÓS A VÍRGULA, SEM UTILIZAR O SÍMBOLO % (EX.: 12,35)</div>"""


def respostas(a):
    out = ['<p style="margin:16px 0 4px"><b>a) Elaborar a Estrutura de Resultados;</b></p>',
           f'<table style="{TABLE}"><tbody>']
    for lab, v in a["estrutura"]:
        out.append(f'<tr><td style="{CELL};font-weight:bold">{lab}</td><td style="{CELL}">R$ {cz(v.v, TOL["r"])}</td></tr>')
    out.append("</tbody></table>")
    out.append('<p style="margin:16px 0 4px"><b>b) Tabela de custo pela margem de contribuição;</b></p>')
    out.append(f'<table style="{TABLE}"><thead><tr>' + "".join(f'<th style="{TH}">{h}</th>' for h in
               ["PROD.", "MC TOTAL %", "CF UNIT", "CUSTO TOTAL", "PV"]) + "</tr></thead><tbody>")
    for nome, sh, cfu, ct, pv in a["prods"]:
        out.append(f'<tr><td style="{CELL};text-align:center;font-weight:bold">{nome}</td>'
                   f'<td style="{CELL}">{cz(sh.v, TOL["p"])}</td><td style="{CELL}">R$ {cz(cfu.v, TOL["cfu"])}</td>'
                   f'<td style="{CELL}">R$ {cz(ct.v, TOL["u"])}</td><td style="{CELL}">R$ {cz(pv.v, TOL["u"])}</td></tr>')
    out.append("</tbody></table>")
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
    assert n_sub == 6 + 4 * len(ANS[e["n"]]["prods"])
    assert not re.search(r"\{(?!1:NUMERICAL:=-?\d+\.\d\d:[\d.]+\})", qtext.replace("{{", "")), "chave fora do padrão"
    total += n_sub
    fb = "<h3>Resolução passo a passo</h3>" + inline(e["sol"])
    assert "{" not in fb
    qs.append(f"""  <question type="cloze">
    <name><text>MC Ex. {e['n']} – {e['empresa'].replace(' Ltda.', '')} – {e['tit']}</text></name>
    <questiontext format="html"><text>{cdata(qtext)}</text></questiontext>
    <generalfeedback format="html"><text>{cdata(fb)}</text></generalfeedback>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber>custeio-mc-ex{e['n']}</idnumber>
  </question>""")
    print(f"Ex {e['n']}: {n_sub} lacunas")

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "\n".join(qs) + "\n</quiz>\n"
open(OUT, "w", encoding="utf-8").write(xml)
print("total", total)
