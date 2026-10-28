# Gerador dos exercícios de custeio pela margem de contribuição

- `calc.py`: fórmulas do PPTX "Método Contemporâneo Margem Contribuição", validadas contra a tabela dos slides (itens A, B e C).
- `dados.py`: gastos e produtos dos 5 exercícios (troque valores aqui para criar novas versões).
- `gen.py`: enunciado, resolução passo a passo, gabarito e respostas.
- `page.py`: página HTML → `python3 page.py ../margem-de-contribuicao-na-pratica.html`
- `moodle.py`: XML Moodle (Cloze) → `python3 moodle.py ../custeio-margem-contribuicao-moodle-cloze.xml`

Tolerâncias do Moodle no dicionário `TOL` de `moodle.py` (R$ totais 0,01; MC% 0,02; CF unit 0,05; custo e PV 0,10).
Ao mudar `dados.py`, o gerador confere sozinho se quantidade × preço soma a receita e se a MP das fichas soma a MP do DRE.
- `planilha.py`: preenche o modelo do professor (`planilha_modelo.xlsx`), uma aba por exercício, com fórmulas → `python3 planilha.py ../Planilha_MC_resolvida.xlsx` (depois abra no Excel para recalcular).
