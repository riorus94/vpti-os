# VPTI AI Operating System (VAOS)

AI operational-intelligence platform that turns VPTI regulation and institutional knowledge into grounded, structured, actionable output. Built in Python (FastAPI). Telegram is the MVP interface.

See [CONTEXT.md](CONTEXT.md) for the domain glossary, [docs/PRD.md](docs/PRD.md) for the product spec, and [docs/adr/](docs/adr/) for architectural decisions.

## Agent skills

### Issue tracker

Issues and PRDs live as local markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical roles using the default strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
