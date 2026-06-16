import frappe


def execute():
	"""
	Backfill estado='Realizado' en taburbDesembolso para filas que tenían
	realizado=1 antes de que se eliminara el campo Check.

	Sin este patch, los desembolsos ya marcados como realizados aparecerían
	con estado en blanco y el reporte CXC los trataría como no realizados,
	mostrando $0 y saldo_banco inflado al monto total de la línea de crédito.
	"""
	frappe.db.sql("""
		UPDATE `taburbDesembolso`
		SET estado = 'Realizado'
		WHERE realizado = 1
		  AND (estado IS NULL OR estado = '' OR estado != 'Realizado')
	""")

	count = frappe.db.sql("SELECT ROW_COUNT()")[0][0]
	frappe.logger().info(
		f"backfill_desembolso_estado: {count} filas actualizadas a estado='Realizado'"
	)
