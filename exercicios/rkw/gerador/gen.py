"""Monta enunciado, resolução passo a passo e respostas de cada exercício como uma lista de blocos,
que docx_gen.py (Word) e moodle.py (Cloze) desenham cada um no seu formato.

Blocos: ("h", texto) · ("p", texto com <b>) · ("table", cabeçalho, linhas, colunas à direita, linhas em negrito)
        ("eq", texto) · ("interp", texto) · ("note", texto) · ("list", [textos])
"""
from calc import rkw
from dados import EXS, DRV_LABEL, DRV_UNID


def m(v, nd=2):
    s = f"{abs(v):,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + s


def rs(v):
    return "R$ " + m(v)


def q(v):
    return m(v, 0) if float(v).is_integer() else m(v, 2)


def m4(v):
    """custo unitário do direcionador: 2 casas se exato, senão 4"""
    return m(v) if abs(v * 100 - round(v * 100)) < 1e-9 else m(v, 4)


def pct(v):
    return q(v) + "%"


def enunciado(d):
    C, prod = d["centros"], [c for c in d["centros"] if c not in d["apoio"]]
    B = [("p", t) for t in d["contexto"]]
    B.append(("p", "Para isso, a empresa levantou os seguintes dados do mês:"))
    tot = sum(v for _, v, _ in d["itens"])
    B.append(("table", "Custos indiretos e de transformação do mês", ["Item de custo", "Valor (R$)", "Direcionador"],
              [[i, m(v), DRV_LABEL[k]] for i, v, k in d["itens"]] + [["TOTAL", m(tot), ""]], [1], [len(d["itens"])]))
    drvs = [k for k in ("Funcionários", "Área", "Potência", "Requisições", "Ordens") if k in d["drivers"]]
    rows = [[DRV_LABEL[k]] + [q(d["drivers"][k][c]) for c in C] for k in drvs]
    rows.append(["Horas trabalhadas por funcionário/mês"] + ["–" if c in d["apoio"] else q(d["horas"]) for c in C])
    B.append(("table", "Direcionadores por centro de custos", ["Direcionador"] + C, rows, list(range(1, len(C) + 1)), []))
    B.append(("table", "Tempo de processo (minutos por unidade)", ["Produto / Seção"] + prod,
              [[p["nome"]] + [q(p["t"][c]) for c in prod] for p in d["produtos"]], list(range(1, len(prod) + 1)), []))
    B.append(("table", "Matéria-prima, custos variáveis e margem de lucro desejada",
              ["Produto", "Matéria-prima (R$/un)", "CVV (%)", "CVP (%)", "Lucro desejado (%)"],
              [[p["nome"], m(p["mp"]), m(p["cvv"]), m(p["cvp"]), m(d["lucro"])] for p in d["produtos"]], [1, 2, 3, 4], []))
    ap = " e ".join(d["apoio"])
    pede = [f"a) Elabore a <b>Matriz RKW</b>: distribuição primária (1º rateio) para todos os centros e distribuição "
            f"secundária (2º rateio) de {ap} para os centros produtivos, chegando ao custo total de cada centro produtivo.",
            "b) Calcule o <b>custo por minuto</b> de cada centro produtivo (minutos disponíveis = horas/mês × 60 × nº de funcionários).",
            "c) Calcule o <b>custo RKW</b> (custo de transformação) de cada produto.",
            "d) Calcule o <b>custo total</b> e o <b>preço de venda</b> de cada produto para o lucro desejado.",
            "e) Interprete os resultados: qual centro mais pesa no custo de transformação e o que isso indica para a gestão?"]
    B.append(("h", "Pede-se"))
    B.append(("list", pede))
    B.append(("note", "Convenções: salários são custos diretos de cada centro; os demais itens são distribuídos pelo "
              "direcionador indicado; os centros de apoio são distribuídos pelo nº de funcionários dos centros que os "
              "recebem; use o custo por minuto arredondado com 2 casas; CVV, CVP e lucro são percentuais do preço de venda."))
    return B


def resolucao(d, R):
    C, prod, apoio = d["centros"], R["prod"], d["apoio"]
    B = []
    # Passo 1
    B.append(("h", "Passo 1 – Distribuição primária (1º rateio)"))
    B.append(("p", "Cada item de custo é dividido pelo total do seu direcionador, o que dá um custo por unidade do "
              "direcionador; esse valor é multiplicado pela quantidade de cada centro. Os salários já pertencem a "
              "cada centro e entram direto."))
    eqs = []
    for L in R["linhas"]:
        if L["drv"] == "Direto":
            continue
        u = DRV_UNID[L["drv"]]
        base = d["drivers"][L["drv"]]
        eqs.append(f"<b>{L['item']}</b>: {rs(L['valor'])} ÷ {q(L['soma'])} {u} = R$ {m4(L['unit'])} por {u} → "
                   + "; ".join(f"{c}: {q(base[c])} × {m4(L['unit'])} = {m(L['dist'][c])}" for c in C))
    B.append(("list", eqs))
    rows = []
    for L in R["linhas"]:
        base = d["drivers"].get(L["drv"])
        rows.append([L["item"], m(L["valor"]), "Direto" if L["drv"] == "Direto" else f"{DRV_LABEL[L['drv']]}"]
                    + [(m(L["dist"][c]) if L["dist"][c] else "–") for c in C])
    rows.append(["1º RATEIO Σ", m(sum(L["valor"] for L in R["linhas"])), ""] + [m(R["prim"][c]) for c in C])
    # Passo 2 dentro da mesma matriz
    for s in R["sec"]:
        rows.append([f"2º RATEIO – {s['de']}", "", "Nº de funcionários"]
                    + [("(" + m(s["valor"]) + ")") if c == s["de"] else (m(s["parts"][c]) if c in s["parts"] else "") for c in C])
    rows.append(["Σ TOTAL", "", ""] + ["–" if c in apoio else m(R["total"][c]) for c in C])
    ABR = {"Administração": "Adm.", "Almoxarifado": "Almox.", "Manutenção": "Manut."} if len(C) >= 5 else {}
    matriz = ("table", "Matriz RKW (R$)", ["Item", "Valor", "Base de rateio"] + [ABR.get(c, c) for c in C], rows,
              [1] + list(range(3, 3 + len(C))), [len(R["linhas"])] + [len(rows) - 1])
    # Passo 2
    B.append(("h", "Passo 2 – Distribuição secundária (2º rateio)"))
    if len(apoio) == 1:
        B.append(("p", f"O centro de apoio ({apoio[0]}) não trabalha nos produtos; seu custo vai para os centros "
                  "produtivos na proporção do nº de funcionários."))
    else:
        B.append(("p", f"Com dois centros de apoio, a distribuição é feita em degraus: primeiro {apoio[0]} (para "
                  f"{apoio[1]} e para os produtivos), depois {apoio[1]}, já com o que recebeu, só para os produtivos."))
    f = d["drivers"]["Funcionários"]
    for s in R["sec"]:
        u = s["valor"] / s["base"]
        B.append(("eq", f"<b>{s['de']}</b>: {rs(s['valor'])} ÷ {q(s['base'])} funcionários ("
                  + " + ".join(f"{q(f[c])}" for c in s["recebem"]) + f") = R$ {m4(u)} por funcionário → "
                  + "; ".join(f"{c}: {q(f[c])} × {m4(u)} = {m(s['parts'][c])}" for c in s["recebem"])))
    B.append(matriz)
    B.append(("p", "Conferência: a soma dos totais dos centros produtivos ("
              + " + ".join(m(R["total"][c]) for c in prod) + f" = {rs(sum(R['total'].values()))}) "
              f"é igual ao total dos custos do mês. Nada se perde no rateio, apenas muda de lugar."))
    # Passo 3
    B.append(("h", "Passo 3 – Custo por minuto dos centros produtivos"))
    rows = [[c, m(R["total"][c]), f"{q(d['horas'])} × 60 × {q(f[c])} = {m(R['mins'][c], 0)}",
             m(R["taxa_cheia"][c], 4), m(R["taxa"][c])] for c in prod]
    B.append(("table", "", ["Centro", "Custo total (R$)", "Minutos disponíveis", "R$/min (cheio)", "R$/min (2 casas)"],
              rows, [1, 3, 4], []))
    # Passo 4
    B.append(("h", "Passo 4 – Custo RKW de cada produto"))
    B.append(("p", "Custo RKW = Σ (tempo do produto no centro × custo por minuto do centro)."))
    rows = []
    for p in R["P"]:
        rows.append([p["nome"]] + [f"{q(p['t'][c])} × {m(R['taxa'][c])} = {m(p['parc'][c])}" for c in prod] + [m(p["rkw"])])
    B.append(("table", "", ["Produto"] + prod + ["Custo RKW (R$)"], rows, list(range(1, len(prod) + 2)), []))
    # Passo 5
    B.append(("h", "Passo 5 – Custo total e preço de venda"))
    B.append(("eq", "<b>Custo total</b> = (MP + Custo RKW) ÷ [(100 − (CVV + CVP)) ÷ 100]"))
    B.append(("eq", "<b>Preço de venda</b> = (MP + Custo RKW) ÷ [(100 − (CVV + CVP + L)) ÷ 100]"))
    eqs = []
    for p in R["P"]:
        base = p["mp"] + p["rkw"]
        eqs.append(f"<b>{p['nome']}</b>: CT = ({m(p['mp'])} + {m(p['rkw'])}) ÷ [(100 − ({q(p['cvv'])} + {q(p['cvp'])})) ÷ 100] "
                   f"= {m(base)} ÷ {m((100 - p['perc']) / 100)} = <b>{rs(p['ct'])}</b>; "
                   f"PV = {m(base)} ÷ [(100 − ({q(p['cvv'])} + {q(p['cvp'])} + {q(d['lucro'])})) ÷ 100] "
                   f"= {m(base)} ÷ {m((100 - p['perc'] - d['lucro']) / 100)} = <b>{rs(p['pv'])}</b>")
    B.append(("list", eqs))
    B.append(("table", "Resumo", ["Produto", "MP (R$)", "Custo RKW (R$)", "Custo total (R$)", "Preço de venda (R$)"],
              [[p["nome"], m(p["mp"]), m(p["rkw"]), m(p["ct"]), m(p["pv"])] for p in R["P"]], [1, 2, 3, 4], []))
    B.append(("note", "Se o custo por minuto for usado sem arredondar (4 casas), o custo RKW muda poucos centavos: "
              + "; ".join(f"{p['nome']}: {m(p['rkw_cheio'])}" for p in R["P"]) + ". No Moodle as duas formas são aceitas."))
    B.append(("h", "Interpretação gerencial"))
    for t in interpretacao(d, R):
        B.append(("interp", t))
    return B


def interpretacao(d, R):
    prod = R["prod"]
    tot = sum(R["total"].values())
    maior = max(prod, key=lambda c: R["total"][c])
    caro = max(prod, key=lambda c: R["taxa"][c])
    barato = min(prod, key=lambda c: R["taxa"][c])
    out = [f"<b>{maior}</b> concentra {pct(round(R['total'][maior] / tot * 100, 1))} dos custos de transformação "
           f"({rs(R['total'][maior])}). Já o minuto mais caro é o de <b>{caro}</b> (R$ {m(R['taxa'][caro])}/min), "
           f"contra R$ {m(R['taxa'][barato])}/min em {barato}. Centro com muito custo e pouca gente (ou muito "
           "equipamento) tem minuto caro: cada minuto economizado ali vale mais do que nos outros centros."]
    apoio_tot = sum(R["prim"][a] for a in d["apoio"])
    out.append(f"Os centros de apoio somam {rs(apoio_tot)} ({pct(round(apoio_tot / tot * 100, 1))} do total) e chegam "
               "aos produtos só pelo 2º rateio. Como o critério é o nº de funcionários, centros com mais gente recebem "
               "mais estrutura, mesmo que usem menos a administração. Vale discutir com a turma se esse critério é o "
               "mais justo para a empresa.")
    for p in R["P"]:
        p["peso_rkw"] = p["rkw"] / (p["mp"] + p["rkw"]) * 100
    hi = max(R["P"], key=lambda p: p["peso_rkw"])
    lo = min(R["P"], key=lambda p: p["peso_rkw"])
    out.append(f"No <b>{hi['nome']}</b> a transformação (RKW) representa {pct(round(hi['peso_rkw'], 1))} do custo de "
               f"fabricação (MP + RKW); no <b>{lo['nome']}</b>, {pct(round(lo['peso_rkw'], 1))}. Onde o RKW pesa mais, "
               "ganhos de produtividade (tempo de processo) reduzem o custo; onde a MP domina, o foco é compras e "
               "aproveitamento de material.")
    out.append(f"O preço de venda calculado embute {q(d['lucro'])}% de lucro sobre o preço. Ele é o preço que cobre "
               "os custos com a margem desejada, não necessariamente o preço que o mercado aceita: se a concorrência "
               "pratica valores menores, a empresa precisa atacar custo ou rever o mix.")
    return out


def build():
    out = []
    for d in EXS:
        R = rkw(d)
        out.append(dict(d=d, R=R, enun=enunciado(d), sol=resolucao(d, R)))
    return out
