import frappe
from urbanizacion.patches.v1_0.fix_lotes_v2_extras import PRECIO_VARA, _rebuild_observaciones


def execute():
	"""Corrige monto_financiar y observaciones tras recalcular v2_extras."""
	frappe.db.sql(
		"""
		UPDATE `tabCartaReserva` cr
		JOIN `tabLotes` l ON l.name = cr.lote
		SET
			cr.monto_financiar = GREATEST(
				ROUND(
					COALESCE(cr.precio, 0)
					+ COALESCE(cr.costo_adicional, 0)
					+ CASE WHEN cr.esquinero = 'Si' THEN 2000 ELSE 0 END
					+ COALESCE(l.v2_extras, 0) * %s
					- COALESCE(cr.descuento, 0),
				2) - COALESCE(cr.monto_prima, 0),
			0)
		WHERE cr.estado = 'Activa'
		  AND l.m2_extras IS NOT NULL AND l.m2_extras > 0
		""",
		(PRECIO_VARA,),
	)

	cartas = frappe.db.sql(
		"""
		SELECT cr.name, cr.precio, cr.costo_adicional, cr.esquinero,
		       cr.descuento, cr.monto_reservacion, cr.monto_prima,
		       cr.saldo_neto_prima, cr.precio_total, cr.monto_financiar,
		       cr.observaciones, l.v2_extras
		FROM `tabCartaReserva` cr
		JOIN `tabLotes` l ON l.name = cr.lote
		WHERE cr.estado = 'Activa'
		  AND l.m2_extras IS NOT NULL AND l.m2_extras > 0
		""",
		as_dict=True,
	)
	for cr in cartas:
		frappe.db.set_value(
			'CartaReserva',
			cr.name,
			'observaciones',
			_rebuild_observaciones(cr),
			update_modified=False,
		)

	frappe.db.sql(
		"""
		UPDATE `tabContratoVenta` cv
		JOIN `tabCartaReserva` cr ON cr.name = cv.carta_reserva
		JOIN `tabLotes` l ON l.name = cr.lote
		SET
			cv.precio_total    = cr.precio_total,
			cv.monto_financiar = cr.monto_financiar,
			cv.saldo_prima     = cr.saldo_neto_prima
		WHERE cr.estado = 'Activa'
		  AND l.m2_extras IS NOT NULL AND l.m2_extras > 0
		""",
	)

	frappe.db.sql(
		"""
		UPDATE `taburbDesembolso` d
		JOIN (
			SELECT cv.name, cv.monto_financiar
			FROM `tabContratoVenta` cv
			JOIN `tabCartaReserva` cr ON cr.name = cv.carta_reserva
			JOIN `tabLotes` l ON l.name = cr.lote
			WHERE cr.estado = 'Activa'
			  AND l.m2_extras IS NOT NULL AND l.m2_extras > 0
		) cv ON cv.name = d.parent
		SET d.monto = ROUND(cv.monto_financiar * d.porcentaje / 100, 2)
		WHERE d.parenttype = 'ContratoVenta'
		  AND (d.realizado = 0 OR d.realizado IS NULL)
		""",
	)
