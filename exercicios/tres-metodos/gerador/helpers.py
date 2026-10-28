"""Funções de formatação compartilhadas (copiadas do gerador de margem de contribuição)."""
from decimal import Decimal
from calc import r2, tabela



class N:
    """resposta numérica. kind: 'r' = R$ total, 'u' = R$ unitário, 'p' = %"""
    def __init__(self, v, kind="r"):
        self.v, self.kind = float(v), kind


# ---------------- formatação ----------------
def num(x, nd=2):
    d = Decimal(repr(r2(x))) if nd == 2 else Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd))
    s = f"{d:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x):
    return ("−R$&nbsp;" + num(-x)) if r2(x) < 0 else "R$&nbsp;" + num(x)


def pc(x):
    return num(x) + "%"


def pn(x):
    """percentual dentro da fórmula, sem casas desnecessárias: 7 / 24 / 6,8"""
    v = round(float(x), 2)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").replace(".", ",")


def qn(q):
    return f"{q:,}".replace(",", ".")


def fr(n, d):
    return f'<span class="fr"><span class="n">{n}</span><span class="d">{d}</span></span>'


def eq(lhs, *parts, res=None):
    body = " <span class=op>=</span> ".join(parts)
    out = f'<div class="eq"><span class="lhs">{lhs}</span> <span class=op>=</span> {body}'
    if res is not None:
        out += f' <span class=op>=</span> <b class="res">{res}</b>'
    return out + "</div>"


def table(head, rows, cls="", align=None, foot=None):
    al = align or ("l" + "r" * (len(head) - 1))
    h = "".join(f"<th>{c}</th>" for c in head)
    body = "".join("<tr>" + "".join(f'<td class="{al[i]}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    f = ""
    if foot:
        f = "<tfoot>" + "".join("<tr>" + "".join(f'<td class="{al[i]}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in foot) + "</tfoot>"
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody>{f}</table></div>'


def interp(txt):
    return f'<div class="interp"><span class="tag">Interpretação gerencial</span><p>{txt}</p></div>'


def note(txt):
    return f'<div class="note">{txt}</div>'


PILL = {"MP": ('cvp', 'CVP · MP'), "CVP": ('cvp', 'CVP'), "CVV": ('cvv', 'CVV'), "CF": ('cf', 'CF')}
WHY = {"MP": "Varia com a produção; entra em R$ pela ficha técnica de cada produto.",
       "CVP": "Acompanha o volume produzido.",
       "CVV": "Acompanha o valor ou o volume vendido.",
       "CF": "Não muda com o volume produzido ou vendido no mês."}


