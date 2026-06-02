# Agent Instructions for `urbanizacion`

This repository contains the private Frappe/ERPNext v15 app `urbanizacion` for Inversiones BEL. Treat it as production-impacting business software, not as a throwaway customization.

These instructions are aligned with the Frappe Framework Guides and Bench reference docs:

- Frappe Guides index: https://docs.frappe.io/framework/user/en/guides
- Exporting customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- Doctype production migrations: https://docs.frappe.io/framework/user/en/guides/deployment/how-to-migrate-doctype-changes-to-production
- Migrations: https://docs.frappe.io/framework/user/en/guides/deployment/migrations
- Client Script: https://docs.frappe.io/framework/user/en/desk/scripting/client-script
- Server Script: https://docs.frappe.io/framework/user/en/desk/scripting/server-script
- Hooks: https://docs.frappe.io/framework/user/en/python-api/hooks
- Workspace access: https://docs.frappe.io/framework/user/en/desk/workspace/access
- `bench migrate`: https://docs.frappe.io/framework/user/en/bench/reference/migrate
- `bench backup`: https://docs.frappe.io/framework/user/en/bench/reference/backup

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
- If a change affects permissions, workflows, Server Scripts, Client Scripts, DocTypes, hooks, pages, workspaces, or fixtures, assume it can affect production behavior.

## Citation and Dispute Handling

- When correcting, refuting, or pushing back on a user request about Frappe/ERPNext behavior, cite the relevant official documentation URL from the reference list above.
- Prefer official Frappe/ERPNext/Bench documentation over memory or third-party examples.
- If documentation and local site behavior differ, state both clearly: cite the documentation, then show the local command/output that proves the site-specific behavior.
- For risky actions such as production migration, fixture overwrite, field removal, Server Script behavior, Client Script limitations, permissions, or workspace visibility, include the specific URL that supports the recommendation.
- If no source was checked, do not present the claim as documentation-backed; say it is an inference from local code or prior project context.

## Official Frappe Behavior to Respect

- `bench migrate` updates the site to the current app state. According to the Bench reference, it runs migrate hooks, patches, schema/background-job sync, fixture sync, dashboard/desktop-icon/web-page sync, translations, search index rebuild, and `after_migrate` hooks.
- Frappe schema changes come from DocType JSON files in the app. Developer mode updates DocType `.json` files automatically when saving DocTypes in a development environment.
- Deleted DocType fields are soft-deleted: database columns are not removed immediately, but fields stop being visible/usable through document metadata. Do not treat this as harmless; it can still break UI, reports, scripts, permissions, and business behavior.
- Frappe does not support reverse schema migrations. Do not rely on "rolling back migrate" as a safety plan.
- Data migrations belong in app patches: create an `execute` function in a Python patch module and register it in `patches.txt`, or use `bench create-patch` where appropriate.
- Exported customizations can replace property setters and custom permissions on the target site. Review customization exports carefully before deploying.
- Client Script validation only applies in the standard browser form view. If the rule must also apply through API, imports, background jobs, or System Console, implement server-side validation.
- Server Scripts are disabled by default in Frappe v15 for security on shared benches. This app may use Server Script fixtures, so verify server scripts are enabled on target sites and prefer Python controllers/hooks for durable business-critical logic.
- Workspaces can be restricted by module and role. A visible Workspace is not enough; its cards, shortcuts, links, and target DocTypes must also be permitted for the user.

## Frappe/ERPNext Development Rules

- Prefer app code, DocType JSON, hooks, patches, and fixtures over database-only changes.
- Changes made in Desk must be exported to code before they are considered deployable.
- After changing fixtures or DocTypes, run `bench --site <site> migrate` to verify import and schema behavior.
- Do not remove DocType fields if data may already exist. If a field must be removed, document the decision and provide a patch or archival plan.
- Do not depend on soft-deleted columns for normal runtime behavior. If old values matter, migrate/archive them before removing the field from metadata.
- Keep child-table DocTypes out of workspace navigation unless there is a specific reason.
- Use server-side validation for business-critical rules. Client Scripts are UX helpers, not security boundaries.
- For role or permission-sensitive features, validate permissions on the server, not only in JavaScript.
- Keep public web exposure off for internal operational pages unless explicitly approved.
- Prefer Python hooks/controllers over Server Scripts for long-lived, business-critical logic when practical.

## Fixtures and Customizations

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
- Check for accidental deletion of fields, permissions, roles, pages, dashboards, desktop icons, workspace blocks, or property setters.
- Keep `DocType Link` records deduplicated.
- Do not reintroduce public access for internal pages.
- Review permission fixtures/customizations carefully because exported customizations can replace target-site custom permissions/property setters.
- Remember that migrate synchronizes fixtures, dashboards, desktop icons, and web pages, so fixture mistakes are deployment mistakes.

Useful checks:

```bash
python3 -m json.tool urbanizacion/fixtures/doctype.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/client_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/server_script.json >/dev/null
python3 -m json.tool urbanizacion/fixtures/print_format.json >/dev/null
```

## Hooks, Server Scripts, and Client Scripts

- Use `doc_events` hooks for durable CRUD-event logic when possible.
- Use `doctype_js` or app JS files for durable form enhancements when practical.
- Treat Server Scripts as powerful but security-sensitive. Confirm they are enabled intentionally on each target site.
- Avoid `After Save` side effects that can repeat on every save unless transition detection is explicit.
- For transition-based behavior, compare the current document with `doc_before_save` or `doc.get_doc_before_save()`.
- Do not swallow critical failures with broad `except Exception: pass`; log or surface errors when business state depends on the action.
- Client Scripts may improve form UX, filters, buttons, read-only states, and alerts, but must not be the only enforcement layer for business rules.

## Workspace and Desk Rules

- End users should access the module through `/app/<workspace-slug>`, not `/app/module-def/<Module>`.
- Keep the `Urbanizacion` Workspace visible only to intended roles/modules.
- Ensure Workspace content blocks, cards, shortcuts, and links render real user-facing content.
- Validate as a target non-Administrator user, not only as Administrator/System Manager.
- If an item does not appear, check in this order: Workspace access, role permissions, DocType `istable`, card/shortcut content, cache.

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

When Python code changes, run targeted syntax checks and tests where possible:

```bash
python3 -m compileall urbanizacion
```

Validate on testing first:

```bash
cd /home/frappe/frappe-bench
bench --site testing15.inversionesbel.com migrate
bench --site testing15.inversionesbel.com clear-cache
```

Recommended metadata checks:

```bash
bench --site testing15.inversionesbel.com mariadb <<'SQL'
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

Only after testing succeeds, update production with a full backup:

```bash
cd /home/frappe/frappe-bench
bench --site erp.inversionesbel.com backup --with-files
bench --site erp.inversionesbel.com migrate
bench --site erp.inversionesbel.com clear-cache
```

After production migration, repeat the same metadata checks on `erp.inversionesbel.com` and report the backup timestamp/path.

## Pull Request Review Rules

When reviewing a PR:

- Prioritize findings over summaries.
- Look for data-loss risk, fixture regression, security regression, permission drift, and migration failure.
- Verify whether fields are being removed from DocTypes. Remember: soft-deleted fields can still break metadata-driven behavior.
- Check whether permission changes require patches such as `frappe.permissions.reset_perms(...)` rather than assuming permissions auto-update.
- Check Server Scripts and hooks for repeated `After Save` side effects.
- Check Client Scripts for business logic that should be server-side.
- Check Web Pages, Pages, and Workspaces for unintended public exposure or role drift.
- Check role changes against intended access.
- Do not merge until risks are documented or accepted.

## Commit and Push Rules

- Use one commit per explicit task.
- Use clear messages, for example:
  - `fix(fixtures): preserve ActividadObra peso field`
  - `fix(security): restrict confirmar contrato server-side`
  - `docs: align agent instructions with Frappe guides`
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
