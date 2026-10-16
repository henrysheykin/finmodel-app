# finmodel-app

Custom Excel financial models from a short brief: wizard → payment → deterministic
generator → LibreOffice recalculation → independent checks → download link.

Status: early build, run by autonomous Claude sessions. Start here:

- `CLAUDE.md` — product, architecture, rules and the run protocol for agents
- `docs/BACKLOG.md` — tasks with dependencies, skills and definitions of done
- `docs/STATUS.md` — weekly status (written by the Monday PM run)
- `docs/HUMAN_TODO.md` — decisions, accounts and reviews only the owner can do
- `docs/RUNLOG.md` — what each run did
- `poc/` — working prototype (cafe model, 894 formulas, challenger passes)
- `design/` — approved landing design source

## Developer quick start

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"          # LibreOffice (`soffice`) must be on PATH for engine tests
ruff check . && ruff format --check . && pytest -q

python -m engine.build engine/briefs/cafe.json /tmp/cafe.xlsx [--tier light --granularity annual --years 5]
python -m engine.recalc /tmp/cafe.xlsx                                   # recalc + error scan
python -m engine.challenger engine/briefs/cafe.json /tmp/cafe.xlsx       # independent check
uvicorn app.main:app --reload                                            # web (/healthz)
```

Docker: `docker build -t finmodel-app .` then `docker run -p 8000:8000 finmodel-app`
(web) or `docker run finmodel-app python -m worker.main` (worker).
