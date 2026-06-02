---
name: commit-policy
description: Enforce disciplined Git commits for production-impacting projects. Use when Codex is asked to commit, merge, push, prepare changes for review, split work into focused commits, or decide whether changes should be committed in a Frappe/ERPNext app or any repository where small auditable commits matter.
---

# Commit Policy

Use this skill whenever a task involves Git commits, merges, pushes, deployment commits, or preparing repository changes for review.

## Principles

- Keep every commit focused on one explicit task.
- Do not mix unrelated changes in the same commit.
- Do not hide risky behavior inside broad commits.
- Prefer small, reviewable, reversible commits.
- Preserve user work and remote work. Never revert changes you did not make unless explicitly instructed.
- Do not amend commits unless explicitly requested.
- Do not use destructive commands such as `git reset --hard`, `git checkout --`, or force push unless explicitly requested and confirmed.

## Pre-Commit Workflow

Before committing:

```bash
git status -sb
git diff --stat
git diff --check
```

Then inspect the actual diff for the files being committed:

```bash
git diff -- <file-or-directory>
```

For staged changes:

```bash
git diff --cached --stat
git diff --cached --check
git diff --cached
```

## Commit Scope Rules

Use separate commits for separate concerns:

- Documentation changes.
- Fixture or metadata changes.
- Business logic changes.
- Security/permission changes.
- Database migration patches.
- Test-only changes.
- Deployment-only changes.

Do not combine these unless the user explicitly asks and the coupling is unavoidable.

## Frappe/ERPNext-Specific Rules

For Frappe/ERPNext apps:

- Commit DocType JSON, fixtures, hooks, patches, and generated metadata only after validating them.
- If Desk changes were made, export them to code before committing.
- If fixtures changed, validate JSON before committing.
- If DocTypes, permissions, pages, workspaces, Server Scripts, Client Scripts, or hooks changed, treat the commit as production-impacting.
- If a migration patch is needed, commit the patch and the `patches.txt` update together.
- If a field is removed from a DocType, document the data-loss risk or include an archival/migration patch.

Recommended checks:

```bash
python3 -m json.tool urbanizacion/fixtures/doctype.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/client_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/server_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/print_format.json >/dev/null
python3 -m compileall urbanizacion
```

Run only checks that apply to the changed files. If a check cannot be run, say so in the final report.

## Commit Message Rules

Use clear, concise messages.

Preferred format:

```text
<type>(<scope>): <summary>
```

Good examples:

```text
docs: add agent instructions
fix(fixtures): preserve ActividadObra peso field
fix(security): restrict importar-lotes to Urbanizacion Manager
fix(urbAmbiente): cambiar cantidad a float a peticion de diego
chore(deploy): document production migration checklist
```

Avoid vague messages:

```text
changes
fix stuff
update files
misc
```

## When User Requests Commit

If the user says `commit`, commit only the current intended task.

Process:

1. Review `git status -sb`.
2. Identify files that belong to the requested task.
3. Exclude unrelated dirty files.
4. Stage only the intended files.
5. Run `git diff --cached --stat` and `git diff --cached --check`.
6. Commit with a focused message.
7. Report the commit hash and remaining dirty state.

## When User Requests Push

Before pushing:

```bash
git status -sb
git log --oneline --decorate --max-count=8
```

Then push the current branch only if:

- The branch is correct.
- Local commits are intentional.
- There are no unresolved conflicts.
- The user requested push or the task clearly includes publishing.

Use:

```bash
git push origin <branch>
```

For this project, the main branch is `master`.

## When Merging PRs

Before merge:

- Fetch the target branch and PR/head branch.
- Review changed files and diff.
- Look for security, data-loss, migration, and permission risks.
- Document accepted risks before merging.
- Do not merge merely because Git says it is mergeable.

After merge:

- Run applicable validation.
- Commit or record any documentation separately if needed.
- Push only after the merge is clean and intentional.

## Final Report

After committing or pushing, report:

- Commit hash(es).
- Branch and remote sync state.
- Files or areas changed.
- Validations run.
- Any remaining uncommitted changes.
- Any risk that remains.
