# Gerador dos exercícios de custeio tradicional

- `calc.py`: fórmulas do PPTX (marginal, absorção integral e ideal, pontos de equilíbrio), validadas contra o exemplo do roupeiro dos slides.
- `gen.py`: dados e resolução dos 5 exercícios.
- `page.py`: gera a página HTML → `python3 page.py ../custeio-na-pratica.html`
- `moodle.py`: gera o XML Moodle (Cloze) → `python3 moodle.py ../custeio-tradicional-moodle-cloze.xml`

Para mudar a tolerância das respostas no Moodle, edite `TOL_R` (R$) e `TOL_P` (%) no topo de `moodle.py`.
- `excel.py`: gera a planilha de resolução com fórmulas → `python3 excel.py ../Planilha_Resolucao_Custeio_na_Pratica.xlsx` (depois recalcular no Excel/LibreOffice)
