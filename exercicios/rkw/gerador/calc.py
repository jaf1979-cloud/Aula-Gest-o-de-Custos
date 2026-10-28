"""Método RKW como nos slides do professor (Métodos Contemporâneos de Custeio – RKW).

1. Distribuição primária: cada item de custo vai aos centros pelo seu direcionador
   (salários são diretos de cada centro).
2. Distribuição secundária: centros de apoio vão aos centros produtivos pelo nº de funcionários
   dos produtivos (slide 11). Com dois centros de apoio, em degraus: o primeiro distribui para o
   segundo e para os produtivos; o segundo, depois, só para os produtivos.
3. Custo por minuto do centro produtivo = custo total ÷ (horas/mês × 60 × nº funcionários),
   arredondado em 2 casas (regra das respostas no Moodle).
4. Custo RKW = Σ tempo do produto no centro × custo por minuto.
5. Custo total = (MP + RKW) ÷ [(100 − (CVV + CVP)) / 100];
   Preço de venda = (MP + RKW) ÷ [(100 − (CVV + CVP + L)) / 100].
"""


def r2(v):
    return round(v + 1e-9, 2)


def rkw(d):
    """d: dict com centros, apoio (lista ordenada), itens, drivers, horas, produtos."""
    C = d["centros"]
    apoio = d["apoio"]
    prod = [c for c in C if c not in apoio]
    func = d["drivers"]["Funcionários"]
    prim = {c: 0.0 for c in C}
    linhas = []
    for nome, valor, drv in d["itens"]:
        if drv == "Direto":
            # nome = "Salários <Centro>"
            alvo = d["salario_de"][nome]
            dist = {c: (valor if c == alvo else 0.0) for c in C}
            soma = None
        else:
            base = d["drivers"][drv]
            soma = sum(base[c] for c in C)
            dist = {c: valor * base[c] / soma for c in C}
        for c in C:
            prim[c] += dist[c]
        linhas.append(dict(item=nome, valor=valor, drv=drv, soma=soma,
                           unit=(valor / soma if soma else None), dist=dist))
    # secundária em degraus
    atual = dict(prim)
    sec = []
    for i, a in enumerate(apoio):
        recebem = [c for c in C if c not in apoio[: i + 1]]
        base = sum(func[c] for c in recebem)
        val = atual[a]
        parts = {c: val * func[c] / base for c in recebem}
        for c in recebem:
            atual[c] += parts[c]
        atual[a] = 0.0
        sec.append(dict(de=a, valor=val, base=base, recebem=recebem, parts=parts))
    total = {c: atual[c] for c in prod}
    mins = {c: d["horas"] * 60 * func[c] for c in prod}
    taxa_cheia = {c: total[c] / mins[c] for c in prod}
    taxa = {c: r2(taxa_cheia[c]) for c in prod}
    P = []
    for p in d["produtos"]:
        parc = {c: p["t"][c] * taxa[c] for c in prod}
        rk = r2(sum(parc.values()))
        rk_cheio = sum(p["t"][c] * taxa_cheia[c] for c in prod)
        perc = p["cvv"] + p["cvp"]
        ct = (p["mp"] + rk) / ((100 - perc) / 100)
        pv = (p["mp"] + rk) / ((100 - perc - d["lucro"]) / 100)
        ct_cheio = (p["mp"] + rk_cheio) / ((100 - perc) / 100)
        pv_cheio = (p["mp"] + rk_cheio) / ((100 - perc - d["lucro"]) / 100)
        P.append(dict(p, parc=parc, rkw=rk, rkw_cheio=rk_cheio, ct=r2(ct), pv=r2(pv),
                      ct_cheio=ct_cheio, pv_cheio=pv_cheio, perc=perc))
    return dict(prod=prod, prim=prim, linhas=linhas, sec=sec, total=total, mins=mins,
                taxa=taxa, taxa_cheia=taxa_cheia, P=P)
