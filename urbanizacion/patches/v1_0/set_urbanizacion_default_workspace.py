import frappe


URBANIZACION_WORKSPACE = "Urbanizacion"


def execute() -> None:
    if not frappe.db.exists("Workspace", URBANIZACION_WORKSPACE):
        return

    users = frappe.db.sql(
        """
        select distinct u.name
        from `tabUser` u
        join `tabHas Role` hr on hr.parent = u.name
        where hr.role like 'Urbanizacion%%'
          and u.enabled = 1
          and u.user_type = 'System User'
          and coalesce(u.default_workspace, '') = ''
        order by u.name
        """,
        as_dict=True,
    )

    for row in users:
        frappe.db.set_value(
            "User",
            row.name,
            "default_workspace",
            URBANIZACION_WORKSPACE,
            update_modified=True,
        )
        frappe.clear_cache(user=row.name)
