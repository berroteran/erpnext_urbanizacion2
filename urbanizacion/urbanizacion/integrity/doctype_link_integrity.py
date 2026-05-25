import frappe

UNIQUE_INDEX_NAME = "uniq_parent_group_link_field"


def deduplicate_doctype_link_rows() -> int:
    """Remove duplicate DocType Link rows, keeping one row per logical key."""
    rows = frappe.db.get_all(
        "DocType Link",
        fields=["name", "parent", "group", "link_doctype", "link_fieldname"],
        order_by="parent asc, `group` asc, link_doctype asc, link_fieldname asc, name asc",
    )

    seen = set()
    remove_names = []
    for row in rows:
        key = (
            row.parent,
            row.group,
            row.link_doctype,
            row.link_fieldname or "",
        )
        if key in seen:
            remove_names.append(row.name)
        else:
            seen.add(key)

    for name in remove_names:
        frappe.delete_doc("DocType Link", name, ignore_permissions=True, force=True)

    return len(remove_names)


def has_unique_index() -> bool:
    rows = frappe.db.sql(
        """
        select index_name
        from information_schema.statistics
        where table_schema = database()
          and table_name = "tabDocType Link"
          and index_name = %(index_name)s
          and non_unique = 0
        limit 1
        """,
        {"index_name": UNIQUE_INDEX_NAME},
    )
    return bool(rows)


def ensure_unique_index() -> bool:
    """Create unique index for logical DocType Link key if missing."""
    if has_unique_index():
        return False

    # Avoid implicit-commit guard in frappe.db.sql for DDL.
    frappe.db.commit()
    frappe.db._cursor.execute(
        """
        alter table `tabDocType Link`
        add unique index `uniq_parent_group_link_field`
        (`parent`, `group`, `link_doctype`, `link_fieldname`)
        """
    )
    frappe.db.commit()
    return True


def harden_doctype_link_integrity() -> tuple[int, bool]:
    """Apply dedupe + unique index hardening. Returns (rows_removed, index_created)."""
    rows_removed = deduplicate_doctype_link_rows()
    index_created = ensure_unique_index()
    return rows_removed, index_created
