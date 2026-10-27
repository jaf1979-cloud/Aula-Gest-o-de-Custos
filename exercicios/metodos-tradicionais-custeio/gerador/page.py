import sys
from gen import *
from gen import GAB

OUT = sys.argv[1]
EX = build()

# ---------------- página ----------------
CSS = open(__file__.replace("page.py", "page.css")).read()
parts = []
parts.append("""<title>Custeio na Prática</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>""" + CSS + "</style>")
parts.append("""<header class="top"><div class="wrap">
<p class="eyebrow">Gestão de Custos · UTFPR · Métodos tradicionais de custeio</p>
<h1>Custeio na Prática</h1>
<p class="lede">Cinco exercícios resolvidos passo a passo, em cinco indústrias diferentes: classificação de custos, DRE analítico,
pontos de equilíbrio, custeio marginal, absorção integral e absorção ideal.</p>
<nav class="toc">""" + "".join(f'<a href="#ex{e["n"]}"><b>{e["n"]}</b><span>{e["ind"]}</span><i>{e["tit"]}</i></a>' for e in EX) +
             '<a href="#gabarito" class="gab"><b>G</b><span>Gabarito</span><i>Respostas resumidas</i></a></nav></div></header>')

parts.append("""<main class="wrap">
<section class="formulas" id="formulas">
<h2>Fórmulas utilizadas</h2>
<div class="fgrid">
<div class="fcard"><span class="mth mar">Custeio marginal (absorção plena)</span>
<div class="eq"><span class="lhs">CUSTO</span> = """ + fr("MP", fr("100 − (CVV + CVP + CF)", "100")) + """</div>
<div class="eq"><span class="lhs">PREÇO</span> = """ + fr("MP", fr("100 − (CVV + CVP + CF + L)", "100")) + """</div>
<p>CF entra como % da receita.</p></div>
<div class="fcard"><span class="mth int">Absorção integral</span>
<div class="eq"><span class="lhs">CF unit.</span> = """ + fr("CF total", "Σ itens produzidos") + """</div>
<div class="eq"><span class="lhs">CUSTO</span> = """ + fr("MP + CF unit.", fr("100 − (CVV + CVP)", "100")) + """</div>
<div class="eq"><span class="lhs">PREÇO</span> = """ + fr("MP + CF unit.", fr("100 − (CVV + CVP + L)", "100")) + """</div></div>
<div class="fcard"><span class="mth ide">Absorção ideal</span>
<div class="eq"><span class="lhs">CF unit.</span> = """ + fr("CF total", "Σ itens vendidos") + """</div>
<p>Custo e preço com as mesmas fórmulas da absorção integral.</p></div>
<div class="fcard"><span class="mth pe">Pontos de equilíbrio</span>
<div class="eq"><span class="lhs">PE<sub>c</sub></span> = """ + fr("CF", "MC%") + """</div>
<div class="eq"><span class="lhs">PE<sub>f</sub></span> = """ + fr("CF − Depreciação", "MC%") + """</div>
<div class="eq"><span class="lhs">PE<sub>e</sub></span> = """ + fr("CF + Ativo × taxa", "MC%") + """</div></div>
</div>
<div class="premissas"><h3>Premissas adotadas</h3><ul>
<li><b>CVP na fórmula = CVP total % − MP %.</b> A matéria-prima entra em R$ pela ficha técnica, como no exemplo do roupeiro (CVP 50% − MP 40% = 10%).</li>
<li>CVV, CVP, CF e L são percentuais sobre a receita do DRE. MC% = 100% − CVP total% − CVV%.</li>
<li>O CF unitário é calculado pela simples contagem de itens (produzidos ou vendidos), como nos slides, e arredondado a 2 casas antes de entrar na fórmula.</li>
<li>Resultados arredondados a 2 casas (0,005 para cima). Os slides truncam: 70,00 ÷ 0,52 = 134,615… aparece como 134,61 nos slides e 134,62 aqui. A diferença nunca passa de R$&nbsp;0,01.</li>
<li>As fórmulas de ponto de equilíbrio não estão nos slides de custeio. Usamos o critério usual da disciplina: o financeiro retira a depreciação e o econômico soma o custo de oportunidade do capital.</li>
<li>Salários de mensalistas, inclusive os da fábrica, são tratados como custo fixo, como no DRE analítico dos slides.</li>
</ul></div>
<button type="button" id="tg" class="tg" aria-pressed="false">Ocultar resoluções (modo aula)</button>
</section>""")

for e in EX:
    parts.append(f"""<section class="ex" id="ex{e['n']}">
<div class="exhead"><span class="exn">Exercício {e['n']}</span><span class="ind">{e['ind']} · {e['empresa']}</span>
<h2>{e['tit']}</h2><div class="tags">{''.join(f'<span>{t}</span>' for t in e['tags'])}</div></div>
<div class="enun"><h3>Enunciado</h3>{e['enun']}</div>
<details class="sol" open><summary>Resolução passo a passo</summary><div class="solb">{e['sol']}</div></details>
</section>""")

rows = "".join(f'<tr><td class="c">{a}</td><td class="l">{b}</td><td class="r">{c}</td></tr>' for a, b, c in GAB)
parts.append(f"""<section class="ex" id="gabarito"><div class="exhead"><span class="exn">Gabarito</span><h2>Respostas resumidas</h2></div>
<div class="tw"><table class="data gabt"><thead><tr><th>Ex.</th><th>Item</th><th>Resposta</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="muted">Valores arredondados a 2 casas. Diferenças de R$&nbsp;0,01 em relação a quem trunca os resultados (como nos slides) são esperadas.</p></section>
</main>
<footer class="wrap foot">Prof. José Ângelo Ferreira · Gestão de Custos · UTFPR. Empresas e números fictícios, criados para fins didáticos.</footer>
<script>
(function(){{var b=document.getElementById('tg');b.addEventListener('click',function(){{var on=b.getAttribute('aria-pressed')!=='true';
document.querySelectorAll('details.sol').forEach(function(d){{d.open=!on;}});b.setAttribute('aria-pressed',on);
b.textContent=on?'Mostrar resoluções':'Ocultar resoluções (modo aula)';}});}})();
</script>""")

open(OUT, "w").write("\n".join(parts))
print("ok", len(GAB), "respostas")
for g in GAB:
    print(" | ".join(g).replace("&nbsp;", " "))
