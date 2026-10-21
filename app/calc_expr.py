"""The calculator expression language (ADR-014, E34): a small, safe formula language.

Python twin of the evaluator in ``web/static/calc.js``. The two must agree on every formula, so any change here
needs the same change there; ``tests/test_calculators.py`` runs both on the same cases.

Grammar (lowest precedence first)::

    comparison := sum (("<" | "<=" | ">" | ">=" | "==" | "!=") sum)*      -> 1 or 0
    sum        := product (("+" | "-") product)*
    product    := unary (("*" | "/") unary)*
    unary      := ("-" | "+") unary | power
    power      := atom ("^" unary)?                                       right associative, -2^2 = -4
    atom       := number | name | name "(" args ")" | "(" comparison ")"

``×``, ``÷`` and ``−`` are accepted as aliases of ``*``, ``/`` and ``-``. Functions: ``min(a, b, ...)``,
``max(a, b, ...)``, ``round(x)``, ``round(x, digits)`` (half away from zero, digits 0..9), ``abs(x)`` and
``if(cond, a, b)`` (only the chosen branch is evaluated; a condition is true when it is not 0).

A value that cannot be computed (division by zero, ``0 ^ -1``, a negative base with a fractional exponent,
overflow) is ``None`` and spreads through every operation that uses it; the pages show it as "—". There is no
``eval`` or ``exec``: the formula is tokenised, parsed to a tuple tree and walked.
"""

from __future__ import annotations

import math
import re

MAX_LENGTH = 500
MAX_DEPTH = 40
NAME_RE = re.compile(r"[a-z][a-z0-9_]*")
FUNCTIONS: dict[str, tuple[int, int | None]] = {  # name -> (min args, max args or None)
    "min": (2, None),
    "max": (2, None),
    "round": (1, 2),
    "abs": (1, 1),
    "if": (3, 3),
}
RESERVED = frozenset(FUNCTIONS)

_TOKEN = re.compile(
    r"[ \t\r\n]*(?:(?P<num>[0-9]+(?:\.[0-9]+)?|\.[0-9]+)|(?P<name>[a-z][a-z0-9_]*)|(?P<op><=|>=|==|!=|[-+*/^<>(),×÷−]))"
)
_ALIAS = {"×": "*", "÷": "/", "−": "-"}

Value = float | None


class ExprError(ValueError):
    """The formula is not valid (syntax, unknown function, wrong number of arguments)."""


def tokenize(src: str) -> list[tuple[str, str]]:
    if len(src) > MAX_LENGTH:
        raise ExprError(f"formula longer than {MAX_LENGTH} characters")
    out: list[tuple[str, str]] = []
    pos = 0
    while True:
        while pos < len(src) and src[pos] in " \t\r\n":
            pos += 1
        if pos >= len(src):
            return out
        m = _TOKEN.match(src, pos)
        if not m:
            raise ExprError(f"unexpected character {src[pos]!r} at position {pos}")
        pos = m.end()
        if m["num"] is not None:
            out.append(("num", m["num"]))
        elif m["name"] is not None:
            out.append(("name", m["name"]))
        else:
            out.append(("op", _ALIAS.get(m["op"], m["op"])))


class _Parser:
    def __init__(self, tokens: list[tuple[str, str]]):
        self.t = tokens
        self.i = 0
        self.depth = 0

    def peek(self) -> tuple[str, str] | None:
        return self.t[self.i] if self.i < len(self.t) else None

    def op(self, *ops: str) -> str | None:
        tok = self.peek()
        if tok and tok[0] == "op" and tok[1] in ops:
            self.i += 1
            return tok[1]
        return None

    def expect(self, o: str) -> None:
        if not self.op(o):
            raise ExprError(f"expected {o!r}")

    def parse(self):
        node = self.comparison()
        if self.peek() is not None:
            raise ExprError(f"unexpected {self.peek()[1]!r}")
        return node

    def comparison(self):
        node = self.sum()
        while (o := self.op("<=", ">=", "==", "!=", "<", ">")) is not None:
            node = ("bin", o, node, self.sum())
        return node

    def sum(self):
        node = self.product()
        while (o := self.op("+", "-")) is not None:
            node = ("bin", o, node, self.product())
        return node

    def product(self):
        node = self.unary()
        while (o := self.op("*", "/")) is not None:
            node = ("bin", o, node, self.unary())
        return node

    def unary(self):
        self.depth += 1
        if self.depth > MAX_DEPTH:
            raise ExprError("formula nested too deeply")
        try:
            if (o := self.op("-", "+")) is not None:
                inner = self.unary()
                return ("neg", inner) if o == "-" else inner
            return self.power()
        finally:
            self.depth -= 1

    def power(self):
        node = self.atom()
        if self.op("^"):
            return ("bin", "^", node, self.unary())
        return node

    def atom(self):
        tok = self.peek()
        if tok is None:
            raise ExprError("unexpected end of formula")
        kind, text = tok
        if kind == "num":
            self.i += 1
            return ("num", float(text))
        if kind == "name":
            self.i += 1
            if self.op("("):
                if text not in FUNCTIONS:
                    raise ExprError(f"unknown function {text!r}")
                args = [self.comparison()]
                while self.op(","):
                    args.append(self.comparison())
                self.expect(")")
                lo, hi = FUNCTIONS[text]
                if len(args) < lo or (hi is not None and len(args) > hi):
                    want = str(lo) if hi == lo else f"{lo}+" if hi is None else f"{lo}-{hi}"
                    raise ExprError(f"{text}() takes {want} arguments")
                return ("call", text, args)
            if text in FUNCTIONS:
                raise ExprError(f"{text!r} is a function; write {text}(...)")
            return ("var", text)
        if self.op("("):
            self.depth += 1
            if self.depth > MAX_DEPTH:
                raise ExprError("formula nested too deeply")
            node = self.comparison()
            self.depth -= 1
            self.expect(")")
            return node
        raise ExprError(f"unexpected {text!r}")


def parse(src: str):
    """Parse a formula to a tuple tree; raises ExprError."""
    return _Parser(tokenize(src)).parse()


def variables(node) -> set[str]:
    """Every input or output key the formula uses."""
    kind = node[0]
    if kind == "var":
        return {node[1]}
    if kind == "neg":
        return variables(node[1])
    if kind == "bin":
        return variables(node[2]) | variables(node[3])
    if kind == "call":
        out: set[str] = set()
        for a in node[2]:
            out |= variables(a)
        return out
    return set()


def _finite(x: float) -> Value:
    return x if math.isfinite(x) else None


def _round(x: float, digits: float) -> Value:
    if digits != math.floor(digits) or not 0 <= digits <= 9:
        return None
    m = 10.0 ** int(digits)
    scaled = abs(x) * m + 0.5
    if not math.isfinite(scaled):
        return None
    r = float(math.floor(scaled)) / m
    return r if x >= 0 else -r


def _power(a: float, b: float) -> Value:
    if a == 0 and b < 0:
        return None
    if a < 0 and b != math.floor(b):
        return None
    try:
        return _finite(a**b)
    except OverflowError:
        return None


def evaluate(node, env: dict[str, Value]) -> Value:
    """Value of a parsed formula; ``None`` when it cannot be computed. ``env`` maps every key to a value."""
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "var":
        if node[1] not in env:
            raise ExprError(f"unknown name {node[1]!r}")
        return env[node[1]]
    if kind == "neg":
        v = evaluate(node[1], env)
        return None if v is None else -v
    if kind == "bin":
        o = node[1]
        a, b = evaluate(node[2], env), evaluate(node[3], env)
        if a is None or b is None:
            return None
        if o == "+":
            return _finite(a + b)
        if o == "-":
            return _finite(a - b)
        if o == "*":
            return _finite(a * b)
        if o == "/":
            return None if b == 0 else _finite(a / b)
        if o == "^":
            return _power(a, b)
        return 1.0 if {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b, "==": a == b, "!=": a != b}[o] else 0.0
    name, args = node[1], node[2]
    if name == "if":
        cond = evaluate(args[0], env)
        if cond is None:
            return None
        return evaluate(args[1] if cond != 0 else args[2], env)
    vals = [evaluate(a, env) for a in args]
    if any(v is None for v in vals):
        return None
    if name == "min":
        return min(vals)  # type: ignore[type-var]
    if name == "max":
        return max(vals)  # type: ignore[type-var]
    if name == "abs":
        return abs(vals[0])  # type: ignore[arg-type]
    return _round(vals[0], vals[1] if len(vals) > 1 else 0.0)  # type: ignore[arg-type]


# ---------- number formats (shared with calc.js) ----------

FORMATS: dict[str, tuple[str, int, str]] = {  # name -> (prefix, decimals, suffix)
    "int": ("", 0, ""),
    "number1": ("", 1, ""),
    "number2": ("", 2, ""),
    "money": ("$", 0, ""),
    "money2": ("$", 2, ""),
    "percent": ("", 1, "%"),
    "percent0": ("", 0, "%"),
    "multiple": ("", 2, "x"),
}
NONE_TEXT = "—"  # em dash
DISPLAY_LIMIT = 1e15


def format_value(value: Value, fmt: str) -> str:
    """Display text of a value in a named format, e.g. ``-$1,234.50``; "—" when it cannot be computed."""
    from decimal import ROUND_HALF_UP, Decimal

    prefix, decimals, suffix = FORMATS[fmt]
    if value is None or not math.isfinite(value) or abs(value) >= DISPLAY_LIMIT:
        return NONE_TEXT
    q = Decimal(abs(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    text = f"{q:,.{decimals}f}"
    sign = "-" if value < 0 and q != 0 else ""
    return f"{sign}{prefix}{text}{suffix}"
