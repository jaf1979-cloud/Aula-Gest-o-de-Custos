import sys
from gen import build, GAB, fr

OUT = sys.argv[1]
EX = build()

CSS = open(__file__.replace("page.py", "page.css")).read() + """
ul.seta{list-style:none;padding-left:0;columns:2 300px;column-gap:28px;margin:10px 0}
ul.seta li{padding:2px 0 2px 1.6em;position:relative;break-inside:avoid}
ul.seta li::before{content:"➔";position:absolute;left:0;color:var(--teal)}
ul.seta li b{font-variant-numeric:tabular-nums}
table.wide{font-size:13.5px} table.wide th{font-size:12.5px;padding:6px 7px} table.wide td{padding:5px 7px}
tfoot td{border-top:2px solid var(--line);background:var(--soft)}
.fcard .eq{font-size:15px}
"""
P = []
P.append("""<title>Margem de Contribuição na Prática</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>""" + CSS + "</style>")
P.append("""<header class="top"><div class="wrap">
<p class="eyebrow">Gestão de Custos · UTFPR · Método contemporâneo de custeio</p>
<h1>Margem de Contribuição na Prática</h1>
<p class="lede">Cinco exercícios resolvidos passo a passo, em cinco indústrias: estrutura de resultados, margem de contribuição
unitária e total, rateio do custo fixo pela participação na margem, custo total e preço de venda.</p>
<nav class="toc">""" + "".join(f'<a href="#ex{e["n"]}"><b>{e["n"]}</b><span>{e["ind"]}</span><i>{e["tit"]}</i></a>' for e in EX) +
         '<a href="#gabarito"><b>G</b><span>Gabarito</span><i>Respostas resumidas</i></a></nav></div></header>')

P.append("""<main class="wrap">
<section class="formulas" id="formulas">
<h2>Fórmulas utilizadas</h2>
<div class="fgrid">
<div class="fcard"><span class="mth ide">Custos variáveis do item</span>
<div class="eq"><span class="lhs">CVP $</span> = PV × CVP%</div>
<div class="eq"><span class="lhs">CVV $</span> = PV × CVV%</div>
<div class="eq"><span class="lhs">CVT $</span> = CVP + CVV + MP</div>
<p>CVP% = CVP total% − MP% (DRE).</p></div>
<div class="fcard"><span class="mth pe">Margem de contribuição</span>
<div class="eq"><span class="lhs">MC unit $</span> = PV − CVT</div>
<div class="eq"><span class="lhs">MC unit %</span> = """ + fr("MC unit $", "PV") + """ × 100</div>
<div class="eq"><span class="lhs">MC total $</span> = MC unit $ × quant.</div>
<div class="eq"><span class="lhs">MC total %</span> = """ + fr("MC total item $", "Σ MC total itens") + """ × 100</div></div>
<div class="fcard"><span class="mth mar">Custo fixo unitário</span>
<div class="eq"><span class="lhs">CF unit</span> = """ + fr("CF total × MC total item %", "quantidade item") + """</div>
<p>Cada produto absorve o custo fixo na proporção da margem que gera.</p></div>
<div class="fcard"><span class="mth int">Custo e preço</span>
<div class="eq"><span class="lhs">CUSTO</span> = """ + fr("MP + CF unit", fr("100 − (CVV + CVP)", "100")) + """</div>
<div class="eq"><span class="lhs">PV</span> = """ + fr("MP + CF unit", fr("100 − (CVV + CVP + L)", "100")) + """</div></div>
</div>
<div class="premissas"><h3>Premissas adotadas</h3><ul>
<li><b>CVP na fórmula = CVP total % − MP %.</b> A matéria-prima entra em R$ pela ficha técnica de cada produto.</li>
<li>Mão de obra direta paga a mensalistas é custo fixo; o prêmio de produtividade, a energia das máquinas, os gastos gerais de fabricação variáveis
e o frete sobre compras são CVP. Esse é o mesmo critério do modelo de exercício da disciplina.</li>
<li>Nas tabelas de produtos, quantidade × preço atual soma a receita do mês e quantidade × MP soma a matéria-prima do DRE.
Por isso a soma das margens totais dos produtos fecha com a MC da Estrutura de Resultados.</li>
<li>Os cálculos seguem com todas as casas, como a planilha dos slides (custo do item A = 84,08; PV = 101,48). Os valores exibidos estão arredondados a 2 casas.</li>
</ul></div>
<button type="button" id="tg" class="tg" aria-pressed="false">Ocultar resoluções (modo aula)</button>
</section>""")

for e in EX:
    P.append(f"""<section class="ex" id="ex{e['n']}">
<div class="exhead"><span class="exn">Exercício {e['n']}</span><span class="ind">{e['ind']} · {e['empresa']}</span>
<h2>{e['tit']}</h2><div class="tags">{''.join(f'<span>{t}</span>' for t in e['tags'])}</div></div>
<div class="enun"><h3>Enunciado</h3>{e['enun']}</div>
<details class="sol" open><summary>Resolução passo a passo</summary><div class="solb">{e['sol']}</div></details>
</section>""")

rows = "".join(f'<tr><td class="c">{a}</td><td class="l">{b}</td><td class="r">{c}</td></tr>' for a, b, c in GAB)
P.append(f"""<section class="ex" id="gabarito"><div class="exhead"><span class="exn">Gabarito</span><h2>Respostas resumidas</h2></div>
<div class="tw"><table class="data gabt"><thead><tr><th>Ex.</th><th>Item</th><th>Resposta</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="muted">Valores arredondados a 2 casas. Quem arredonda os passos intermediários pode encontrar diferenças de R$&nbsp;0,01.</p></section>
</main>
<footer class="wrap foot">Prof. José Ângelo Ferreira · Gestão de Custos · UTFPR. Empresas e números fictícios, criados para fins didáticos.</footer>
<script>
(function(){{var b=document.getElementById('tg');b.addEventListener('click',function(){{var on=b.getAttribute('aria-pressed')!=='true';
document.querySelectorAll('details.sol').forEach(function(d){{d.open=!on;}});b.setAttribute('aria-pressed',on);
b.textContent=on?'Mostrar resoluções':'Ocultar resoluções (modo aula)';}});}})();
</script>""")

open(OUT, "w").write("\n".join(P))
print("ok", len(GAB), "linhas de gabarito")
