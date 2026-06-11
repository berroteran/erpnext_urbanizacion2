import re

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}
	if not filters.get("proyecto"):
		frappe.throw(_("El filtro Proyecto es obligatorio"))

	columns = get_columns()
	data = get_data(filters)
	return columns, data


# ---------------------------------------------------------------------------
# Columns
# ---------------------------------------------------------------------------

def get_columns():
	return [
		{"label": _("No."),                    "fieldname": "idx",           "fieldtype": "Int",          "width": 55},
		{"label": _("Cliente"),                "fieldname": "cliente",        "fieldtype": "Data",         "width": 230},
		{"label": _("Estatus"),                "fieldname": "estatus",        "fieldtype": "Data",         "width": 110},
		{"label": _("Modelo"),                 "fieldname": "modelo",         "fieldtype": "Data",         "width": 100},
		{"label": _("Bloque"),                 "fieldname": "bloque",         "fieldtype": "Data",         "width": 80},
		{"label": _("M² Casa"),                "fieldname": "m2_casa",        "fieldtype": "Float",        "width": 80,  "precision": 2},
		{"label": _("Avance Obra"),            "fieldname": "avance",         "fieldtype": "Percent",      "width": 100},
		{"label": _("Por Ejecutar"),           "fieldname": "x_ejecutar",     "fieldtype": "Percent",      "width": 100},
		{"label": _("Valor Venta"),            "fieldname": "precio_total",   "fieldtype": "Currency",     "options": "USD", "width": 130},
		{"label": _("Banco"),                  "fieldname": "banco",          "fieldtype": "Data",         "width": 90},
		{"label": _("Prima"),                  "fieldname": "monto_prima",    "fieldtype": "Currency",     "options": "USD", "width": 120},
		{"label": _("Fecha Reserva"),          "fieldname": "fecha_reserva",  "fieldtype": "Date",         "width": 110},
		{"label": _("Reserva Pagada"),         "fieldname": "monto_reserva",  "fieldtype": "Currency",     "options": "USD", "width": 120},
		{"label": _("Abonos Prima"),           "fieldname": "abonos_prima",   "fieldtype": "Currency",     "options": "USD", "width": 120},
		{"label": _("Saldo Prima"),            "fieldname": "saldo_prima",    "fieldtype": "Currency",     "options": "USD", "width": 120},
		{"label": _("Línea de Crédito"),       "fieldname": "linea_credito",  "fieldtype": "Currency",     "options": "USD", "width": 135},
		{"label": _("1er Desemb. Fecha"),      "fieldname": "des1_fecha",     "fieldtype": "Date",         "width": 120},
		{"label": _("1er Desembolso"),         "fieldname": "des1_monto",     "fieldtype": "Currency",     "options": "USD", "width": 130},
		{"label": _("2do Desemb. Fecha"),      "fieldname": "des2_fecha",     "fieldtype": "Date",         "width": 120},
		{"label": _("2do Desembolso"),         "fieldname": "des2_monto",     "fieldtype": "Currency",     "options": "USD", "width": 130},
		{"label": _("3er Desemb. Fecha"),      "fieldname": "des3_fecha",     "fieldtype": "Date",         "width": 120},
		{"label": _("3er Desembolso"),         "fieldname": "des3_monto",     "fieldtype": "Currency",     "options": "USD", "width": 130},
		{"label": _("4to Desemb. Fecha"),      "fieldname": "des4_fecha",     "fieldtype": "Date",         "width": 120},
		{"label": _("4to Desembolso"),         "fieldname": "des4_monto",     "fieldtype": "Currency",     "options": "USD", "width": 130},
		{"label": _("Saldo Banco"),            "fieldname": "saldo_banco",    "fieldtype": "Currency",     "options": "USD", "width": 120},
		{"label": _("Saldo Cliente Proyect."), "fieldname": "saldo_cliente",  "fieldtype": "Currency",     "options": "USD", "width": 155},
		{"label": _("Alerta"),                 "fieldname": "alerta",         "fieldtype": "Data",         "width": 95},
		{"label": _("Contrato"),               "fieldname": "contrato",       "fieldtype": "Link",         "width": 145, "options": "ContratoVenta"},
		{"label": _("Carta Reserva"),          "fieldname": "carta_reserva",  "fieldtype": "Link",         "width": 145, "options": "CartaReserva"},
	]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def get_data(filters):
	proyecto = filters.get("proyecto")

	# 1. All lotes for this project, ordered numerically
	lotes = frappe.db.sql("""
		SELECT
			l.name, l.bloque, l.numero_lote, l.m2_casa, l.precio AS lote_precio,
			l.estado AS lote_estado,
			COALESCE(cm.modelo, l.catalogo_modelos, '') AS modelo
		FROM `tabLotes` l
		LEFT JOIN `tabCatalogoModelos` cm ON cm.name = l.catalogo_modelos
		WHERE l.proyecto = %s
	""", proyecto, as_dict=True)

	if not lotes:
		return []

	# Sort lotes numerically (handles "L-1", "L-10", "B2-5", etc.)
	lotes.sort(key=lambda x: _natural_key(x.numero_lote or ""))
	lote_names = [l.name for l in lotes]

	# 2. CartaReserva – active first, then most recently modified
	#    We take one carta per lote: prefer Activa, fallback to most recent Cancelada
	cartas_raw = frappe.db.sql("""
		SELECT
			cr.name, cr.lote, cr.nombre_solicitante, cr.banco,
			cr.monto_prima, cr.monto_reservacion, cr.saldo_neto_prima,
			cr.monto_financiar, cr.estado, cr.fecha,
			cr.precio AS cr_precio
		FROM `tabCartaReserva` cr
		WHERE cr.lote IN %s
		ORDER BY
			CASE cr.estado WHEN 'Activa' THEN 0 ELSE 1 END ASC,
			cr.modified DESC
	""", [lote_names], as_dict=True)

	carta_por_lote = {}
	for cr in cartas_raw:
		if cr.lote not in carta_por_lote:
			carta_por_lote[cr.lote] = cr

	# 3. ContratoVenta – one per lote (most recent)
	contratos_raw = frappe.db.sql("""
		SELECT
			cv.name, cv.lote, cv.carta_reserva,
			cv.nombre_comprador, cv.nombre_comprador2,
			cv.precio_total, cv.monto_prima, cv.monto_reserva,
			cv.saldo_prima, cv.monto_financiar, cv.confirmado
		FROM `tabContratoVenta` cv
		WHERE cv.lote IN %s
		ORDER BY cv.modified DESC
	""", [lote_names], as_dict=True)

	contrato_por_lote = {}
	for cv in contratos_raw:
		if cv.lote not in contrato_por_lote:
			contrato_por_lote[cv.lote] = cv

	# 4. Desembolsos realizados for all contratos
	contrato_names = [cv.name for cv in contratos_raw]
	desembolsos_por_contrato = {}
	if contrato_names:
		desembolsos = frappe.db.sql("""
			SELECT parent, monto, realizado, fecha_realizado, idx
			FROM `taburbDesembolso`
			WHERE parent IN %s
			ORDER BY parent, idx ASC
		""", [contrato_names], as_dict=True)
		for d in desembolsos:
			desembolsos_por_contrato.setdefault(d.parent, []).append(d)

	# 5. SeguimientoObra – most recent per lote (for construction progress)
	seguimientos_raw = frappe.db.sql("""
		SELECT lote, porcentaje_avance
		FROM `tabSeguimientoObra`
		WHERE lote IN %s
		ORDER BY modified DESC
	""", [lote_names], as_dict=True)

	seguimiento_por_lote = {}
	for s in seguimientos_raw:
		if s.lote not in seguimiento_por_lote:
			seguimiento_por_lote[s.lote] = s

	# 6. Build rows
	estatus_filter = filters.get("estatus")
	banco_filter = filters.get("banco")

	rows = []
	for lote in lotes:
		carta = carta_por_lote.get(lote.name)
		contrato = contrato_por_lote.get(lote.name)
		desembolsos = desembolsos_por_contrato.get(contrato.name if contrato else "", [])
		seguimiento = seguimiento_por_lote.get(lote.name)

		row = _build_row(lote, carta, contrato, desembolsos, seguimiento)

		if estatus_filter and row["estatus"] != estatus_filter:
			continue
		if banco_filter and row["banco"] != banco_filter:
			continue

		rows.append(row)

	for i, row in enumerate(rows, 1):
		row["idx"] = i

	return rows


# ---------------------------------------------------------------------------
# Row builder
# ---------------------------------------------------------------------------

def _build_row(lote, carta, contrato, desembolsos, seguimiento=None):
	estatus = _get_estatus(lote, carta, contrato)

	# --- Financial fields: contrato is authoritative, carta is fallback ---
	if contrato:
		cliente = contrato.nombre_comprador or ""
		if contrato.nombre_comprador2:
			cliente += " / " + contrato.nombre_comprador2
		precio_total  = contrato.precio_total  or 0
		monto_prima   = contrato.monto_prima   or 0
		monto_reserva = contrato.monto_reserva or 0
		saldo_prima   = contrato.saldo_prima   or 0
		linea_credito = contrato.monto_financiar or 0
		banco         = (carta.banco if carta else "") or ""
		fecha_reserva = carta.fecha if carta else None
	elif carta:
		cliente       = carta.nombre_solicitante or ""
		precio_total  = carta.cr_precio          or 0
		monto_prima   = carta.monto_prima        or 0
		monto_reserva = carta.monto_reservacion  or 0
		saldo_prima   = carta.saldo_neto_prima   or 0
		linea_credito = carta.monto_financiar    or 0
		banco         = carta.banco              or ""
		fecha_reserva = carta.fecha
	else:
		cliente       = ""
		precio_total  = lote.lote_precio or 0
		monto_prima   = 0
		monto_reserva = 0
		saldo_prima   = 0
		linea_credito = 0
		banco         = ""
		fecha_reserva = None

	# --- Abonos de prima: pagos realizados contra la prima (excluye reserva inicial) ---
	abonos_prima = max(0, monto_prima - monto_reserva - saldo_prima)

	# --- Avance de obra desde SeguimientoObra ---
	avance     = (seguimiento.porcentaje_avance or 0) if seguimiento else 0
	x_ejecutar = max(0, 100 - avance)

	# --- Desembolsos (up to 4, ordered by idx) ---
	des = {}
	for i, d in enumerate(desembolsos[:4], 1):
		if d.realizado:
			des[f"des{i}_fecha"]  = d.fecha_realizado
			des[f"des{i}_monto"]  = d.monto or 0
		else:
			des[f"des{i}_fecha"]  = None
			des[f"des{i}_monto"]  = 0

	total_desembolsado = sum(d.monto or 0 for d in desembolsos if d.realizado)
	saldo_banco   = linea_credito - total_desembolsado
	saldo_cliente = saldo_prima + saldo_banco
	alerta        = "SOBREGIRO" if saldo_banco < 0 else ""

	return {
		"idx":           0,
		"cliente":        cliente,
		"estatus":        estatus,
		"alerta":         alerta,
		"modelo":         lote.modelo or "",
		"bloque":         lote.bloque or "",
		"m2_casa":        lote.m2_casa or 0,
		"avance":         avance,
		"x_ejecutar":     x_ejecutar,
		"precio_total":   precio_total,
		"banco":          banco,
		"monto_prima":    monto_prima,
		"fecha_reserva":  fecha_reserva,
		"monto_reserva":  monto_reserva,
		"abonos_prima":   abonos_prima,
		"saldo_prima":    saldo_prima,
		"linea_credito":  linea_credito,
		"des1_fecha":     des.get("des1_fecha"),
		"des1_monto":     des.get("des1_monto", 0),
		"des2_fecha":     des.get("des2_fecha"),
		"des2_monto":     des.get("des2_monto", 0),
		"des3_fecha":     des.get("des3_fecha"),
		"des3_monto":     des.get("des3_monto", 0),
		"des4_fecha":     des.get("des4_fecha"),
		"des4_monto":     des.get("des4_monto", 0),
		"saldo_banco":    saldo_banco,
		"saldo_cliente":  saldo_cliente,
		"contrato":       contrato.name if contrato else "",
		"carta_reserva":  carta.name if carta else "",
	}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_estatus(lote, carta, contrato):
	if contrato and contrato.confirmado:
		return "FORMALIZADO"
	# Carta cancelada tiene precedencia sobre contrato no confirmado (dato sucio)
	if carta and carta.estado == "Cancelada" and (not contrato or not contrato.confirmado):
		return "CANCELADA"
	if contrato and not contrato.confirmado:
		return "RESERVA"
	if carta and carta.estado == "Activa":
		return "RESERVA"
	return "INVENTARIO"


def _natural_key(text):
	"""Sort key that orders strings with embedded numbers numerically."""
	return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", text)]
