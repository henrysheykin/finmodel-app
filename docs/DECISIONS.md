# Decisions

Short ADRs. Format: id, date, decision, why, consequences. Append, never rewrite.

## ADR-000 — Working agreement (2026-10-16)
- Code lives in this repo; autonomous scheduled sessions build it task by task
  from `docs/BACKLOG.md` following the protocol in `CLAUDE.md`.
- Agents squash-merge their own PRs when CI is green (approved by Henry).
- Engineering track runs daily, marketing on weekdays, PM review on Mondays.
- The LLM fills a validated brief; deterministic templates build the workbook;
  an independent challenger must pass before any delivery.

## ADR-001 — Stack
- To be written in E01 (proposal in CLAUDE.md: Python 3.12, FastAPI, SQLAlchemy,
  DB-polled worker, openpyxl + LibreOffice, Docker).
