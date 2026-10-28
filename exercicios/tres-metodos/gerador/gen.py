"""Monta enunciado, resolução e respostas dos 3 exercícios comparativos (integral, ideal e margem de contribuição)."""
import unicodedata
from calc import r2, tabela
from dados import EXS
from helpers import N, num, brl, pc, pn, qn, fr, eq, table, interp, note, PILL, WHY

GAB = []
ANS = {}

METODOS = [("int", "Absorção integral", "mth int", "itens produzidos"),
           ("ide", "Absorção ideal", "mth ide", "itens vendidos"),
           ("mc", "Margem de contribuição", "mth mar", None)]


def foco(e, c):
    n, P = e["n"], c["P"]
    if n == 1:
        A, B = P
        return (f"Na absorção integral o custo fixo é dividido pelas {qn(c['sp'])} bicicletas produzidas; na ideal, só pelas {qn(c['sv'])} vendidas. "
                f"Por isso a integral mostra custo menor: {brl(c['cf'] * (c['sp'] - c['sv']) / c['sp'])} de custo fixo ficam \"guardados\" no estoque "
                f"das {qn(c['sp'] - c['sv'])} bicicletas não vendidas e só aparecem no resultado quando elas forem vendidas. "
                f"A ideal trata essa ociosidade comercial como custo do mês. Pela margem de contribuição, a mountain bike (A), que gera mais margem, "
                f"absorve {pc(A['mc']['share'])} do custo fixo, e o seu preço calculado ({brl(A['mc']['pvn'])}) fica acima dos outros dois métodos. "
                f"A urbana (B) faz o caminho inverso: o preço pela MC ({brl(B['mc']['pvn'])}) é o menor dos três.")
    if n == 2:
        A, B, C = P
        return (f"O vinho reserva fica meses em barricas, então a vinícola produz bem mais do que vende. A integral reparte o custo fixo por "
                f"{qn(c['sp'])} garrafas e a ideal por {qn(c['sv'])}. A diferença de CF unitário ({brl(A['int']['cfu'])} contra {brl(A['ide']['cfu'])}) "
                f"é pequena por garrafa, mas no total representa {brl(c['cf'] * (c['sp'] - c['sv']) / c['sp'])} levados para o estoque. "
                f"O suco (C) mostra o efeito mais forte do critério de rateio: por unidade de contagem ele recebe o mesmo CF que um espumante. "
                f"Pela absorção, o seu preço calculado ({brl(C['int']['pvn'])} a {brl(C['ide']['pvn'])}) passa do preço de mercado ({brl(C['pv'])}). "
                f"Pela MC, ele recebe só {brl(C['mc']['cfu'])} por litro e o preço calculado ({brl(C['mc']['pvn'])}) fica abaixo do praticado.")
    if n == 3:
        A, B, C = P
        return (f"Aqui aparece o limite de ratear o custo fixo por <b>contagem de unidades</b>. Na absorção, uma carreta de {brl(C['pv'])} recebe "
                f"o mesmo CF que uma plantadeira de {brl(B['pv'])}: {brl(C['int']['cfu'])} na integral. Isso leva o custo da carreta a {brl(C['int']['ct'])}, "
                f"acima do preço que o mercado paga. Pela margem de contribuição, a carreta absorve {pc(C['mc']['share'])} do CF "
                f"({brl(C['mc']['cfu'])} por unidade) e a plantadeira {pc(B['mc']['share'])} ({brl(B['mc']['cfu'])} por unidade). "
                f"Nenhum dos critérios é \"o verdadeiro\": um gestor que confiasse só na absorção poderia abandonar a carreta, que tem MC positiva e ajuda a pagar a estrutura. "
                f"Esse caso abre espaço para discutir métodos com direcionadores, como ABC ou UEP.")


def build():
    return [build_one(e) for e in EXS]


def build_one(e):
    n, g, P0 = e["n"], e["gastos"], e["prods"]
    s = lambda k: sum(v for _, v, c in g if c == k)
    R = sum(p["qv"] * p["pv"] for p in P0)
    mp, cvpo, cvv, cf = s("MP"), s("CVP"), s("CVV"), s("CF")
    assert abs(mp - sum(p["qv"] * p["mp"] for p in P0)) < 1e-6
    cvp = mp + cvpo
    mc, lo = R - cvp - cvv, R - cvp - cvv - cf
    cvp_pct, cvv_pct = round(cvpo / R * 100, 10), round(cvv / R * 100, 10)
    assert r2(cvp_pct) == cvp_pct and r2(cvv_pct) == cvv_pct
    div_c = (100 - (cvv_pct + cvp_pct)) / 100
    sp, sv = sum(p["qp"] for p in P0), sum(p["qv"] for p in P0)
    mrows, soma = tabela([dict(nome=p["nome"], desc=p["desc"], q=p["qv"], pv=p["pv"], mp=p["mp"], L=p["L"]) for p in P0], cvp_pct, cvv_pct, cf)
    assert abs(soma - mc) < 0.01 and all(r["mcu"] > 0 for r in mrows)
    P = []
    for p, mr in zip(P0, mrows):
        d = dict(p)
        d["div_p"] = (100 - (cvv_pct + cvp_pct + p["L"])) / 100
        for k, den in (("int", sp), ("ide", sv)):
            cfu = cf / den
            d[k] = dict(cfu=cfu, ct=(p["mp"] + cfu) / div_c, pvn=(p["mp"] + cfu) / d["div_p"])
        d["mc"] = mr
        P.append(d)
    c = dict(P=P, cf=cf, sp=sp, sv=sv, R=R)

    # ---------- enunciado ----------
    h = [f"<p>A <b>{e['empresa'].upper()}</b>, de {e['cidade']}, faturou <b>{brl(R)}</b> no mês corrente e teve os seguintes custos:</p>"]
    h.append(table(["Gasto", "R$"], [[d, num(v)] for d, v, _ in sorted(g, key=lambda x: unicodedata.normalize("NFD", x[0]).encode("ascii", "ignore").lower())], "data"))
    h.append("<p><b>Sabe-se que:</b></p>")
    h.append(table(["Prod.", "Descrição", "Matéria-prima (R$/un.)", "Quantidade vendida", "Produção do mês", "Preço praticado (R$)", "Margem de lucro desejada"],
                   [[p["nome"], p["desc"], num(p["mp"]), qn(p["qv"]), qn(p["qp"]), num(p["pv"]), f"{pn(p['L'])}%"] for p in P0],
                   "data", align="llrrrrr"))
    h.append("""<p>Calcular os custos dos produtos e os preços de venda pelos métodos de <b>CUSTEIO POR ABSORÇÃO INTEGRAL</b>,
    <b>CUSTEIO POR ABSORÇÃO IDEAL</b> e <b>CUSTEIO PELA MARGEM DE CONTRIBUIÇÃO</b>, garantindo as margens de lucro indicadas.</p>""")
    h.append("""<ol class="q" type="a"><li>Elaborar o <b>DRE sintético</b> (receita, CVV, CVP, CF e lucro operacional).</li>
    <li>Calcular o CF unitário, o custo total e o preço de venda pela <b>absorção integral</b>.</li>
    <li>Calcular o CF unitário, o custo total e o preço de venda pela <b>absorção ideal</b>.</li>
    <li>Calcular a MC total %, o CF unitário, o custo total e o preço de venda pela <b>margem de contribuição</b>.</li>
    <li>Comparar os resultados dos três métodos com o preço praticado.</li></ol>""")
    enun = "".join(h)

    # ---------- resolução ----------
    S = ["<h4>Passo 0 · Classificação dos gastos</h4>",
         "<p>Pergunta-chave: <i>se a empresa produzir e vender o dobro, este gasto dobra?</i> Dobra com a produção: CVP. Dobra com a venda: CVV. Não muda: CF.</p>"]
    order = {"MP": 0, "CVP": 1, "CVV": 2, "CF": 3}
    S.append(table(["Gasto", "Classe", "R$", "Por quê"],
                   [[d, f'<span class="pill {PILL[k][0]}">{PILL[k][1]}</span>', num(v), WHY[k]] for d, v, k in sorted(g, key=lambda x: order[x[2]])],
                   "data", align="lcrl"))
    S.append(note("Publicidade <b>proporcional às vendas</b> é CVV; manutenção de máquinas <b>da produção</b> é CVP; "
                  "salários, vale-refeição e a manutenção dos equipamentos de escritório são CF."))

    S.append("<h4>a) DRE sintético</h4>")
    S.append(table(["Conta", "R$", "% da receita"], [
        ["<b>Receita</b>", f"<b>{num(R)}</b>", "100,00%"],
        ["(−) Custo variável de vendas (CVV)", num(cvv), pc(cvv / R * 100)],
        ["(−) Custo variável de produção (CVP)", num(cvp), pc(cvp / R * 100)],
        ['<span class="sub">dos quais matéria-prima</span>', num(mp), pc(mp / R * 100)],
        ["<b>(=) Margem de contribuição</b>", f"<b>{num(mc)}</b>", pc(mc / R * 100)],
        ["(−) Custo fixo (CF)", num(cf), pc(cf / R * 100)],
        ["<b>(=) Lucro operacional</b>", f"<b>{num(lo)}</b>", f"<b>{pc(lo / R * 100)}</b>"]], "dre"))
    S.append(note(f"A receita confere com as vendas: {' + '.join(f'{qn(p['qv'])} × {num(p['pv'])}' for p in P0)} = {brl(R)}."))
    S.append("<p>Percentuais que entram nas fórmulas (a matéria-prima sai do CVP porque entra em R$ pela ficha técnica):</p>")
    S.append(eq("CVP %", fr(f"{num(cvp)} − {num(mp)}", num(R)) + " × 100", res=pc(cvp_pct)))
    S.append(eq("CVV %", fr(num(cvv), num(R)) + " × 100", res=pc(cvv_pct)))
    S.append(f"<p>Divisor do custo: (100 − ({pn(cvv_pct)} + {pn(cvp_pct)})) ÷ 100 = <b>{num(div_c, 2)}</b>. "
             "Divisor do preço: (100 − (CVV + CVP + L)) ÷ 100, um para cada margem de lucro.</p>")

    for key, nome, cls, base in METODOS[:2]:
        letra = "b" if key == "int" else "c"
        den = sp if key == "int" else sv
        S.append(f'<h4>{letra}) {nome}</h4>')
        S.append(eq("CF unit", fr("CF total", f"Σ {base}"), fr(num(cf), " + ".join(qn(p["qp"] if key == "int" else p["qv"]) for p in P0)),
                    fr(num(cf), qn(den)), res=brl(P[0][key]["cfu"])))
        for p in P:
            m = p[key]
            S.append(f'<p class="prod">Produto {p["nome"]}<span>{p["desc"]} · MP {brl(p["mp"])} · lucro {pn(p["L"])}%</span></p>')
            S.append(eq("CUSTO", fr("MP + CF unit", fr("100 − (CVV + CVP)", "100")),
                        fr(f"{num(p['mp'])} + {num(m['cfu'])}", fr(f"100 − ({pn(cvv_pct)} + {pn(cvp_pct)})", "100")), res=brl(m["ct"])))
            S.append(eq("PV", fr("MP + CF unit", fr("100 − (CVV + CVP + L)", "100")),
                        fr(f"{num(p['mp'])} + {num(m['cfu'])}", fr(f"100 − ({pn(cvv_pct)} + {pn(cvp_pct)} + {pn(p['L'])})", "100")), res=brl(m["pvn"])))
        if key == "int":
            est = cf * (sp - sv) / sp
            S.append(interp(f"Cada unidade produzida carrega {brl(P[0]['int']['cfu'])} de custo fixo. Como foram produzidas {qn(sp)} e vendidas {qn(sv)}, "
                            f"{brl(est)} de custo fixo ficam no estoque e só vão para o resultado quando esses itens forem vendidos."))
        else:
            S.append(interp(f"Todo o custo fixo do mês ({brl(cf)}) é carregado pelas {qn(sv)} unidades vendidas. O CF unitário sobe de "
                            f"{brl(P[0]['int']['cfu'])} para {brl(P[0]['ide']['cfu'])}: a ideal trata a capacidade não vendida como custo do período, e não como estoque."))

    S.append("<h4>d) Margem de contribuição</h4>")
    head = ["Prod.", "Quant. vendida", "PV praticado", "MP", "CVP R$", "CVV R$", "CVT", "MC unit R$", "MC unit %", "MC total R$", "MC total %",
            "CF unit", "Custo total", "Lucro", "PV"]
    trs = [[r["nome"], qn(r["q"]), num(r["pv"]), num(r["mp"]), num(r["cvp"]), num(r["cvv"]), num(r["cvt"]), num(r["mcu"]), pc(r["mcu_pct"]),
            num(r["mct"]), pc(r["share"]), num(r["cfu"]), f"<b>{num(r['ct'])}</b>", f"{pn(r['L'])}%", f"<b>{num(r['pvn'])}</b>"] for r in mrows]
    S.append(table(head, trs, "data wide", align="c" + "r" * 14,
                   foot=[["", "", "", "", "", "", "", "", "<b>Total</b>", f"<b>{num(soma)}</b>", "<b>100,00%</b>", "", "", "", ""]]))
    S.append(note(f"A soma das margens totais ({brl(soma)}) fecha com a margem de contribuição do DRE. "
                  "Na MC o custo fixo é distribuído pela margem que cada produto gera nas <b>vendas</b>, e não pela produção."))
    for r in mrows:
        S.append(f'<p class="prod">Produto {r["nome"]}<span>{r["desc"]} · PV praticado {brl(r["pv"])} · {qn(r["q"])} un. vendidas</span></p>')
        S.append(eq("CVT $", "MP + PV × CVP% + PV × CVV%", f"{num(r['mp'])} + {num(r['cvp'])} + {num(r['cvv'])}", res=num(r["cvt"])))
        S.append(eq("MC total $", "(PV − CVT) × quant.", f"({num(r['pv'])} − {num(r['cvt'])}) × {qn(r['q'])}", res=num(r["mct"])))
        S.append(eq("MC total %", fr(num(r["mct"]), num(soma)) + " × 100", res=pc(r["share"])))
        S.append(eq("CF unit", fr("CF total × MC total %", "quant. vendida"), fr(f"{num(cf)} × {pn(round(r['share'], 2))}%", qn(r["q"])), res=num(r["cfu"])))
        S.append(eq("CUSTO", fr(f"{num(r['mp'])} + {num(r['cfu'])}", fr(f"100 − ({pn(cvv_pct)} + {pn(cvp_pct)})", "100")), res=brl(r["ct"])))
        S.append(eq("PV", fr(f"{num(r['mp'])} + {num(r['cfu'])}", fr(f"100 − ({pn(cvv_pct)} + {pn(cvp_pct)} + {pn(r['L'])})", "100")), res=brl(r["pvn"])))

    S.append("<h4>e) Os três métodos lado a lado</h4>")
    rows = []
    for p in P:
        for key, nome, _, _ in METODOS:
            m = p[key]
            rows.append([f"{p['nome']} · {p['desc']}" if key == "int" else "", nome, num(m["cfu"]), num(m["ct"]), f"<b>{num(m['pvn'])}</b>",
                         num(p["pv"]) if key == "int" else "",
                         '<span class="bad">abaixo do custo</span>' if p["pv"] < m["ct"] - 0.005 else
                         ('<span class="ok">atinge a meta</span>' if p["pv"] >= m["pvn"] - 0.005 else "cobre o custo")])
    S.append(table(["Produto", "Método", "CF unit", "Custo total", "PV calculado", "PV praticado", "Situação do preço praticado"], rows, "data", align="llrrrrl"))
    S.append(note("Os valores intermediários aparecem com 2 casas, mas a conta segue com todas as casas, como na planilha dos slides."))
    S.append(interp(foco(e, c)))

    # ---------- gabarito e respostas ----------
    GAB.append((str(n), "Receita / CVV / CVP / CF / LO", " / ".join(brl(x) for x in (R, cvv, cvp, cf, lo))))
    for key, nome, _, _ in METODOS:
        for p in P:
            m = p[key]
            GAB.append((str(n), f"{nome} · {p['nome']}: CF unit / custo / PV", f"{brl(m['cfu'])} / {brl(m['ct'])} / {brl(m['pvn'])}"))
    ANS[n] = dict(dre=[("Receita", R), ("Custo Variável de Vendas", cvv), ("Custo Variável de Produção", cvp), ("Custo Fixo", cf), ("Lucro Operacional", lo)],
                  P=P)
    tags = ["DRE sintético", "Absorção integral", "Absorção ideal", "Margem de contribuição", "Produção ≠ vendas"]
    return dict(n=n, ind=e["ind"], empresa=e["empresa"], tit=e["tit"], tags=tags, enun=enun, sol="".join(S))
