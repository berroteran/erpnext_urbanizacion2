import frappe


def execute():
	"""
	Copia precio_base del CatalogoModelos al campo precio de cada Lote existente.

	Tabla afectada:
	  - tabLotes: precio = CatalogoModelos.precio_base
	"""
	frappe.db.sql("""
		UPDATE tabLotes AS l
		JOIN tabCatalogoModelos AS c ON c.name = l.catalogo_modelos
		SET l.precio = c.precio_base
		WHERE (l.precio IS NULL OR l.precio = 0)
		  AND c.precio_base > 0
	""")

	frappe.db.commit()
