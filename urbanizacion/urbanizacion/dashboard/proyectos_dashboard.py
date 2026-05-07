from frappe import _


def get_data(data=None):
	return {
		"fieldname": "proyecto",
		"transactions": [
			{
				"label": _("Urbanizacion"),
				"items": ["Lotes"],
			}
		],
	}
