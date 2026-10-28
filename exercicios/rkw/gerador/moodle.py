"""Gera o XML do Moodle (questões Cloze) com os mesmos cálculos do Word.
Uso: python3 moodle.py ../rkw-moodle-cloze.xml
Na chave do Cloze o decimal é ponto (exigência do Moodle); o aluno digita com vírgula."""
import re
import sys
from gen import build, m

OUT = sys.argv[1]
CATEGORIA = "$course$/top/Métodos Contemporâneos de Custeio/RKW"
TABLE = "border-collapse:collapse;margin:8px 0"
CELL = "border:1px solid #c9d2dc;padding:4px 8px"
TH = CELL + ";background:#eaf1f5;color:#0b2a63;text-align:left"
R = ";text-align:right;white-space:nowrap"


def table(title, head, rows, right, bold_rows):
    out = []
    if title:
        out.append(f'<p style="margin:16px 0 4px;font-weight:bold;text-transform:uppercase;color:#0b2a63">{title}</p>')
    out.append(f'<div style="overflow-x:auto"><table style="{TABLE}"><thead><tr>'
               + "".join(f'<th style="{TH}{R if i in right else ""}">{h}</th>' for i, h in enumerate(head)) + "</tr></thead><tbody>")
    for k, row in enumerate(rows):
        bg = ";background:#fff3c4;font-weight:bold" if k in bold_rows else ""
        out.append("<tr>" + "".join(
            f'<td style="{CELL}{R if i in right else ""}{bg}{";font-weight:bold" if i == 0 else ""}">{v}</td>'
            for i, v in enumerate(row)) + "</tr>")
    return "".join(out) + "</tbody></table></div>"


def html(blocks):
    out = []
    for b in blocks:
        k = b[0]
        if k == "h":
            out.append(f'<h4 style="color:#0b2a63;margin:20px 0 8px">{b[1]}</h4>')
        elif k == "p":
            out.append(f"<p>{b[1]}</p>")
        elif k == "eq":
            out.append(f'<p style="margin:6px 0 6px 16px">{b[1]}</p>')
        elif k == "list":
            out.append('<ul style="list-style:none;padding-left:16px">' + "".join(f"<li style=\"margin:4px 0\">➔&nbsp; {x}</li>" for x in b[1]) + "</ul>")
        elif k == "table":
            out.append(table(*b[1:]))
        elif k == "note":
            out.append(f'<p style="border:1px dashed #b9c3cc;padding:8px 12px;color:#4a5866;font-size:14px">{b[1]}</p>')
        elif k == "interp":
            out.append(f'<p style="border-left:4px solid #0f9e93;background:#e2f4f2;padding:10px 14px;margin:10px 0">{b[1]}</p>')
    return "".join(out)


def cz(v, tol):
    return "{1:NUMERICAL:=%.2f:%s}" % (round(v, 2) + 0.0, f"{tol:.2f}")


def tol_u(v, alt, base):
    """aceita o valor com custo/min em 2 casas e com custo/min cheio (+ folga de centavos)"""
    return max(base, round(abs(v - alt) + 0.02, 2), round(abs(v) * 0.0005, 2))


REGRAS = """<div style="border:2px solid #0b2a63;padding:10px 14px;margin:16px 0;background:#f3f6f8">
<b>RESPOSTAS</b><br>
NÃO UTILIZAR PONTO PARA MILHAR E USAR VÍRGULA PARA AS DECIMAIS PARA VALORES MONETÁRIOS (EX.: 100200,00)<br>
UTILIZAR 2 CASAS APÓS A VÍRGULA PARA VALORES MONETÁRIOS E 2 CASAS APÓS A VÍRGULA PARA VALORES NUMÉRICOS (EX.: 200,00; 0,19)<br>
O CUSTO POR MINUTO DEVE SER ARREDONDADO COM 2 CASAS E USADO ASSIM NO CÁLCULO DO CUSTO RKW</div>"""


def respostas(e):
    d, Rr = e["d"], e["R"]
    C, prod, apoio = d["centros"], Rr["prod"], d["apoio"]
    out = [table("a) Matriz RKW", ["Seções"] + C,
                 [["1º rateio Σ"] + ["R$ " + cz(Rr["prim"][c], 0.05) for c in C],
                  ["Σ Total (após 2º rateio)"] + ["–" if c in apoio else "R$ " + cz(Rr["total"][c], 0.10) for c in C]], [], [])]
    out.append(table("b) Custo por minuto dos centros produtivos", ["Seção"] + prod,
                     [["R$/min"] + ["R$ " + cz(Rr["taxa"][c], 0.01) for c in prod]], [], []))
    out.append(table("c) e d) Custo RKW, custo total e preço de venda", ["Produto", "Custo RKW", "Custo total", "Preço de venda"],
                     [[p["nome"], "R$ " + cz(p["rkw"], tol_u(p["rkw"], p["rkw_cheio"], 0.05)),
                       "R$ " + cz(p["ct"], tol_u(p["ct"], p["ct_cheio"], 0.10)),
                       "R$ " + cz(p["pv"], tol_u(p["pv"], p["pv_cheio"], 0.10))] for p in Rr["P"]], [], []))
    return "".join(out)


def cdata(s):
    assert "]]>" not in s
    return f"<![CDATA[{s}]]>"


qs = [f"""  <question type="category">
    <category><text>{CATEGORIA}</text></category>
  </question>"""]
total = 0
for e in build():
    d = e["d"]
    enun = [b for b in e["enun"] if not (b[0] == "list" or (b[0] == "h" and b[1] == "Pede-se"))]
    pede = '<p><b>Com base nos dados, preencha:</b> a) a Matriz RKW (1º rateio de todos os centros e total dos centros produtivos após o 2º rateio); b) o custo por minuto de cada centro produtivo; c) e d) o custo RKW, o custo total e o preço de venda de cada produto.</p>'
    qtext = f"<h3>Exercício {d['n']} · {d['setor']} – {d['empresa']}</h3>" + html(enun) + pede + REGRAS + respostas(e)
    n_sub = qtext.count("{1:NUMERICAL")
    assert n_sub == len(d["centros"]) + 2 * len(e["R"]["prod"]) + 3 * len(d["produtos"]), n_sub
    assert not re.search(r"\{(?!1:NUMERICAL:=-?\d+\.\d\d:[\d.]+\})", qtext), "chave fora do padrão"
    total += n_sub
    fb = "<h3>Resolução passo a passo</h3>" + html(e["sol"])
    assert "{" not in fb
    qs.append(f"""  <question type="cloze">
    <name><text>RKW Ex. {d['n']} – {d['empresa'].replace(' Ltda.', '').replace(' S.A.', '')}</text></name>
    <questiontext format="html"><text>{cdata(qtext)}</text></questiontext>
    <generalfeedback format="html"><text>{cdata(fb)}</text></generalfeedback>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber>custeio-rkw-ex{d['n']}</idnumber>
  </question>""")
    print(f"Ex {d['n']}: {n_sub} lacunas")

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "\n".join(qs) + "\n</quiz>\n"
open(OUT, "w", encoding="utf-8").write(xml)
print("total", total)
