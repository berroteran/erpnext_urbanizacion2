import frappe


MANAGED_DOCTYPES = (
	"Proyectos",
	"CatalogoModelos",
	"ContratoVenta",
	"CartaReserva",
	"Lotes",
	"Adendum",
	"AdendumExtra",
	"ActividadObra",
	"FotoAvance",
	"SeguimientoObra",
	"CambioLote",
)

PERMISSION_FIELDS = (
	"idx",
	"role",
	"permlevel",
	"select",
	"read",
	"write",
	"create",
	"delete",
	"submit",
	"cancel",
	"amend",
	"report",
	"import",
	"export",
	"print",
	"email",
	"share",
	"if_owner",
	"set_user_permissions",
)


def sync_custom_docperms(doctypes=None):
	"""Keep Custom DocPerm aligned with app-managed DocType permissions.

	Frappe gives Custom DocPerm priority over DocPerm. If stale Custom DocPerm
	rows exist, field-level permissions from fixtures can be silently ignored.
	"""
	doctypes = doctypes or MANAGED_DOCTYPES

	for doctype in doctypes:
		source_permissions = frappe.get_all(
			"DocPerm",
			filters={"parent": doctype, "parenttype": "DocType", "parentfield": "permissions"},
			fields=PERMISSION_FIELDS,
			order_by="idx asc",
		)
		if not source_permissions:
			continue

		for name in frappe.get_all("Custom DocPerm", filters={"parent": doctype}, pluck="name"):
			frappe.delete_doc("Custom DocPerm", name, force=True, ignore_permissions=True)

		for permission in source_permissions:
			doc = frappe.new_doc("Custom DocPerm")
			doc.parent = doctype
			for fieldname in PERMISSION_FIELDS:
				doc.set(fieldname, permission.get(fieldname))
			doc.insert(ignore_permissions=True)

		frappe.clear_cache(doctype=doctype)
		frappe.clear_document_cache("DocType", doctype)


def after_migrate():
	sync_custom_docperms()
