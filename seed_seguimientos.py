import frappe
from frappe.utils import today, add_days

import os
os.chdir("/home/frappe/frappe-bench")
frappe.init(site="urbanizacion.local", sites_path="sites")
frappe.connect()
frappe.set_user("Administrator")

# ── Verificar datos existentes ──────────────────────────────────────────────
lotes     = frappe.get_all("Lotes", fields=["name","bloque","catalogo_modelos"], limit=40)
proyectos = frappe.get_all("Proyectos", fields=["name"], limit=5)

print(f"Lotes: {len(lotes)}  Proyectos: {len(proyectos)}")
if proyectos:
    print("Primer proyecto:", proyectos[0].name)

# ── Actividades reales del proyecto (44 actividades) ────────────────────────
ACTIVIDADES_BASE = [
    # Fase 1 — Fundaciones/Estructura
    {"actividad": "Trazo y nivelación"},
    {"actividad": "Excavación Estructural"},
    {"actividad": "Mejoramiento"},
    {"actividad": "Acero de Fundaciones"},
    {"actividad": "Concreto de Fundaciones"},
    {"actividad": "Acero de Columnas y vigas"},
    {"actividad": "Malla de Paredes"},
    {"actividad": "Esperas Sanitarias"},
    {"actividad": "Esperas Eléctricas"},
    {"actividad": "Formaleta de Paredes"},
    {"actividad": "Concreto de Paredes"},
    {"actividad": "Estructura de Techos"},
    {"actividad": "Cubiertas de Techos"},   # Hito II Desembolso
    {"actividad": "Flashing de Techos"},
    # Fase 2 — Acabados interiores
    {"actividad": "Jamba Puertas y Ventanas"},
    {"actividad": "Conformación/Compactación"},
    {"actividad": "Cascote de Piso"},
    {"actividad": "Chapisco en Paredes"},
    {"actividad": "Fino en Paredes"},
    {"actividad": "Inst. Eléctricas"},
    {"actividad": "Inst. Sanitarias"},
    {"actividad": "Estructurado de Cielo Falso"},
    {"actividad": "Cielo Falso/Pasta"},
    {"actividad": "Fascias/Aleros"},
    {"actividad": "Lijado de Cielo Falso"},
    {"actividad": "Arenillado de Piso"},
    {"actividad": "Instalación Piso"},
    {"actividad": "Rodapié de Piso"},
    {"actividad": "Marcos de Puertas"},
    {"actividad": "Puertas/Herrajes & Pintura"},
    {"actividad": "Ventanas"},
    {"actividad": "Azulejos en baño"},      # Hito III Desembolso
    # Fase 3 — Terminaciones exteriores
    {"actividad": "Carpintería/Muebles"},
    {"actividad": "Pechera en Cocina"},
    {"actividad": "Accesorios Eléctricos"},
    {"actividad": "Aparatos Sanitarios"},
    {"actividad": "Pintura de Paredes y Cielo"},
    {"actividad": "Cajas de Registro"},
    {"actividad": "Cajas Pluvial+Línea"},
    {"actividad": "Biodigestor"},
    {"actividad": "Pozo de Absorción"},
    {"actividad": "Huellas Vehiculares"},
    {"actividad": "Conformación de Terreno"},
    {"actividad": "Anden Peatonal"},        # Hito IV Desembolso
    {"actividad": "Pre-Entrega"},
    {"actividad": "Entrega Final al Cliente"},
]

def build_actividades(estado_obra):
    """Genera las 44 actividades con estado según el estado general de la obra."""
    if estado_obra in ("Entregada", "Terminada"):
        return [dict(a, estado="Completada") for a in ACTIVIDADES_BASE]
    elif estado_obra == "En Proceso":
        return [dict(a, estado="En Proceso") for a in ACTIVIDADES_BASE]
    else:  # Pendiente
        return [dict(a, estado="Pendiente") for a in ACTIVIDADES_BASE]

# ── Definir muestra de seguimientos ────────────────────────────────────────
proyecto = proyectos[0].name if proyectos else "PRY-001"

CONTRATISTAS = ["Constructora BEL", "García & Hijos", "Obras Nica S.A.", "Ingeniería del Norte"]
ESTADOS      = ["Entregada", "Terminada", "En Proceso", "En Proceso", "Pendiente"]

seed_data = []
for i, lote in enumerate(lotes[:30]):
    estado      = ESTADOS[i % len(ESTADOS)]
    contratista = CONTRATISTAS[i % len(CONTRATISTAS)]
    avance      = {"Entregada": 100, "Terminada": 100,
                   "En Proceso": (40 + (i * 7) % 55), "Pendiente": 0}[estado]
    dias_offset = -30 + (i * 4)
    pre_offset  = dias_offset - 15
    cliente_off = dias_offset + (5 if i % 3 == 0 else -3)

    seed_data.append({
        "lote"                  : lote.name,
        "proyecto"              : proyecto,
        "contratista"           : contratista,
        "estado_obra"           : estado,
        "porcentaje_avance"     : avance,
        "fecha_inicio"          : add_days(today(), -120 + i * 2),
        "fecha_entrega_estimada": add_days(today(), dias_offset),
        "fecha_pre_entrega"     : add_days(today(), pre_offset) if estado != "Pendiente" else None,
        "fecha_entrega_cliente" : add_days(today(), cliente_off) if estado == "Entregada" else None,
        "tipo_seguimiento"      : "Inventario",
        "actividades"           : build_actividades(estado),
    })

# ── Insertar (omitir si ya existe seguimiento para ese lote) ───────────────
creados  = 0
omitidos = 0
for d in seed_data:
    existe = frappe.db.exists("SeguimientoObra", {"lote": d["lote"], "docstatus": ["<", 2]})
    if existe:
        omitidos += 1
        continue
    doc = frappe.get_doc({"doctype": "SeguimientoObra", **d})
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    creados += 1

print(f"\nResultado: {creados} creados, {omitidos} ya existían.")
frappe.destroy()
