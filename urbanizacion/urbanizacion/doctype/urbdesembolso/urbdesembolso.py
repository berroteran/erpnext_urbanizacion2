import frappe
from frappe.model.document import Document

class urbDesembolso(Document):
    def validate(self):
        if self.estado == "Realizado" and not self.fecha_realizado:
            frappe.throw("El desembolso marcado como Realizado debe tener una Fecha Realizado.")
        # Evita fechas huérfanas cuando el estado no es Realizado
        if self.estado != "Realizado" and self.fecha_realizado:
            self.fecha_realizado = None
