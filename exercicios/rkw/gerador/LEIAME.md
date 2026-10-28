# Gerador dos exercícios de custeio RKW

- `calc.py`: método dos slides (1º rateio pelos direcionadores, 2º rateio dos centros de apoio pelo nº de funcionários, em degraus quando há dois centros de apoio; custo/min = custo do centro ÷ (horas × 60 × funcionários), arredondado em 2 casas; CT = (MP + RKW) ÷ [(100 − (CVV + CVP)) ÷ 100]; PV com L no divisor).
- `dados.py`: dados dos 5 exercícios. `gen.py`: enunciado, resolução e interpretação (blocos).
- `docx_gen.py` → `python3 docx_gen.py ../rkw-exercicios-enunciados.docx ../rkw-exercicios-resolucao.docx`
- `moodle.py` → `python3 moodle.py ../rkw-moodle-cloze.xml` (tolerâncias aceitam também o custo/min sem arredondar).
- `confere_modelo.py`: confere o exemplo da empresa DR dos slides e o exercício Churrasqueiras & Grelhas Premium.

## O que a conferência mostrou (out/2026)
- Slides (empresa DR): a linha TOTAL do 1º rateio soma 36.660,39 e 24.918,70, mas o certo é 36.610,39 e 24.898,70 (soma 71.070 ≠ 71.000). Os totais 42.196,75 e 28.873,25 herdam o erro (certo: 42.146,75 e 28.853,25); o custo/min arredondado (0,10 e 0,096) não muda. PV P1 = 150,40 (slide: 150,04); CT P2 = 84,51 (slide: 84,61).
- Churrasqueiras (planilha): energia rateada por 320/600/1200 (são os m²), não pela potência 70/620/1000. O 2º rateio (6.448,12 / 12.896,24) usa 3 e 6 funcionários, mas o custo/min usa 18 e 55. Custo/min com 176 h e 3 casas (0,265 / 0,169).
- Churrasqueiras (Cloze): as respostas de RKW (5,94 e 7,39) saem exatamente de custo/min 0,23 e 0,15, que é o que dá com 200 h/mês e 2 casas. Grelha 2: (66,00 + 7,39) ÷ 0,75 = 97,85; a chave está 67,85 (provável erro de digitação, fora da tolerância de 2).

- `xlsx_gen.py` → `python3 xlsx_gen.py "Matriz RKW.xlsx" ../rkw-exercicios-resolucao.xlsx`: preenche o modelo de planilha do professor, uma aba por exercício, tudo com fórmulas (dados de entrada em tabelas próprias; custo/min com ARRED de 2 casas).
