from frappe import _


def get_data(data=None):
	return {
		"fieldname": "lote",
		"internal_links": {
			"Proyectos": "proyecto",
		},
		"transactions": [
			{
				"label": _("Urbanizacion"),
				"items": ["Proyectos"],
			}
		],
	}
