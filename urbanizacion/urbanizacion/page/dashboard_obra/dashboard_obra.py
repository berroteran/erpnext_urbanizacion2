import frappe
from frappe import _


@frappe.whitelist()
def get_dashboard_data(proyecto=None):
    if not frappe.has_permission("SeguimientoObra", "read"):
        frappe.throw(_("Sin permisos para ver el dashboard de obra"), frappe.PermissionError)

    conditions = ""
    cr_conditions = ""
    values = {}
    if proyecto:
        conditions = "AND so.proyecto = %(proyecto)s"
        cr_conditions = "AND cr.proyecto = %(proyecto)s"
        values["proyecto"] = proyecto

    rows = frappe.db.sql(
        """
        SELECT
            so.name                  AS seguimiento,
            so.lote                  AS lote,
            l.bloque                 AS bloque,
            so.proyecto              AS proyecto,
            cm.modelo                AS modelo,
            so.contratista           AS contratista,
            so.tipo_seguimiento,
            so.estado_obra,
            so.porcentaje_avance,
            so.fecha_inicio,
            so.fecha_entrega_estimada,
            so.fecha_pre_entrega,
            so.fecha_entrega_cliente,
            so.contrato,
            DATEDIFF(so.fecha_entrega_estimada, CURDATE()) AS dias_restantes
        FROM `tabSeguimientoObra` so
        LEFT JOIN `tabLotes` l  ON l.name = so.lote
        LEFT JOIN `tabCatalogoModelos` cm ON cm.name = l.catalogo_modelos
        WHERE so.docstatus < 2
        {conditions}
        ORDER BY l.bloque, CAST(SUBSTRING_INDEX(so.lote, '-', -1) AS UNSIGNED)
        """.format(conditions=conditions),
        values,
        as_dict=True,
    )

    for row in rows:
        row["porcentaje_avance"] = row["porcentaje_avance"] or 0
        if row["dias_restantes"] is None:
            row["dias_restantes"] = 0

    banco_rows = frappe.db.sql(
        """
        SELECT
            COALESCE(NULLIF(cr.banco, ''), 'Sin Banco') AS banco,
            COUNT(*) AS total
        FROM `tabCartaReserva` cr
        WHERE cr.docstatus < 2
          AND cr.estado = 'Activa'
          {cr_conditions}
        GROUP BY banco
        ORDER BY total DESC
        """.format(cr_conditions=cr_conditions),
        values,
        as_dict=True,
    )

    return {"seguimientos": rows, "bancos": banco_rows}
