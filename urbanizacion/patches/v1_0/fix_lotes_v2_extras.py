import frappe

FACTOR = 1.418415
PRECIO_VARA = 90

_AUTO_KEYS = (
	'Precio base:',
	'Costo adicional:',
	'Cargo esquinero:',
	'Varas extras',
	'Descuento:',
	'Precio total:',
	'Monto de reservacion:',
	'Monto a financiar:',
	'Prima:',
	'Saldo neto de prima',
	'Lote esquinero:',
	'Metros extras:',
)


def _usd(n):
	return f"$ {float(n or 0):,.2f}"


def _rebuild_observaciones(cr):
	"""Replica la logica de calcularCarta del Client Script.
	Reconstruye solo las lineas automaticas y preserva las manuales.
	"""
	precio_base = float(cr.get('precio') or 0)
	adicional   = float(cr.get('costo_adicional') or 0)
	esquinero   = 2000.0 if cr.get('esquinero') == 'Si' else 0.0
	v2_extras   = float(cr.get('v2_extras') or 0)
	cv          = v2_extras * PRECIO_VARA
	md          = float(cr.get('descuento') or 0)
	mr          = float(cr.get('monto_reservacion') or 0)
	mp          = float(cr.get('monto_prima') or 0)
	pt          = float(cr.get('precio_total') or 0)
	mf          = float(cr.get('monto_financiar') or 0)
	sn          = float(cr.get('saldo_neto_prima') or 0)

	lines = [f'Precio base: {_usd(precio_base)}']
	if adicional > 0:
		lines.append(f'Costo adicional: +{_usd(adicional)}')
	if esquinero > 0:
		lines.append(f'Cargo esquinero: +{_usd(esquinero)}')
	if cv > 0:
		lines.append(f'Varas extras ({v2_extras:.2f} V2 x $90): +{_usd(cv)}')
	if md > 0:
		lines.append(f'Descuento: -{_usd(md)}')
	lines.append(f'Precio total: {_usd(pt)}')
	lines.append(f'Monto de reservacion: -{_usd(mr)}')
	lines.append(f'Monto a financiar: -{_usd(mf)}')
	lines.append(f'Prima: {_usd(max(mp, 0))}')
	if mr > 0:
		lines.append(f'  Saldo neto de prima (prima - reservacion): {_usd(max(sn, 0))}')

	existing = (cr.get('observaciones') or '').split('\n')
	user_lines = [
		l for l in existing
		if l.strip() and not any(l.strip().startswith(k) for k in _AUTO_KEYS)
	]
	return '\n'.join(lines + user_lines)


def execute():
	"""
	Corrige Lotes.v2_extras omitido por recalculate_varas_factor y propaga
	el cambio a CartaReserva (precio_total, monto_financiar, observaciones) y
	ContratoVenta (precio_total, monto_financiar, saldo_prima, desembolsos).

	Solo afecta lotes con m2_extras > 0 y cartas en estado Activa.
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

	# Rebuild observaciones replicando la logica de calcularCarta del Client Script.
	# Lee precio_total y monto_financiar ya actualizados por el UPDATE anterior.
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
