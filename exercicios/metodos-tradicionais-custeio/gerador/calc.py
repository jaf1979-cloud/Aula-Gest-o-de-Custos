"""Motor de cálculo dos 5 exercícios (fórmulas do PPTX 'Método Custeio por Absorção').

Notação do PPTX (percentuais sobre a receita, em %):
  CVP  = CVP total % - MP %   (a matéria-prima entra pela ficha técnica, em R$)
  CVV  = custo variável de vendas %
  CF   = custo fixo %  (só no custeio marginal / absorção plena)
  Marginal : CUSTO = MP / [(100-(CVV+CVP+CF))/100]      PRECO = MP / [(100-(CVV+CVP+CF+L))/100]
  Integral : CFu = CF R$ / soma produzidos ; CUSTO = (MP+CFu) / [(100-(CVV+CVP))/100] ; PRECO idem + L
  Ideal    : CFu = CF R$ / soma vendidos   ; mesmas fórmulas da integral
Pontos de equilíbrio (critério usual, não está no PPTX):
  PEc = CF / MC%   PEf = (CF - Depreciação) / MC%   PEe = (CF + Ativo x taxa) / MC%
"""
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN


def r2(x):
    return Decimal(repr(float(x))).quantize(Decimal("0.01"), ROUND_HALF_UP)


def t2(x):
    return Decimal(repr(float(x))).quantize(Decimal("0.01"), ROUND_DOWN)


def dre_pct(receita, cvp, cvv, cf, mp):
    p = lambda v: v / receita * 100
    return dict(cvp_tot=p(cvp), cvp=p(cvp) - p(mp), mp=p(mp), cvv=p(cvv), cf=p(cf),
                mc=p(receita - cvp - cvv), lo=p(receita - cvp - cvv - cf))


def marginal(mp, d, L):
    soma_c = d["cvv"] + d["cvp"] + d["cf"]
    div_c = (100 - soma_c) / 100
    div_p = (100 - soma_c - L) / 100
    return dict(soma_c=soma_c, div_c=div_c, div_p=div_p, custo=r2(mp / div_c), preco=r2(mp / div_p),
                custo_raw=mp / div_c, preco_raw=mp / div_p)


def absorcao(mp, cfu, d, L):
    soma_c = d["cvv"] + d["cvp"]
    div_c = (100 - soma_c) / 100
    div_p = (100 - soma_c - L) / 100
    base = mp + cfu
    return dict(soma_c=soma_c, div_c=div_c, div_p=div_p, base=base, custo=r2(base / div_c),
                preco=r2(base / div_p), custo_raw=base / div_c, preco_raw=base / div_p)


def pe(cf, mc_pct, dep=0.0, opp=0.0):
    m = mc_pct / 100
    return dict(pec=r2(cf / m), pef=r2((cf - dep) / m), pee=r2((cf + opp) / m))


# ---------- Validação com o exemplo do roupeiro (slides 15 a 20) ----------
_d = dict(cvp=10, cvv=20, cf=18)
assert t2(marginal(70, _d, 0)["custo_raw"]) == Decimal("134.61")
assert t2(marginal(70, _d, 10)["preco_raw"]) == Decimal("166.66")
assert t2(absorcao(70, 18000 / 2000, _d, 0)["custo_raw"]) == Decimal("112.85")
assert t2(absorcao(70, 18000 / 2000, _d, 10)["preco_raw"]) == Decimal("131.66")
assert t2(absorcao(70, 18000 / 1000, _d, 0)["custo_raw"]) == Decimal("125.71")
assert t2(absorcao(70, 18000 / 1000, _d, 10)["preco_raw"]) == Decimal("146.66")
