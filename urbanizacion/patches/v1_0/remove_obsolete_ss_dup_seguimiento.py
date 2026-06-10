import frappe


def execute():
	"""
	Elimina SS-DUP-urbSeguimientoObra de la DB.
	El script validaba que la suma de pesos de actividades fuera 100%, pero el campo
	'peso' fue removido en el refactor bd8d275. El fixture ya no lo incluye desde
	ese commit, pero sync_fixtures no borra registros huerfanos.
	"""
	frappe.delete_doc("Server Script", "SS-DUP-urbSeguimientoObra", ignore_missing=True)
