"""Motor de cálculo do custeio pela margem de contribuição (método contemporâneo).

Fórmulas do PPTX "Método Contemporâneo Margem Contribuição" (percentuais sobre a receita do DRE):
  CVP %  = CVP total % - MP %        (a MP entra em R$ pela ficha técnica)
  CVP $  = PV x CVP %                 CVV $ = PV x CVV %
  CVT $  = CVP $ + CVV $ + MP
  MC unit $ = PV - CVT                MC unit % = MC unit $ / PV x 100
  MC total $ = MC unit $ x quantidade
  MC total % = MC total item $ / soma MC total itens x 100
  CF unit = CF total x MC total % / quantidade
  CUSTO = (MP + CF unit) / [(100 - (CVV + CVP)) / 100]
  PV    = (MP + CF unit) / [(100 - (CVV + CVP + L)) / 100]
Cada resultado intermediário é arredondado a 2 casas antes de seguir, como o aluno faz na calculadora.
"""
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN


def r2(x):
    return float(Decimal(repr(float(x))).quantize(Decimal("0.01"), ROUND_HALF_UP))


def t2(x):
    return float(Decimal(repr(float(x))).quantize(Decimal("0.01"), ROUND_DOWN))


def tabela(prods, cvp_pct, cvv_pct, cf):
    """prods: lista de dicts com nome, q, pv, mp, L. Devolve linhas com todos os passos.
    O cálculo usa precisão total (como a planilha dos slides); a exibição arredonda a 2 casas."""
    rows = []
    for p in prods:
        r = dict(p)
        r["cvp"] = p["pv"] * cvp_pct / 100
        r["cvv"] = p["pv"] * cvv_pct / 100
        r["cvt"] = r["cvp"] + r["cvv"] + p["mp"]
        r["mcu"] = p["pv"] - r["cvt"]
        r["mcu_pct"] = r["mcu"] / p["pv"] * 100
        r["mct"] = r["mcu"] * p["q"]
        rows.append(r)
    soma = sum(r["mct"] for r in rows)
    div_c = (100 - (cvv_pct + cvp_pct)) / 100
    for r in rows:
        r["share"] = r["mct"] / soma * 100
        r["cfu"] = cf * r["share"] / 100 / r["q"]
        r["base"] = r["mp"] + r["cfu"]
        r["div_c"] = div_c
        r["div_p"] = (100 - (cvv_pct + cvp_pct + r["L"])) / 100
        r["ct"] = r["base"] / div_c
        r["pvn"] = r["base"] / r["div_p"]
    return rows, soma


# ---------- Validação com o exemplo dos slides (itens A, B, C; CF = 18.000; CVP 10%; CVV 20%) ----------
_p = [dict(nome="A", q=1000, pv=100.0, mp=55.0, L=12), dict(nome="B", q=2500, pv=80.0, mp=40.0, L=25),
      dict(nome="C", q=1200, pv=45.0, mp=19.0, L=10)]
_r, _s = tabela(_p, 10, 20, 18000)
assert r2(_s) == 70000.0
assert [r2(x["share"]) for x in _r] == [21.43, 57.14, 21.43]
assert [r2(x["cfu"]) for x in _r] == [3.86, 4.11, 3.21]
assert [r2(x["ct"]) for x in _r] == [84.08, 63.02, 31.73]
assert [r2(x["pvn"]) for x in _r] == [101.48, 98.03, 37.02]
assert [r2(x["mcu_pct"]) for x in _r] == [15.0, 20.0, 27.78]
