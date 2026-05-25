import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "fixtures"


def _load(name):
    with (BASE / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _dump(name, data):
    with (BASE / name).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
        f.write("\n")


def normalize_doctype_link():
    rows = _load("doctype_link.json")
    seen = set()
    out = []
    for row in rows:
        key = (
            row.get("parent") or "",
            row.get("group") or "",
            row.get("link_doctype") or "",
            row.get("link_fieldname") or "",
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)

    out.sort(
        key=lambda r: (
            r.get("parent") or "",
            r.get("group") or "",
            r.get("link_doctype") or "",
            r.get("link_fieldname") or "",
            r.get("name") or "",
        )
    )

    if out != rows:
        _dump("doctype_link.json", out)


def audit_critical_fixtures():
    checks = {
        "doctype.json": "expected custom DocTypes exported",
        "workspace.json": "expected Urbanizacion workspace",
        "web_page.json": "expected importar-lotes page",
    }
    for filename, note in checks.items():
        data = _load(filename)
        if not isinstance(data, list) or not data:
            raise ValueError(f"{filename}: invalid or empty fixture ({note})")


if __name__ == "__main__":
    normalize_doctype_link()
    audit_critical_fixtures()
