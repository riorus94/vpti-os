# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues at
[riorus94/vpti-os](https://github.com/riorus94/vpti-os/issues). Use the `gh` CLI
for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body-file <file>` (use a
  file or heredoc for multi-line bodies). Apply a triage label with `--label`.
- **Read an issue**: `gh issue view <number> --comments`.
- **List issues**: `gh issue list --state open --json number,title,labels --jq '...'`
  with `--label` / `--state` filters.
- **Comment**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

`gh` infers the repo from `git remote -v` automatically inside the clone.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Notes

- The canonical product spec is `docs/PRD.md` (not an issue).
- The original 12 tracer-bullet issues (9 MVP `#1`–`#9`, 3 Phase-2 `#10`–`#12`)
  were migrated here from `.scratch/` markdown; "Blocked by" sections reference
  the GitHub issue numbers.
