from urbanizacion.urbanizacion.doctype_link_guard import sync_urbanizacion_doctype_links
from urbanizacion.urbanizacion.integrity.doctype_link_integrity import harden_doctype_link_integrity


def execute() -> None:
    harden_doctype_link_integrity()
    sync_urbanizacion_doctype_links()
