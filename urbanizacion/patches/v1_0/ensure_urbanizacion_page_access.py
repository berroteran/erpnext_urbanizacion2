import frappe


URBANIZACION_ROLES = (
    "Urbanizacion Manager",
    "Urbanizacion Operador",
    "Urbanizacion Consulta",
    "Urbanizacion Vendedor",
    "Urbanizacion Tecnico",
)


def execute() -> None:
    for role in URBANIZACION_ROLES:
        _ensure_page_read_permission(role)

    frappe.clear_cache(doctype="Page")


def _ensure_page_read_permission(role: str) -> None:
    existing = frappe.db.exists(
        "Custom DocPerm",
        {"parent": "Page", "role": role, "permlevel": 0},
    )

    if existing:
        doc = frappe.get_doc("Custom DocPerm", existing)
        doc.read = 1
        doc.write = 0
        doc.create = 0
        doc.delete = 0
        doc.submit = 0
        doc.cancel = 0
        doc.save(ignore_permissions=True)
        return

    max_idx = (
        frappe.db.sql(
            "select coalesce(max(idx), 0) from `tabCustom DocPerm` where parent=%s",
            "Page",
        )[0][0]
        or 0
    )
    frappe.get_doc(
        {
            "doctype": "Custom DocPerm",
            "parent": "Page",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "idx": max_idx + 1,
            "role": role,
            "permlevel": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 0,
            "export": 0,
            "import": 0,
            "share": 0,
            "print": 0,
            "email": 0,
            "if_owner": 0,
        }
    ).insert(ignore_permissions=True)
