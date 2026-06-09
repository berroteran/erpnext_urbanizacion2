import frappe

FACTOR = 1.418415
PRECIO_VARA = 90


def execute():
	"""
	Corrige Lotes.v2_extras omitido por recalculate_varas_factor y propaga
	el cambio a CartaReserva (precio_total, monto_financiar) y ContratoVenta
	(precio_total, monto_financiar, saldo_prima, desembolsos).

	Solo afecta lotes con m2_extras > 0.
	"""
	frappe.db.sql(
		"UPDATE `tabLotes` SET v2_extras = m2_extras * %s"
		" WHERE m2_extras IS NOT NULL AND m2_extras > 0",
		(FACTOR,),
	)

	frappe.db.sql(
		"""
		UPDATE `tabCartaReserva` cr
		JOIN `tabLotes` l ON l.name = cr.lote
		SET
			cr.precio_total = ROUND(
				COALESCE(cr.precio, 0)
				+ COALESCE(cr.costo_adicional, 0)
				+ CASE WHEN cr.esquinero = 'Si' THEN 2000 ELSE 0 END
				+ COALESCE(l.v2_extras, 0) * %s
				- COALESCE(cr.descuento, 0),
			2),
			cr.monto_financiar = GREATEST(
				cr.precio_total - COALESCE(cr.monto_prima, 0),
			0)
		WHERE cr.estado = 'Activa'
		  AND l.m2_extras IS NOT NULL AND l.m2_extras > 0
		""",
		(PRECIO_VARA,),
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
			WHERE l.m2_extras IS NOT NULL AND l.m2_extras > 0
		) cv ON cv.name = d.parent
		SET d.monto = ROUND(cv.monto_financiar * d.porcentaje / 100, 2)
		WHERE d.parenttype = 'ContratoVenta'
		  AND (d.realizado = 0 OR d.realizado IS NULL)
		""",
	)
