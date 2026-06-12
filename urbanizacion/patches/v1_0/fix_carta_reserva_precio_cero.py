import frappe


def execute():
	"""
	Corrige CartaReserva records donde precio=0 por error de merge.
	Toma Lotes.precio como fuente de verdad y recalcula precio_total,
	monto_financiar y saldo_neto_prima con la misma lógica del Client Script.
	"""
	affected = frappe.db.get_all(
		"CartaReserva",
		filters={"precio": 0, "lote": ["not in", ["", None]]},
		fields=[
			"name", "lote", "costo_adicional", "esquinero",
			"descuento", "monto_prima", "monto_reservacion",
		],
	)

	if not affected:
		frappe.logger().info("fix_carta_reserva_precio_cero: sin registros afectados.")
		return

	fixed = 0
	skipped = 0

	for cr in affected:
		lote_data = frappe.db.get_value(
			"Lotes", cr["lote"], ["precio", "v2_extras"], as_dict=True
		)

		if not lote_data or not lote_data.get("precio"):
			frappe.logger().warning(
				f"fix_carta_reserva_precio_cero: {cr['name']} — lote {cr['lote']} "
				"sin precio, se omite."
			)
			skipped += 1
			continue

		precio         = lote_data.precio or 0
		v2_extras      = lote_data.v2_extras or 0
		adicional      = cr.costo_adicional or 0
		cargo_esquinero = 2000 if cr.esquinero == "Si" else 0
		cargo_extras   = v2_extras * 90
		descuento      = cr.descuento or 0
		monto_prima    = cr.monto_prima or 0
		monto_reserva  = cr.monto_reservacion or 0

		precio_total     = precio + adicional + cargo_esquinero + cargo_extras - descuento
		monto_financiar  = max(0, precio_total - monto_prima)
		saldo_neto_prima = max(0, monto_prima - monto_reserva)

		frappe.db.set_value(
			"CartaReserva",
			cr["name"],
			{
				"precio":          precio,
				"precio_total":    precio_total,
				"monto_financiar": monto_financiar,
				"saldo_neto_prima": saldo_neto_prima,
			},
			update_modified=True,
		)

		frappe.logger().info(
			f"fix_carta_reserva_precio_cero: {cr['name']} "
			f"precio={precio} precio_total={precio_total} "
			f"monto_financiar={monto_financiar} saldo_neto_prima={saldo_neto_prima}"
		)
		fixed += 1

	frappe.logger().info(
		f"fix_carta_reserva_precio_cero: {fixed} corregido(s), {skipped} omitido(s) "
		f"de {len(affected)} afectado(s)."
	)
