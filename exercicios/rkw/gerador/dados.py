"""Dados dos 5 exercícios de custeio RKW (indústria). Horas = horas trabalhadas por funcionário no mês."""


def sal(*pares):
    return {f"Salários {c}": c for c in pares}


def ex(n, empresa, setor, tit, contexto, centros, apoio, horas, lucro, salarios, outros, drivers, produtos, unidade="unidade"):
    itens = [(f"Salários {c}", v, "Direto") for c, v in salarios] + outros
    return dict(n=n, empresa=empresa, setor=setor, tit=tit, contexto=contexto, centros=centros, apoio=apoio,
                horas=horas, lucro=lucro, itens=itens, salario_de=sal(*[c for c, _ in salarios]),
                drivers=drivers, produtos=produtos, unidade=unidade)


EXS = [
    ex(1, "Cutelaria Lâmina Gaúcha Ltda.", "Cutelaria artesanal", "Facas forjadas",
       ["A <b>Cutelaria Lâmina Gaúcha</b> é uma empresa familiar da Serra Gaúcha que fabrica facas forjadas à mão "
        "em aço carbono, muito procuradas por churrasqueiros e chefs de cozinha. A linha principal tem dois modelos: "
        "a <b>Faca do Chef 8\"</b> e a <b>Faca Campeira 10\"</b>.",
        "Nos últimos meses o preço do aço subiu e a família percebeu que não sabe quanto custa, de fato, cada faca. "
        "Até hoje o preço era definido \"olhando a concorrência\". Para saber quanto custa cada modelo, sobretudo a Campeira, "
        "que exige mais tempo de forja, a empresa decidiu aplicar o <b>Método RKW</b>, dividindo a fábrica em três "
        "centros de custos: Administração (apoio), Forjamento e Afiação (produtivos)."],
       ["Administração", "Forjamento", "Afiação"], ["Administração"], 176, 15,
       [("Administração", 18000), ("Forjamento", 42000), ("Afiação", 30000)],
       [("Aluguel", 12000, "Área"), ("Seguro do imóvel", 4800, "Área"), ("Energia elétrica", 16500, "Potência"),
        ("Material auxiliar", 6300, "Requisições"), ("Manutenção de equipamentos", 9600, "Ordens")],
       {"Funcionários": {"Administração": 6, "Forjamento": 8, "Afiação": 6},
        "Área": {"Administração": 150, "Forjamento": 500, "Afiação": 350},
        "Potência": {"Administração": 20, "Forjamento": 180, "Afiação": 100},
        "Requisições": {"Administração": 4, "Forjamento": 30, "Afiação": 16},
        "Ordens": {"Administração": 0, "Forjamento": 12, "Afiação": 8}},
       [dict(nome="Faca do Chef 8\"", t={"Forjamento": 25, "Afiação": 18}, mp=48.00, cvv=12, cvp=6),
        dict(nome="Faca Campeira 10\"", t={"Forjamento": 32, "Afiação": 22}, mp=61.50, cvv=12, cvp=6)]),

    ex(2, "Fundição Ferro Forte S.A.", "Fundição", "Panelas de ferro fundido",
       ["A <b>Fundição Ferro Forte</b>, de Minas Gerais, produz utensílios de ferro fundido para cozinha: "
        "<b>panela 3 L</b>, <b>frigideira 26 cm</b> e <b>chapa bifeteira</b>. Os produtos passam por três seções "
        "produtivas: Moldagem (preparação dos moldes de areia), Fusão e Vazamento (forno de indução) e Acabamento "
        "(rebarbação, jateamento e cura com óleo vegetal).",
        "O forno de indução consome muita energia e a diretoria suspeita que a chapa bifeteira, que fica mais tempo "
        "na fusão, \"carrega\" os custos dos outros itens. Para verificar, o controller montou a <b>Matriz RKW</b> "
        "com os gastos do mês de agosto."],
       ["Administração", "Moldagem", "Fusão", "Acabamento"], ["Administração"], 176, 12,
       [("Administração", 22000), ("Moldagem", 36000), ("Fusão", 48000), ("Acabamento", 27000)],
       [("Energia elétrica", 38000, "Potência"), ("Aluguel", 18000, "Área"), ("Seguro do imóvel", 6000, "Área"),
        ("Material auxiliar", 9000, "Requisições"), ("Manutenção de equipamentos", 14000, "Ordens")],
       {"Funcionários": {"Administração": 8, "Moldagem": 9, "Fusão": 10, "Acabamento": 7},
        "Área": {"Administração": 200, "Moldagem": 600, "Fusão": 800, "Acabamento": 400},
        "Potência": {"Administração": 25, "Moldagem": 120, "Fusão": 600, "Acabamento": 80},
        "Requisições": {"Administração": 6, "Moldagem": 40, "Fusão": 25, "Acabamento": 29},
        "Ordens": {"Administração": 0, "Moldagem": 10, "Fusão": 22, "Acabamento": 8}},
       [dict(nome="Panela 3 L", t={"Moldagem": 14, "Fusão": 9, "Acabamento": 12}, mp=38.00, cvv=14, cvp=5),
        dict(nome="Frigideira 26 cm", t={"Moldagem": 10, "Fusão": 6, "Acabamento": 15}, mp=27.50, cvv=14, cvp=5),
        dict(nome="Chapa bifeteira", t={"Moldagem": 18, "Fusão": 12, "Acabamento": 8}, mp=52.00, cvv=14, cvp=5)]),

    ex(3, "Marcenaria Industrial Serra Azul Ltda.", "Moveleira", "Módulos de cozinha planejada",
       ["A <b>Marcenaria Industrial Serra Azul</b>, do polo moveleiro de Arapongas (PR), fabrica módulos de cozinha em "
        "MDF vendidos para lojas de móveis planejados: <b>armário aéreo</b>, <b>gaveteiro</b> e <b>balcão de pia</b>.",
        "A fábrica tem três seções produtivas: Corte CNC, Montagem e Pintura (laca PU). A Montagem é a seção com mais "
        "gente, enquanto o Corte CNC é a mais automatizada. O gerente comercial quer renegociar os preços com as lojas "
        "e pediu o custo de cada módulo e o preço de venda que garanta lucro de 10%. A jornada é de 168 horas por mês."],
       ["Administração", "Corte CNC", "Montagem", "Pintura"], ["Administração"], 168, 10,
       [("Administração", 26000), ("Corte CNC", 34000), ("Montagem", 52000), ("Pintura", 31000)],
       [("Aluguel", 24000, "Área"), ("Seguro do imóvel", 7500, "Área"), ("Energia elétrica", 21000, "Potência"),
        ("Material auxiliar", 12400, "Requisições"), ("Manutenção de equipamentos", 10800, "Ordens")],
       {"Funcionários": {"Administração": 9, "Corte CNC": 6, "Montagem": 14, "Pintura": 7},
        "Área": {"Administração": 250, "Corte CNC": 700, "Montagem": 900, "Pintura": 650},
        "Potência": {"Administração": 30, "Corte CNC": 350, "Montagem": 90, "Pintura": 160},
        "Requisições": {"Administração": 8, "Corte CNC": 36, "Montagem": 62, "Pintura": 44},
        "Ordens": {"Administração": 0, "Corte CNC": 18, "Montagem": 6, "Pintura": 12}},
       [dict(nome="Armário aéreo", t={"Corte CNC": 22, "Montagem": 45, "Pintura": 30}, mp=185.00, cvv=15, cvp=6),
        dict(nome="Gaveteiro", t={"Corte CNC": 18, "Montagem": 38, "Pintura": 25}, mp=142.00, cvv=15, cvp=6),
        dict(nome="Balcão de pia", t={"Corte CNC": 35, "Montagem": 70, "Pintura": 48}, mp=398.00, cvv=15, cvp=6)]),

    ex(4, "Implementos Campo Forte Ltda.", "Metalmecânica", "Peças para implementos agrícolas",
       ["A <b>Implementos Campo Forte</b>, de Cascavel (PR), fabrica peças de reposição para implementos agrícolas: "
        "<b>lâmina de plaina</b>, <b>engate rápido</b> e <b>suporte de disco</b>. A produção passa por Corte e Dobra, "
        "Soldagem e Pintura.",
        "Diferente dos casos anteriores, a empresa tem <b>dois centros de apoio</b>: a Administração e a Manutenção "
        "interna. Na distribuição secundária, a Administração é distribuída primeiro, pelo nº de funcionários, para a "
        "Manutenção e para os centros produtivos; em seguida, a Manutenção (já com a parcela recebida da "
        "Administração) é distribuída para os centros produtivos, também pelo nº de funcionários."],
       ["Administração", "Manutenção", "Corte e Dobra", "Soldagem", "Pintura"], ["Administração", "Manutenção"], 176, 15,
       [("Administração", 24000), ("Manutenção", 15000), ("Corte e Dobra", 35000), ("Soldagem", 61000), ("Pintura", 21000)],
       [("Energia elétrica", 32000, "Potência"), ("Aluguel", 20000, "Área"), ("Seguro do imóvel", 5000, "Área"),
        ("Material auxiliar", 11000, "Requisições")],
       {"Funcionários": {"Administração": 8, "Manutenção": 4, "Corte e Dobra": 7, "Soldagem": 10, "Pintura": 5},
        "Área": {"Administração": 180, "Manutenção": 120, "Corte e Dobra": 600, "Soldagem": 700, "Pintura": 400},
        "Potência": {"Administração": 25, "Manutenção": 40, "Corte e Dobra": 320, "Soldagem": 450, "Pintura": 110},
        "Requisições": {"Administração": 5, "Manutenção": 18, "Corte e Dobra": 30, "Soldagem": 45, "Pintura": 22}},
       [dict(nome="Lâmina de plaina", t={"Corte e Dobra": 20, "Soldagem": 26, "Pintura": 12}, mp=210.00, cvv=13, cvp=7),
        dict(nome="Engate rápido", t={"Corte e Dobra": 12, "Soldagem": 18, "Pintura": 8}, mp=96.00, cvv=13, cvp=7),
        dict(nome="Suporte de disco", t={"Corte e Dobra": 15, "Soldagem": 10, "Pintura": 9}, mp=74.00, cvv=13, cvp=7)]),

    ex(5, "Bicicletas Pedal Sul S.A.", "Bicicletas", "Bicicletas urbana, MTB e infantil",
       ["A <b>Bicicletas Pedal Sul</b>, de Joinville (SC), fabrica quadros de aço e alumínio e monta bicicletas "
        "completas: <b>Urbana aro 26</b>, <b>MTB aro 29</b> e <b>Infantil aro 16</b>. A fábrica tem quatro seções "
        "produtivas: Corte de Tubos, Soldagem de Quadros, Pintura Eletrostática e Montagem Final.",
        "Os centros de apoio são a Administração e o Almoxarifado. A Administração é distribuída primeiro (pelo nº de "
        "funcionários) para o Almoxarifado e para os centros produtivos; depois o Almoxarifado é distribuído para os "
        "centros produtivos, também pelo nº de funcionários. A diretoria quer saber o custo e o preço de venda da MTB aro 29, "
        "carro-chefe da marca, para um lucro de 12%, e quanto cada seção pesa no custo de transformação."],
       ["Administração", "Almoxarifado", "Corte", "Soldagem", "Pintura", "Montagem"], ["Administração", "Almoxarifado"], 176, 12,
       [("Administração", 28000), ("Almoxarifado", 12000), ("Corte", 22000), ("Soldagem", 41000), ("Pintura", 24000), ("Montagem", 46000)],
       [("Energia elétrica", 30000, "Potência"), ("Aluguel", 32000, "Área"), ("Seguro do imóvel", 8000, "Área"),
        ("Material auxiliar", 14000, "Requisições"), ("Manutenção de equipamentos", 16000, "Ordens")],
       {"Funcionários": {"Administração": 10, "Almoxarifado": 4, "Corte": 5, "Soldagem": 9, "Pintura": 5, "Montagem": 12},
        "Área": {"Administração": 220, "Almoxarifado": 300, "Corte": 250, "Soldagem": 400, "Pintura": 350, "Montagem": 600},
        "Potência": {"Administração": 30, "Almoxarifado": 15, "Corte": 140, "Soldagem": 360, "Pintura": 180, "Montagem": 60},
        "Requisições": {"Administração": 10, "Almoxarifado": 0, "Corte": 24, "Soldagem": 48, "Pintura": 36, "Montagem": 62},
        "Ordens": {"Administração": 0, "Almoxarifado": 2, "Corte": 14, "Soldagem": 20, "Pintura": 9, "Montagem": 5}},
       [dict(nome="Urbana aro 26", t={"Corte": 12, "Soldagem": 28, "Pintura": 18, "Montagem": 35}, mp=420.00, cvv=16, cvp=6),
        dict(nome="MTB aro 29", t={"Corte": 15, "Soldagem": 36, "Pintura": 22, "Montagem": 48}, mp=780.00, cvv=16, cvp=6),
        dict(nome="Infantil aro 16", t={"Corte": 8, "Soldagem": 16, "Pintura": 12, "Montagem": 22}, mp=190.00, cvv=16, cvp=6)]),
]

DRV_LABEL = {"Funcionários": "Nº de funcionários", "Área": "Área ocupada (m²)", "Potência": "Potência instalada (kW)",
             "Requisições": "Nº de requisições de material", "Ordens": "Nº de ordens de manutenção", "Direto": "Direto (da própria seção)"}
DRV_UNID = {"Área": "m²", "Potência": "kW", "Requisições": "requisição", "Ordens": "ordem", "Funcionários": "funcionário"}
