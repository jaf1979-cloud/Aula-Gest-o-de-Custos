"""Preenche a 'PLANILHA PROVA MC - Absorção' (modelo do professor) com a resolução dos 3 exercícios.
Edita o XML do pacote para preservar imagens, logotipos e rótulos desenhados do modelo.
Uso: python3 planilha_prova.py modelo.xlsx saida_sem_cache.xlsx
Abas: Ex1 MC, Ex1 Absorção, Ex2 MC, ... (o MC copia 'Questão 2', a Absorção copia 'Questão 1')."""
import copy, re, sys, zipfile
from lxml import etree
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dados import EXS

SRC, OUT = sys.argv[1], sys.argv[2]
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
XDR = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
q = lambda t: f"{{{NS}}}{t}"
zin = zipfile.ZipFile(SRC)
files = {n: zin.read(n) for n in zin.namelist()}

# ---------------- estilos: clona um xf trocando o formato numérico ----------------
sty = etree.fromstring(files["xl/styles.xml"])
cellXfs = sty.find(q("cellXfs"))
numFmts = sty.find(q("numFmts"))
FMT = {"brl": 44, "pct": 10, "int": 3}
_cache = {}


def fmt_style(s, kind):
    key = (s, kind)
    if key not in _cache:
        xf = copy.deepcopy(cellXfs[int(s)])
        xf.set("numFmtId", str(FMT[kind])); xf.set("applyNumberFormat", "1")
        cellXfs.append(xf); cellXfs.set("count", str(len(cellXfs)))
        _cache[key] = str(len(cellXfs) - 1)
    return _cache[key]


def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def split(ref):
    m = re.match(r"([A-Z]+)(\d+)", ref)
    return m.group(1), int(m.group(2))


class Sheet:
    def __init__(self, xml):
        self.root = etree.fromstring(xml)
        self.data = self.root.find(q("sheetData"))

    def row(self, r):
        for el in self.data:
            rr = int(el.get("r"))
            if rr == r:
                return el
            if rr > r:
                new = etree.Element(q("row")); new.set("r", str(r)); el.addprevious(new); return new
        new = etree.SubElement(self.data, q("row")); new.set("r", str(r)); return new

    def cell(self, ref):
        col, r = split(ref)
        row = self.row(r)
        for c in row:
            cc, _ = split(c.get("r"))
            if cc == col:
                return c
            if col2n(cc) > col2n(col):
                new = etree.Element(q("c")); new.set("r", ref); c.addprevious(new); return new
        new = etree.SubElement(row, q("c")); new.set("r", ref); return new

    def set(self, ref, v=None, f=None, fmt=None):
        c = self.cell(ref)
        for ch in list(c):
            c.remove(ch)
        if "t" in c.attrib:
            del c.attrib["t"]
        if fmt:
            c.set("s", fmt_style(c.get("s", "0"), fmt))
        if f is not None:
            etree.SubElement(c, q("f")).text = f
        elif isinstance(v, str):
            c.set("t", "inlineStr"); is_ = etree.SubElement(c, q("is")); t = etree.SubElement(is_, q("t")); t.text = v
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        elif v is not None:
            etree.SubElement(c, q("v")).text = repr(float(v)) if not float(v).is_integer() else str(int(v))

    def style_of(self, ref):
        return self.cell(ref).get("s", "0")

    def shift(self, start, k, tmpl_row):
        """insere k linhas antes de 'start', copiando o estilo da linha tmpl_row (colunas B:D)."""
        for el in reversed(list(self.data)):
            r = int(el.get("r"))
            if r >= start:
                el.set("r", str(r + k))
                for c in el:
                    cc, _ = split(c.get("r")); c.set("r", f"{cc}{r + k}")
        src = self.row(tmpl_row)
        for i in range(k):
            r = start + i
            new = copy.deepcopy(src); new.set("r", str(r))
            for c in list(new):
                cc, _ = split(c.get("r")); c.set("r", f"{cc}{r}")
                for ch in list(c):
                    c.remove(ch)
                c.attrib.pop("t", None)
            nxt = [el for el in self.data if int(el.get("r")) > r]
            nxt[0].addprevious(new) if nxt else self.data.append(new)
        dim = self.root.find(q("dimension"))
        if dim is not None:
            a, b = dim.get("ref").split(":"); bc, br = split(b); dim.set("ref", f"{a}:{bc}{br + k}")

    def width(self, col, w):
        cols = self.root.find(q("cols")); n = col2n(col)
        for c in cols:
            if int(c.get("min")) <= n <= int(c.get("max")):
                if c.get("min") == c.get("max"):
                    c.set("width", str(w)); c.set("customWidth", "1"); return
        new = etree.Element(q("col")); new.set("min", str(n)); new.set("max", str(n)); new.set("width", str(w)); new.set("customWidth", "1")
        after = [c for c in cols if int(c.get("min")) > n]
        after[0].addprevious(new) if after else cols.append(new)

    def unprotect(self):
        p = self.root.find(q("sheetProtection"))
        if p is not None:
            self.root.remove(p)

    def fix_heights(self, upto=60):
        """fixa a altura padrão (16) nas linhas sem altura própria, para o conteúdo não encolher as linhas
        e desalinhar os rótulos desenhados do modelo (o LibreOffice ajusta a altura automaticamente)."""
        for el in self.data:
            if int(el.get("r")) <= upto and el.get("ht") is None:
                el.set("ht", "16"); el.set("customHeight", "1")

    def tobytes(self):
        return etree.tostring(self.root, xml_declaration=True, encoding="UTF-8", standalone=True)


def shift_drawing(xml, from_row0, k):
    root = etree.fromstring(xml)
    for anc in root:
        fr = anc.find(f"{{{XDR}}}from")
        if fr is None:
            continue
        if int(fr.find(f"{{{XDR}}}row").text) >= from_row0:
            for tag in ("from", "to"):
                el = anc.find(f"{{{XDR}}}{tag}/{{{XDR}}}row")
                el.text = str(int(el.text) + k)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


# ---------------- preenchimento ----------------
def gastos(e):
    g = e["gastos"]
    mp = [(d, v) for d, v, c in g if c == "MP"]
    return mp + [(d, v) for d, v, c in g if c == "CVP"], [(d, v) for d, v, c in g if c == "CVV"], [(d, v) for d, v, c in g if c == "CF"]


def dre(sh, e, L):
    """L: dicionário de linhas do modelo. Devolve a linha do lucro operacional após inserir linhas de CF."""
    cvp, cvv, cf = gastos(e)
    R = sum(p["qv"] * p["pv"] for p in e["prods"])
    n_cf = L["lo"] - L["cf"] - 1
    extra = max(0, len(cf) - n_cf)
    assert len(cvv) <= L["cvp"] - L["cvv"] - 1 and len(cvp) <= L["cvt"] - L["cvp"] - 1
    if extra:
        sh.shift(L["lo"], extra, L["lo"] - 1)
    lo = L["lo"] + extra
    sh.set(f"C{L['rec']}", R)
    for r0, items in ((L["cvv"] + 1, cvv), (L["cvp"] + 1, cvp), (L["cf"] + 1, cf)):
        bstyle = sh.style_of(f"B{r0}")
        for i, (d, v) in enumerate(items):
            sh.cell(f"B{r0 + i}").set("s", bstyle)
            sh.set(f"B{r0 + i}", d); sh.set(f"C{r0 + i}", v)
    sh.set(f"C{L['cvv']}", f=f"SUM(C{L['cvv'] + 1}:C{L['cvp'] - 1})")
    sh.set(f"C{L['cvp']}", f=f"SUM(C{L['cvp'] + 1}:C{L['cvt'] - 1})")
    sh.set(f"C{L['cvt']}", f=f"C{L['cvv']}+C{L['cvp']}")
    sh.set(f"C{L['mc']}", f=f"C{L['rec']}-C{L['cvt']}")
    sh.set(f"C{L['cf']}", f=f"SUM(C{L['cf'] + 1}:C{lo - 1})")
    sh.set(f"C{lo}", f=f"C{L['mc']}-C{L['cf']}")
    rows = [L["rec"], L["cvv"], L["cvp"], L["cvt"], L["mc"], L["cf"], lo]
    rows += [L["cvv"] + 1 + i for i in range(len(cvv))] + [L["cvp"] + 1 + i for i in range(len(cvp))] + [L["cf"] + 1 + i for i in range(len(cf))]
    for r in rows:
        sh.set(f"D{r}", f=f"C{r}/$C${L['rec']}", fmt="pct")
    for r in rows:  # garante formato monetário em C
        c = sh.cell(f"C{r}"); c.set("s", fmt_style(c.get("s", "0"), "brl"))
    return lo, extra


def fill_mc(sh, e):
    L = dict(rec=10, cvv=12, cvp=20, cvt=31, mc=33, cf=35, lo=46)
    lo, extra = dre(sh, e, L)
    cf = L["cf"]
    sh.set("H3", f"Exercício {e['n']} · {e['empresa']} · Custeio pela margem de contribuição")
    base = {c: sh.style_of(f"{c}10") for c in "HIJKLMNOPQRSTUVWX"}
    for i, p in enumerate(e["prods"]):
        r = 10 + i
        for c in base:
            sh.cell(f"{c}{r}").set("s", base[c])
        sh.set(f"H{r}", f"{p['nome']} · {p['desc']}")
        sh.set(f"I{r}", p["qv"], fmt="int"); sh.set(f"J{r}", p["pv"], fmt="brl"); sh.set(f"K{r}", p["mp"], fmt="brl")
        sh.set(f"L{r}", f="($C$20-$C$21)/$C$10", fmt="pct")
        sh.set(f"M{r}", f=f"J{r}*L{r}", fmt="brl")
        sh.set(f"N{r}", f="$C$12/$C$10", fmt="pct")
        sh.set(f"O{r}", f=f"J{r}*N{r}", fmt="brl")
        sh.set(f"P{r}", f=f"K{r}+M{r}+O{r}", fmt="brl")
        sh.set(f"Q{r}", f=f"J{r}-P{r}", fmt="brl")
        sh.set(f"R{r}", f=f"Q{r}/J{r}", fmt="pct")
        sh.set(f"S{r}", f=f"Q{r}*I{r}", fmt="brl")
        sh.set(f"T{r}", f=f"S{r}/$S$17", fmt="pct")
        sh.set(f"U{r}", f=f"$C${cf}*T{r}/I{r}", fmt="brl")
        sh.set(f"V{r}", f=f"(K{r}+U{r})/(1-(L{r}+N{r}))", fmt="brl")
        sh.set(f"W{r}", p["L"] / 100, fmt="pct")
        sh.set(f"X{r}", f=f"(K{r}+U{r})/(1-(L{r}+N{r}+W{r}))", fmt="brl")
    sh.set("S17", f="SUM(S10:S16)", fmt="brl"); sh.set("T17", f="SUM(T10:T16)", fmt="pct")
    sh.set("H20", "Conferência: Σ MC total dos produtos − MC do DRE (deve ser 0)"); sh.set("S20", f="S17-C33", fmt="brl")
    sh.set("H21", "Conferência: Σ vendas × preço − receita (deve ser 0)"); sh.set("S21", f="SUMPRODUCT(I10:I16,J10:J16)-C10", fmt="brl")
    sh.width("H", 34)
    for c in "IJKLMNOPQRSTUVWX":
        sh.width(c, 17 if c in "SVX" else 15)
    return extra


def fill_abs(sh, e):
    L = dict(rec=8, cvv=10, cvp=18, cvt=29, mc=31, cf=33, lo=44)
    lo, extra = dre(sh, e, L)
    sh.set("I2", f"Exercício {e['n']} · {e['empresa']} · Custeio por absorção integral e ideal")
    for top, key in ((8, "qp"), (18, "qv")):
        base = {c: sh.style_of(f"{c}{top}") for c in "IJKLMNOPQ"}
        last = top + 4 if top == 8 else top + 5
        for i, p in enumerate(e["prods"]):
            r = top + i
            for c in base:
                sh.cell(f"{c}{r}").set("s", base[c])
            sh.set(f"I{r}", f"{p['nome']} · {p['desc']}")
            sh.set(f"J{r}", p[key], fmt="int")
            sh.set(f"K{r}", p["mp"], fmt="brl")
            sh.set(f"L{r}", f="$C$10/$C$8", fmt="pct")
            sh.set(f"M{r}", f="($C$18-$C$19)/$C$8", fmt="pct")
            sh.set(f"N{r}", f=f"$C$33/SUM($J${top}:$J${last})", fmt="brl")
            sh.set(f"O{r}", f=f"(K{r}+N{r})/(1-(L{r}+M{r}))", fmt="brl")
            sh.set(f"P{r}", p["L"] / 100, fmt="pct")
            sh.set(f"Q{r}", f=f"(K{r}+N{r})/(1-(L{r}+M{r}+P{r}))", fmt="brl")
    sh.set("I13", "Integral: QUANT. = produção do mês; CF unit = CF ÷ Σ produzido")
    sh.set("I24", "Ideal: QUANT. = vendas do mês; CF unit = CF ÷ Σ vendido")
    sh.width("I", 34)
    for c in "JKLMNOPQ":
        sh.width(c, 16)
    return extra


# ---------------- montagem do pacote ----------------
wbx = etree.fromstring(files["xl/workbook.xml"])
rels = etree.fromstring(files["xl/_rels/workbook.xml.rels"])
ct = files["[Content_Types].xml"].decode()
sheets = wbx.find(q("sheets"))
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
for s in list(sheets):
    if s.get("name").startswith("Questão"):
        sheets.remove(s)
for r in list(rels):
    if r.get("Target") in ("worksheets/sheet2.xml", "worksheets/sheet3.xml"):
        rels.remove(r)
fmls = sheets[0]
sheets.remove(fmls)

new_sheets, n_sheet, n_draw, n_rid = [], 10, 10, 100
for e in EXS:
    for kind, src, dsrc, fill, lo_row0 in (("MC", "sheet3", "drawing3", fill_mc, 44), ("Absorção", "sheet2", "drawing2", fill_abs, 42)):
        sh = Sheet(files[f"xl/worksheets/{src}.xml"])
        sh.unprotect()
        extra = fill(sh, e)
        dxml = files[f"xl/drawings/{dsrc}.xml"]
        if extra:
            dxml = shift_drawing(dxml, lo_row0, extra)
        sname, dname = f"sheet{n_sheet}", f"drawing{n_draw}"
        for r in range(1, 61):
            sh.row(r)
        sh.fix_heights()
        files[f"xl/worksheets/{sname}.xml"] = sh.tobytes()
        files[f"xl/worksheets/_rels/{sname}.xml.rels"] = files[f"xl/worksheets/_rels/{src}.xml.rels"].replace(f"{dsrc}.xml".encode(), f"{dname}.xml".encode())
        files[f"xl/drawings/{dname}.xml"] = dxml
        files[f"xl/drawings/_rels/{dname}.xml.rels"] = files[f"xl/drawings/_rels/{dsrc}.xml.rels"]
        ct = ct.replace("</Types>", f'<Override PartName="/xl/worksheets/{sname}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                                    f'<Override PartName="/xl/drawings/{dname}.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/></Types>')
        rid = f"rId{n_rid}"
        rel = etree.SubElement(rels, f"{{{PR}}}Relationship"); rel.set("Id", rid)
        rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"); rel.set("Target", f"worksheets/{sname}.xml")
        el = etree.SubElement(sheets, q("sheet")); el.set("name", f"Exercício {e['n']} {kind}"); el.set("sheetId", str(n_sheet)); el.set(f"{{{RNS}}}id", rid)
        new_sheets.append(f"Exercício {e['n']} {kind}")
        n_sheet += 1; n_draw += 1; n_rid += 1
sheets.append(fmls)
for n in ("xl/worksheets/sheet2.xml", "xl/worksheets/sheet3.xml", "xl/worksheets/_rels/sheet2.xml.rels", "xl/worksheets/_rels/sheet3.xml.rels",
          "xl/drawings/drawing2.xml", "xl/drawings/drawing3.xml", "xl/drawings/_rels/drawing2.xml.rels", "xl/drawings/_rels/drawing3.xml.rels"):
    files.pop(n)
for p in ("worksheets/sheet2.xml", "worksheets/sheet3.xml", "drawings/drawing2.xml", "drawings/drawing3.xml"):
    ct = re.sub(rf'<Override PartName="/xl/{p}"[^>]*/>', "", ct)
bv = wbx.find(q("bookViews"))
if bv is not None:
    for v in bv:
        v.set("activeTab", "0"); v.attrib.pop("firstSheet", None)
calc = wbx.find(q("calcPr")); calc.set("fullCalcOnLoad", "1")
files["xl/workbook.xml"] = etree.tostring(wbx, xml_declaration=True, encoding="UTF-8", standalone=True)
files["xl/_rels/workbook.xml.rels"] = etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True)
files["[Content_Types].xml"] = ct.encode()
files["xl/styles.xml"] = etree.tostring(sty, xml_declaration=True, encoding="UTF-8", standalone=True)
app = files["docProps/app.xml"].decode()
names = new_sheets + ["FORMULAS"]
app = re.sub(r"<vt:i4>\d+</vt:i4>", f"<vt:i4>{len(names)}</vt:i4>", app, count=1)
app = re.sub(r"<TitlesOfParts>.*</TitlesOfParts>", '<TitlesOfParts><vt:vector size="%d" baseType="lpstr">%s</vt:vector></TitlesOfParts>'
             % (len(names), "".join(f"<vt:lpstr>{n}</vt:lpstr>" for n in names)), app)
files["docProps/app.xml"] = app.encode()
for n in ("xl/worksheets/sheet10.xml",):
    pass
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for n in ["[Content_Types].xml"] + [n for n in files if n != "[Content_Types].xml"]:
        z.writestr(n, files[n])
print("ok", names)
