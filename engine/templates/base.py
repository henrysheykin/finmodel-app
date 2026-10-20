"""Template base class. A template = driver specs + revenue/cost lines + a
plain-Python reference of the same economics. Everything else (headcount, P&L
tail, fixed assets, working capital, debt, cash flow, balance sheet, sheets,
checks) comes from the framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from engine.brief import Brief, Role
from engine.core import HC, HEADCOUNT_DRIVERS, Top
from engine.goals import ALL_GOAL_KEYS, apply_goal, goal_specs, validate_goal
from engine.spec import STANDARD_DRIVERS, DriverSpec, Line, Timing, role_driver_specs, validate_against


class Template(ABC):
    key: str = ""
    title: str = ""
    business_types: tuple[str, ...] = ()

    # -- catalog (ADR-009): read by the wizard, the landing page and scripts/build_samples.py ----------
    #: position in the wizard's business-type list
    order: int = 100
    #: drivers the customer can type in the wizard's "key numbers" step (must exist in all_specs)
    key_numbers: tuple[str, ...] = ()
    #: landing page sample row; empty title = not listed
    sample_title: str = ""
    sample_desc: str = ""
    #: stage defaults used for samples/<key>-full.xlsx
    sample_stage: str = "growing"

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
    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        """Plain-Python twin of revenue/opex/capex lines for period ``p`` (no openpyxl, no formulas)."""

    # -- optional hooks ------------------------------------------------------
    def liability_lines(self, t: Timing) -> list[Line]:
        """Extra working-capital liabilities (balances, agg="last"), e.g. deferred revenue."""
        return []

    def extra_lines(self, t: Timing) -> list[Line]:
        """Helper lines appended to the period grid (e.g. burn for runway); not part of the P&L."""
        return []

    def kpi_rows(self, t: Timing) -> list:
        """Annual KPI table (``StmtRow`` list) shown on the Dashboard (Full) or P&L (Light)."""
        return []

    #: loan repayment: "straight" (equal principal) or "annuity" (level mortgage payment) — engine/core.py
    loan_style: str = "straight"
    #: add the property Returns sheet (engine/returns.py): IRR / NPV of a purchase with an exit at the horizon
    returns: bool = False

    kpi_title: str = "Key metrics"
    #: KPI rows the challenger recomputes: kpi row key -> reference series key
    kpi_checked: dict[str, str] = {}
    #: reference ``kpis`` series that are flows (summed per year), the rest are balances
    kpi_flows: tuple[str, ...] = ()

    def default_brief(self, stage: str) -> Brief:
        """Illustrative starting brief for a wizard stage (used by the sample-data path)."""
        raise NotImplementedError(f"template {self.key!r} has no stage defaults")

    # -- provided ----------------------------------------------------------
    def all_specs(self, roles: list[Role], tier: str = "full") -> list[DriverSpec]:
        """Template + headcount + standard drivers, plus the tier's module drivers (engine/goals.py)."""
        specs = list(self.driver_specs())
        if roles:
            for r in roles:
                specs += role_driver_specs(r.key, r.title)
            specs += HEADCOUNT_DRIVERS
        return specs + STANDARD_DRIVERS + goal_specs(tier)

    def opex_keys(self, t: Timing) -> list[str]:
        return [ln.key for ln in self.opex_lines(t)]

    def validate(self, brief: Brief) -> None:
        """Validate the brief as it will be built: with its tier's module drivers (``apply_goal``) added."""
        specs = self.all_specs(brief.roles, brief.tier)
        data = brief.model_dump()
        data["drivers"] = [d for d in data["drivers"] if d["key"] not in ALL_GOAL_KEYS]
        # template / standard drivers first, so a missing one is reported on its own
        validate_against(Brief.model_validate(data), [s for s in specs if s.key not in ALL_GOAL_KEYS])
        brief = apply_goal(brief, tpl=self)
        validate_against(brief, specs)
        validate_goal(brief)
        if any("{payroll_total}" in ln.formula for ln in self.opex_lines(Timing("monthly", 1))) and not brief.roles:
            from engine.brief import BriefError

            raise BriefError(f"template {self.key!r} needs at least one headcount role")
