from decimal import Decimal
from calc import r2, dre_pct, marginal, absorcao, pe

GAB = []  # (exercicio, item, resposta)
ANS = {}  # respostas estruturadas para o Moodle (cloze)


class N:
    """resposta numérica: kind 'r' = R$ (tol 0,01), 'p' = % (1 casa, tol 0,05)"""
    def __init__(self, v, kind="r"):
        self.v, self.kind = float(v), kind


class MC:
    def __init__(self, correct, options):
        assert correct in options
        self.correct, self.options = correct, options


def dre_ans(R, cvp, cvv, cf):
    p = lambda v: N(v / R * 100, "p")
    mc = R - cvp - cvv
    return [["Receita", N(R), p(R)], ["Custo variável de produção (CVP)", N(cvp), p(cvp)], ["Custo variável de vendas (CVV)", N(cvv), p(cvv)],
            ["Custo variável total", N(cvp + cvv), p(cvp + cvv)], ["Margem de contribuição", N(mc), p(mc)],
            ["Custos fixos", N(cf), p(cf)], ["Lucro operacional", N(mc - cf), p(mc - cf)]]


# ---------------- formatação ----------------
def num(x, nd=2):
    d = Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd)) if not isinstance(x, Decimal) else x.quantize(Decimal(1).scaleb(-nd))
    if nd == 2 and not isinstance(x, Decimal):
        d = r2(x)
    s = f"{d:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x):
    return "R$&nbsp;" + num(x)


def pc(x, nd=2):
    return num(x, nd) + "%"


def pn(x):
    """percentual dentro da fórmula, sem %: 10 / 22,5 / 7,25"""
    v = round(float(x), 4)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    s = f"{v:.2f}".rstrip("0")
    return s.replace(".", ",")


def fr(n, d):
    return f'<span class="fr"><span class="n">{n}</span><span class="d">{d}</span></span>'


def eq(lhs, *parts, res=None):
    body = " <span class=op>=</span> ".join(parts)
    out = f'<div class="eq"><span class="lhs">{lhs}</span> <span class=op>=</span> {body}'
    if res is not None:
        out += f' <span class=op>=</span> <b class="res">{res}</b>'
    return out + "</div>"


def table(head, rows, cls="", foot=None, align=None):
    h = "".join(f"<th>{c}</th>" for c in head)
    body = ""
    for r in rows:
        tds = ""
        for i, c in enumerate(r):
            a = (align or "l" + "r" * (len(head) - 1))[i]
            tds += f'<td class="{a}">{c}</td>'
        body += f"<tr>{tds}</tr>"
    f = ""
    if foot:
        f = "<tfoot>" + "".join("<tr>" + "".join(f'<td class="{(align or "l"+"r"*(len(head)-1))[i]}">{c}</td>' for i, c in enumerate(fr_)) + "</tr>" for fr_ in foot) + "</tfoot>"
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody>{f}</table></div>'


def interp(txt):
    return f'<div class="interp"><span class="tag">Interpretação gerencial</span><p>{txt}</p></div>'


def note(txt):
    return f'<div class="note">{txt}</div>'


def dre_table(R, groups, cf_items=None):
    """groups: list of (label, total, [(item, valor)])"""
    rows = []
    rows.append([f"<b>1. Receita sobre vendas</b>", f"<b>{num(R)}</b>", "<b>100,00%</b>"])
    for code, label, total, items in groups:
        rows.append([f"<b>{code} {label}</b>", f"<b>{num(total)}</b>", f"<b>{pc(total / R * 100)}</b>"])
        for i, (it, v) in enumerate(items, 1):
            rows.append([f'<span class="sub">{code.rstrip(".")}.{i} {it}</span>', num(v), pc(v / R * 100)])
    return rows


# ================= EXERCÍCIO 1 =================
def ex1():
    R = 480000.0
    CVP = [("Leite <i>in natura</i> (matéria-prima)", 168000.0), ("Embalagens primárias (potes, filmes, rótulos)", 19200.0),
           ("Energia elétrica da fábrica", 14400.0), ("Prêmio de produtividade da produção", 4800.0),
           ("Frete sobre compras de leite", 9600.0)]
    CVV = [("ICMS sobre vendas", 57600.0), ("PIS/COFINS sobre vendas", 14400.0),
           ("Comissão dos vendedores", 14400.0), ("Frete de entrega aos supermercados", 9600.0)]
    CF = [("Salários da fábrica (mensalistas) + encargos", 38000.0), ("Salários da administração + encargos", 22000.0),
          ("Pró-labore dos sócios", 17000.0), ("Depreciação de máquinas e câmaras frias", 12000.0),
          ("Aluguel do centro de distribuição", 8000.0), ("Seguros", 2400.0), ("Telefone e internet", 1600.0),
          ("Honorários contábeis", 3000.0), ("Material de expediente", 500.0),
          ("Manutenção predial (contrato mensal fixo)", 2500.0), ("IPTU e taxas municipais", 1000.0)]
    cvp, cvv, cf = sum(v for _, v in CVP), sum(v for _, v in CVV), sum(v for _, v in CF)
    assert (cvp, cvv, cf) == (216000, 96000, 108000)
    mp = CVP[0][1]
    d = dre_pct(R, cvp, cvv, cf, mp)
    mc, lo = R - cvp - cvv, R - cvp - cvv - cf
    dep, ativo, tx = 12000.0, 1800000.0, 1.5
    opp = ativo * tx / 100
    P = pe(cf, d["mc"], dep, opp)
    ms = (R - float(P["pec"])) / R * 100

    allitems = [(n, v, "CVP") for n, v in CVP] + [(n, v, "CVV") for n, v in CVV] + [(n, v, "CF") for n, v in CF]
    order = [0, 9, 5, 14, 1, 11, 6, 16, 10, 2, 7, 18, 3, 12, 8, 17, 4, 13, 15, 19]
    assert sorted(order) == list(range(len(allitems)))
    lista = [allitems[i] for i in order]

    just = {
        "Leite <i>in natura</i> (matéria-prima)": "Varia com o volume produzido; é a MP da ficha técnica.",
        "Embalagens primárias (potes, filmes, rótulos)": "Cada pote produzido consome embalagem.",
        "Energia elétrica da fábrica": "Consumo das máquinas acompanha a produção (critério do DRE dos slides).",
        "Prêmio de produtividade da produção": "Pago por volume produzido.",
        "Frete sobre compras de leite": "Acompanha o volume de MP comprado para produzir.",
        "ICMS sobre vendas": "Incide sobre cada venda.", "PIS/COFINS sobre vendas": "Incide sobre o faturamento.",
        "Comissão dos vendedores": "Percentual sobre o valor vendido.", "Frete de entrega aos supermercados": "Acompanha o volume entregue.",
    }

    h = []
    h.append("""<p>A <b>Laticínios Serra Verde Ltda.</b>, de Francisco Beltrão (PR), produz queijos, iogurtes e bebidas lácteas
    e vende para redes de supermercados do Sudoeste do Paraná. A controladoria levantou os gastos do mês de março:</p>""")
    h.append(f"<p><b>Receita sobre vendas: {brl(R)}</b> (40% à vista e 60% a prazo).</p>")
    rows = [[n, num(v)] for n, v, _ in lista]
    h.append(table(["Gasto do mês", "R$"], rows, "data"))
    h.append(f"""<p>Informações adicionais: o ativo total da empresa é de {brl(ativo)} e os sócios esperam uma remuneração mínima
    de {pn(tx)}% ao mês sobre esse capital.</p>""")
    h.append("""<ol class="q" type="a">
    <li>Classifique cada gasto em <b>CVP</b> (custo variável de produção), <b>CVV</b> (custo variável de vendas) ou <b>CF</b> (custo fixo).</li>
    <li>Monte o <b>DRE analítico</b> (R$ e % da receita): CVP, CVV, custo variável total, margem de contribuição, CF e lucro operacional.</li>
    <li>Calcule os pontos de equilíbrio <b>financeiro</b>, <b>contábil</b> e <b>econômico</b>.</li>
    <li>Calcule a <b>margem de segurança</b> da empresa no mês.</li>
    <li>Com os percentuais do DRE, calcule o custo e o preço de venda, pelo <b>custeio marginal</b>, do queijo minas frescal (peça de 500 g),
    cuja ficha técnica indica MP = 9,80, para uma margem de lucro de 10%.</li></ol>""")
    enun = "".join(h)

    s = []
    s.append("<h4>a) Classificação dos gastos</h4>")
    s.append("<p>A pergunta-chave é: <i>se a fábrica produzir e vender o dobro, este gasto dobra?</i> Se dobra com a produção, é CVP; se dobra com a venda, é CVV; se não muda, é CF.</p>")
    rows = []
    for n, v, c in lista:
        j = just.get(n, "Não muda com o volume produzido ou vendido no mês.")
        rows.append([n, f'<span class="pill {c.lower()}">{c}</span>', j])
    s.append(table(["Gasto", "Classe", "Por quê"], rows, "data", align="lcl"))
    s.append(note("Os salários da fábrica foram tratados como CF porque são pagos a mensalistas, independentemente do volume. Só o prêmio de produtividade varia com a produção."))

    s.append("<h4>b) DRE analítico</h4>")
    rows = dre_table(R, [("2.", "Custos variáveis de produção (CVP)", cvp, CVP), ("3.", "Custos variáveis de vendas (CVV)", cvv, CVV)])
    rows.append(["<b>4. Custo variável total (2 + 3)</b>", f"<b>{num(cvp + cvv)}</b>", f"<b>{pc((cvp + cvv) / R * 100)}</b>"])
    rows.append(['<b>5. Margem de contribuição (1 − 4)</b>', f"<b>{num(mc)}</b>", f"<b>{pc(d['mc'])}</b>"])
    rows.append(["<b>6. Custos fixos (CF)</b>", f"<b>{num(cf)}</b>", f"<b>{pc(d['cf'])}</b>"])
    for i, (it, v) in enumerate(CF, 1):
        rows.append([f'<span class="sub">6.{i} {it}</span>', num(v), pc(v / R * 100)])
    rows.append(['<b>7. Lucro operacional (5 − 6)</b>', f"<b>{num(lo)}</b>", f"<b>{pc(d['lo'])}</b>"])
    s.append(table(["Item", "R$", "%"], rows, "dre"))
    s.append(interp(f"""De cada R$&nbsp;100,00 vendidos, R$&nbsp;{num(d['mc'])} sobram depois de pagar os custos variáveis. Esse valor é a
    margem de contribuição: é com ela que a empresa paga os R$&nbsp;{num(cf)} de estrutura fixa. O que sobra, {pc(d['lo'])} da receita,
    é o lucro operacional do mês."""))

    s.append("<h4>c) Pontos de equilíbrio</h4>")
    s.append(f"<p>Margem de contribuição percentual: MC% = {pc(d['mc'])} = {num(d['mc']/100, 2)} (na forma decimal).</p>")
    s.append(eq("PE<sub>contábil</sub>", fr("CF", "MC%"), fr(num(cf), num(d['mc']/100)), res=brl(P['pec'])))
    s.append(eq("PE<sub>financeiro</sub>", fr("CF − Depreciação", "MC%"), fr(f"{num(cf)} − {num(dep)}", num(d['mc']/100)),
                fr(num(cf - dep), num(d['mc']/100)), res=brl(P['pef'])))
    s.append(f"<p>Custo de oportunidade do capital: {num(ativo)} × {pn(tx)}% = {brl(opp)} por mês.</p>")
    s.append(eq("PE<sub>econômico</sub>", fr("CF + Ativo × taxa", "MC%"), fr(f"{num(cf)} + {num(opp)}", num(d['mc']/100)),
                fr(num(cf + opp), num(d['mc']/100)), res=brl(P['pee'])))
    s.append(interp(f"""Com receita de {brl(P['pef'])} a empresa consegue pagar as contas do mês em dinheiro, porque a depreciação não sai do caixa.
    Com {brl(P['pec'])} ela não tem lucro nem prejuízo contábil. Só a partir de {brl(P['pee'])} os sócios recebem o mínimo que esperam
    sobre o capital investido. A receita atual de {brl(R)} supera os três pontos, então a Serra Verde cria valor no mês."""))

    s.append("<h4>d) Margem de segurança</h4>")
    s.append(eq("MS", fr("Receita − PE<sub>contábil</sub>", "Receita"), fr(f"{num(R)} − {num(P['pec'])}", num(R)), res=pc(ms)))
    s.append(interp(f"""As vendas podem cair até {pc(ms)} antes de a empresa entrar no prejuízo contábil. Para um laticínio que depende de contratos com
    redes de supermercado, essa folga mostra quanto a perda de um grande cliente afetaria o resultado."""))

    s.append("<h4>e) Custo e preço do queijo minas frescal (custeio marginal)</h4>")
    s.append(f"""<p>Primeiro tiramos a matéria-prima do CVP, porque ela já entra em R$ pela ficha técnica:
    CVP = {pn(d['cvp_tot'])}% − {pn(d['mp'])}% = <b>{pn(d['cvp'])}%</b>. Depois usamos CVV = {pn(d['cvv'])}% e CF = {pn(d['cf'])}%.</p>""")
    m = marginal(9.80, d, 10)
    s.append(eq("CUSTO", fr("MP", fr("100 − (CVV + CVP + CF)", "100")),
                fr("9,80", fr(f"100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])})", "100")),
                fr("9,80", num(m['div_c'], 3).rstrip("0").rstrip(",")), res=brl(m['custo'])))
    s.append(eq("PREÇO", fr("MP", fr("100 − (CVV + CVP + CF + L)", "100")),
                fr("9,80", fr(f"100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])} + 10)", "100")),
                fr("9,80", num(m['div_p'], 3).rstrip("0").rstrip(",")), res=brl(m['preco'])))
    s.append(interp(f"""O markup divisor de venda é {num(m['div_p'], 3).rstrip('0').rstrip(',')}: a matéria-prima representa só {pc(9.80 / float(m['preco']) * 100)} do preço.
    O restante paga impostos, comissões, fretes, a parcela da estrutura fixa e o lucro de 10%."""))

    GAB.extend([
        ("1", "CVP / CVV / CF", f"{brl(cvp)} / {brl(cvv)} / {brl(cf)}"),
        ("1", "MC / LO", f"{brl(mc)} ({pc(d['mc'])}) / {brl(lo)} ({pc(d['lo'])})"),
        ("1", "PE financeiro / contábil / econômico", f"{brl(P['pef'])} / {brl(P['pec'])} / {brl(P['pee'])}"),
        ("1", "Margem de segurança", pc(ms)),
        ("1", "Queijo minas: custo / preço (marginal)", f"{brl(m['custo'])} / {brl(m['preco'])}"),
    ])
    ANS[1] = [("tab", "a) Classifique cada gasto", ["Gasto", "Classe"], [[n, MC(c, ["CVP", "CF", "CVV"])] for n, _, c in lista]),
              ("tab", "b) DRE analítico", ["Conta", "R$", "%"], dre_ans(R, cvp, cvv, cf)),
              ("tab", "c) Pontos de equilíbrio", ["Ponto de equilíbrio", "R$"],
               [["Financeiro", N(P['pef'])], ["Contábil", N(P['pec'])], ["Econômico", N(P['pee'])]]),
              ("tab", "d) Margem de segurança", ["Indicador", "%"], [["Margem de segurança", N(ms, "p")]]),
              ("tab", "e) Queijo minas frescal (custeio marginal)", ["Item", "Custo", "Preço"], [["Queijo minas frescal", N(m['custo']), N(m['preco'])]])]
    return dict(n=1, ind="Laticínios", empresa="Laticínios Serra Verde", tit="Classificação, DRE e pontos de equilíbrio",
                tags=["CVP · CVV · CF", "DRE analítico", "PE financeiro, contábil e econômico", "Margem de segurança"],
                enun=enun, sol="".join(s))


# ================= EXERCÍCIO 2 =================
def ex2():
    R, MP, OCVP, CVV, CF = 350000.0, 105000.0, 35000.0, 63000.0, 77000.0
    cvp = MP + OCVP
    d = dre_pct(R, cvp, CVV, CF, MP)
    lo = R - cvp - CVV - CF
    itens = [("Dobradiça 3\" (par)", 8.40, 10), ("Fechadura de embutir", 46.50, 15), ("Puxador de inox 30 cm", 12.90, 8),
             ("Trinco de sobrepor", 5.60, 20)]
    h = [f"""<p>A <b>Metalúrgica Ferraço Ltda.</b>, de Caxias do Sul (RS), fabrica ferragens para portas e móveis. O DRE de setembro apresentou:</p>"""]
    h.append(table(["Conta", "R$"], [["Receita sobre vendas", num(R)], ["Matéria-prima (aço, latão, zamac)", num(MP)],
                                    ["Outros custos variáveis de produção (energia, insumos, frete sobre compras)", num(OCVP)],
                                    ["Custos variáveis de vendas (impostos, comissões, frete de entrega)", num(CVV)],
                                    ["Custos fixos", num(CF)]], "data"))
    h.append("<p>A engenharia de produto informou a matéria-prima de cada item (ficha técnica) e a diretoria definiu a margem de lucro desejada:</p>")
    h.append(table(["Item", "MP (R$/un.)", "Lucro desejado"], [[n, num(mp), f"{l}%"] for n, mp, l in itens], "data"))
    h.append("""<ol class="q" type="a">
    <li>Calcule os percentuais do DRE (CVP sem a matéria-prima, CVV, CF e lucro operacional).</li>
    <li>Calcule o custo e o preço de venda de cada item pelo <b>custeio marginal</b> (absorção plena).</li>
    <li>O principal concorrente vende a fechadura de embutir por R$&nbsp;120,00. Se a Ferraço acompanhar esse preço, qual margem de lucro ela obtém?</li>
    <li>Por que a empresa não conseguiria aplicar uma margem de lucro de 50% em nenhum item?</li></ol>""")

    s = ["<h4>a) Percentuais do DRE</h4>"]
    s.append(table(["Conta", "R$", "%"], [
        ["Receita", num(R), "100,00%"], ["CVP total (MP + outros)", num(cvp), pc(d['cvp_tot'])],
        ['<span class="sub">Matéria-prima</span>', num(MP), pc(d['mp'])],
        ["CVV", num(CVV), pc(d['cvv'])], ["Margem de contribuição", num(R - cvp - CVV), pc(d['mc'])],
        ["CF", num(CF), pc(d['cf'])], ["<b>Lucro operacional</b>", f"<b>{num(lo)}</b>", f"<b>{pc(d['lo'])}</b>"]], "dre"))
    s.append(f"<p>Para a fórmula: <b>CVP = {pn(d['cvp_tot'])}% − {pn(d['mp'])}% = {pn(d['cvp'])}%</b>, CVV = {pn(d['cvv'])}% e CF = {pn(d['cf'])}%. "
             f"Soma = {pn(d['cvp'] + d['cvv'] + d['cf'])}%.</p>")
    s.append(note("A matéria-prima sai do percentual porque já está no numerador da fórmula, em reais, pela ficha técnica. Se ficasse nos dois lugares, seria contada duas vezes."))

    s.append("<h4>b) Custo e preço pelo custeio marginal</h4>")
    m0 = marginal(1, d, 0)
    s.append(eq("Markup divisor de custo", fr(f"100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])})", "100"), res=num(m0['div_c'], 2)))
    rows, ans_it = [], []
    for n, mp, L in itens:
        m = marginal(mp, d, L)
        ans_it.append([n, N(m['custo']), N(m['preco'])])
        s.append(f'<div class="prod">{n} <span>MP = {num(mp)} · L = {L}%</span></div>')
        s.append(eq("CUSTO", fr(num(mp), num(m['div_c'])), res=brl(m['custo'])))
        s.append(eq("PREÇO", fr(num(mp), fr(f"100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])} + {L})", "100")),
                    fr(num(mp), num(m['div_p'])), res=brl(m['preco'])))
        rows.append([n, num(mp), f"{L}%", num(m['div_p']), num(1 / m['div_p'], 4), brl(m['custo']), brl(m['preco'])])
        GAB.append(("2", f"{n}: custo / preço", f"{brl(m['custo'])} / {brl(m['preco'])}"))
    s.append(table(["Item", "MP", "L", "Divisor", "Multiplicador", "Custo", "Preço"], rows, "data res"))
    s.append(interp("""No custeio marginal o custo fixo entra como percentual da receita. Por isso todos os itens têm o mesmo divisor de custo (0,50):
    o custo é sempre o dobro da matéria-prima. O que muda entre os preços é só a margem de lucro desejada. Repare no multiplicador:
    a fechadura, com 15% de lucro, é vendida por 2,86 vezes a sua MP."""))

    s.append("<h4>c) Margem obtida ao preço do concorrente</h4>")
    p_merc, mp_f = 120.0, 46.50
    Lobt = 100 - (d['cvv'] + d['cvp'] + d['cf']) - mp_f / p_merc * 100
    s.append("<p>Isolando L na fórmula do preço: <i>MP ÷ Preço = (100 − (CVV + CVP + CF + L)) ÷ 100</i>.</p>")
    s.append(eq("MP ÷ Preço", fr("46,50", "120,00"), res=f"0,3875 = {num(mp_f / p_merc * 100)}%"))
    s.append(eq("L", f"100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])}) − {num(mp_f / p_merc * 100)}", res=pc(Lobt)))
    s.append(interp(f"""A R$&nbsp;120,00 a fechadura ainda dá lucro, mas de {pc(Lobt)}, abaixo dos 15% desejados. A empresa tem três caminhos:
    aceitar a margem menor, reduzir a matéria-prima (renegociar o latão, revisar o projeto) ou baixar CVV e CF. Isso é o raciocínio de
    <i>custo-meta</i>: o mercado fixa o preço e a empresa ajusta o custo."""))
    GAB.append(("2", "Margem obtida na fechadura a R$ 120,00", pc(Lobt)))
    ANS[2] = [("tab", "a) Percentuais para a fórmula", ["Percentual", "%"],
               [["CVP (sem matéria-prima)", N(d['cvp'], "p")], ["CVV", N(d['cvv'], "p")], ["CF", N(d['cf'], "p")], ["Lucro operacional", N(d['lo'], "p")]]),
              ("tab", "b) Custeio marginal", ["Item", "Custo", "Preço"], ans_it),
              ("tab", "c) Preço do concorrente", ["Indicador", "%"], [["Margem de lucro obtida na fechadura a R$ 120,00", N(Lobt, "p")]]),
              ("tab", "d) Com L = 50%", ["Pergunta", "Resposta"],
               [["O divisor da fórmula do preço fica", MC("igual a zero, então o preço não pode ser calculado", ["igual a 0,50, então o preço dobra", "igual a zero, então o preço não pode ser calculado", "negativo, então o preço fica negativo"])]])]

    s.append("<h4>d) Por que não é possível aplicar L = 50%?</h4>")
    s.append(f"""<p>Com L = 50%, o divisor fica (100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])} + 50)) ÷ 100 = 0. Não existe divisão por zero:
    o preço tenderia ao infinito. Cada R$&nbsp;100,00 de receita já está comprometido em {pn(d['cvp'] + d['cvv'] + d['cf'])}% com custos, então a
    soma dos percentuais mais o lucro tem de ficar abaixo de 100%.</p>""")
    s.append(interp("""Quanto mais perto de 100% chega a soma (CVV + CVP + CF + L), mais o preço dispara. Quem tem estrutura de custos pesada tem pouco espaço
    para margem. Antes de pedir mais lucro, a empresa precisa reduzir custo."""))
    return dict(n=2, ind="Metalúrgica", empresa="Metalúrgica Ferraço", tit="Preço de venda pelo custeio marginal",
                tags=["Custeio marginal", "Markup divisor", "Custo-meta"], enun="".join(h), sol="".join(s))


# ================= EXERCÍCIO 3 =================
def ex3():
    R, MP, CVPt, CVV, CF = 600000.0, 210000.0, 270000.0, 120000.0, 144000.0
    d = dre_pct(R, CVPt, CVV, CF, MP)
    P = [("Cômoda 4 gavetas", 120.00, 800, 600, 12), ("Mesa de jantar 6 lugares", 210.00, 500, 400, 15),
         ("Cadeira estofada", 45.00, 1700, 1000, 10)]
    sp, sv = sum(p[2] for p in P), sum(p[3] for p in P)
    cfi, cfd = float(r2(CF / sp)), float(r2(CF / sv))
    assert (cfi, cfd) == (48.0, 72.0)
    h = [f"""<p>A <b>Móveis Pinheiral Ltda.</b>, de Arapongas (PR), polo moveleiro do Norte do Paraná, montou um estoque para a feira de
    lançamentos de novembro. Por isso, em outubro <b>produziu mais do que vendeu</b>. O DRE do mês mostrou:</p>"""]
    h.append(table(["Conta", "R$"], [["Receita sobre vendas", num(R)], ["Custos variáveis de produção (inclui MP de " + num(MP) + ")", num(CVPt)],
                                    ["Custos variáveis de vendas", num(CVV)], ["Custos fixos", num(CF)]], "data"))
    h.append(table(["Produto", "MP (R$/un.)", "Produzidas", "Vendidas", "Lucro desejado"],
                   [[n, num(mp), f"{pr:,}".replace(",", "."), f"{v:,}".replace(",", "."), f"{l}%"] for n, mp, pr, v, l in P], "data"))
    h.append("""<ol class="q" type="a">
    <li>Calcule CVP (sem MP), CVV e o lucro operacional em % da receita.</li>
    <li>Calcule o custo fixo unitário pelo <b>custeio por absorção integral</b> e pelo <b>custeio por absorção ideal</b>.</li>
    <li>Calcule o custo e o preço de venda de cada produto pelos dois métodos.</li>
    <li>Quanto de custo fixo do mês fica "guardado" no estoque pelo método integral?</li>
    <li>Qual método o gerente comercial deve usar para formar preço neste mês? Justifique.</li></ol>""")

    s = ["<h4>a) Percentuais do DRE</h4>"]
    s.append(table(["Conta", "R$", "%"], [["Receita", num(R), "100,00%"], ["CVP total", num(CVPt), pc(d['cvp_tot'])],
                                          ['<span class="sub">Matéria-prima</span>', num(MP), pc(d['mp'])], ["CVV", num(CVV), pc(d['cvv'])],
                                          ["CF", num(CF), pc(d['cf'])], ["<b>Lucro operacional</b>", f"<b>{num(R - CVPt - CVV - CF)}</b>", f"<b>{pc(d['lo'])}</b>"]], "dre"))
    s.append(f"<p>CVP = {pn(d['cvp_tot'])}% − {pn(d['mp'])}% = <b>{pn(d['cvp'])}%</b>; CVV = <b>{pn(d['cvv'])}%</b>. Na absorção o CF não entra como %: entra em R$ por unidade.</p>")

    s.append("<h4>b) Custo fixo unitário</h4>")
    s.append(eq("CF unit.<sub>integral</sub>", fr("CF total", "Σ itens produzidos"), fr(num(CF), f"{sp:,}".replace(",", ".")), res=brl(cfi)))
    s.append(eq("CF unit.<sub>ideal</sub>", fr("CF total", "Σ itens vendidos"), fr(num(CF), f"{sv:,}".replace(",", ".")), res=brl(cfd)))

    s.append("<h4>c) Custo e preço de venda</h4>")
    rows, difs, ans_i, ans_d = [], [], [], []
    for n, mp, pr, v, L in P:
        a, b = absorcao(mp, cfi, d, L), absorcao(mp, cfd, d, L)
        ans_i.append([n, N(a['custo']), N(a['preco'])]); ans_d.append([n, N(b['custo']), N(b['preco'])])
        s.append(f'<div class="prod">{n} <span>MP = {num(mp)} · L = {L}%</span></div>')
        s.append('<div class="two">')
        s.append('<div><span class="mth int">Absorção integral</span>')
        s.append(eq("CUSTO", fr(f"{num(mp)} + {num(cfi)}", fr(f"100 − ({pn(d['cvv'])} + {pn(d['cvp'])})", "100")), fr(num(a['base']), num(a['div_c'])), res=brl(a['custo'])))
        s.append(eq("PREÇO", fr(num(a['base']), fr(f"100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {L})", "100")), fr(num(a['base']), num(a['div_p'])), res=brl(a['preco'])))
        s.append('</div><div><span class="mth ide">Absorção ideal</span>')
        s.append(eq("CUSTO", fr(f"{num(mp)} + {num(cfd)}", num(b['div_c'])), fr(num(b['base']), num(b['div_c'])), res=brl(b['custo'])))
        s.append(eq("PREÇO", fr(num(b['base']), num(b['div_p'])), res=brl(b['preco'])))
        s.append('</div></div>')
        dif = (float(b['preco']) / float(a['preco']) - 1) * 100
        difs.append(dif)
        rows.append([n, brl(a['custo']), brl(a['preco']), brl(b['custo']), brl(b['preco']), "+" + pc(dif, 1)])
        GAB.append(("3", f"{n}: integral custo / preço", f"{brl(a['custo'])} / {brl(a['preco'])}"))
        GAB.append(("3", f"{n}: ideal custo / preço", f"{brl(b['custo'])} / {brl(b['preco'])}"))
    s.append(table(["Produto", "Custo integral", "Preço integral", "Custo ideal", "Preço ideal", "Ideal vs. integral"], rows, "data res"))

    est = cfi * (sp - sv)
    s.append("<h4>d) Custo fixo que fica no estoque</h4>")
    s.append(eq("CF no estoque", "CF unit.<sub>integral</sub> × (produzidas − vendidas)", f"{num(cfi)} × ({sp:,} − {sv:,})".replace(",", "."), res=brl(est)))
    s.append(f"<p>Dos {brl(CF)} de custo fixo do mês, {brl(cfi * sv)} vão para o resultado junto com os produtos vendidos e {brl(est)} ficam no estoque, "
             "para serem reconhecidos quando esses móveis forem vendidos na feira.</p>")
    GAB.append(("3", "CF unitário integral / ideal", f"{brl(cfi)} / {brl(cfd)}"))
    GAB.append(("3", "CF que fica no estoque (integral)", brl(est)))
    ANS[3] = [("tab", "a) Percentuais", ["Percentual", "%"], [["CVP (sem matéria-prima)", N(d['cvp'], "p")], ["CVV", N(d['cvv'], "p")], ["Lucro operacional", N(d['lo'], "p")]]),
              ("tab", "b) Custo fixo unitário", ["Método", "CF unitário"], [["Absorção integral", N(cfi)], ["Absorção ideal", N(cfd)]]),
              ("tab", "c) Absorção integral", ["Produto", "Custo", "Preço"], ans_i),
              ("tab", "c) Absorção ideal", ["Produto", "Custo", "Preço"], ans_d),
              ("tab", "d) Custo fixo no estoque", ["Item", "R$"], [["CF que fica no estoque pelo método integral", N(est)]]),
              ("tab", "e) Formação de preço", ["Pergunta", "Resposta"],
               [["Método mais prudente para formar preço num mês de formação de estoque", MC("Absorção ideal", ["Absorção integral", "Absorção ideal"])]])]

    s.append("<h4>e) Qual método usar para formar o preço?</h4>")
    s.append(interp(f"""O <b>integral</b> divide o CF pelas {sp:,} unidades produzidas e chega a preços menores, porque parte do custo fixo foi para o estoque.
    O <b>ideal</b> divide o CF só pelas {sv:,} unidades vendidas e exige que as vendas do mês paguem toda a estrutura, por isso os preços sobem entre
    {pc(min(difs), 1)} e {pc(max(difs), 1)}. O aumento é maior na cadeira, porque o CF extra pesa mais sobre uma MP pequena. Para um mês de formação de estoque o preço pelo ideal é o mais prudente: garante que o caixa do mês cubra o CF. O integral só é
    seguro se a empresa tiver certeza de que venderá o estoque da feira.
    <br><br><b>Ponto crítico:</b> nos dois métodos a cadeira (MP = 45,00) recebe o mesmo CF por unidade que a mesa (MP = 210,00). Dividir o CF pela
    simples contagem de peças ignora que uma mesa ocupa muito mais tempo de máquina e de montagem. Essa limitação é a porta de entrada para
    métodos como UEP e ABC.""".replace(f"{sp:,}", f"{sp:,}".replace(",", ".")).replace(f"{sv:,}", f"{sv:,}".replace(",", "."))))
    return dict(n=3, ind="Moveleira", empresa="Móveis Pinheiral", tit="Absorção integral × ideal com produção maior que vendas",
                tags=["Absorção integral", "Absorção ideal", "CF no estoque"], enun="".join(h), sol="".join(s))


# ================= EXERCÍCIO 4 =================
def ex4():
    R = 320000.0
    lanc = [("Receita", R, "R"), ("Comissão dos representantes", 16000.0, "CVV"), ("Tecido e aviamentos (matéria-prima)", 96000.0, "MP"),
            ("Frete de entrega", 9600.0, "CVV"), ("Energia elétrica da fábrica", 12800.0, "CVP"),
            ("Linhas, etiquetas e embalagens", 6400.0, "CVP"), ("Impostos sobre a venda", 32000.0, "CVV"),
            ("Salário da produção (mensalistas)", 28000.0, "CF"), ("Salário da administração", 14000.0, "CF"),
            ("Depreciação", 4000.0, "CF"), ("Aluguel do galpão", 6000.0, "CF"), ("Outras despesas fixas", 12000.0, "CF")]
    MP = sum(v for _, v, c in lanc if c == "MP")
    cvp = MP + sum(v for _, v, c in lanc if c == "CVP")
    cvv = sum(v for _, v, c in lanc if c == "CVV")
    cf = sum(v for _, v, c in lanc if c == "CF")
    d = dre_pct(R, cvp, cvv, cf, MP)
    assert (cvp, cvv, cf) == (115200, 57600, 64000)
    P = [("Camiseta básica", 9.60, 4000, 3600, 15), ("Calça jeans", 38.50, 2000, 1700, 20), ("Jaqueta jeans", 72.00, 600, 500, 25),
         ("Vestido midi", 44.00, 1400, 1000, 18), ("Bermuda sarja", 21.00, 2000, 1200, 12)]
    sp, sv = sum(p[2] for p in P), sum(p[3] for p in P)
    cfi, cfd = float(r2(cf / sp)), float(r2(cf / sv))
    assert (cfi, cfd) == (6.40, 8.00)
    h = ["""<p>A <b>Confecções Vale do Itajaí Ltda.</b>, de Brusque (SC), produz moda casual em jeans e malha. Os resultados de agosto foram:</p>"""]
    h.append(table(["Conta", "R$"], [[n, num(v)] for n, v, _ in lanc], "data"))
    h.append("<p>O quadro abaixo traz a matéria-prima por peça, as quantidades produzidas e vendidas e a margem de lucro desejada:</p>")
    h.append(table(["Produto", "MP", "Produzidas", "Vendidas", "Margem de lucro"],
                   [[n, num(mp), f"{pr:,}".replace(",", "."), f"{v:,}".replace(",", "."), f"{l}%"] for n, mp, pr, v, l in P], "data"))
    h.append("""<ol class="q" type="a">
    <li>Elabore o DRE (R$ e %): receita, CVP, CVV, custo variável total, margem de contribuição, CF e lucro operacional.</li>
    <li>Calcule o custo e o preço de venda de cada produto pelos três métodos: <b>custeio marginal</b>, <b>absorção integral</b> e <b>absorção ideal</b>,
    garantindo as margens de lucro desejadas.</li>
    <li>Compare os resultados. Para quais produtos o custeio marginal dá o preço mais alto, e por quê?</li></ol>""")

    s = ["<h4>a) DRE</h4>"]
    rows = [["Receita", num(R), "100,00%"], ["Custo variável de produção", num(cvp), pc(cvp / R * 100)],
            ['<span class="sub">dos quais matéria-prima</span>', num(MP), pc(d['mp'])], ["Custo variável de vendas", num(cvv), pc(d['cvv'])],
            ["Custo variável total", num(cvp + cvv), pc((cvp + cvv) / R * 100)], ["<b>Margem de contribuição</b>", f"<b>{num(R - cvp - cvv)}</b>", f"<b>{pc(d['mc'])}</b>"],
            ["Custos fixos", num(cf), pc(d['cf'])], ["<b>Lucro operacional</b>", f"<b>{num(R - cvp - cvv - cf)}</b>", f"<b>{pc(d['lo'])}</b>"]]
    s.append(table(["Receita / custos", "R$", "%"], rows, "dre"))
    s.append(f"""<p>Classificação usada: CVP = tecido e aviamentos + energia da fábrica + linhas, etiquetas e embalagens; CVV = comissão + frete de entrega
    + impostos; CF = salários, depreciação, aluguel e outras despesas fixas.</p>
    <p>Percentuais para as fórmulas: <b>CVP = {pn(d['cvp_tot'])}% − {pn(d['mp'])}% = {pn(d['cvp'])}%</b> · <b>CVV = {pn(d['cvv'])}%</b> · <b>CF = {pn(d['cf'])}%</b>.</p>""")
    GAB.append(("4", "CVP / CVV / CF", f"{brl(cvp)} ({pc(cvp / R * 100)}) / {brl(cvv)} ({pc(d['cvv'])}) / {brl(cf)} ({pc(d['cf'])})"))
    GAB.append(("4", "MC / LO", f"{brl(R - cvp - cvv)} ({pc(d['mc'])}) / {brl(R - cvp - cvv - cf)} ({pc(d['lo'])})"))

    s.append("<h4>b) Os três métodos</h4>")
    s.append('<div class="mrow"><span class="mth mar">Custeio marginal</span> divisor de custo = (100 − (' +
             f"{pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])}))/100 = {num(marginal(1, d, 0)['div_c'])}</div>")
    s.append(f'<div class="mrow"><span class="mth int">Absorção integral</span> CF unit. = {num(cf)} ÷ {sp:,} = <b>{num(cfi)}</b>; '.replace(f"{sp:,}", f"{sp:,}".replace(",", ".")) +
             f"divisor de custo = (100 − ({pn(d['cvv'])} + {pn(d['cvp'])}))/100 = {num(absorcao(1, 0, d, 0)['div_c'])}</div>")
    s.append(f'<div class="mrow"><span class="mth ide">Absorção ideal</span> CF unit. = {num(cf)} ÷ {sv:,} = <b>{num(cfd)}</b>; mesmo divisor da integral</div>'.replace(f"{sv:,}", f"{sv:,}".replace(",", ".")))
    rows, mais, menos, spread, a_m, a_i, a_d = [], [], [], [], [], [], []
    for n, mp, pr, v, L in P:
        m, a, b = marginal(mp, d, L), absorcao(mp, cfi, d, L), absorcao(mp, cfd, d, L)
        ps = [m['preco'], a['preco'], b['preco']]
        a_m.append([n, N(m['custo']), N(m['preco'])]); a_i.append([n, N(a['custo']), N(a['preco'])]); a_d.append([n, N(b['custo']), N(b['preco'])])
        if m['preco'] == max(ps): mais.append(n.lower())
        if m['preco'] == min(ps): menos.append(n.lower())
        spread.append((n, (float(max(ps)) / float(min(ps)) - 1) * 100))
        s.append(f'<div class="prod">{n} <span>MP = {num(mp)} · L = {L}%</span></div><div class="three">')
        s.append(f'<div><span class="mth mar">Marginal</span>' +
                 eq("CUSTO", fr(num(mp), num(m['div_c'])), res=brl(m['custo'])) +
                 eq("PREÇO", fr(num(mp), fr(f"100 − ({pn(d['cvv'])}+{pn(d['cvp'])}+{pn(d['cf'])}+{L})", "100")), fr(num(mp), num(m['div_p'])), res=brl(m['preco'])) + "</div>")
        s.append(f'<div><span class="mth int">Integral</span>' +
                 eq("CUSTO", fr(f"{num(mp)} + {num(cfi)}", num(a['div_c'])), res=brl(a['custo'])) +
                 eq("PREÇO", fr(num(a['base']), fr(f"100 − ({pn(d['cvv'])}+{pn(d['cvp'])}+{L})", "100")), fr(num(a['base']), num(a['div_p'])), res=brl(a['preco'])) + "</div>")
        s.append(f'<div><span class="mth ide">Ideal</span>' +
                 eq("CUSTO", fr(f"{num(mp)} + {num(cfd)}", num(b['div_c'])), res=brl(b['custo'])) +
                 eq("PREÇO", fr(num(b['base']), num(b['div_p'])), res=brl(b['preco'])) + "</div></div>")
        rows.append([n, brl(m['custo']), brl(m['preco']), brl(a['custo']), brl(a['preco']), brl(b['custo']), brl(b['preco'])])
        GAB.append(("4", f"{n}: marginal / integral / ideal (preço)", f"{brl(m['preco'])} / {brl(a['preco'])} / {brl(b['preco'])}"))
        GAB.append(("4", f"{n}: marginal / integral / ideal (custo)", f"{brl(m['custo'])} / {brl(a['custo'])} / {brl(b['custo'])}"))
    s.append('<div class="tw"><table class="data res"><thead><tr><th rowspan=2>Produto</th><th colspan=2>Marginal</th><th colspan=2>Abs. integral</th><th colspan=2>Abs. ideal</th></tr>'
             '<tr><th>Custo</th><th>Preço</th><th>Custo</th><th>Preço</th><th>Custo</th><th>Preço</th></tr></thead><tbody>' +
             "".join("<tr>" + "".join(f'<td class="{"l" if i == 0 else "r"}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows) + "</tbody></table></div>")

    # ponto de virada: MP em que marginal = integral no custo
    mp_star = cfi * m['div_c'] / (a['div_c'] - m['div_c'])
    s.append("<h4>c) Comparação entre os métodos</h4>")
    assert menos == ["camiseta básica"], menos
    big = max(spread, key=lambda x: x[1])
    s.append(interp(f"""O custeio marginal dá o preço mais alto para {", ".join(mais[:-1])} e {mais[-1]}, e o mais baixo para a {menos[0]}.
    O motivo está na forma de distribuir o CF:
    <br>• no <b>marginal</b>, o CF entra como {pn(d['cf'])}% no divisor, ou seja, é distribuído <i>em proporção à matéria-prima</i>: quem tem MP cara recebe mais CF;
    <br>• na <b>absorção</b>, todas as peças recebem o mesmo CF em reais ({num(cfi)} ou {num(cfd)}), seja uma camiseta, seja uma jaqueta.
    <br><br>Igualando os dois custos (marginal e integral), a virada acontece em MP ≈ R$&nbsp;{num(mp_star)}: acima desse valor o marginal atribui mais custo
    que a absorção integral. Só a camiseta (MP = 9,60) fica abaixo da virada.
    <br><br>Nenhum dos critérios é "o certo"; todos são aproximações. Entre o menor e o maior preço calculado, a diferença chega a {pc(big[1], 1)} na {big[0].lower()}.
    Num mercado competitivo de moda, um preço distorcido pelo critério de rateio significa perder volume ou deixar margem na mesa."""))
    GAB.append(("4", "MP em que custo marginal = custo integral", brl(mp_star)))
    ANS[4] = [("tab", "a) DRE", ["Receita / custos", "R$", "%"], dre_ans(R, cvp, cvv, cf)),
              ("tab", "b) Custeio marginal", ["Produto", "Custo", "Preço"], a_m),
              ("tab", "b) Custeio por absorção integral", ["Produto", "Custo", "Preço"], a_i),
              ("tab", "b) Custeio por absorção ideal", ["Produto", "Custo", "Preço"], a_d),
              ("tab", "c) Comparação", ["Pergunta", "Resposta"],
               [["Produto em que o custeio marginal dá o MENOR preço dos três métodos", MC(menos[0].capitalize() if False else [p[0] for p in P if p[0].lower() == menos[0]][0], [p[0] for p in P])]])]
    return dict(n=4, ind="Têxtil / confecção", empresa="Confecções Vale do Itajaí", tit="Os três métodos lado a lado",
                tags=["DRE", "Marginal", "Absorção integral", "Absorção ideal"], enun="".join(h), sol="".join(s))


# ================= EXERCÍCIO 5 =================
def ex5():
    R, CVPt, MP, CVV, CF, dep = 250000.0, 125000.0, 100000.0, 37500.0, 50000.0, 10000.0
    d = dre_pct(R, CVPt, CVV, CF, MP)
    ativo, tx = 1200000.0, 1.25
    opp = ativo * tx / 100
    PE = pe(CF, d['mc'], dep, opp)
    P = [("Balde 20 L", 6.30, 6500, 5000, 19.90), ("Bombona 50 L", 18.40, 2000, 1500, 49.90), ("Caixa organizadora 30 L", 9.10, 4000, 3500, 24.90)]
    L = 10
    sp, sv = sum(p[2] for p in P), sum(p[3] for p in P)
    cfi, cfd = float(r2(CF / sp)), float(r2(CF / sv))
    assert (cfi, cfd) == (4.0, 5.0)
    nv = [3000, 1000, 2000]
    sv2 = sum(nv)
    cfd2 = float(r2(CF / sv2))
    h = ["""<p>A <b>Polimix Embalagens Plásticas Ltda.</b>, de Joinville (SC), injeta baldes, bombonas e caixas organizadoras em polipropileno.
    O DRE de julho foi:</p>"""]
    h.append(table(["Conta", "R$"], [["Receita sobre vendas", num(R)], ["Custos variáveis de produção (inclui resina PP de " + num(MP) + ")", num(CVPt)],
                                    ["Custos variáveis de vendas", num(CVV)], ["Custos fixos (inclui depreciação das injetoras de " + num(dep) + ")", num(CF)]], "data"))
    h.append(f"<p>Ativo total: {brl(ativo)}. Custo de oportunidade do capital: {pn(tx)}% ao mês. Margem de lucro desejada em todos os produtos: {L}%.</p>")
    h.append(table(["Produto", "MP", "Produzidas", "Vendidas", "Preço de mercado"],
                   [[n, num(mp), f"{pr:,}".replace(",", "."), f"{v:,}".replace(",", "."), brl(pm)] for n, mp, pr, v, pm in P], "data"))
    h.append(f"""<ol class="q" type="a">
    <li>Calcule os pontos de equilíbrio financeiro, contábil e econômico.</li>
    <li>Calcule o preço de venda de cada produto pelos três métodos tradicionais.</li>
    <li>Compare os preços calculados com o preço de mercado. A Polimix é competitiva?</li>
    <li>Uma grande rede de varejo suspendeu os pedidos e as vendas do mês seguinte devem cair para 3.000 baldes, 1.000 bombonas e 2.000 caixas.
    Mantidos os demais dados, recalcule o preço pela <b>absorção ideal</b> e compare de novo com o mercado.</li>
    <li>Que decisão o gestor deve tomar diante do resultado do item (d)?</li></ol>""")

    s = ["<h4>a) Pontos de equilíbrio</h4>"]
    s.append(f"<p>MC = {num(R)} − {num(CVPt)} − {num(CVV)} = {brl(R - CVPt - CVV)} → MC% = {pc(d['mc'])}. Custo de oportunidade = {num(ativo)} × {pn(tx)}% = {brl(opp)}.</p>")
    s.append(eq("PE<sub>financeiro</sub>", fr(f"{num(CF)} − {num(dep)}", num(d['mc'] / 100)), res=brl(PE['pef'])))
    s.append(eq("PE<sub>contábil</sub>", fr(num(CF), num(d['mc'] / 100)), res=brl(PE['pec'])))
    s.append(eq("PE<sub>econômico</sub>", fr(f"{num(CF)} + {num(opp)}", num(d['mc'] / 100)), res=brl(PE['pee'])))
    s.append(interp(f"""A receita de julho ({brl(R)}) supera os três pontos. A folga sobre o PE econômico é de {pc((R - float(PE['pee'])) / R * 100)}:
    uma queda de vendas maior que isso já faz a empresa remunerar o capital abaixo do esperado."""))
    GAB.append(("5", "PE financeiro / contábil / econômico", f"{brl(PE['pef'])} / {brl(PE['pec'])} / {brl(PE['pee'])}"))
    a5_pe = [["Financeiro", N(PE['pef'])], ["Contábil", N(PE['pec'])], ["Econômico", N(PE['pee'])]]
    a5_p, a5_q = [], []
    s.append("<h4>b) Preço pelos três métodos</h4>")
    s.append(f"""<p>CVP = {pn(d['cvp_tot'])}% − {pn(d['mp'])}% = <b>{pn(d['cvp'])}%</b> · CVV = <b>{pn(d['cvv'])}%</b> · CF = <b>{pn(d['cf'])}%</b> · L = <b>{L}%</b><br>
    Divisor marginal = (100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {pn(d['cf'])} + {L}))/100 = <b>{num(marginal(1, d, L)['div_p'])}</b> ·
    Divisor absorção = (100 − ({pn(d['cvv'])} + {pn(d['cvp'])} + {L}))/100 = <b>{num(absorcao(1, 0, d, L)['div_p'])}</b><br>
    CF unit. integral = {num(CF)} ÷ {sp:,} = <b>{num(cfi)}</b> · CF unit. ideal = {num(CF)} ÷ {sv:,} = <b>{num(cfd)}</b></p>""".replace(f"{sp:,}", f"{sp:,}".replace(",", ".")).replace(f"{sv:,}", f"{sv:,}".replace(",", ".")))
    rows = []
    for n, mp, pr, v, pm in P:
        m, a, b = marginal(mp, d, L), absorcao(mp, cfi, d, L), absorcao(mp, cfd, d, L)
        s.append(f'<div class="prod">{n} <span>MP = {num(mp)}</span></div><div class="three">')
        s.append('<div><span class="mth mar">Marginal</span>' + eq("PREÇO", fr(num(mp), num(m['div_p'])), res=brl(m['preco'])) + "</div>")
        s.append('<div><span class="mth int">Integral</span>' + eq("PREÇO", fr(f"{num(mp)} + {num(cfi)}", num(a['div_p'])), fr(num(a['base']), num(a['div_p'])), res=brl(a['preco'])) + "</div>")
        s.append('<div><span class="mth ide">Ideal</span>' + eq("PREÇO", fr(f"{num(mp)} + {num(cfd)}", num(b['div_p'])), fr(num(b['base']), num(b['div_p'])), res=brl(b['preco'])) + "</div></div>")
        folga = (pm / float(b['preco']) - 1) * 100
        rows.append([n, brl(m['preco']), brl(a['preco']), brl(b['preco']), brl(pm), f'<span class="ok">+{pc(folga, 1)}</span>'])
        GAB.append(("5", f"{n}: preço marginal / integral / ideal", f"{brl(m['preco'])} / {brl(a['preco'])} / {brl(b['preco'])}"))
        a5_p.append([n, N(m['preco']), N(a['preco']), N(b['preco'])])
    s.append("<h4>c) Comparação com o mercado</h4>")
    s.append(table(["Produto", "Marginal", "Integral", "Ideal", "Mercado", "Mercado vs. ideal"], rows, "data res"))
    s.append(interp("""Mesmo pelo método mais exigente (ideal), os três produtos têm preço calculado abaixo do mercado. A Polimix é competitiva e tem
    espaço para praticar o preço de mercado e ganhar margem acima dos 10%, principalmente na bombona."""))

    s.append("<h4>d) Queda nas vendas: novo preço pela absorção ideal</h4>")
    s.append(eq("CF unit.<sub>ideal</sub>", fr(num(CF), f"{sv2:,}".replace(",", ".")), res=f"{brl(cfd2)} <span class=muted>(antes: {num(cfd)})</span>"))
    rows = []
    bad = []
    for (n, mp, pr, v, pm), q in zip(P, nv):
        b2 = absorcao(mp, cfd2, d, L)
        s.append(eq(f"PREÇO {n.split()[0].lower()}", fr(f"{num(mp)} + {num(cfd2)}", num(b2['div_p'])), fr(num(b2['base']), num(b2['div_p'])), res=brl(b2['preco'])))
        ok = float(b2['preco']) <= pm
        if not ok:
            bad.append(n)
        rows.append([n, brl(b2['preco']), brl(pm), '<span class="ok">abaixo do mercado</span>' if ok else '<span class="bad">acima do mercado</span>'])
        GAB.append(("5", f"{n}: preço ideal após a queda", brl(b2['preco'])))
        a5_q.append([n, N(b2['preco']), MC("abaixo do mercado" if ok else "acima do mercado", ["abaixo do mercado", "acima do mercado"])])
    assert bad == ["Balde 20 L", "Caixa organizadora 30 L"]
    ANS[5] = [("tab", "a) Pontos de equilíbrio", ["Ponto de equilíbrio", "R$"], a5_pe),
              ("tab", "b) Preço de venda", ["Produto", "Marginal", "Absorção integral", "Absorção ideal"], a5_p),
              ("tab", "c) Competitividade", ["Pergunta", "Resposta"],
               [["Pelo método ideal, os preços calculados ficam", MC("abaixo do mercado nos três produtos", ["abaixo do mercado nos três produtos", "acima do mercado nos três produtos", "acima do mercado só na bombona"])]]),
              ("tab", "d) Queda nas vendas: novo CF unitário (ideal)", ["Item", "R$"], [["CF unitário ideal", N(cfd2)]]),
              ("tab", "d) Queda nas vendas: novo preço (ideal)", ["Produto", "Preço", "Situação"], a5_q),
              ("tab", "e) Decisão", ["Pergunta", "Resposta"],
               [["Decisão recomendada no curto prazo", MC("manter o preço de mercado enquanto houver margem de contribuição e buscar volume",
                 ["repassar o novo custo ao preço", "manter o preço de mercado enquanto houver margem de contribuição e buscar volume", "suspender a produção do balde e da caixa"])]])]
    s.append(table(["Produto", "Preço ideal (nova venda)", "Mercado", "Situação"], rows, "data res", align="lrrl"))

    s.append("<h4>e) Decisão</h4>")
    s.append(interp(f"""Pelo custeio ideal, a queda nas vendas faz o CF unitário subir de {num(cfd)} para {num(cfd2)} e o balde e a caixa organizadora
    ficam mais caros que o mercado. Se o gestor repassar esse aumento, vende ainda menos, o CF unitário sobe de novo e a empresa entra na
    <b>espiral da morte</b> do preço.
    <br><br>A decisão correta não é subir o preço. O custo fixo de {brl(CF)} existe com ou sem a venda e não muda no curto prazo. Enquanto o preço de mercado
    cobrir os custos variáveis e deixar margem de contribuição, vale continuar vendendo e buscar novos clientes para recuperar volume. Lição: o
    custeio por absorção é útil para mostrar o custo "cheio", mas para decisões de preço no curto prazo a margem de contribuição é a melhor referência."""))
    return dict(n=5, ind="Plásticos / embalagens", empresa="Polimix Embalagens", tit="Preço, mercado e a espiral da morte",
                tags=["Pontos de equilíbrio", "Três métodos", "Preço de mercado", "Queda de volume"], enun="".join(h), sol="".join(s))



def build():
    return [ex1(), ex2(), ex3(), ex4(), ex5()]


