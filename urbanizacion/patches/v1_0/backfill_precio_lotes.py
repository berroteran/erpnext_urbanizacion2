import frappe


def execute():
	"""
	Copia precio_base del CatalogoModelos al campo precio de cada Lote existente
	y sincroniza ese precio a las CartaReservas activas vinculadas.

	Tablas afectadas:
	  - tabLotes        : precio = CatalogoModelos.precio_base
	  - tabCartaReserva : precio = tabLotes.precio (cartas activas)
	"""
	frappe.db.sql("""
		UPDATE tabLotes AS l
		JOIN tabCatalogoModelos AS c ON c.name = l.catalogo_modelos
		SET l.precio = c.precio_base
		WHERE (l.precio IS NULL OR l.precio = 0)
		  AND c.precio_base > 0
	""")

	frappe.db.sql("""
		UPDATE tabCartaReserva AS cr
		JOIN tabLotes AS l ON l.name = cr.lote
		SET cr.precio = l.precio
		WHERE cr.estado = 'Activa'
		  AND (cr.precio IS NULL OR cr.precio = 0)
		  AND l.precio > 0
	""")
