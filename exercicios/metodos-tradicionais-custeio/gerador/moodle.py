"""Gera o XML do Moodle (questões Cloze / respostas embutidas) a partir dos mesmos cálculos da página."""
import re
import sys
from gen import build, ANS, N, MC

OUT = sys.argv[1]
CATEGORIA = "$course$/top/Métodos Tradicionais de Custeio/Exercícios práticos"
TOL_R = 0.011   # R$: aceita resultado arredondado ou truncado (±0,01)
TOL_P = 0.051   # %: aceita 1 casa decimal

EX = build()

# ---------- estilos inline (o Moodle não carrega a folha de estilo da página) ----------
ST = {
    "fr": "display:inline-block;vertical-align:middle;text-align:center;margin:0 2px",
    "n": "display:block;padding:0 4px 2px;border-bottom:1px solid #333",
    "d": "display:block;padding:2px 4px 0",
    "eq": "display:block;margin:10px 0;line-height:2",
    "lhs": "font-weight:bold;color:#0b2a63",
    "op": "color:#5a6878;margin:0 4px",
    "res": "background:#fff3c4;color:#3d2f00;padding:2px 8px;border-radius:4px;font-weight:bold;white-space:nowrap",
    "interp": "border-left:4px solid #0f9e93;background:#e2f4f2;padding:10px 14px;margin:14px 0",
    "tag": "font-weight:bold;text-transform:uppercase;font-size:12px;color:#0b7d72",
    "note": "border:1px dashed #b9c3cc;padding:8px 12px;color:#4a5866;font-size:14px;margin:10px 0",
    "prod": "font-weight:bold;font-size:17px;margin:16px 0 4px",
    "mth": "display:inline-block;font-weight:bold;font-size:12px;text-transform:uppercase;padding:2px 8px;border-radius:4px;margin:6px 0",
    "mar": "background:#efe8fa;color:#6a3fb5", "int": "background:#e9edf1;color:#4f5d6e", "ide": "background:#dff2ef;color:#0b7d72",
    "pill": "font-weight:bold;font-size:13px;padding:1px 8px;border-radius:4px",
    "cvp": "background:#dff2ef;color:#0b7d72", "cvv": "background:#fdeedf;color:#c25a00", "cf": "background:#efe8fa;color:#6a3fb5",
    "ok": "color:#1e7b3a;font-weight:bold", "bad": "color:#c62828;font-weight:bold",
    "sub": "display:inline-block;padding-left:1.2em;color:#4a5866", "muted": "color:#5a6878;font-size:14px",
    "tw": "overflow-x:auto;margin:10px 0",
    "two": "display:block", "three": "display:block",
    "r": "text-align:right;white-space:nowrap", "c": "text-align:center", "l": "",
}
TABLE = "border-collapse:collapse;margin:8px 0"
CELL = "border:1px solid #c9d2dc;padding:4px 8px"
TH = CELL + ";background:#eaf1f5;color:#0b2a63;text-align:left"


def inline(html):
    def cls(m):
        tag, names = m.group(1), m.group(2).split()
        st = "" if tag == "table" else ";".join(ST.get(n, "") for n in names if ST.get(n))
        base = {"table": TABLE, "td": CELL, "th": TH}.get(tag, "")
        style = ";".join(x for x in (base, st) if x)
        return f'<{tag} style="{style}"' if style else f"<{tag}"
    html = re.sub(r'<(\w+) class="?([\w ]+)"?', cls, html)
    html = re.sub(r"<table\b(?![^>]*style)", f'<table style="{TABLE}"', html)
    html = re.sub(r"<td\b(?![^>]*style)", f'<td style="{CELL}"', html)
    html = re.sub(r"<th\b(?![^>]*style)", f'<th style="{TH}"', html)
    html = re.sub(r"<h4>", '<h4 style="color:#0b2a63;margin:22px 0 8px;border-top:1px dashed #c9d2dc;padding-top:12px">', html)
    return html


def fnum(v, nd):
    return f"{v:.{nd}f}"


def cloze(c):
    if isinstance(c, N):
        if c.kind == "p":
            return "{1:NUMERICAL:=%s:%s}" % (fnum(round(c.v, 4), 4).rstrip("0").rstrip("."), TOL_P)
        return "{1:NUMERICAL:=%s:%s}" % (fnum(round(c.v, 2), 2), TOL_R)
    if isinstance(c, MC):
        for o in c.options:
            assert not re.search(r"[{}#~/\"\\:]", o), o
        return "{1:MULTICHOICE:" + "~".join(("=" if o == c.correct else "") + o for o in c.options) + "}"
    return str(c)


def resp_block(blocks):
    out = []
    for kind, title, head, rows in blocks:
        out.append(f'<p style="margin:16px 0 4px"><b>{title}</b></p>')
        out.append(f'<table style="{TABLE}"><thead><tr>' + "".join(f'<th style="{TH}">{h}</th>' for h in head) + "</tr></thead><tbody>")
        for r in rows:
            out.append("<tr>" + "".join(f'<td style="{CELL}">{cloze(c)}</td>' for c in r) + "</tr>")
        out.append("</tbody></table>")
    return "".join(out)


REGRAS = """<div style="border:2px solid #0b2a63;padding:10px 14px;margin:16px 0;background:#f3f6f8">
<b>RESPOSTAS</b><br>
NÃO UTILIZAR PONTO PARA MILHAR E USAR VÍRGULA PARA AS DECIMAIS NOS VALORES MONETÁRIOS (EX.: 100000,00)<br>
UTILIZAR 2 CASAS APÓS A VÍRGULA PARA VALORES MONETÁRIOS (EX.: 200,00)<br>
PARA VALORES EM PERCENTUAL UTILIZAR 1 CASA APÓS A VÍRGULA (EX.: 12,6). NÃO UTILIZAR O SÍMBOLO % APÓS A NUMERAÇÃO<br>
NA FÓRMULA, CVP = CVP TOTAL % − MATÉRIA-PRIMA %</div>"""


def cdata(s):
    assert "]]>" not in s
    return f"<![CDATA[{s}]]>"


qs = [f"""  <question type="category">
    <category><text>{CATEGORIA}</text></category>
  </question>"""]
total = 0
for e in EX:
    blocks = ANS[e["n"]]
    qtext = (f"<h3>{e['ind']} · {e['empresa']}</h3>" + inline(e["enun"]) + REGRAS + resp_block(blocks))
    n_sub = qtext.count("{1:")
    total += n_sub
    fb = "<h3>Resolução passo a passo</h3>" + inline(e["sol"])
    qs.append(f"""  <question type="cloze">
    <name><text>Ex. {e['n']} – {e['empresa']} – {e['tit']}</text></name>
    <questiontext format="html"><text>{cdata(qtext)}</text></questiontext>
    <generalfeedback format="html"><text>{cdata(fb)}</text></generalfeedback>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber>custeio-trad-ex{e['n']}</idnumber>
  </question>""")
    print(f"Ex {e['n']}: {n_sub} lacunas")

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "\n".join(qs) + "\n</quiz>\n"
open(OUT, "w", encoding="utf-8").write(xml)
print("total", total)
