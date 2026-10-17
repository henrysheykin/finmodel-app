"""Building blocks shared by all templates: driver specs, period lines, timing.

A template describes its calculation grid as a list of ``Line`` objects. Each
line has one formula written in a tiny template language that the builder turns
into an Excel formula for every period column:

    {rev}          line ``rev`` in the same period
    {rev[-1]}      line ``rev`` in the previous period (needs ``first`` for period 1)
    {in:cogs_pct}  the active (scenario-selected) value of driver ``cogs_pct``
    {p}            period number (1..N)          {y}   year number (1..H)
    {mpp}          months per period (1 or 12)   {ppy} periods per year (12 or 1)
    {dpp}          days per period (30 or 360)

The same formula text is used for every period (``first`` optionally replaces
it in period 1 only, e.g. an opening balance), which is how the "same formula
across every period" rule is enforced by construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from engine.brief import Brief, BriefError

Fmt = Literal["usd", "usd2", "pct", "int", "dec1", "dec3", "days", "x"]
FORMATS: dict[str, str] = {
    "usd": "$#,##0;($#,##0);-",
    "usd2": "$#,##0.00;($#,##0.00);-",
    "pct": "0.0%;(0.0%);-",
    "int": "#,##0;(#,##0);-",
    "dec1": "#,##0.0;(#,##0.0);-",
    "dec3": "0.000",
    "days": "#,##0;(#,##0);-",
    "x": "0.0x",
}


@dataclass(frozen=True)
class DriverSpec:
    key: str
    label: str
    unit: str
    fmt: Fmt
    min: float
    max: float
    order: Literal["asc", "desc", "none"] = "none"  # asc: Low <= Base <= High
    section: str = "Business drivers"
    integer: bool = False


@dataclass(frozen=True)
class Line:
    key: str
    label: str
    formula: str
    group: str
    fmt: Fmt = "usd"
    first: str | None = None
    agg: Literal["sum", "last", "first", "none"] = "sum"
    bold: bool = False
    total: bool = False
    section: str | None = None  # starts a new section header before this line


@dataclass
class StmtRow:
    """One row of an annual statement / KPI table (kind: line | formula)."""

    key: str
    label: str
    kind: str  # line | formula | link | section
    src: str | tuple[str, str] = ""
    fmt: str = "usd"
    bold: bool = False
    total: bool = False
    neg: bool = False


@dataclass(frozen=True)
class Timing:
    granularity: str
    years: int

    @property
    def mpp(self) -> int:
        return 1 if self.granularity == "monthly" else 12

    @property
    def ppy(self) -> int:
        return 12 if self.granularity == "monthly" else 1

    @property
    def dpp(self) -> int:
        return 30 if self.granularity == "monthly" else 360

    @property
    def periods(self) -> int:
        return self.years * self.ppy

    def year_of(self, p: int) -> int:
        return (p * self.mpp + 11) // 12

    @property
    def period_word(self) -> str:
        return "month" if self.granularity == "monthly" else "year"


# Drivers every template gets (financing, working capital, tax, depreciation).
STANDARD_DRIVERS: list[DriverSpec] = [
    DriverSpec("equity", "Equity raised at start", "$", "usd", 0, 1e9, section="Funding"),
    DriverSpec("loan_amount", "Loan drawn at start", "$", "usd", 0, 1e9, section="Funding"),
    DriverSpec("loan_rate", "Loan interest rate per year", "%", "pct", 0, 0.5, section="Funding"),
    DriverSpec("loan_term_years", "Loan repayment term", "years", "int", 1, 30, section="Funding", integer=True),
    DriverSpec(
        "ar_days", "Customer payment terms (receivable days)", "days", "days", 0, 365, section="Working capital"
    ),
    DriverSpec("inv_days", "Inventory held (days of COGS)", "days", "days", 0, 365, section="Working capital"),
    DriverSpec("ap_days", "Supplier payment terms (payable days)", "days", "days", 0, 365, section="Working capital"),
    DriverSpec("dep_years", "Depreciation period for capex", "years", "int", 1, 40, section="Tax & depreciation"),
    DriverSpec("tax_rate", "Income tax rate", "%", "pct", 0, 0.6, section="Tax & depreciation"),
]


def role_driver_specs(role_key: str, title: str) -> list[DriverSpec]:
    sec = "Headcount"
    return [
        DriverSpec(f"{role_key}_fte", f"{title}: headcount (FTE)", "FTE", "dec1", 0, 10000, "asc", sec),
        DriverSpec(f"{role_key}_salary", f"{title}: salary per FTE per year", "$", "usd", 0, 5e6, section=sec),
        DriverSpec(f"{role_key}_fte_g", f"{title}: headcount growth per year", "%", "pct", -0.5, 3, "asc", sec),
        DriverSpec(
            f"{role_key}_start", f"{title}: first month on payroll", "month #", "int", 1, 60, section=sec, integer=True
        ),
    ]


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)

    def raise_if_any(self) -> None:
        if self.errors:
            raise BriefError("; ".join(self.errors))


def validate_against(brief: Brief, specs: list[DriverSpec]) -> None:
    """Every spec'd driver present, nothing unknown, values within bounds and ordered."""
    rep = ValidationReport()
    by_key = {s.key: s for s in specs}
    given = {d.key: d for d in brief.drivers}
    missing = [k for k in by_key if k not in given]
    unknown = [k for k in given if k not in by_key]
    if missing:
        rep.errors.append(f"missing drivers: {missing}")
    if unknown:
        rep.errors.append(f"unknown drivers: {unknown}")
    for k, d in given.items():
        s = by_key.get(k)
        if s is None:
            continue
        vals = (d.low, d.base, d.high)
        for name, v in zip(("low", "base", "high"), vals, strict=True):
            if not (s.min <= v <= s.max):
                rep.errors.append(f"{k}.{name}={v} outside [{s.min}, {s.max}]")
            if s.integer and v != int(v):
                rep.errors.append(f"{k}.{name}={v} must be a whole number")
        if s.order == "asc" and not (d.low <= d.base <= d.high):
            rep.errors.append(f"{k}: needs Low <= Base <= High, got {vals}")
        if s.order == "desc" and not (d.low >= d.base >= d.high):
            rep.errors.append(f"{k}: needs Low >= Base >= High (cost driver), got {vals}")
    rep.raise_if_any()
