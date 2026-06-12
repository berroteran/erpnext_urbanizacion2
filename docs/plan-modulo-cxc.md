# Plan: Módulo de Cuentas por Cobrar (CXC)

> Estado: **EN PROGRESO — Fase 1 completa, columnas de costo en curso**
> Fuente del análisis: `CUENTAS POR COBRAR SAN GABRIEL (1).xlsx` (hoja `CXC SAN GABRIEL`), analizado el 2026-06-10.
> Decisiones tomadas con el usuario el 2026-06-10 (ver sección "Decisiones").
>
> **Este documento es el contexto vivo del módulo CXC**: al avanzar cada fase se debe
> actualizar la sección "Bitácora de avance" y el estado de las fases, en la misma sesión
> en que se haga el avance.

## 0. Bitácora de avance

| Fecha | Avance | Estado |
|---|---|---|
| 2026-06-10 | Análisis del Excel, decisiones de diseño con el usuario, plan creado | ✅ |
| 2026-06-10 | Cambio de dirección (encargado del módulo): CXC se entrega como **reporte custom dentro del módulo de Contabilidad**, conectado directamente a ContratoVenta y CartaReserva. Ver sección 2.1 | ✅ Decidido |
| 2026-06-10 | Fase 1 — Reporte CXC creado: `urbanizacion/urbanizacion/report/cuentas_por_cobrar_urbanizacion/`. Script Report `is_standard=Yes`, **`module=Urbanizacion`** (no Accounts — Frappe buscaría en erpnext), `ref_doctype=ContratoVenta`. Lee en vivo: Lotes, CartaReserva, ContratoVenta, urbDesembolso. Filtros: Proyecto (req), Estatus, Banco. Migrate local OK. | ✅ Código listo / local funcionando |
| 2026-06-10 | Reporte añadido al workspace Accounting via `after_migrate` idempotente (`workspace_setup.py`). Añade Card Break + Link en `ws.links` y bloque `card` en `ws.content`. Verificado local OK. Pendiente: validar en `/app/accounting` local y desplegar a testing. | ✅ Local listo |
| 2026-06-11 | **Columnas Costo Promedio y X Ejecutar**: decisión de usuario — el costo/m² es por proyecto, no por modelo. Se agrega campo `costo_m2` (Float, non_negative, precisión 2) a `Proyectos` en sección "Cálculo de Costos y Facturación" (antes oculta, ahora visible). Reporte actualizado: nueva columna "Costo Promedio" = `m2_casa × proyecto.costo_m2`; "Por Ejecutar" cambia de `Percent` a `Currency USD` = `costo_promedio × (1 - avance%)`. Verificado local: reporte ejecuta OK, campo `costo_m2 decimal(21,2)` en `tabProyectos`. | ✅ Local listo |
| 2026-06-11 | **Problema conocido: `bench migrate` falla** con `pymysql.err.OperationalError: (1292, "Truncated incorrect DECIMAL value: '')` en fase de patches. No es de nuestros cambios. Workaround hasta resolver: `bench execute frappe.utils.fixtures.sync_fixtures --kwargs '{"app":"urbanizacion"}'` + `bench execute frappe.db.updatedb --args '["Proyectos"]'` + `clear-cache`. Ver sección 2.3. | ⚠️ Issue pre-existente |
| — | Retención y Devolución Boletas: pendiente definir dónde viven (¿campos en ContratoVenta?) | ❓ Pregunta abierta |
| — | Fase 2 — Modelo (ReciboCobro, AdendumCuota, saldos, hooks) — **POSPUESTO**, usuario indicó enfocarse en columnas del reporte primero | ⬜ Pendiente |
| — | Fase 2 — UX (Print Format, Client Scripts, workspace) | ⬜ Pendiente |
| — | Fase 3 — Reporte CXC (columnas mensuales, extras) — requiere ReciboCobro | ⬜ Pendiente |
| — | Fase 4 — Migración histórica San Gabriel | ⬜ Pendiente |
| — | Fase 5 — Futuro (lotes a cuotas, costo/avance) | ⬜ Pendiente |

## 1. Objetivo

Reemplazar el control de cuentas por cobrar que hoy se lleva en Excel (proyecto San Gabriel)
por un módulo dentro de la app `urbanizacion`. La información nace de `CartaReserva` y
`ContratoVenta`; el módulo registra los cobros (recibos), calcula saldos y produce el
reporte CXC equivalente al Excel, incluyendo flujo mensual cobrado.

## 2. Decisiones tomadas (2026-06-10)

1. **Módulo autónomo** dentro de `urbanizacion` con DocTypes propios. NO se integra con
   Customer/Payment Entry/Sales Invoice de ERPNext.
2. **El sistema genera los recibos** (numeración propia + formato de impresión). Reemplaza
   el talonario ROC/REC actual.
3. **Moneda: todo en USD.** Si el cliente paga en córdobas se registran monto C$, tipo de
   cambio y el equivalente USD (el USD es el que afecta el saldo).
4. **Alcance v1**: CXC núcleo (reserva/prima/desembolsos/boletas/saldos/reporte mensual)
   **+** cuotas de adendums y extras.
   **Fuera de v1** (fases futuras): ventas de lote a cuotas sin banco (caso Lote 151
   San José, abonos quincenales de $100) y columnas de costo/avance de obra
   (costo promedio m², % avance, "por ejecutar").

## 2.2 Lecciones técnicas aprendidas (2026-06-10)

- **`module` del reporte debe ser `"Urbanizacion"`, no `"Accounts"`**: Frappe construye el
  path Python como `{app_del_modulo}.{modulo}.report.{nombre}`. Si se usa `"Accounts"`,
  busca en `erpnext.accounts.report.*` y falla con `ModuleNotFoundError`.
- **Entorno local es Linux nativo** (no WSL). Bench en `/home/mistake/frappe-bench`, sitio
  `urbanizacion.local`. No usar `wsl -u frappe` ni `sudo -u frappe`; correr bench directo
  como usuario `mistake`. Scripts en `scripts/sync-wsl.sh` y `scripts/migrate-local.sh`
  tienen rutas WSL antiguas (`/mnt/c/...`) — usar rsync manual desde
  `/home/mistake/Escritorio/ErpNext/erpnext-bel-urbanizacion/` a
  `/home/mistake/frappe-bench/apps/urbanizacion/`.
- **Workspace de Accounting**: el bloque visual vive en `ws.content` (JSON con bloques
  tipo `card`, `shortcut`, `header`). Los links en `ws.links` (child table `Workspace Link`)
  usan `type="Card Break"` para secciones y `type="Link"` para ítems. Los reportes custom
  de testing ("Rpt POZOS", "Probando2") están en esa estructura — pendiente ver su posición
  exacta desde System Console en testing para replicar correctamente.

## 2.3 Issue: bench migrate falla en local (2026-06-11)

`bench migrate` falla con `pymysql.err.OperationalError: (1292, "Truncated incorrect DECIMAL value: '')` durante la fase de patches. No es causado por nuestros cambios. **El migrate llega a completar la actualización de DocTypes (100%) pero aborta en patches**, por lo que el fixture sync y la adición de columnas nuevas no ocurren.

**Workaround hasta resolver el issue del DECIMAL:**

```bash
# 1. Sync de archivos repo → bench
rsync -a --delete \
  --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.claude' --exclude='docs' --exclude='*.xlsx' \
  /home/mistake/Escritorio/ErpNext/erpnext-bel-urbanizacion/ \
  /home/mistake/frappe-bench/apps/urbanizacion/

# 2. Importar fixtures al DB
cd /home/mistake/frappe-bench
bench --site urbanizacion.local execute frappe.utils.fixtures.sync_fixtures \
  --kwargs '{"app": "urbanizacion"}'

# 3. Si se agregó un campo nuevo a un DocType custom, forzar schema update:
bench --site urbanizacion.local execute frappe.db.updatedb --args '["NombreDocType"]'

# 4. Limpiar caché
bench --site urbanizacion.local clear-cache
```

**Pendiente:** identificar qué patch frappe falla con el DECIMAL y reportar/parchear.

## 2.1 Cambio de dirección (2026-06-10, indicación del encargado del módulo)

Requisitos nuevos que **prevalecen** sobre lo anterior donde haya conflicto:

1. **CXC debe vivir dentro del módulo de Contabilidad (Accounting)** del Desk, en la
   sección "Custom Reports" (junto a los reportes existentes del sitio: "Probando2",
   "prueba 01", "Rpt POZOS DE INFILTRACION (LA CALZADA…)").
2. **El entregable es un reporte custom** (DocType `Report`), no una pantalla nueva.
3. **Conexión directa con `ContratoVenta` y `CartaReserva`**: el reporte lee en vivo de
   esas tablas; no debe depender de cargas manuales ni de datos duplicados.
4. **Diseño para el cambio**: el encargado anticipa que columnas/lógica se irán
   modificando con el tiempo. Por eso la lógica debe estar **versionada en git** (no
   editada a mano en cada sitio) para poder propagar cambios local → testing → producción
   con `bench migrate`.

**Entornos** (contexto operativo del usuario):
- **Local**: esta rama / banco de desarrollo.
- **Testing**: `testing15.inversionesbel.com` — en línea, con usuarios reales haciendo pruebas.
- **Producción**: `erp.inversionesbel.com`.

**Implicación técnica importante**: un reporte creado a mano en Desk (como los de la
captura) vive solo en la base de datos de ese sitio y NO viaja entre entornos. Para
mantener los 3 sistemas en sincronía hay dos opciones:
- **Opción A (recomendada)**: Script Report en código dentro de la app
  (`urbanizacion/urbanizacion/report/cuentas_por_cobrar/`), con `ref_doctype` =
  ContratoVenta. Para que aparezca bajo Contabilidad, asignarle el módulo/workspace
  correspondiente o agregar un shortcut/link en el workspace Accounting (el workspace
  Accounting es de ERPNext, así que el link se agregaría como fixture o vía patch).
- **Opción B**: reporte tipo Query/Script creado en Desk y exportado como fixture
  (`{"dt": "Report", "filters": [["name", "=", "Cuentas por Cobrar Urbanizacion"]]}`
  en `hooks.py`). Más frágil: ediciones en Desk en testing/prod pueden divergir del repo.

Decidir A vs B al iniciar la implementación; en ambos casos el JSON/Python del reporte
queda en el repo y se despliega con migrate.

## 3. Análisis del Excel (resumen verificado con fórmulas)

Una fila por lote del proyecto (L-1..L-29). Columnas y fórmulas reales:

| Columna Excel | Significado | Fórmula |
|---|---|---|
| ESTATUS | INVENTARIO / RESERVA / FORMALIZADO / CANCELADA | manual |
| MODELO, BLOQUE, M² | identificación del lote | — |
| COSTO PROMEDIO U$470 | costo construcción = M² × costo/m² (lookup hoja KPI externa) | `VLOOKUP(modelo)*F` |
| AVANCE AL <fecha> | % avance físico de obra | manual (vendría de SeguimientoObra) |
| X EJECUTAR | inversión faltante para terminar la casa | `G − G*H` |
| VALOR DE VENTA INV. BEL | precio del contrato | manual |
| BANCO | BAC / BANPRO / BDF / LAFISE / FP (fondos propios) | manual |
| MONTO DE PRIMA | prima pactada ("usar el del contrato" — nota gerencia) | manual |
| FECHA RESERVA / RESERVA | fecha y monto de la reserva (típico $1,000–2,000) | manual |
| ABONOS DE PRIMA | suma de abonos del cliente a la prima | suma de recibos |
| SALDO DE PRIMA | `PRIMA − (RESERVA + ABONOS)` | `=+L-SUM(N:O)` |
| LINEA DE CREDITO | monto a financiar = `VENTA − PRIMA` | `=+J-L` |
| DESEMBOLSOS 1–4 (fecha+valor) | desembolsos del banco a Inversiones BEL | manual |
| GASTOS DE INSC ESC DE LPH | gastos de inscripción de escritura — **informativo** | manual |
| RETENCION DE BOLETAS | monto que el banco retiene (suma al saldo banco) | manual |
| ACREDITADO A BANCO | **informativo** | manual |
| DEVOLUCION BOLETAS | devolución de la retención (resta del saldo) | manual |
| SALDO DE BANCO | `LC − ΣDESEMBOLSOS + RETENCIÓN − DEVOLUCIÓN` | `=+Q-S+U-X-Z-AB-AC` |
| SALDO CLIENTE PROYECTADO | `SALDO PRIMA + SALDO BANCO` | `=+P+AD` |
| Columnas mensuales nov25–dic26 | monto cobrado/recibido en cada mes (suma de recibos del mes) | manual |
| EXTRA DE CASAS | cobros por extras (acabados, coladera, agua/luz, duroblock…) | manual |

**Notas de celda del Excel** (información crítica que hoy vive en comentarios):
- Cada monto tiene notas con números de recibo `ROC: 6644 14/3/26` o `REC: 6593`, y
  referencias de transferencia `TF301493189`. Última numeración vista: ~ROC 6766 (jun-2026).
- Adendums pagados en cuotas: ej. "$10,000 en 8 cuotas de $1,306.90", "reconocimiento de
  adendum $7,000 en 5 cuotas de $1,421.07".
- Intereses: "los $950.07 interés de adeudo", "$499.15 intereses por financiamiento",
  "$400 interés del adendum" → necesitan tipo de cobro "Interés/Otros".
- Pagos en córdobas: "depositó en córdoba C$36,624.30 = US$1,000".
- Mini-tabla "Gerencia" (filas 37-38): control de PRIMA y ADENDUM con abono/saldo.

**Anotaciones de gerencia dentro del Excel** (filas 36-43):
- "Crear un módulo de clientes o revisar si ya existe uno".
- Definición de estados: *reserva* = existe carta; *formalizado* = firma de contrato;
  *inventario* = puede tener avances sin cliente; *cancelado* = carta de finiquito.
- "El costo promedio es el costo por metro cuadrado aproximado"; "Módulo de avances";
  "X ejecutar = lo que falta de inversión para completar la casa"; "Valor final de la
  casa = contrato"; prima: "usar el del contrato".

## 4. Estado actual del sistema (lo que ya existe)

- `CartaReserva`: monto_prima, monto_reservacion, saldo_neto_prima, recibo_caja (Data),
  numero_referencia, monto_financiar, banco (Select), estado (Activa/Cancelada), confirmado.
- `ContratoVenta`: precio_total, monto_prima, monto_reserva, saldo_prima, monto_financiar,
  child table `desembolsos` → `urbDesembolso` (porcentaje, monto, estado
  Pendiente/Por Solicitar/Programado/Realizado, realizado, fecha_realizado), confirmado.
- `Adendum`: tipo (Adéndum/Proforma/Reconocimiento de Deuda), extras (child `AdendumExtra`),
  total, forma_pago (texto libre). **No tiene plan de cuotas ni registro de pagos.**
- `SeguimientoObra`: porcentaje_avance (fuente futura de la columna AVANCE).
- `Lotes`: estado Disponible/Reservado/Vendido.
- **No existe ningún DocType de recibos/pagos.** Hueco central que cubre este módulo.
- Fixtures gestionados vía `hooks.py` (DocType custom=1, Client/Server Script, etc.).
  Los DocTypes nuevos de este módulo deben agregarse a los filtros de fixtures de
  `hooks.py` (Client Script, Server Script, Property Setter, Print Format, etc.).

## 5. Diseño propuesto

### 5.1 DocType nuevo: `ReciboCobro` (documento principal, submittable)

DocType **en código** (carpeta `urbanizacion/urbanizacion/doctype/recibocobro/`) con
controlador Python — política AGENTS.md: lógica de negocio durable en controladores, no
en Server Scripts.

Campos propuestos:
- `naming_series`: `ROC-.####` (decidir si continúa desde ~6800 — pregunta abierta).
- `fecha` (Date, hoy por defecto), `proyecto` (Link Proyectos), `lote` (Link Lotes),
  `contrato` (Link ContratoVenta), `carta_reserva` (Link CartaReserva),
  `adendum` (Link Adendum, depends_on tipo_cobro = Cuota Adendum),
  `cliente` (Data, fetch del contrato/carta).
- `tipo_cobro` (Select):
  `Reserva | Abono Prima | Cancelación Prima | Desembolso Banco | Retención Boletas |
  Devolución Boletas | Cuota Adendum | Extra | Interés | Otros`.
- `numero_desembolso` (Int 1–4, depends_on Desembolso Banco).
- `numero_cuota` (Data ej. "2/8", depends_on Cuota Adendum).
- `monto_usd` (Currency, **el que afecta saldos**).
- `pagado_en_cordobas` (Check) → `monto_cordobas` (Currency), `tipo_cambio` (Float),
  validación servidor: `monto_usd ≈ monto_cordobas / tipo_cambio`.
- `forma_pago` (Select: Efectivo / Transferencia / Depósito / Cheque),
  `referencia_bancaria` (Data, ej. TF301493189), `banco_origen` (Select, mismo options
  que CartaReserva.banco).
- `concepto`/`observaciones` (Small Text), `comprobante` (Attach).
- Submittable (`is_submittable=1`): inmutable tras emitir; anulación = cancel con motivo
  (`motivo_anulacion`, obligatorio al cancelar). Permiso de cancelar solo
  `Urbanizacion Manager`.
- **Print Format** "Recibo de Cobro" (fixture) para impresión del recibo oficial.

Validaciones de servidor (controller, no Client Script):
- Reserva/Abono Prima no puede exceder el saldo de prima pendiente.
- Desembolso Banco no puede exceder el saldo de banco pendiente.
- Cuota Adendum no puede exceder saldo del adendum.
- Contrato o carta de reserva obligatorios según tipo; coherencia lote↔contrato.

### 5.2 Plan de cuotas en `Adendum`

- Child table nueva `AdendumCuota` (en código): `numero` (Int), `fecha_programada` (Date),
  `monto` (Currency), `pagado` (Check, read-only), `recibo` (Link ReciboCobro, read-only),
  `fecha_pago` (Date, read-only).
- Campos nuevos en Adendum: `total_pagado`, `saldo_pendiente` (read-only, calculados al
  validar/cancelar recibos tipo Cuota Adendum).
- Botón/acción para generar plan: N cuotas iguales a partir de fecha inicial.

### 5.3 Campos de saldo en `ContratoVenta` (read-only, calculados)

Sección "Cuenta por Cobrar" con: `total_abonado_prima`, `saldo_prima_actual`,
`linea_credito` (= precio_total − monto_prima), `total_desembolsado`,
`retencion_boletas`, `devolucion_boletas`, `saldo_banco`, `saldo_cliente_proyectado`
(= saldo_prima_actual + saldo_banco), y un HTML con el historial de recibos.

Recalculo en `on_submit` / `on_cancel` de ReciboCobro (hook `doc_events` en `hooks.py`).
El recibo de Desembolso Banco también marca la fila correspondiente de `urbDesembolso`
(estado Realizado, fecha_realizado) — mantener consistencia bidireccional.

### 5.4 Estatus CXC (columna ESTATUS del Excel)

Derivado, no manual (regla de gerencia anotada en el Excel):
- `INVENTARIO`: lote sin carta de reserva activa.
- `RESERVA`: CartaReserva activa sin contrato confirmado.
- `FORMALIZADO`: ContratoVenta confirmado.
- `CANCELADA`: carta/contrato cancelado (carta de finiquito). Evaluar campo
  `carta_finiquito` (Attach) + fecha en CartaReserva/ContratoVenta para documentarlo.

### 5.5 Reporte: Script Report "Cuentas por Cobrar"

Réplica del Excel, en `urbanizacion/urbanizacion/report/cuentas_por_cobrar/`:
- Filtros: proyecto (obligatorio), estatus, banco, rango de fechas para columnas mensuales.
- Columnas fijas: No., Cliente, Estatus, Modelo, Bloque, Valor Venta, Banco, Prima,
  Fecha/Monto Reserva, Abonos Prima, Saldo Prima, Línea de Crédito, Desembolsos 1-4
  (fecha+valor), Retención, Devolución, Saldo Banco, Saldo Cliente Proyectado, Extras.
- Columnas dinámicas mensuales: suma de `monto_usd` de recibos submitted por mes
  (equivalente a columnas AH..AU del Excel).
- Fila de totales.
- (Fase futura: columnas costo promedio / % avance / por ejecutar desde SeguimientoObra
  y CatalogoModelos.)

### 5.6 Permisos y workspace

- `ReciboCobro`: crear/submit → `Urbanizacion Manager` + `Urbanizacion Operador`;
  cancelar → solo Manager; lectura → `Urbanizacion Consulta`.
- Agregar shortcut/card de ReciboCobro y el reporte CXC al Workspace `Urbanizacion`.
- Validar como usuario no-Administrator (regla AGENTS.md).

### 5.7 Migración de datos históricos

- Patch/página de importación NO automática en v1: el Excel tiene errores (`#REF!`,
  `#ERROR!`) y los recibos históricos viven en notas de celda con formato libre.
- Propuesta: script de importación asistida (bench execute o página interna tipo
  `importar-lotes`) que cargue por contrato los acumulados iniciales
  (abonos de prima históricos, desembolsos ya recibidos) como recibos de "carga inicial"
  con su número ROC original en `referencia_bancaria`/campo `numero_recibo_externo`.
- Alternativa mínima: campos de "saldo inicial migrado" por contrato. Decidir en
  implementación.

## 6. Fases de implementación

> Reordenadas el 2026-06-10 tras el cambio de dirección (sección 2.1): el primer
> entregable es el reporte custom en Contabilidad.

1. **Fase 1 — Reporte CXC en Contabilidad (primer entregable)**: reporte custom
   "Cuentas por Cobrar" visible en el módulo Accounting, leyendo en vivo de
   ContratoVenta + CartaReserva (+ Adendum). Primera versión con lo que ya existe en
   esos DocTypes (precio, prima, reserva, saldo prima, monto a financiar, desembolsos
   de `urbDesembolso`, banco, estado). Lógica versionada en git y desplegable con
   migrate a testing y producción.
2. **Fase 2 — Modelo de cobros**: DocTypes `ReciboCobro` + `AdendumCuota`, campos de
   saldo en ContratoVenta/Adendum, hooks `doc_events`, validaciones de servidor,
   permisos. El reporte se enriquece con abonos reales y columnas mensuales.
3. **Fase 3 — UX**: Print Format del recibo, Client Scripts (filtros de links, botones
   "Registrar cobro" desde ContratoVenta/CartaReserva, generador de plan de cuotas),
   workspace.
4. **Fase 4 — Migración histórica**: importación asistida de San Gabriel desde el Excel.
5. **Fase 5 (futuro)**: ventas de lote a cuotas sin banco (Lote 151 San José),
   columnas de costo/avance de obra, numeración/caja multiproyecto si aplica.

El reporte se irá modificando con el tiempo (expectativa explícita del encargado):
cada cambio de columnas/lógica se hace en el repo, se valida en testing con usuarios
y luego se migra a producción.

Cada fase: validar en `testing15.inversionesbel.com` antes de producción, con backup
completo antes de `migrate` en `erp.inversionesbel.com` (AGENTS.md).

## 7. Preguntas abiertas (resolver antes/durante implementación)

### 7.1 Sobre columnas del reporte (foco actual — 2026-06-11)

1. **Retención de Boletas / Devolución de Boletas**: no existen en ningún DocType actual.
   Afectan el Saldo Banco (`LC − Σdesembolsos + retención − devolución`). ¿Dónde viven?
   - Opción A: campos Currency en `ContratoVenta` (editables por el usuario).
   - Opción B: tipos de cobro en `ReciboCobro` (requiere Fase 2).
   - Opción C: omitir por ahora y mostrar Saldo Banco sin retención/devolución.

2. **Gastos de inscripción LPH y "Acreditado a banco"**: informativos en el Excel.
   ¿Se incluyen en el reporte como columnas, o se omiten completamente?

3. **Abonos de Prima**: actualmente derivado como `prima − reserva − saldo_prima`.
   Esto es correcto mientras no exista `ReciboCobro`. Confirmar si es aceptable como
   dato provisional o si se prefiere mostrar vacío (`0`) hasta tener recibos reales.

4. **Columnas mensuales (Nov25–Dic26)**: requieren `ReciboCobro`. ¿Se omiten por ahora
   o se reserva el espacio con columnas en cero?

5. **"Costo Promedio" en el reporte**: actualmente muestra `0` para proyectos sin
   `costo_m2` configurado. ¿Se oculta la columna si el proyecto no tiene ese valor,
   o se muestra `0`?

### 7.2 Sobre ReciboCobro (Fase 2 — pospuesta, para retomar después)

6. **Numeración ROC**: ¿continúa desde ~6800 o inicia serie nueva? ¿ROC y REC son series distintas?
7. **Devolución de boletas**: semántica exacta — ¿devolución al cliente o pago directo a BEL?
8. **Intereses**: ¿aumentan la deuda (se cargan al saldo) o solo se cobran como recibo informativo?
9. **Anulación de recibos**: ¿quién autoriza y se requiere motivo impreso?
10. **Vendedor por cobro**: ¿se necesita campo vendedor en ReciboCobro o basta el de la carta?
