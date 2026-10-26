"""Automatisk retting av 1T-01-likninger-og-ulikheter.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1a', 'losning_1a skal være løsningene av 2x² - 3x - 2 = 0', "lik(losning_1a, [S('-1/2'), 2])"),
    ('1b', 'losning_1b skal være løsningene av (x + 3)/(x - 1) = x', 'lik(losning_1b, [-1, 3])'),
    ('1c', 'losning_1c skal være løsningene av x³ = 4x', 'lik(losning_1c, [-2, 0, 2])'),
    ('2a', 'ulikhet_2a skal være intervallet x > 4', "lik(ulikhet_2a, S('Interval.open(4, oo)'))"),
    ('2b', 'ulikhet_2b skal være intervallet -2 ≤ x ≤ 3', "lik(ulikhet_2b, S('Interval(-2, 3)'))"),
    ('2c', 'ulikhet_2c skal være x < -2 eller x > 2', "lik(ulikhet_2c, S('Union(Interval.open(-oo, -2), Interval.open(2, oo))'))"),
    ('3', 'ulikhet_3 skal være x < -1 eller x ≥ 2', "lik(ulikhet_3, S('Union(Interval.open(-oo, -1), Interval(2, oo))'))"),
    ('4', 'bredder skal være intervallet 5 ≤ x ≤ 10', "lik(bredder, S('Interval(5, 10)'))"),
    ('5', 'k_to_losninger skal være k < -2 eller k > 6', "lik(k_to_losninger, S('Union(Interval.open(-oo, -2), Interval.open(6, oo))'))"),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
