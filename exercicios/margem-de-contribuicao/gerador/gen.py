"""Monta enunciado, resolução passo a passo e respostas (Moodle) dos 5 exercícios."""
from decimal import Decimal
from calc import r2, tabela
from dados import EXS

GAB = []   # (exercício, item, resposta) para o gabarito resumido
ANS = {}   # respostas para o Cloze


class N:
    """resposta numérica. kind: 'r' = R$ total, 'u' = R$ unitário, 'p' = %"""
    def __init__(self, v, kind="r"):
        self.v, self.kind = float(v), kind


# ---------------- formatação ----------------
def num(x, nd=2):
    d = Decimal(repr(r2(x))) if nd == 2 else Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd))
    s = f"{d:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x):
    return ("−R$&nbsp;" + num(-x)) if r2(x) < 0 else "R$&nbsp;" + num(x)


def pc(x):
    return num(x) + "%"


def pn(x):
    """percentual dentro da fórmula, sem casas desnecessárias: 7 / 24 / 6,8"""
    v = round(float(x), 2)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").replace(".", ",")


def qn(q):
    return f"{q:,}".replace(",", ".")


def fr(n, d):
    return f'<span class="fr"><span class="n">{n}</span><span class="d">{d}</span></span>'


def eq(lhs, *parts, res=None):
    body = " <span class=op>=</span> ".join(parts)
    out = f'<div class="eq"><span class="lhs">{lhs}</span> <span class=op>=</span> {body}'
    if res is not None:
        out += f' <span class=op>=</span> <b class="res">{res}</b>'
    return out + "</div>"


def table(head, rows, cls="", align=None, foot=None):
    al = align or ("l" + "r" * (len(head) - 1))
    h = "".join(f"<th>{c}</th>" for c in head)
    body = "".join("<tr>" + "".join(f'<td class="{al[i]}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    f = ""
    if foot:
        f = "<tfoot>" + "".join("<tr>" + "".join(f'<td class="{al[i]}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in foot) + "</tfoot>"
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody>{f}</table></div>'


def interp(txt):
    return f'<div class="interp"><span class="tag">Interpretação gerencial</span><p>{txt}</p></div>'


def note(txt):
    return f'<div class="note">{txt}</div>'


PILL = {"MP": ('cvp', 'CVP · MP'), "CVP": ('cvp', 'CVP'), "CVV": ('cvv', 'CVV'), "CF": ('cf', 'CF')}
WHY = {"MP": "Varia com a produção; entra em R$ pela ficha técnica de cada produto.",
       "CVP": "Acompanha o volume produzido.",
       "CVV": "Acompanha o valor ou o volume vendido.",
       "CF": "Não muda com o volume produzido ou vendido no mês."}


# ---------------- textos específicos de cada exercício ----------------
def foco(e, ctx):
    n, rows, R, lo, mc, cf = e["n"], ctx["rows"], ctx["R"], ctx["lo"], ctx["mc"], ctx["cf"]
    by = {r["nome"]: r for r in rows}
    if n == 1:
        A, B, D = by["A"], by["B"], by["D"]
        return (f"A bota (B) tem a maior margem unitária em reais ({brl(B['mcu'])} por par), mas a menor em percentual ({pc(B['mcu_pct'])}). "
                f"Já o tênis (A), com {qn(A['q'])} pares, gera a maior margem total e por isso recebe {pc(A['share'])} do custo fixo. "
                f"Os preços atuais rendem um lucro operacional de {pc(lo / R * 100)} da receita, abaixo das margens desejadas (10% a 20%). "
                f"Por isso todos os preços calculados ficam acima dos atuais. A sandália (D) é a que está mais perto da meta: "
                f"faltam {brl(D['pvn'] - D['pv'])} por par.")
    if n == 2:
        A, C = by["A"], by["C"]
        return (f"Indústria de alimentos trabalha com margem apertada: só {pc(mc / R * 100)} da receita sobra como margem de contribuição, porque "
                f"a matéria-prima consome {pc(ctx['mp'] / R * 100)} e os custos variáveis de vendas, {pc(ctx['cvv_pct'])}. "
                f"O cream cracker (A) tem a menor MC unitária em % ({pc(A['mcu_pct'])}), mas o volume faz dele um grande gerador de margem total "
                f"({pc(A['share'])} do custo fixo vai para ele). A rosquinha (C) tem a melhor MC% ({pc(C['mcu_pct'])}): "
                f"incentivar o mix na direção dela melhora o resultado sem mexer em preço.")
    if n == 3:
        pec = cf / (mc / R)
        return (f"A empresa teve prejuízo de {brl(-lo)}, mas <b>todos os produtos têm margem de contribuição positiva</b>. Cortar um deles pioraria o resultado: "
                f"a margem que ele gera sumiria e o custo fixo de {brl(cf)} continuaria lá. O problema é de preço e de volume. "
                f"O custo total de cada item já é maior que o preço praticado (veja a tabela), ou seja, todos são vendidos abaixo do custo pleno. "
                f"Com MC de {pc(mc / R * 100)}, a receita precisaria chegar a {brl(pec)} (CF ÷ MC%) só para empatar. "
                f"Caminhos: renegociar preços com distribuidores, priorizar a pastilha (A), que tem a maior MC%, e revisar o custo fixo.")
    if n == 4:
        C = by["C"]
        return (f"Na venda direta os custos variáveis de vendas chegam a {pc(ctx['cvv_pct'])} da receita (ICMS de 18% e comissão de 12% das revendedoras). "
                f"Com isso o divisor do custo cai para {num(rows[0]['div_c'])}: cada real de MP e de custo fixo precisa de quase dois reais de preço. "
                f"Atenção ao deo colônia (C): por gerar a maior margem total, ele recebe {pc(C['share'])} do custo fixo, embora seja só {qn(C['q'])} unidades. "
                f"O preço calculado ({brl(C['pvn'])}) fica muito acima do atual ({brl(C['pv'])}). "
                f"Esse é um efeito do próprio critério: quem contribui mais absorve mais custo fixo. "
                f"O preço calculado é uma referência; antes de reajustar, a empresa deve olhar o preço de mercado e a sensibilidade das revendedoras.")
    if n == 5:
        C, B, D = by["C"], by["B"], by["D"]
        return (f"Na cerâmica o gás natural dos fornos é custo variável relevante: o CVP sem a MP é de {pc(ctx['cvp_pct'])}, o dobro das outras indústrias da lista. "
                f"O revestimento de parede (C) já está praticamente na meta ({brl(C['pvn'])} calculado contra {brl(C['pv'])} praticado). "
                f"Os porcelanatos (B e D) estão bem abaixo do preço calculado, porque têm metas de lucro maiores (18% e 20%) e absorvem "
                f"{pc(B['share'] + D['share'])} do custo fixo. Antes de reajustar, vale comparar com o preço por m² dos concorrentes: "
                f"porcelanato é um mercado com muita oferta.")


# ---------------- montagem ----------------
def build():
    out = []
    for e in EXS:
        out.append(build_one(e))
    return out


def build_one(e):
    n = e["n"]
    g = e["gastos"]
    R = [v for _, v, c in g if c == "R"][0]
    s = lambda k: sum(v for _, v, c in g if c == k)
    mp, cvpo, cvv, cf = s("MP"), s("CVP"), s("CVV"), s("CF")
    cvp = mp + cvpo
    mc, lo = R - cvp - cvv, R - cvp - cvv - cf
    cvp_pct, cvv_pct = r2(cvpo / R * 100), r2(cvv / R * 100)
    assert abs(cvp_pct - cvpo / R * 100) < 1e-9 and abs(cvv_pct - cvv / R * 100) < 1e-9
    prods = e["prods"]
    assert abs(sum(p["q"] * p["pv"] for p in prods) - R) < 1e-6
    assert abs(sum(p["q"] * p["mp"] for p in prods) - mp) < 1e-6
    rows, soma = tabela(prods, cvp_pct, cvv_pct, cf)
    assert abs(soma - mc) < 0.01, (soma, mc)
    assert all(r["mcu"] > 0 for r in rows)
    ctx = dict(rows=rows, R=R, lo=lo, mc=mc, cf=cf, mp=mp, cvv_pct=cvv_pct, cvp_pct=cvp_pct)

    # ---------- enunciado ----------
    h = [f"""<p>A <b>{e['empresa']}</b>, de {e['cidade']}, {e['intro']}. No mês de {e['mes']} apresentou os seguintes resultados:</p>"""]
    h.append('<ul class="seta">' + "".join(
        f"<li>{('Receitas sobre vendas' if c == 'R' else d)}: <b>{num(v)}</b></li>" for d, v, c in g) + "</ul>")
    h.append("<p>Calcular o custo dos seguintes itens e o preço de venda pelo método do <b>custeio pela margem de contribuição</b>, sabendo que:</p>")
    h.append(table(["Prod.", "Descrição", "Quantidade vendida", "Preço de venda atual (R$)", "Matéria-prima (ficha técnica, R$/un.)", "Lucro desejado"],
                   [[p["nome"], p["desc"], qn(p["q"]), num(p["pv"]), num(p["mp"]), f"{pn(p['L'])}%"] for p in prods], "data", align="llrrrr"))
    h.append("""<p class="muted">A mão de obra direta é paga a mensalistas e não varia com o volume produzido no mês.</p>""")
    h.append("""<ol class="q" type="a">
    <li>Elaborar a <b>Estrutura de Resultados</b> (Receita, CVP, CVV, CF, MC e LO).</li>
    <li>Montar a <b>tabela de custo pela margem de contribuição</b> e calcular, para cada produto, a MC total em %, o custo fixo unitário,
    o <b>custo total</b> e o <b>preço de venda</b>.</li></ol>""")
    enun = "".join(h)

    # ---------- resolução ----------
    S = []
    S.append("<h4>Passo 0 · Classificação dos gastos</h4>")
    S.append("<p>Pergunta-chave: <i>se a empresa produzir e vender o dobro, este gasto dobra?</i> "
             "Dobra com a produção: CVP. Dobra com a venda: CVV. Não muda: CF.</p>")
    cl = [[d, f'<span class="pill {PILL[c][0]}">{PILL[c][1]}</span>', num(v), WHY[c]] for d, v, c in g if c != "R"]
    S.append(table(["Gasto", "Classe", "R$", "Por quê"], cl, "data", align="lcrl"))

    S.append("<h4>a) Estrutura de Resultados</h4>")
    dre = [["<b>1. Receita sobre vendas</b>", f"<b>{num(R)}</b>", "<b>100,00%</b>"]]

    def grp(code, label, total, items):
        dre.append([f"<b>{code} {label}</b>", f"<b>{num(total)}</b>", f"<b>{pc(total / R * 100)}</b>"])
        for i, (d, v) in enumerate(items, 1):
            dre.append([f'<span class="sub">{code.rstrip(".")}.{i} {d}</span>', num(v), pc(v / R * 100)])
    grp("2.", "Custos variáveis de produção (CVP)", cvp, [(d, v) for d, v, c in g if c in ("MP", "CVP")])
    grp("3.", "Custos variáveis de vendas (CVV)", cvv, [(d, v) for d, v, c in g if c == "CVV"])
    dre.append(["<b>4. Custo variável total (2 + 3)</b>", f"<b>{num(cvp + cvv)}</b>", f"<b>{pc((cvp + cvv) / R * 100)}</b>"])
    dre.append(["<b>5. Margem de contribuição (1 − 4)</b>", f"<b>{num(mc)}</b>", f"<b>{pc(mc / R * 100)}</b>"])
    grp("6.", "Custos fixos (CF)", cf, [(d, v) for d, v, c in g if c == "CF"])
    dre.append(["<b>7. Lucro operacional (5 − 6)</b>", f"<b>{num(lo)}</b>", f"<b>{pc(lo / R * 100)}</b>"])
    S.append(table(["Item", "R$", "%"], dre, "dre"))
    S.append(table(["Estrutura de Resultados", "R$"], [["Receita", num(R)], ["CVP", num(cvp)], ["CVV", num(cvv)], ["CF", num(cf)],
                                                    ["MC", num(mc)], ["LO", num(lo)]], "res"))
    res_txt = (f"lucro operacional de {brl(lo)} ({pc(lo / R * 100)} da receita)" if lo >= 0
               else f"<b>prejuízo</b> operacional de {brl(-lo)} ({pc(lo / R * 100)} da receita)")
    S.append(interp(f"""De cada R$&nbsp;100,00 vendidos sobram R$&nbsp;{num(mc / R * 100)} depois dos custos variáveis. Essa é a margem de contribuição,
    que paga os {brl(cf)} de custo fixo. No mês, a {e['empresa'].replace(' Ltda.', '')} teve {res_txt}."""))

    S.append("<h4>b) Percentuais que entram na fórmula</h4>")
    S.append("<p>A matéria-prima sai do CVP, porque ela entra em R$ pela ficha técnica de cada produto:</p>")
    S.append(eq("CVP %", fr("CVP total − MP", "Receita") + " × 100", fr(f"{num(cvp)} − {num(mp)}", num(R)) + " × 100", res=pc(cvp_pct)))
    S.append(eq("CVV %", fr("CVV", "Receita") + " × 100", fr(num(cvv), num(R)) + " × 100", res=pc(cvv_pct)))
    S.append(note(f"Equivalente: CVP total {pc(cvp / R * 100)} − MP {pc(mp / R * 100)} = {pc(cvp_pct)}, como no DRE dos slides (50% − 40% = 10%)."))

    # tabela resumo (estilo do slide 5)
    head = ["Prod.", "Quant.", "Preço", "MP", "CVP R$", "CVV R$", "CVT", "MC unit R$", "MC unit %", "MC total R$", "MC total %",
            "CF unit", "Custo total", "Lucro", "PV"]
    trs = [[r["nome"], qn(r["q"]), num(r["pv"]), num(r["mp"]), num(r["cvp"]), num(r["cvv"]), num(r["cvt"]), num(r["mcu"]),
            pc(r["mcu_pct"]), num(r["mct"]), pc(r["share"]), num(r["cfu"]), f"<b>{num(r['ct'])}</b>", f"{pn(r['L'])}%",
            f"<b>{num(r['pvn'])}</b>"] for r in rows]
    foot = [["", "", "", "", "", "", "", "", "<b>Total</b>", f"<b>{num(soma)}</b>", "<b>100,00%</b>", "", "", "", ""]]
    S.append(f"<p>Tabela de custo pela margem de contribuição (CVP = {pc(cvp_pct)}, CVV = {pc(cvv_pct)}, CF = {brl(cf)}):</p>")
    S.append(table(head, trs, "data wide", align="crrrrrrrrrrrrrr", foot=foot))
    S.append(note(f"A soma das margens totais dos produtos ({brl(soma)}) é igual à margem de contribuição da Estrutura de Resultados. "
                  "Isso acontece porque as quantidades vendidas a preço atual somam a receita do mês e a MP das fichas técnicas soma a MP do DRE."))

    S.append("<h4>Passos 1 a 6 · Margem de contribuição de cada produto</h4>")
    for r in rows:
        S.append(f'<p class="prod">Produto {r["nome"]}<span>{r["desc"]} · PV atual {brl(r["pv"])} · MP {brl(r["mp"])} · {qn(r["q"])} un.</span></p>')
        S.append(eq("CVP $", f"PV × CVP%", f"{num(r['pv'])} × {pn(cvp_pct)}%", res=num(r["cvp"])))
        S.append(eq("CVV $", f"PV × CVV%", f"{num(r['pv'])} × {pn(cvv_pct)}%", res=num(r["cvv"])))
        S.append(eq("CVT $", "CVP + CVV + MP", f"{num(r['cvp'])} + {num(r['cvv'])} + {num(r['mp'])}", res=num(r["cvt"])))
        S.append(eq("MC unit $", "PV − CVT", f"{num(r['pv'])} − {num(r['cvt'])}", res=num(r["mcu"])))
        S.append(eq("MC unit %", fr(num(r["mcu"]), num(r["pv"])) + " × 100", res=pc(r["mcu_pct"])))
        S.append(eq("MC total $", "MC unit × quant.", f"{num(r['mcu'])} × {qn(r['q'])}", res=num(r["mct"])))

    S.append("<h4>Passo 7 · MC total em % (participação de cada produto)</h4>")
    S.append(f"<p>Soma das margens totais: Σ = {' + '.join(num(r['mct']) for r in rows)} = <b>{num(soma)}</b></p>")
    for r in rows:
        S.append(eq(f"MC total % ({r['nome']})", fr(num(r["mct"]), num(soma)) + " × 100", res=pc(r["share"])))

    S.append("<h4>Passos 8 a 10 · Custo fixo unitário, custo total e preço de venda</h4>")
    S.append(f"<p>Divisor do custo: (100 − ({pn(cvv_pct)} + {pn(cvp_pct)})) ÷ 100 = <b>{num(rows[0]['div_c'], 4).rstrip('0').rstrip(',')}</b>.</p>")
    for r in rows:
        S.append(f'<p class="prod">Produto {r["nome"]}<span>{r["desc"]} · lucro desejado {pn(r["L"])}%</span></p>')
        S.append(eq("CF unit", fr("CF total × MC total %", "quantidade"), fr(f"{num(cf)} × {pn(round(r['share'], 2))}%", qn(r["q"])), res=num(r["cfu"])))
        S.append(eq("CUSTO", fr("MP + CF unit", fr("100 − (CVV + CVP)", "100")),
                    fr(f"{num(r['mp'])} + {num(r['cfu'])}", fr(f"100 − ({pn(cvv_pct)} + {pn(cvp_pct)})", "100")), res=brl(r["ct"])))
        S.append(eq("PV", fr("MP + CF unit", fr("100 − (CVV + CVP + L)", "100")),
                    fr(f"{num(r['mp'])} + {num(r['cfu'])}", fr(f"100 − ({pn(cvv_pct)} + {pn(cvp_pct)} + {pn(r['L'])})", "100")), res=brl(r["pvn"])))
    S.append(note("Os valores intermediários aparecem com 2 casas, mas a conta segue com todas as casas, como na planilha dos slides. "
                  "Quem arredonda o CF unitário antes de dividir pode achar R$&nbsp;0,01 de diferença no custo ou no preço."))

    S.append("<h4>Leitura dos resultados · preço calculado × preço praticado</h4>")
    cmp_rows = []
    for r in rows:
        dif = (r["pvn"] - r["pv"]) / r["pv"] * 100
        sit = ('<span class="bad">abaixo do custo</span>' if r["pv"] < r["ct"] else
               ('<span class="ok">praticamente na meta</span>' if abs(dif) < 0.5 else "cobre o custo, lucro abaixo da meta"))
        cmp_rows.append([f"{r['nome']} · {r['desc']}", num(r["pv"]), num(r["ct"]), num(r["pvn"]),
                         ("+" if dif >= 0 else "") + pc(dif), sit])
    S.append(table(["Produto", "PV atual", "Custo total", "PV calculado", "Reajuste p/ meta", "Situação"], cmp_rows, "data", align="lrrrrl"))
    S.append(interp(foco(e, ctx)))

    # ---------- gabarito e respostas ----------
    GAB.append((str(n), "Receita / CVP / CVV", f"{brl(R)} / {brl(cvp)} / {brl(cvv)}"))
    GAB.append((str(n), "CF / MC / LO", f"{brl(cf)} / {brl(mc)} / {brl(lo)}"))
    for r in rows:
        GAB.append((str(n), f"Produto {r['nome']}: MC total % / CF unit / custo / PV",
                    f"{pc(r['share'])} / {brl(r['cfu'])} / {brl(r['ct'])} / {brl(r['pvn'])}"))
    ANS[n] = dict(
        estrutura=[("Receita", N(R)), ("CVP", N(cvp)), ("CVV", N(cvv)), ("CF", N(cf)), ("MC", N(mc)), ("LO", N(lo))],
        prods=[(r["nome"], N(r["share"], "p"), N(r["cfu"], "u"), N(r["ct"], "u"), N(r["pvn"], "u")) for r in rows],
    )
    tags = ["Estrutura de Resultados", "MC unitária e total", "CF pela participação na MC", "Custo e preço de venda"]
    return dict(n=n, ind=e["ind"], empresa=e["empresa"], tit=e["tit"], tags=tags, enun=enun, sol="".join(S),
                rows=rows, R=R, lo=lo)
