"""Confere o método com (1) o exemplo da empresa DR dos slides e (2) o exercício Churrasqueiras & Grelhas Premium."""
from calc import rkw, r2

# (1) Slides – empresa DR
dr = dict(centros=["ADM", "Usinagem", "Frezagem"], apoio=["ADM"], horas=200, lucro=10,
          salario_de={"Sal ADM": "ADM", "Sal Usi": "Usinagem", "Sal Fre": "Frezagem"},
          itens=[("Sal ADM", 8000, "Direto"), ("Sal Usi", 25000, "Direto"), ("Sal Fre", 18000, "Direto"),
                 ("Energia", 6000, "Potência"), ("Seguro", 5000, "Área"), ("Mat aux", 9000, "Requisições")],
          drivers={"Funcionários": {"ADM": 10, "Usinagem": 35, "Frezagem": 25},
                   "Potência": {"ADM": 200, "Usinagem": 400, "Frezagem": 500},
                   "Área": {"ADM": 800, "Usinagem": 6000, "Frezagem": 3200},
                   "Requisições": {"ADM": 0, "Usinagem": 50, "Frezagem": 20}},
          produtos=[dict(nome="P1", t={"Usinagem": 54, "Frezagem": 30}, mp=97, cvv=15, cvp=5),
                    dict(nome="P2", t={"Usinagem": 27, "Frezagem": 72}, mp=58, cvv=15, cvp=5)])
R = rkw(dr)
print("DR primária", {k: r2(v) for k, v in R["prim"].items()}, "(slide: 9.490,91 / 36.660,39 / 24.918,70)")
print("DR totais", {k: r2(v) for k, v in R["total"].items()}, "(slide: 42.196,75 / 28.873,25)")
print("DR taxa cheia", R["taxa_cheia"], "(slide: 0,10 / 0,096)")
for p in R["P"]:
    rk = sum(p["t"][c] * {"Usinagem": 0.10, "Frezagem": 0.096}[c] for c in p["t"])
    print(p["nome"], "RKW slide", round(rk, 2), "CT", r2((p["mp"] + round(rk, 2)) / 0.8), "PV", r2((p["mp"] + round(rk, 2)) / 0.7))

# (2) Churrasqueiras – planilha (energia pelo m², 2º rateio 3:6, minutos com 18 e 55 func., 176 h, taxa 3 casas)
adm, cor, est = 19344.36, 43922.80, 85012.84
print("\nChurrasqueiras – 2º rateio 3:6 →", r2(adm * 3 / 9), r2(adm * 6 / 9), "| por 18:55 →", r2(adm * 18 / 73), r2(adm * 55 / 73))
tc, te = 50370.92, 97909.08
for h in (176, 200):
    a, b = tc / (h * 60 * 18), te / (h * 60 * 55)
    print(f"{h} h: taxa corte {a:.4f} estamparia {b:.4f}")
for nome, tt, mp in (("Grelha 1", (18, 12), 62), ("Grelha 2", (23, 14), 66)):
    pl = tt[0] * 0.265 + tt[1] * 0.169
    cz = tt[0] * 0.23 + tt[1] * 0.15
    print(nome, f"planilha RKW {pl:.2f} CT {(mp + pl) / 0.75:.2f} | cloze (0,23/0,15) RKW {cz:.2f} CT {(mp + cz) / 0.75:.2f}")
# energia pelo direcionador correto (potência 70/620/1000)
print("Energia por potência:", [r2(14000 * k / 1690) for k in (70, 620, 1000)], "| planilha usou 320/600/1200:", [r2(14000 * k / 2120) for k in (320, 600, 1200)])
