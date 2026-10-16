"""Template base class. A template = driver specs + revenue/cost lines + a
plain-Python reference of the same economics. Everything else (headcount, P&L
tail, fixed assets, working capital, debt, cash flow, balance sheet, sheets,
checks) comes from the framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from engine.brief import Brief, Role
from engine.core import HEADCOUNT_DRIVERS, Top
from engine.spec import STANDARD_DRIVERS, DriverSpec, Line, Timing, role_driver_specs, validate_against


class Template(ABC):
    key: str = ""
    title: str = ""
    business_types: tuple[str, ...] = ()

    # -- what a template must provide ------------------------------------
    @abstractmethod
    def driver_specs(self) -> list[DriverSpec]:
        """Template-specific drivers (standard and headcount drivers are added automatically)."""

    @abstractmethod
    def revenue_lines(self, t: Timing) -> list[Line]:
        """Revenue build. Must define ``rev`` and ``cogs`` (negative)."""

    @abstractmethod
    def opex_lines(self, t: Timing) -> list[Line]:
        """Operating expenses, all negative. Use ``{payroll_total}`` for headcount cost."""

    @abstractmethod
    def capex_lines(self, t: Timing) -> list[Line]:
        """Capital spending per period. Must define ``capex`` (positive)."""

    @abstractmethod
    def reference_top(self, d: dict, p: int, y: int, t: Timing, payroll: float) -> Top:
        """Plain-Python twin of revenue/opex/capex lines for period ``p`` (no openpyxl, no formulas)."""

    # -- provided ----------------------------------------------------------
    def all_specs(self, roles: list[Role]) -> list[DriverSpec]:
        specs = list(self.driver_specs())
        if roles:
            for r in roles:
                specs += role_driver_specs(r.key, r.title)
            specs += HEADCOUNT_DRIVERS
        return specs + STANDARD_DRIVERS

    def opex_keys(self, t: Timing) -> list[str]:
        return [ln.key for ln in self.opex_lines(t)]

    def validate(self, brief: Brief) -> None:
        validate_against(brief, self.all_specs(brief.roles))
        if any("{payroll_total}" in ln.formula for ln in self.opex_lines(Timing("monthly", 1))) and not brief.roles:
            from engine.brief import BriefError

            raise BriefError(f"template {self.key!r} needs at least one headcount role")
