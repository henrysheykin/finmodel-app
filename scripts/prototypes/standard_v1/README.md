# Workbook standard v1 — prototype (reference only)

Built `design/workbook-standard-v1-prototype.xlsx` (2026-10-20) for Henry's review of ADR-013.
It takes a real engine workbook (SaaS, established stage, Full, 5 years, monthly, goal modules on), renames the
engine Dashboard to KPIs, adds Cover / Dashboard / Summary / Scenarios / Sources & Uses and restyles everything,
then proves that all 16,964 engine cells are unchanged in all three scenarios.

Not production code: row positions are SaaS-specific and the Scenarios sheet's Low / Base / High columns are a
build-time snapshot. Tasks E26–E33 implement the standard in `engine/`. Use this for layout constants, chart
settings that survive LibreOffice, and the look to match.

    python scripts/prototypes/standard_v1/proto_run.py     # writes var/prototype-standard-v1/ (set PROTO_DIR to move)
