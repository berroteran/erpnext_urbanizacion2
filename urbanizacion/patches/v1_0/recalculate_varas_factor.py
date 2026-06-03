import frappe


def execute():
	"""
	Recalcula campos de varas cuadradas usando el factor aprobado por catastro (1.418415).
	Factor anterior: 1.4196
	Factor nuevo:    1.418415

	Tablas afectadas:
	  - tabLotes         : v2_terreno, v2_casa
	  - tabCatalogoModelos: area_varas
	  - tabCartaReserva  : v2_terreno, v2_casa
	"""
	FACTOR = 1.418415

	frappe.db.sql(
		"UPDATE tabLotes SET v2_terreno = m2_terreno * %s WHERE m2_terreno IS NOT NULL AND m2_terreno > 0",
		(FACTOR,)
	)
	frappe.db.sql(
		"UPDATE tabLotes SET v2_casa = m2_casa * %s WHERE m2_casa IS NOT NULL AND m2_casa > 0",
		(FACTOR,)
	)
	frappe.db.sql(
		"UPDATE tabCatalogoModelos SET area_varas = area_construccion * %s WHERE area_construccion IS NOT NULL AND area_construccion > 0",
		(FACTOR,)
	)
	frappe.db.sql(
		"UPDATE tabCartaReserva SET v2_terreno = m2_terreno * %s WHERE m2_terreno IS NOT NULL AND m2_terreno > 0",
		(FACTOR,)
	)
	frappe.db.sql(
		"UPDATE tabCartaReserva SET v2_casa = m2_casa * %s WHERE m2_casa IS NOT NULL AND m2_casa > 0",
		(FACTOR,)
	)

	frappe.db.commit()
