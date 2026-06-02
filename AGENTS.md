# Agent Instructions for `urbanizacion`

This repository contains the private Frappe/ERPNext v15 app `urbanizacion` for Inversiones BEL. Treat it as production-impacting business software, not as a throwaway customization.

## Environment

- Main bench: `/home/frappe/frappe-bench`
- App path: `/home/frappe/frappe-bench/apps/urbanizacion`
- Frappe/ERPNext major version: `v15`
- Main branch: `master`
- Normal bench operations must run as user `frappe`.
- Production site: `erp.inversionesbel.com`
- Testing site: `testing15.inversionesbel.com`

Use this command pattern for bench and app work:

```bash
sudo -u frappe bash -lc 'cd /home/frappe/frappe-bench && <command>'
sudo -u frappe bash -lc 'cd /home/frappe/frappe-bench/apps/urbanizacion && <command>'
```

## Core Safety Rules

- Never run destructive Git commands such as `git reset --hard`, `git checkout --`, or forced pushes unless explicitly requested and confirmed.
- Never revert user or remote changes without understanding them first.
- Do not change production before validating on `testing15.inversionesbel.com`.
- Always create a full backup before running `migrate` on `erp.inversionesbel.com`.
- Keep each commit focused on one explicit task.
- Do not silently mix documentation, fixture changes, business logic, and deployment changes in the same commit.
- If a change affects permissions, workflows, Server Scripts, Client Scripts, DocTypes, or fixtures, assume it can affect production behavior.

## Frappe/ERPNext Development Rules

- Prefer app code and fixtures over database-only changes.
- Changes made in Desk must be exported to code before they are considered deployable.
- After changing fixtures, run `bench --site <site> migrate` to verify import behavior.
- Do not remove DocType fields if data may already exist. If a field must be removed, document the decision and provide a migration or archival plan.
- Keep child-table DocTypes out of workspace navigation unless there is a specific reason.
- Use server-side validation for business-critical rules. Client Scripts are UX helpers, not security boundaries.
- For role or permission-sensitive features, validate permissions on the server, not only in JavaScript.
- Keep public web exposure off for internal operational pages unless explicitly approved.

## Fixtures

The app intentionally versions site configuration through fixtures. Be careful with:

- `DocType`
- `Workspace`
- `Client Script`
- `Server Script`
- `Property Setter`
- `Workflow`
- `Notification`
- `Print Format`
- `DocType Link`
- `Web Page`
- `Role`

When editing fixtures:

- Validate JSON before committing.
- Avoid partial or hand-written DocField metadata when possible; prefer exporting from Frappe.
- Check for accidental deletion of fields, permissions, roles, pages, dashboards, or workspace blocks.
- Keep `DocType Link` records deduplicated.
- Do not reintroduce public access for internal pages.

Useful checks:

```bash
python3 -m json.tool urbanizacion/fixtures/doctype.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/client_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/server_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/print_format.json >/dev/null
```

## Known Business-Critical Areas

- `Lotes`
- `Proyectos`
- `CartaReserva`
- `ContratoVenta`
- `Adendum`
- `SeguimientoObra`
- Internal page: `/app/importar-lotes`
- Workspace: `Urbanizacion`

Current important invariants:

- `urbAmbiente.cantidad` must remain `Float`.
- `importar-lotes` must remain internal and restricted to `Urbanizacion Manager` unless explicitly changed.
- `DocType Link` duplicates should remain `0`.
- Connections between `Proyectos` and `Lotes` are part of the expected UX.
- Business actions such as confirmation, reservation, contract creation, and lot state transitions require server-side safeguards.

## Validation Workflow

Before changing code:

```bash
cd /home/frappe/frappe-bench/apps/urbanizacion
git status -sb
git fetch origin master --prune
```

After changing code or fixtures:

```bash
cd /home/frappe/frappe-bench/apps/urbanizacion
git diff --stat
git diff --check
python3 -m json.tool urbanizacion/fixtures/doctype.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/client_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/server_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/print_format.json >/dev/null
```

Validate on testing first:

```bash
cd /home/frappe/frappe-bench
bench --site testing15.inversionesbel.com migrate
bench --site testing15.inversionesbel.com clear-cache
```

Recommended metadata checks:

```bash
bench --site testing15.inversionesbel.com mariadb <<SQL
SELECT parent, fieldname, fieldtype, hidden, read_only
FROM `tabDocField`
WHERE parent IN ("ContratoVenta", "CartaReserva", "ActividadObra", "urbAmbiente")
  AND fieldname IN ("confirmado", "peso", "cantidad", "monto_financiar")
ORDER BY parent, idx;

SELECT role
FROM `tabHas Role`
WHERE parenttype = "Page"
  AND parent = "importar-lotes"
ORDER BY role;

SELECT COUNT(*) AS duplicate_doctype_links
FROM (
  SELECT parent, `group`, link_doctype, link_fieldname, COUNT(*) c
  FROM `tabDocType Link`
  GROUP BY parent, `group`, link_doctype, link_fieldname
  HAVING COUNT(*) > 1
) d;
SQL
```

Only after testing succeeds, update production with a backup:

```bash
cd /home/frappe/frappe-bench
bench --site erp.inversionesbel.com backup --with-files
bench --site erp.inversionesbel.com migrate
bench --site erp.inversionesbel.com clear-cache
```

## Pull Request Review Rules

When reviewing a PR:

- Prioritize findings over summaries.
- Look for data-loss risk, fixture regression, security regression, permission drift, and migration failure.
- Verify whether fields are being removed from DocTypes.
- Check Server Scripts for repeated `After Save` side effects.
- Check Client Scripts for business logic that should be server-side.
- Check Web Pages and Pages for unintended public exposure.
- Check role changes against intended access.
- Do not merge until risks are documented or accepted.

## Commit and Push Rules

- Use one commit per explicit task.
- Use clear messages, for example:
  - `fix(fixtures): preserve ActividadObra peso field`
  - `fix(security): restrict confirmar contrato server-side`
  - `docs: add PR7 developer guide`
- Before pushing, confirm:

```bash
git status -sb
git log --oneline --decorate --max-count=5
```

## Communication Expectations

- Be explicit about what changed, where, and why.
- Report validations run and any validation not run.
- If production was touched, report the backup timestamp/path.
- If a risk remains, say so directly.
- Prefer small, reversible steps over broad edits.
