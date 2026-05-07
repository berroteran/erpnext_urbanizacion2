import frappe


@frappe.whitelist()
def get_internal_import_page():
	# Reuse existing importer only for authenticated users with access to Lotes.
	if not frappe.has_permission("Lotes", ptype="read"):
		frappe.throw("No tiene permisos para acceder a Importar Lotes.")

	data = frappe.db.get_value(
		"Web Page",
		"importar-lotes",
		["main_section_html", "javascript", "title"],
		as_dict=True,
	)
	if not data:
		frappe.throw("No se encontró la configuración de Importar Lotes.")

	return {
		"title": data.title or "Importar Lotes",
		"html": data.main_section_html or "",
		"javascript": data.javascript or "",
	}
