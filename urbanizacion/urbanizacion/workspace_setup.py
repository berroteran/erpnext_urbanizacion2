"""
Agrega el reporte CXC al workspace de Accounting de forma idempotente.
Se llama desde after_migrate en hooks.py — funciona en los 3 entornos
(local, testing, producción) sin necesidad de configuración manual.
"""

import json

import frappe

CARD_LABEL = "Cuentas por Cobrar Urbanizacion"
REPORT_NAME = "Cuentas por Cobrar Urbanizacion"
REPORT_LABEL = "Cuentas por Cobrar"
WORKSPACE = "Accounting"
CARD_BLOCK_ID = "urb-cxc-urbanizacion-cuentas-cobrar"


def after_migrate():
	try:
		if not frappe.db.exists("Workspace", WORKSPACE):
			return
		if not frappe.db.exists("Report", REPORT_NAME):
			return

		ws = frappe.get_doc("Workspace", WORKSPACE)

		_ensure_links(ws)
		_ensure_content_block(ws)

		ws.save(ignore_permissions=True)
		# bench migrate corre fuera de una request; no hay commit automático garantizado
		frappe.db.commit()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "workspace_setup.after_migrate")


def _ensure_links(ws):
	"""Añade Card Break + Link en ws.links si no existen ambos."""
	has_card_break = any(
		l.type == "Card Break" and l.label == CARD_LABEL
		for l in ws.links
	)
	has_link = any(
		l.type == "Link" and l.link_to == REPORT_NAME
		for l in ws.links
	)
	if has_card_break and has_link:
		return

	if not has_card_break:
		ws.append("links", {
			"type": "Card Break",
			"label": CARD_LABEL,
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		})
	if not has_link:
		ws.append("links", {
			"type": "Link",
			"label": REPORT_LABEL,
			"link_type": "Report",
			"link_to": REPORT_NAME,
			"is_query_report": 1,
			"hidden": 0,
			"onboard": 0,
		})


def _ensure_content_block(ws):
	"""Añade el bloque card en ws.content si no existe."""
	content = json.loads(ws.content or "[]")

	already_in_content = any(
		b.get("type") == "card" and b.get("data", {}).get("card_name") == CARD_LABEL
		for b in content
	)
	if already_in_content:
		return

	content.append({
		"id": CARD_BLOCK_ID,
		"type": "card",
		"data": {"card_name": CARD_LABEL, "col": 4},
	})
	ws.content = json.dumps(content)
