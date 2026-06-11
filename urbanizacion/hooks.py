app_name = "urbanizacion"
app_title = "Urbanizacion"
app_publisher = "Inversiones BEL"
app_description = "Modulo Urbanizacion"
app_email = "soporte@inversionesbel.com"
app_license = "mit"

fixtures = [
	{"dt": "DocType", "filters": [["module", "=", "Urbanizacion"], ["custom", "=", 1]]},
	{"dt": "Workspace", "filters": [["module", "=", "Urbanizacion"]]},
	{"dt": "Client Script", "filters": [["dt", "in", ["Proyectos","CatalogoModelos","ContratoVenta","CartaReserva","Lotes","Adendum","AdendumExtra","ActividadObra","FotoAvance","SeguimientoObra","CambioLote"]]]},
	{"dt": "Server Script", "filters": [["reference_doctype", "in", ["Proyectos","CatalogoModelos","ContratoVenta","CartaReserva","Lotes","Adendum","AdendumExtra","ActividadObra","FotoAvance","SeguimientoObra","CambioLote"]]]},
	{"dt": "Property Setter", "filters": [["doc_type", "in", ["Proyectos","CatalogoModelos","ContratoVenta","CartaReserva","Lotes","Adendum","AdendumExtra","ActividadObra","FotoAvance","SeguimientoObra","CambioLote"]]]},
	{"dt": "Workflow", "filters": [["document_type", "in", ["Proyectos","CatalogoModelos","ContratoVenta","CartaReserva","Lotes","Adendum","AdendumExtra","ActividadObra","FotoAvance","SeguimientoObra","CambioLote"]]]},
	{"dt": "Notification", "filters": [["document_type", "in", ["Proyectos","CatalogoModelos","ContratoVenta","CartaReserva","Lotes","Adendum","AdendumExtra","ActividadObra","FotoAvance","SeguimientoObra","CambioLote"]]]},
	{"dt": "Print Format", "filters": [["doc_type", "in", ["Proyectos","CatalogoModelos","ContratoVenta","CartaReserva","Lotes","Adendum","AdendumExtra","ActividadObra","FotoAvance","SeguimientoObra","CambioLote"]]]},
	{"dt": "Web Page", "filters": [["name", "=", "importar-lotes"]]},
	{"dt": "Role", "filters": [["name", "in", ["Urbanizacion Manager", "Urbanizacion Operador", "Urbanizacion Consulta", "Urbanizacion Vendedor", "Urbanizacion Tecnico"]]]},
]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "urbanizacion",
# 		"logo": "/assets/urbanizacion/logo.png",
# 		"title": "Urbanizacion",
# 		"route": "/urbanizacion",
# 		"has_permission": "urbanizacion.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/urbanizacion/css/urbanizacion.css"
# app_include_js = "/assets/urbanizacion/js/urbanizacion.js"

# include js, css files in header of web template
# web_include_css = "/assets/urbanizacion/css/urbanizacion.css"
# web_include_js = "/assets/urbanizacion/js/urbanizacion.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "urbanizacion/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "urbanizacion/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "urbanizacion.utils.jinja_methods",
# 	"filters": "urbanizacion.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "urbanizacion.install.before_install"
# after_install = "urbanizacion.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "urbanizacion.uninstall.before_uninstall"
# after_uninstall = "urbanizacion.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "urbanizacion.utils.before_app_install"
# after_app_install = "urbanizacion.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "urbanizacion.utils.before_app_uninstall"
# after_app_uninstall = "urbanizacion.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "urbanizacion.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"urbanizacion.tasks.all"
# 	],
# 	"daily": [
# 		"urbanizacion.tasks.daily"
# 	],
# 	"hourly": [
# 		"urbanizacion.tasks.hourly"
# 	],
# 	"weekly": [
# 		"urbanizacion.tasks.weekly"
# 	],
# 	"monthly": [
# 		"urbanizacion.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "urbanizacion.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "urbanizacion.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "urbanizacion.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["urbanizacion.utils.before_request"]
# after_request = ["urbanizacion.utils.after_request"]

# Job Events
# ----------
# before_job = ["urbanizacion.utils.before_job"]
# after_job = ["urbanizacion.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"urbanizacion.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


override_doctype_dashboards = {
	"Proyectos": "urbanizacion.urbanizacion.dashboard.proyectos_dashboard.get_data",
	"Lotes": "urbanizacion.urbanizacion.dashboard.lotes_dashboard.get_data",
}

after_migrate = [
	"urbanizacion.urbanizacion.doctype_link_guard.after_migrate",
	"urbanizacion.urbanizacion.workspace_setup.after_migrate",
]
