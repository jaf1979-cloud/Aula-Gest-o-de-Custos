# Gerador dos exercícios comparativos (absorção integral, absorção ideal e margem de contribuição)

- `dados.py`: gastos e produtos dos 3 exercícios. Receita = Σ vendidos × preço praticado; MP do DRE = Σ vendidos × MP.
- `gen.py`: enunciado, resolução passo a passo, gabarito e respostas. `helpers.py` e `calc.py` vêm do gerador de margem de contribuição.
- `page.py` → `python3 page.py ../tres-metodos-um-cenario.html`
- `moodle.py` → `python3 moodle.py ../tres-metodos-moodle-cloze.xml`
- `confere_modelo_karina.py`: confere o exemplo da Indústria de Bolsas Karina com as mesmas fórmulas.

Tolerâncias em `TOL` (`moodle.py`); custos e preços aceitam no mínimo 0,05% do valor, para absorver o arredondamento da MC total % em valores grandes.
- `docx_enunciados.js`: Word com os enunciados → exporte os dados para JSON e rode `node docx_enunciados.js dados.json ../enunciados-tres-metodos.docx`.
- `planilha_prova.py` + `injeta_cache.py`: preenchem o modelo `planilha_prova_modelo.xlsx` (PLANILHA PROVA MC - Absorção) com fórmulas, 2 abas por exercício (MC e Absorção integral/ideal), editando o XML para manter logos e rótulos. Fluxo: `python3 planilha_prova.py planilha_prova_modelo.xlsx sem_cache.xlsx`, recalcular uma cópia no LibreOffice (recalc.py da skill xlsx) e `python3 injeta_cache.py sem_cache.xlsx recalculada.xlsx ../PLANILHA_PROVA_MC_Absorcao_resolvida.xlsx`.
