import frappe

from urbanizacion.urbanizacion.integrity.doctype_link_integrity import harden_doctype_link_integrity


URBANIZACION_LINKS = [
    {
        "parent": "Proyectos",
        "group": "Urbanizacion",
        "link_doctype": "Lotes",
        "link_fieldname": "proyecto",
    },
    {
        "parent": "Lotes",
        "group": "Urbanizacion",
        "link_doctype": "CartaReserva",
        "link_fieldname": "lote",
    },
    {
        "parent": "Lotes",
        "group": "Urbanizacion",
        "link_doctype": "ContratoVenta",
        "link_fieldname": "lote",
    },
    {
        "parent": "Lotes",
        "group": "Urbanizacion",
        "link_doctype": "SeguimientoObra",
        "link_fieldname": "lote",
    },
]


def ensure_doctype_link(parent: str, group: str, link_doctype: str, link_fieldname: str) -> bool:
    """Ensure a DocType Link row exists exactly once. Returns True if a row was created."""
    exists = frappe.db.exists(
        "DocType Link",
        {
            "parent": parent,
            "group": group,
            "link_doctype": link_doctype,
            "link_fieldname": link_fieldname,
        },
    )
    if exists:
        return False

    doc = frappe.get_doc("DocType", parent)
    doc.append(
        "links",
        {
            "group": group,
            "link_doctype": link_doctype,
            "link_fieldname": link_fieldname,
            "hidden": 0,
            "custom": 1,
        },
    )
    doc.save(ignore_permissions=True)
    return True


def sync_urbanizacion_doctype_links() -> int:
    """Idempotent sync for expected Urbanizacion dashboard connections."""
    created = 0
    for row in URBANIZACION_LINKS:
        created += int(
            ensure_doctype_link(
                parent=row["parent"],
                group=row["group"],
                link_doctype=row["link_doctype"],
                link_fieldname=row["link_fieldname"],
            )
        )
    return created


def after_migrate() -> None:
    """Hook: harden + sync expected links after every migrate."""
    removed, index_created = harden_doctype_link_integrity()
    created = sync_urbanizacion_doctype_links()
    if removed or index_created or created:
        frappe.logger().info(
            "Urbanizacion DocType Link hardening: removed=%s index_created=%s created=%s",
            removed,
            int(index_created),
            created,
        )
