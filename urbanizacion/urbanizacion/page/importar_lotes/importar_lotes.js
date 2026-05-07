frappe.pages["importar-lotes"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Importar Lotes"),
		single_column: true,
	});

	const $body = $("<div class=\"urbanizacion-importar-lotes\"></div>");
	$body.appendTo(page.body);

	frappe.call({
		method: "urbanizacion.urbanizacion.page.importar_lotes.importar_lotes.get_internal_import_page",
		callback: function (r) {
			const payload = r.message || {};
			if (payload.title) page.set_title(payload.title);
			$body.html(payload.html || "<p>No hay contenido configurado.</p>");

			if (payload.javascript) {
				try {
					// Execute the importer logic in desk context.
					new Function(payload.javascript)();
				} catch (e) {
					console.error("Error cargando script de Importar Lotes", e);
					frappe.msgprint({
						title: __("Error"),
						indicator: "red",
						message: __("No se pudo cargar la lógica de Importar Lotes."),
					});
				}
			}
		},
	});
};
