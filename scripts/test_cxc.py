"""
Plan de pruebas — Cuentas por Cobrar Urbanizacion
Cubre: _get_estatus, _build_row, _natural_key, _ensure_content_block,
       _ensure_links (lógica idempotente), estructura JSON del reporte.

Ejecutar con: python3 scripts/test_cxc.py
"""

import importlib.util
import json
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace

# ---------------------------------------------------------------------------
# Loader — importa el módulo sin Frappe
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent
REPORT_PY = ROOT / "urbanizacion/urbanizacion/report/cuentas_por_cobrar_urbanizacion/cuentas_por_cobrar_urbanizacion.py"
REPORT_JSON = ROOT / "urbanizacion/urbanizacion/report/cuentas_por_cobrar_urbanizacion/cuentas_por_cobrar_urbanizacion.json"
ROLE_JSON = ROOT / "urbanizacion/fixtures/role.json"
WORKSPACE_PY = ROOT / "urbanizacion/urbanizacion/workspace_setup.py"

# Stub mínimo de frappe para que el import no falle
import types
frappe_stub = types.ModuleType("frappe")
frappe_stub._ = lambda x: x
sys.modules.setdefault("frappe", frappe_stub)

spec = importlib.util.spec_from_file_location("cxc", REPORT_PY)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

_get_estatus = mod._get_estatus
_build_row   = mod._build_row
_natural_key = mod._natural_key
get_columns  = mod.get_columns

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"

results = []

def run(name, fn):
    try:
        outcome, detail = fn()
        results.append((outcome, name, detail))
        tag = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(outcome, "?")
        print(f"  {tag} {name}")
        if detail and outcome != PASS:
            for line in detail.splitlines():
                print(f"     {line}")
    except Exception as e:
        results.append((FAIL, name, traceback.format_exc()))
        print(f"  ❌ {name}  [EXCEPCIÓN: {e}]")

def ns(**kw):
    return SimpleNamespace(**kw)

# ---------------------------------------------------------------------------
# BLOQUE 1 — _get_estatus: 8 escenarios
# ---------------------------------------------------------------------------

print("\n── BLOQUE 1: _get_estatus ──────────────────────────────────────────")

def t_estatus_formalizado():
    r = _get_estatus(None, None, ns(confirmado=1))
    assert r == "FORMALIZADO", f"got {r}"
    return PASS, ""

def t_estatus_reserva_contrato_no_confirmado():
    "Contrato no confirmado + carta Activa → RESERVA (no CANCELADA)"
    carta = ns(estado="Activa")
    contrato = ns(confirmado=0)
    r = _get_estatus(None, carta, contrato)
    assert r == "RESERVA", f"got {r}"
    return PASS, ""

def t_estatus_cancelada_prioridad():
    "Carta Cancelada + contrato no confirmado → CANCELADA (falso positivo pre-fix)"
    carta = ns(estado="Cancelada")
    contrato = ns(confirmado=0)
    r = _get_estatus(None, carta, contrato)
    assert r == "CANCELADA", f"REGRESIÓN: got {r!r} — fix de _get_estatus no funcionó"
    return PASS, ""

def t_estatus_solo_carta_activa():
    r = _get_estatus(None, ns(estado="Activa"), None)
    assert r == "RESERVA", f"got {r}"
    return PASS, ""

def t_estatus_solo_carta_cancelada():
    r = _get_estatus(None, ns(estado="Cancelada"), None)
    assert r == "CANCELADA", f"got {r}"
    return PASS, ""

def t_estatus_inventario():
    r = _get_estatus(ns(), None, None)
    assert r == "INVENTARIO", f"got {r}"
    return PASS, ""

def t_estatus_contrato_confirmado_ignora_carta():
    "Contrato confirmado + carta Cancelada → FORMALIZADO (contrato gana)"
    r = _get_estatus(None, ns(estado="Cancelada"), ns(confirmado=1))
    assert r == "FORMALIZADO", f"got {r}"
    return PASS, ""

def t_estatus_carta_estado_desconocido():
    "Estado de carta no reconocido ('Pendiente') → INVENTARIO (sin crash)"
    r = _get_estatus(ns(), ns(estado="Pendiente"), None)
    assert r == "INVENTARIO", f"got {r!r}"
    return PASS, ""

run("FORMALIZADO cuando contrato confirmado", t_estatus_formalizado)
run("RESERVA: contrato no confirmado + carta Activa", t_estatus_reserva_contrato_no_confirmado)
run("CANCELADA: carta cancelada tiene precedencia sobre contrato no confirmado", t_estatus_cancelada_prioridad)
run("RESERVA: solo carta Activa", t_estatus_solo_carta_activa)
run("CANCELADA: solo carta Cancelada", t_estatus_solo_carta_cancelada)
run("INVENTARIO: sin carta ni contrato", t_estatus_inventario)
run("FORMALIZADO: contrato confirmado ignora estado de carta", t_estatus_contrato_confirmado_ignora_carta)
run("INVENTARIO: estado de carta desconocido no lanza excepción", t_estatus_carta_estado_desconocido)

# ---------------------------------------------------------------------------
# BLOQUE 2 — _natural_key: ordenamiento numérico de lotes
# ---------------------------------------------------------------------------

print("\n── BLOQUE 2: _natural_key ──────────────────────────────────────────")

def t_natural_orden_basico():
    nums = ["L-10", "L-2", "L-1", "L-20"]
    ordenado = sorted(nums, key=_natural_key)
    assert ordenado == ["L-1", "L-2", "L-10", "L-20"], f"got {ordenado}"
    return PASS, ""

def t_natural_bloque_mixto():
    "Bloques tipo B1-5, B2-3, B1-10"
    nums = ["B1-10", "B1-5", "B2-3", "B1-2"]
    ordenado = sorted(nums, key=_natural_key)
    assert ordenado == ["B1-2", "B1-5", "B1-10", "B2-3"], f"got {ordenado}"
    return PASS, ""

def t_natural_string_vacio():
    "Cadena vacía no lanza excepción"
    result = _natural_key("")
    assert isinstance(result, list), f"expected list, got {type(result)}"
    return PASS, ""

def t_natural_solo_letras():
    nums = ["LOTE-C", "LOTE-A", "LOTE-B"]
    ordenado = sorted(nums, key=_natural_key)
    assert ordenado == ["LOTE-A", "LOTE-B", "LOTE-C"], f"got {ordenado}"
    return PASS, ""

def t_natural_consistencia_estable():
    "Dos llamadas con el mismo input dan mismo resultado"
    a = _natural_key("L-007")
    b = _natural_key("L-007")
    assert a == b, "resultado no es determinista"
    return PASS, ""

run("Orden numérico básico (L-1, L-2, L-10)", t_natural_orden_basico)
run("Bloques mixtos B1-2, B1-5, B1-10, B2-3", t_natural_bloque_mixto)
run("Cadena vacía no lanza excepción", t_natural_string_vacio)
run("Solo letras — orden alfabético", t_natural_solo_letras)
run("Resultado determinista en múltiples llamadas", t_natural_consistencia_estable)

# ---------------------------------------------------------------------------
# BLOQUE 3 — _build_row: cálculos financieros y fuentes de datos
# ---------------------------------------------------------------------------

print("\n── BLOQUE 3: _build_row (cálculos financieros) ─────────────────────")

LOTE_BASE = ns(name="L-001", bloque="B1", numero_lote="1", m2_casa=85.5,
               lote_precio=45000, lote_estado="Activo", modelo="Casa 85")

def t_build_fuente_contrato():
    "Si hay contrato, usa sus campos financieros"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="Juan Pérez", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    carta = ns(name="CR-001", lote="L-001", banco="BAC", fecha="2025-01-10",
               estado="Activa", nombre_solicitante="Juan Pérez",
               cr_precio=48000, monto_prima=9000, monto_reservacion=500,
               saldo_neto_prima=8500, monto_financiar=38000)
    row = _build_row(LOTE_BASE, carta, contrato, [])
    assert row["precio_total"] == 50000, f"precio_total={row['precio_total']}"
    assert row["monto_prima"] == 10000, f"monto_prima={row['monto_prima']}"
    assert row["cliente"] == "Juan Pérez", f"cliente={row['cliente']!r}"
    return PASS, ""

def t_build_abonos_prima_con_contrato():
    "abonos_prima = monto_prima - monto_reserva - saldo_prima (L-2 del Excel: 36040-2000-0=34040)"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=169800, monto_prima=36040, monto_reserva=2000,
                  saldo_prima=0, monto_financiar=133760)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert row["abonos_prima"] == 34040, f"abonos_prima={row['abonos_prima']}"
    return PASS, ""

def t_build_abonos_prima_parciales():
    "abonos_prima refleja pagos parciales (L-4: 16990-2000-7111.2=7878.8)"
    contrato = ns(name="CV-001", lote="L-001", confirmado=0,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=168990, monto_prima=16990, monto_reserva=2000,
                  saldo_prima=7111.2, monto_financiar=152000)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert abs(row["abonos_prima"] - 7878.8) < 0.01, f"abonos_prima={row['abonos_prima']}"
    return PASS, ""

def t_build_abonos_prima_sin_pagos():
    "Sin pagos (solo reserva): abonos_prima=0"
    contrato = ns(name="CV-001", lote="L-001", confirmado=0,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=2000,
                  saldo_prima=8000, monto_financiar=40000)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert row["abonos_prima"] == 0, f"abonos_prima={row['abonos_prima']}"
    return PASS, ""

def t_build_abonos_prima_no_negativo():
    "Dato sucio: saldo_prima > monto_prima — abonos_prima no debe ser negativo"
    contrato = ns(name="CV-001", lote="L-001", confirmado=0,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=5000, monto_reserva=2000,
                  saldo_prima=9000, monto_financiar=40000)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert row["abonos_prima"] >= 0, f"abonos_prima negativo: {row['abonos_prima']}"
    return PASS, ""

def t_build_avance_con_seguimiento():
    "avance = porcentaje_avance del SeguimientoObra; x_ejecutar = 100 - avance"
    seguimiento = ns(porcentaje_avance=96.59)
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    row = _build_row(LOTE_BASE, None, contrato, [], seguimiento)
    assert abs(row["avance"] - 96.59) < 0.01, f"avance={row['avance']}"
    assert abs(row["x_ejecutar"] - 3.41) < 0.01, f"x_ejecutar={row['x_ejecutar']}"
    return PASS, ""

def t_build_avance_sin_seguimiento():
    "Sin SeguimientoObra: avance=0, x_ejecutar=100"
    row = _build_row(LOTE_BASE, None, None, [], None)
    assert row["avance"] == 0, f"avance={row['avance']}"
    assert row["x_ejecutar"] == 100, f"x_ejecutar={row['x_ejecutar']}"
    return PASS, ""

def t_build_avance_completo_no_negativo():
    "avance=100 → x_ejecutar=0 (no negativo)"
    seguimiento = ns(porcentaje_avance=100)
    row = _build_row(LOTE_BASE, None, None, [], seguimiento)
    assert row["x_ejecutar"] == 0, f"x_ejecutar={row['x_ejecutar']}"
    return PASS, ""

def t_build_cliente_dos_compradores():
    "nombre_comprador2 se concatena con ' / '"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="Juan Pérez", nombre_comprador2="María López",
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert row["cliente"] == "Juan Pérez / María López", f"got {row['cliente']!r}"
    return PASS, ""

def t_build_fallback_carta():
    "Sin contrato usa carta como fuente"
    carta = ns(name="CR-001", lote="L-001", banco="BANPRO", fecha="2025-03-01",
               estado="Activa", nombre_solicitante="Ana García",
               cr_precio=47000, monto_prima=9000, monto_reservacion=400,
               saldo_neto_prima=8600, monto_financiar=38000)
    row = _build_row(LOTE_BASE, carta, None, [])
    assert row["precio_total"] == 47000, f"precio_total={row['precio_total']}"
    assert row["cliente"] == "Ana García", f"got {row['cliente']!r}"
    assert row["banco"] == "BANPRO"
    return PASS, ""

def t_build_sin_datos():
    "Sin carta ni contrato usa precio del lote, cliente vacío"
    row = _build_row(LOTE_BASE, None, None, [])
    assert row["precio_total"] == 45000, f"got {row['precio_total']}"
    assert row["cliente"] == "", f"got {row['cliente']!r}"
    assert row["estatus"] == "INVENTARIO"
    return PASS, ""

def t_build_saldo_banco():
    "saldo_banco = linea_credito - total_desembolsado"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    des = [
        ns(realizado=1, fecha_realizado="2025-06-01", monto=15000, idx=1),
        ns(realizado=1, fecha_realizado="2025-09-01", monto=15000, idx=2),
    ]
    row = _build_row(LOTE_BASE, None, contrato, des)
    assert row["saldo_banco"] == 10000, f"saldo_banco={row['saldo_banco']}"
    assert row["des1_monto"] == 15000
    assert row["des2_monto"] == 15000
    assert row["des3_monto"] == 0
    return PASS, ""

def t_build_saldo_cliente():
    "saldo_cliente = saldo_prima + saldo_banco"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=5000, monto_financiar=40000)
    des = [ns(realizado=1, fecha_realizado="2025-06-01", monto=10000, idx=1)]
    row = _build_row(LOTE_BASE, None, contrato, des)
    # saldo_banco = 40000 - 10000 = 30000; saldo_cliente = 5000 + 30000 = 35000
    assert row["saldo_banco"] == 30000, f"saldo_banco={row['saldo_banco']}"
    assert row["saldo_cliente"] == 35000, f"saldo_cliente={row['saldo_cliente']}"
    return PASS, ""

def t_build_desembolso_no_realizado():
    "Desembolso con realizado=0 no suma al total y muestra fecha/monto en cero"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    des = [ns(realizado=0, fecha_realizado="2025-06-01", monto=15000, idx=1)]
    row = _build_row(LOTE_BASE, None, contrato, des)
    assert row["des1_monto"] == 0, f"des1_monto={row['des1_monto']}"
    assert row["des1_fecha"] is None, f"des1_fecha={row['des1_fecha']}"
    assert row["saldo_banco"] == 40000, f"saldo_banco={row['saldo_banco']}"
    return PASS, ""

def t_build_mas_de_4_desembolsos():
    "Solo se procesan los primeros 4 desembolsos"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=50000)
    des = [ns(realizado=1, fecha_realizado=f"2025-0{i}-01", monto=5000, idx=i)
           for i in range(1, 8)]  # 7 desembolsos
    row = _build_row(LOTE_BASE, None, contrato, des)
    # saldo_banco = 50000 - (5000 * 4) = 30000  (solo 4 primeros en columnas)
    # PERO total_desembolsado suma todos los realizados
    total_real = 5000 * 7
    assert row["saldo_banco"] == 50000 - total_real, (
        f"saldo_banco={row['saldo_banco']} — "
        f"total_desembolsado incluye TODOS los desembolsos realizados, no solo los 4 en columnas"
    )
    return PASS, ""

def t_build_saldo_banco_negativo():
    "Desembolsos mayores que línea de crédito → saldo_banco negativo + alerta=SOBREGIRO"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    des = [ns(realizado=1, fecha_realizado="2025-06-01", monto=45000, idx=1)]
    row = _build_row(LOTE_BASE, None, contrato, des)
    assert row["saldo_banco"] == -5000, f"saldo_banco={row['saldo_banco']}"
    assert row.get("alerta") == "SOBREGIRO", f"alerta={row.get('alerta')!r}"
    return PASS, ""

def t_build_valores_none_no_crashean():
    "Campos opcionales con None no deben lanzar excepción"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador=None, nombre_comprador2=None,
                  precio_total=None, monto_prima=None, monto_reserva=None,
                  saldo_prima=None, monto_financiar=None)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert row["precio_total"] == 0
    assert row["cliente"] == ""
    return PASS, ""

run("Contrato es fuente autoritativa sobre carta", t_build_fuente_contrato)
run("abonos_prima: prima completamente pagada (L-2 del Excel)", t_build_abonos_prima_con_contrato)
run("abonos_prima: pagos parciales de prima (L-4 del Excel)", t_build_abonos_prima_parciales)
run("abonos_prima: sin abonos realizados → 0", t_build_abonos_prima_sin_pagos)
run("abonos_prima: dato sucio no produce valor negativo", t_build_abonos_prima_no_negativo)
run("avance: porcentaje desde SeguimientoObra, x_ejecutar = 100 - avance", t_build_avance_con_seguimiento)
run("avance: sin SeguimientoObra → avance=0, x_ejecutar=100", t_build_avance_sin_seguimiento)
run("avance: obra al 100% → x_ejecutar=0 (no negativo)", t_build_avance_completo_no_negativo)
run("Dos compradores concatenados con ' / '", t_build_cliente_dos_compradores)
run("Fallback a carta cuando no hay contrato", t_build_fallback_carta)
run("Sin datos: precio del lote, cliente vacío, INVENTARIO", t_build_sin_datos)
run("saldo_banco = linea_credito - total_desembolsado", t_build_saldo_banco)
run("saldo_cliente = saldo_prima + saldo_banco", t_build_saldo_cliente)
run("Desembolso no realizado: no suma, fecha/monto en cero", t_build_desembolso_no_realizado)
run("Más de 4 desembolsos: saldo_banco usa TODOS los realizados", t_build_mas_de_4_desembolsos)
run("Saldo banco negativo por sobregiro", t_build_saldo_banco_negativo)
run("Campos None en contrato no lanzan excepción", t_build_valores_none_no_crashean)

# ---------------------------------------------------------------------------
# BLOQUE 4 — get_columns: estructura y opciones USD
# ---------------------------------------------------------------------------

print("\n── BLOQUE 4: get_columns (estructura) ──────────────────────────────")

def t_columns_currency_tienen_usd():
    cols = get_columns()
    currency_cols = [c for c in cols if c["fieldtype"] == "Currency"]
    sin_usd = [c["fieldname"] for c in currency_cols if c.get("options") != "USD"]
    if sin_usd:
        return FAIL, f"Columnas Currency sin options=USD: {sin_usd}"
    return PASS, f"{len(currency_cols)} columnas Currency — todas con options=USD"

def t_columns_fieldnames_unicos():
    cols = get_columns()
    names = [c["fieldname"] for c in cols]
    duplicados = [n for n in names if names.count(n) > 1]
    if duplicados:
        return FAIL, f"fieldnames duplicados: {set(duplicados)}"
    return PASS, ""

def t_columns_link_tienen_options():
    cols = get_columns()
    links_sin_options = [c["fieldname"] for c in cols
                         if c["fieldtype"] == "Link" and not c.get("options")]
    if links_sin_options:
        return FAIL, f"Columnas Link sin options (DocType): {links_sin_options}"
    return PASS, ""

def t_columns_no_falta_campo_critico():
    cols = get_columns()
    nombres = {c["fieldname"] for c in cols}
    requeridos = {"precio_total", "saldo_banco", "saldo_cliente", "estatus",
                  "cliente", "banco", "contrato", "carta_reserva",
                  "abonos_prima", "avance", "x_ejecutar"}
    faltantes = requeridos - nombres
    if faltantes:
        return FAIL, f"Campos críticos ausentes: {faltantes}"
    return PASS, ""

def t_columns_nuevas_en_posicion_correcta():
    "avance/x_ejecutar después de m2_casa; abonos_prima después de monto_reserva"
    cols = get_columns()
    nombres = [c["fieldname"] for c in cols]
    idx = {n: i for i, n in enumerate(nombres)}
    errores = []
    if not (idx.get("m2_casa", -1) < idx.get("avance", -1)):
        errores.append("avance debe ir después de m2_casa")
    if not (idx.get("avance", -1) < idx.get("x_ejecutar", -1)):
        errores.append("x_ejecutar debe ir después de avance")
    if not (idx.get("x_ejecutar", -1) < idx.get("precio_total", -1)):
        errores.append("precio_total debe ir después de x_ejecutar")
    if not (idx.get("monto_reserva", -1) < idx.get("abonos_prima", -1)):
        errores.append("abonos_prima debe ir después de monto_reserva")
    if not (idx.get("abonos_prima", -1) < idx.get("saldo_prima", -1)):
        errores.append("saldo_prima debe ir después de abonos_prima")
    if errores:
        return FAIL, "\n".join(errores)
    return PASS, ""

run("Todas las columnas Currency tienen options=USD", t_columns_currency_tienen_usd)
run("fieldnames únicos (sin duplicados)", t_columns_fieldnames_unicos)
run("Columnas Link tienen options (DocType apuntado)", t_columns_link_tienen_options)
run("Campos críticos presentes en columnas", t_columns_no_falta_campo_critico)
run("Nuevas columnas en posición correcta respecto al Excel", t_columns_nuevas_en_posicion_correcta)

# ---------------------------------------------------------------------------
# BLOQUE 5 — workspace_setup: lógica idempotente (sin Frappe)
# ---------------------------------------------------------------------------

print("\n── BLOQUE 5: workspace_setup idempotencia ───────────────────────────")

# Importar workspace_setup con stub de frappe
spec2 = importlib.util.spec_from_file_location("ws_setup", WORKSPACE_PY)
ws_mod = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(ws_mod)

_ensure_links = ws_mod._ensure_links
_ensure_content_block = ws_mod._ensure_content_block
CARD_LABEL = ws_mod.CARD_LABEL
REPORT_NAME = ws_mod.REPORT_NAME
CARD_BLOCK_ID = ws_mod.CARD_BLOCK_ID

def make_ws(links=None, content="[]"):
    ws = SimpleNamespace(links=links or [], content=content)
    ws.append = lambda field, data: getattr(ws, field).append(SimpleNamespace(**data))
    return ws

def t_ws_links_agrega_ambos_si_ninguno():
    ws = make_ws()
    _ensure_links(ws)
    tipos = [(l.type, getattr(l, "label", None), getattr(l, "link_to", None))
             for l in ws.links]
    assert any(t == "Card Break" for t, _, _ in tipos), "falta Card Break"
    assert any(t == "Link" for t, _, _ in tipos), "falta Link"
    return PASS, ""

def t_ws_links_idempotente_ambos_presentes():
    "Si ya existen ambos, no agrega más"
    cb = ns(type="Card Break", label=CARD_LABEL)
    lk = ns(type="Link", link_to=REPORT_NAME)
    ws = make_ws(links=[cb, lk])
    _ensure_links(ws)
    assert len(ws.links) == 2, f"esperaba 2, tiene {len(ws.links)}"
    return PASS, ""

def t_ws_links_agrega_link_si_falta():
    "Solo falta el Link: debe agregar solo el Link"
    cb = ns(type="Card Break", label=CARD_LABEL)
    ws = make_ws(links=[cb])
    _ensure_links(ws)
    tipos = [l.type for l in ws.links]
    assert tipos.count("Link") == 1, f"esperaba 1 Link, tiene {tipos.count('Link')}"
    assert tipos.count("Card Break") == 1, f"Card Break duplicado: {tipos}"
    return PASS, ""

def t_ws_links_agrega_card_break_si_falta():
    "Solo falta el Card Break: debe agregar solo el Card Break"
    lk = ns(type="Link", link_to=REPORT_NAME)
    ws = make_ws(links=[lk])
    _ensure_links(ws)
    tipos = [l.type for l in ws.links]
    assert tipos.count("Card Break") == 1, f"esperaba 1 Card Break, tiene {tipos.count('Card Break')}"
    assert tipos.count("Link") == 1, f"Link duplicado: {tipos}"
    return PASS, ""

def t_ws_content_agrega_bloque_nuevo():
    ws = make_ws(content="[]")
    _ensure_content_block(ws)
    content = json.loads(ws.content)
    assert len(content) == 1, f"esperaba 1 bloque, tiene {len(content)}"
    assert content[0]["type"] == "card"
    assert content[0]["data"]["card_name"] == CARD_LABEL
    return PASS, ""

def t_ws_content_idempotente():
    existing = json.dumps([{"id": CARD_BLOCK_ID, "type": "card",
                             "data": {"card_name": CARD_LABEL, "col": 4}}])
    ws = make_ws(content=existing)
    _ensure_content_block(ws)
    content = json.loads(ws.content)
    assert len(content) == 1, f"duplicó el bloque: tiene {len(content)}"
    return PASS, ""

def t_ws_content_none_no_crashea():
    "ws.content = None no debe lanzar excepción"
    ws = make_ws(content=None)
    _ensure_content_block(ws)
    content = json.loads(ws.content)
    assert len(content) == 1
    return PASS, ""

def t_ws_card_block_id_no_es_generico():
    "CARD_BLOCK_ID debe tener más de 10 chars para evitar colisiones"
    assert len(CARD_BLOCK_ID) > 10, f"ID demasiado corto: {CARD_BLOCK_ID!r}"
    return PASS, f"CARD_BLOCK_ID = {CARD_BLOCK_ID!r}"

run("Links: agrega Card Break y Link cuando workspace vacío", t_ws_links_agrega_ambos_si_ninguno)
run("Links: idempotente cuando ya existen ambos", t_ws_links_idempotente_ambos_presentes)
run("Links: agrega solo Link si falta (Card Break ya existe)", t_ws_links_agrega_link_si_falta)
run("Links: agrega solo Card Break si falta (Link ya existe)", t_ws_links_agrega_card_break_si_falta)
run("Content: agrega bloque nuevo en workspace vacío", t_ws_content_agrega_bloque_nuevo)
run("Content: idempotente cuando ya existe el bloque", t_ws_content_idempotente)
run("Content: ws.content=None no lanza excepción", t_ws_content_none_no_crashea)
run("CARD_BLOCK_ID suficientemente descriptivo (> 10 chars)", t_ws_card_block_id_no_es_generico)

# ---------------------------------------------------------------------------
# BLOQUE 6 — Validación de fixtures JSON
# ---------------------------------------------------------------------------

print("\n── BLOQUE 6: fixtures JSON ──────────────────────────────────────────")

def t_json_report_valido():
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    assert data["doctype"] == "Report"
    assert data["report_type"] == "Script Report"
    assert data["module"] == "Urbanizacion"
    return PASS, ""

def t_json_report_roles_sin_accounts():
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    roles = [r["role"] for r in data.get("roles", [])]
    contaminados = [r for r in roles if r in ("Accounts Manager", "Accounts User")]
    if contaminados:
        return FAIL, f"Roles globales de Accounts aún presentes: {contaminados}"
    return PASS, f"Roles: {roles}"

def t_json_report_tiene_rol_contabilidad():
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    roles = [r["role"] for r in data.get("roles", [])]
    if "Urbanizacion Contabilidad" not in roles:
        return FAIL, f"Rol Urbanizacion Contabilidad no encontrado. Roles: {roles}"
    return PASS, ""

def t_json_report_banco_es_data():
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    filtros = {f["fieldname"]: f for f in data.get("filters", [])}
    banco = filtros.get("banco", {})
    if banco.get("fieldtype") != "Data":
        return FAIL, f"filtro banco sigue siendo {banco.get('fieldtype')!r}, esperado Data"
    if "options" in banco:
        return WARN, f"filtro banco tiene options aún: {banco['options']!r}"
    return PASS, ""

def t_json_role_contabilidad_en_fixture():
    roles = json.loads(ROLE_JSON.read_text(encoding="utf-8"))
    nombres = [r["name"] for r in roles]
    if "Urbanizacion Contabilidad" not in nombres:
        return FAIL, f"Rol no encontrado en role.json. Roles: {nombres}"
    return PASS, f"Roles en fixture: {nombres}"

def t_json_role_fixture_todos_tienen_desk_access():
    roles = json.loads(ROLE_JSON.read_text(encoding="utf-8"))
    sin_desk = [r["name"] for r in roles if not r.get("desk_access")]
    if sin_desk:
        return WARN, f"Roles sin desk_access=1: {sin_desk}"
    return PASS, ""

def t_json_report_modified_no_es_artificial():
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    modified = data.get("modified", "")
    if "23:59:00" in modified:
        return FAIL, f"modified={modified!r} — timestamp artificial para forzar re-import todavía presente"
    return PASS, f"modified={modified!r}"

run("report JSON válido con campos obligatorios", t_json_report_valido)
run("Accounts Manager/User ya no están en roles del reporte", t_json_report_roles_sin_accounts)
run("Rol Urbanizacion Contabilidad presente en reporte", t_json_report_tiene_rol_contabilidad)
run("Filtro banco es fieldtype Data (no Select hardcodeado)", t_json_report_banco_es_data)
run("Rol Urbanizacion Contabilidad en fixtures/role.json", t_json_role_contabilidad_en_fixture)
run("Todos los roles de fixture tienen desk_access=1", t_json_role_fixture_todos_tienen_desk_access)
run("modified del reporte no es timestamp artificial (23:59:00)", t_json_report_modified_no_es_artificial)

# ---------------------------------------------------------------------------
# BLOQUE 7 — Casos borde de negocio: escenarios atípicos
# ---------------------------------------------------------------------------

print("\n── BLOQUE 7: casos borde de negocio ────────────────────────────────")

def t_borde_lote_sin_numero():
    "numero_lote vacío en _natural_key no lanza excepción"
    key = _natural_key(None or "")
    assert isinstance(key, list)
    return PASS, ""

def t_borde_contrato_monto_financiar_cero():
    "linea_credito=0 + desembolsos=0 → saldo_banco=0, saldo_cliente=saldo_prima"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=0)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert row["saldo_banco"] == 0
    assert row["saldo_cliente"] == 9500
    return PASS, ""

def t_borde_contrato_sin_carta_banco_vacio():
    "Sin carta: banco debe ser vacío, no None ni crash"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    row = _build_row(LOTE_BASE, None, contrato, [])
    assert row["banco"] == "", f"banco={row['banco']!r}"
    return PASS, ""

def t_borde_carta_banco_none():
    "carta.banco = None → fila muestra banco vacío, no None"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    carta = ns(name="CR-001", banco=None, fecha="2025-01-01", estado="Activa",
               nombre_solicitante="X", cr_precio=48000, monto_prima=9000,
               monto_reservacion=400, saldo_neto_prima=8600, monto_financiar=38000)
    row = _build_row(LOTE_BASE, carta, contrato, [])
    assert row["banco"] == "", f"banco={row['banco']!r}"
    return PASS, ""

def t_borde_desembolso_monto_none():
    "Desembolso realizado con monto=None no debe lanzar excepción ni sumar None"
    contrato = ns(name="CV-001", lote="L-001", confirmado=1,
                  nombre_comprador="X", nombre_comprador2=None,
                  precio_total=50000, monto_prima=10000, monto_reserva=500,
                  saldo_prima=9500, monto_financiar=40000)
    des = [ns(realizado=1, fecha_realizado="2025-06-01", monto=None, idx=1)]
    row = _build_row(LOTE_BASE, None, contrato, des)
    assert row["des1_monto"] == 0, f"des1_monto={row['des1_monto']}"
    assert row["saldo_banco"] == 40000, f"saldo_banco={row['saldo_banco']}"
    return PASS, ""

def t_borde_lote_precio_none():
    "lote.lote_precio=None en ruta sin carta/contrato → precio_total=0"
    lote = ns(name="L-002", bloque="B2", numero_lote="2", m2_casa=90,
              lote_precio=None, lote_estado="Disponible", modelo="")
    row = _build_row(lote, None, None, [])
    assert row["precio_total"] == 0, f"precio_total={row['precio_total']}"
    return PASS, ""

def t_borde_estatus_contrato_confirmado_truthy():
    "confirmado=1 (int) y confirmado=True ambos deben dar FORMALIZADO"
    assert _get_estatus(None, None, ns(confirmado=1)) == "FORMALIZADO"
    assert _get_estatus(None, None, ns(confirmado=True)) == "FORMALIZADO"
    return PASS, ""

def t_borde_estatus_contrato_confirmado_falsy():
    "contrato no confirmado sin carta → RESERVA (lote no está disponible, hay contrato aunque sea dato sucio)"
    r0 = _get_estatus(ns(), None, ns(confirmado=0))
    rF = _get_estatus(ns(), None, ns(confirmado=False))
    assert r0 == "RESERVA", f"confirmado=0 got {r0!r}"
    assert rF == "RESERVA", f"confirmado=False got {rF!r}"
    return PASS, ""

run("numero_lote vacío/None no rompe ordenamiento", t_borde_lote_sin_numero)
run("monto_financiar=0 → saldo_banco=0, saldo_cliente=saldo_prima", t_borde_contrato_monto_financiar_cero)
run("Sin carta: campo banco es vacío (no None)", t_borde_contrato_sin_carta_banco_vacio)
run("carta.banco=None → campo banco es vacío en la fila", t_borde_carta_banco_none)
run("Desembolso realizado con monto=None no crashea ni suma None", t_borde_desembolso_monto_none)
run("lote.lote_precio=None → precio_total=0 (sin crash)", t_borde_lote_precio_none)
run("confirmado=1 (int) y True → FORMALIZADO", t_borde_estatus_contrato_confirmado_truthy)
run("confirmado=0 sin carta → INVENTARIO", t_borde_estatus_contrato_confirmado_falsy)

# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------

print("\n" + "═" * 70)
total  = len(results)
passed = sum(1 for r in results if r[0] == PASS)
warned = sum(1 for r in results if r[0] == WARN)
failed = sum(1 for r in results if r[0] == FAIL)

print(f"TOTAL: {total}  ✅ {passed} PASS  ⚠️  {warned} WARN  ❌ {failed} FAIL")

if failed:
    print("\n── FALLOS ──────────────────────────────────────────────────────────")
    for outcome, name, detail in results:
        if outcome == FAIL:
            print(f"\n❌ {name}")
            print(f"   {detail}")

if warned:
    print("\n── ADVERTENCIAS ────────────────────────────────────────────────────")
    for outcome, name, detail in results:
        if outcome == WARN:
            print(f"\n⚠️  {name}")
            print(f"   {detail}")

sys.exit(0 if failed == 0 else 1)
