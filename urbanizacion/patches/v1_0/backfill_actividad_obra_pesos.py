import frappe
from frappe.database.schema import add_column


ACTIVITY_WEIGHTS = {
	"Trazo y nivelación": 0.36,
	"Excavación Estructural": 0.86,
	"Mejoramiento": 0.11,
	"Acero de Fundaciones": 3.78,
	"Concreto de Fundaciones": 4.33,
	"Acero de Columnas y vigas": 5.62,
	"Malla de Paredes": 4.84,
	"Esperas Sanitarias": 0.93,
	"Esperas Eléctricas": 0.93,
	"Formaleta de Paredes": 3.95,
	"Concreto de Paredes": 13.6,
	"Estructura de Techos": 4.7,
	"Cubiertas de Techos": 1.36,
	"Flashing de Techos": 0.31,
	"Jamba Puertas y Ventanas": 0.25,
	"Conformación/Compactación": 0.15,
	"Cascote de Piso": 3.02,
	"Chapisco en Paredes": 0.92,
	"Fino en Paredes": 3.41,
	"Inst. Eléctricas": 3.55,
	"Inst. Sanitarias": 2.45,
	"Estructurado de Cielo Falso": 0.95,
	"Cielo Falso/Pasta": 2.03,
	"Fascias/Aleros": 0.41,
	"Lijado de Cielo Falso": 1.1,
	"Arenillado de Piso": 1.1,
	"Instalación Piso": 5.79,
	"Rodapíe de Piso": 0.28,
	"Rodapié de Piso": 0.28,
	"Marcos de Puertas": 2.28,
	"Puertas/Herrajes & Pintura": 2.87,
	"Ventanas": 4.05,
	"Azulejos en baño": 1.57,
	"Carpintería/Muebles": 3.98,
	"Pechera en Cocina": 0.7,
	"Accesorios Eléctricos": 2.92,
	"Aparatos Sanitarios": 3.48,
	"Pintura de Paredes y Cielo": 1.46,
	"Cajas de Registro": 0.4,
	"Cajas Pluvial+Línea": 0.42,
	"Biodigestor": 0.97,
	"Pozo de Absorción": 1.41,
	"Huellas Vehiculares": 0.85,
	"Conformación de Terreno": 0.87,
	"Anden Peatonal": 0.65,
}


def execute():
	"""Backfill historical construction activity weights and recalculate progress."""
	if not frappe.db.has_column("ActividadObra", "porcentaje_peso"):
		add_column("ActividadObra", "porcentaje_peso", "Float", precision=2, default=0, not_null=True)

	for activity, weight in ACTIVITY_WEIGHTS.items():
		frappe.db.sql(
			"""
			UPDATE `tabActividadObra`
			SET porcentaje_peso = %s
			WHERE actividad = %s
			  AND (porcentaje_peso IS NULL OR porcentaje_peso = 0)
			""",
			(weight, activity),
		)

	frappe.db.sql(
		"""
		UPDATE `tabSeguimientoObra` so
		LEFT JOIN (
			SELECT parent,
				SUM(CASE WHEN estado = %s THEN COALESCE(porcentaje_peso, 0) ELSE 0 END) AS avance
			FROM `tabActividadObra`
			GROUP BY parent
		) act ON act.parent = so.name
		SET so.porcentaje_avance = ROUND(COALESCE(act.avance, 0), 1)
		""",
		("Completada",),
	)
