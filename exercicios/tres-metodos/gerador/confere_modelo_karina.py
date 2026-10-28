"""Confere o exemplo da Indústria de Bolsas Karina com as fórmulas usadas no gerador."""
from calc import r2, tabela

R, CVV, CVP, MP, CF = 953300, 260000, 489400, 380000, 154780
assert R - CVV - CVP - CF == 49120
cvp, cvv = (CVP - MP) / R * 100, CVV / R * 100
dc = (100 - cvp - cvv) / 100
for nome, mp, L, ct_int, pv_int, ct_ide, pv_ide in [("Eleganza", 210.90, 16, 454.19, 614.79, 488.72, 661.53),
                                                    ("City", 86.00, 22, 250.28, 390.56, 284.81, 444.44)]:
    dp = (100 - cvp - cvv - L) / 100
    for cfu, ct, pv in ((CF / 2300, ct_int, pv_int), (CF / 1750, ct_ide, pv_ide)):
        assert (r2((mp + cfu) / dc), r2((mp + cfu) / dp)) == (ct, pv)
# Bloco da margem de contribuição: só bate com a City a 138,29 (no bloco da absorção ela custa 86,00)
rows, _ = tabela([dict(nome="E", q=800, pv=690.0, mp=210.90, L=16), dict(nome="C", q=950, pv=525.0, mp=138.29, L=22)], cvp, cvv, CF)
assert [(r2(r["ct"]), r2(r["pvn"])) for r in rows] == [(500.09, 676.91), (360.61, 562.73)]
rows, _ = tabela([dict(nome="E", q=800, pv=690.0, mp=210.90, L=16), dict(nome="C", q=950, pv=525.0, mp=86.0, L=22)], cvp, cvv, CF)
print("Com a City a 86,00 na MC:", [(r2(r["ct"]), r2(r["pvn"])) for r in rows])
print("Receita a preços praticados:", 800 * 690 + 950 * 525, "x faturamento", R)
