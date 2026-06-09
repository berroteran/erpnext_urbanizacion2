# Reporte de revision tecnica - PR #9 hacia `master`

Fecha de revision: 2026-06-06
Repositorio: `berroteran/erpnext-bel-urbanizacion`
Rama base: `master`
PR revisado: `pull/9`
Head revisado: `bd5c7bd`
Merge ref: `8b253d1`

## Resumen ejecutivo

El PR #9 agrega cambios funcionales relevantes en Urbanizacion:

- Calcula avance de obra con pesos ponderados por actividad.
- Agrega `porcentaje_peso` a `ActividadObra`.
- Agrega `precio` a `Lotes`.
- Ajusta el factor de conversion de metros a varas a `1.418415`.
- Agrega patches para recalcular varas y rellenar precios de lotes.
- Agrega validaciones/correos adicionales en Server Scripts.

La intencion funcional es razonable, pero **no recomiendo mezclar este PR todavia** porque hay tres riesgos pendientes:

1. Riesgo alto de recalcular avances existentes de `SeguimientoObra` a `0%`.
2. Campo `Lotes.precio` exportado con metadata incompleta.
3. `git diff --check` falla por whitespace en un patch.

## Archivos modificados por el PR

```text
urbanizacion/fixtures/client_script.json
urbanizacion/fixtures/doctype.json
urbanizacion/fixtures/server_script.json
urbanizacion/patches.txt
urbanizacion/patches/v1_0/backfill_precio_lotes.py
urbanizacion/patches/v1_0/recalculate_varas_factor.py
```

Resumen del diff:

```text
6 files changed, 382 insertions(+), 17 deletions(-)
```

## Hallazgos

### P1 - Riesgo de recalcular avances existentes a `0%`

Se agrega calculo ponderado para `SeguimientoObra` basado en el nuevo campo `ActividadObra.porcentaje_peso`.

Evidencia:

- `urbanizacion/fixtures/server_script.json`
  - Server Script: `urbSeguimientoObra-AvancePonderado`
  - Calcula `porcentaje_avance` sumando `porcentaje_peso` solo de actividades completadas.

```python
total = sum((a.get("porcentaje_peso") or 0) for a in doc.actividades if a.estado == "Completada")
doc.porcentaje_avance = round(total, 1)
```

- `urbanizacion/fixtures/client_script.json`
  - El nuevo campo `porcentaje_peso` se asigna al cargar actividades estandar nuevas.
  - El calculo en cliente tambien depende de `porcentaje_peso`.

- `urbanizacion/fixtures/doctype.json`
  - Se agrega `ActividadObra.porcentaje_peso`.
  - El campo esta oculto (`hidden = 1`).

Problema:

No hay patch que rellene `porcentaje_peso` para actividades ya existentes. Por tanto, registros existentes pueden quedar con `porcentaje_peso = null` o `0`.

Validacion en `testing15`:

```text
seguimiento_count: 2
actividad_count: 92
completadas: 5
```

La tabla actual de `testing15` no tiene todavia la columna `porcentaje_peso`, por lo que despues de migrar, las actividades existentes no tendran pesos asignados automaticamente salvo que se agregue un patch.

Impacto:

Al guardar un `SeguimientoObra` existente despues del merge/migrate, el avance puede recalcularse usando pesos vacios y bajar incorrectamente a `0%` o a un valor menor al real.

Recomendacion:

Agregar un patch que haga backfill de `ActividadObra.porcentaje_peso` para actividades existentes, mapeando por nombre de actividad contra la tabla de pesos estandar definida en el Client Script.

Ejemplo conceptual:

```python
PESOS = {
    "Trazo y nivelacion": 0.36,
    "Excavacion Estructural": 0.86,
    # ... completar tabla oficial
}

for actividad, peso in PESOS.items():
    frappe.db.sql(
        """
        UPDATE `tabActividadObra`
        SET porcentaje_peso = %s
        WHERE actividad = %s
          AND (porcentaje_peso IS NULL OR porcentaje_peso = 0)
        """,
        (peso, actividad),
    )
```

Luego recalcular `SeguimientoObra.porcentaje_avance` para documentos existentes.

Referencia oficial:

- Frappe documenta que los cambios de datos necesarios para una migracion deben ejecutarse mediante patches: https://docs.frappe.io/framework/user/en/guides/deployment/migrations

### P2 - `Lotes.precio` exportado con metadata incompleta

El PR agrega el campo `precio` al DocType `Lotes`, pero aparece en el fixture con metadata minima.

Evidencia en `urbanizacion/fixtures/doctype.json`:

```json
{
  "fieldname": "precio",
  "fieldtype": "Currency",
  "in_list_view": 0,
  "label": "Precio",
  "permlevel": 1
}
```

Problema:

El resto de campos DocField normalmente contiene metadata completa, por ejemplo:

- `parent`
- `parentfield`
- `parenttype`
- `idx`
- `hidden`
- `read_only`
- `reqd`
- `permlevel`
- `print_hide`
- `search_index`
- otros flags propios de Frappe

Esto es inconsistente y fragil para fixtures/migrate. El mismo PR corrige correctamente metadata incompleta de `confirmado`, por lo que `Lotes.precio` deberia seguir el mismo criterio.

Impacto:

Durante `bench migrate`, Frappe sincroniza DocTypes/fixtures contra el sitio. Un DocField incompleto puede generar comportamiento inconsistente o futuros diffs innecesarios.

Recomendacion:

Re-exportar el DocType `Lotes` desde Frappe para que `precio` quede como DocField completo dentro del fixture.

Referencia oficial:

- `bench migrate` sincroniza estado de app, incluyendo schema/fixtures: https://docs.frappe.io/framework/user/en/bench/reference/migrate
- Guia de exportacion de customizaciones: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

### P3 - `git diff --check` falla

Resultado actual:

```text
urbanizacion/patches/v1_0/recalculate_varas_factor.py:37: new blank line at EOF.
```

Impacto:

Es un problema menor, pero incumple la politica del repo de validar `git diff --check` antes de merge.

Recomendacion:

Eliminar la linea en blanco sobrante al final de `recalculate_varas_factor.py`.

## Preguntas abiertas

### 1. Recalculo incondicional de varas

El patch `recalculate_varas_factor.py` recalcula estos campos para todos los registros con metros mayores a cero:

- `tabLotes.v2_terreno`
- `tabLotes.v2_casa`
- `tabCatalogoModelos.area_varas`
- `tabCartaReserva.v2_terreno`
- `tabCartaReserva.v2_casa`

Pregunta:

¿Es intencional sobrescribir todos esos valores existentes? Si algunos fueron ajustados manualmente por negocio, este patch los reemplazara.

Recomendacion:

Confirmar con negocio o documentar que estos campos siempre deben derivarse del factor catastral `1.418415`.

### 2. Pesos de actividades existentes

Pregunta:

¿Las actividades existentes deben recibir pesos por nombre de actividad usando la tabla estandar?

Recomendacion:

Si el nuevo modelo de avance ponderado es obligatorio, si: se debe crear patch de backfill antes del merge.

## Validaciones realizadas

### Git / PR

```text
origin/master: ad04ec4
PR #9 head:   bd5c7bd
PR #9 merge:  8b253d1
```

Commits nuevos del PR contra `master`:

```text
bd5c7bd feat(seguimiento): calcular porcentaje_avance ponderado por actividades BEL
5c902f0 fix(validacion): bloquear guardado cuando prima supera precio total en CartaReserva
f0ca3dd fix(patch): eliminar frappe.db.commit() de recalculate_varas_factor
34674d6 fix(data+ux): corregir patch, advertencia de prima y restaurar extras en CartaReserva
f2a641c fix(security): corregir frappe.has_role en ContratoVenta y agregar correo de confirmacion
2785793 feat(correo): incluir observaciones en el correo de confirmacion de CartaReserva
b6bc899 fix(security): reemplazar frappe.has_role por consulta DB en SS-VAL-CartaReserva-Confirmado
f267c73 fix(carta-reserva): propagar precio desde lotes y corregir guardado de observaciones
d9aef90 feat(lotes): agregar campo precio desde catalogo_modelos con restriccion de roles
aaecbfe fix(data): patch para recalcular varas con factor catastral 1.418415
525492d fix(conversion): actualizar factor m2 a varas a 1.418415 aprobado por catastro
3c78851 fix(fixtures): completar metadata de campos confirmado en DocType fixture
3a23357 fix(security): validar rol Urbanizacion Manager para confirmar documentos
```

### Sintaxis / formato

```text
JSON fixtures: OK
Server Scripts Python syntax: OK
Client Scripts JS syntax: OK
Patch Python syntax: OK
git diff --check: FALLA
```

### Datos actuales en `testing15`

```text
SeguimientoObra existentes: 2
ActividadObra existentes: 92
ActividadObra completadas: 5
```

## Recomendacion final

No mezclar el PR #9 todavia.

Antes de merge, recomiendo:

1. Agregar patch para rellenar `ActividadObra.porcentaje_peso` en registros existentes.
2. Recalcular `SeguimientoObra.porcentaje_avance` existente con el nuevo modelo ponderado.
3. Re-exportar `Lotes.precio` con metadata completa de DocField.
4. Corregir `git diff --check` eliminando la linea en blanco al EOF.
5. Ejecutar `bench --site testing15.inversionesbel.com migrate` en ambiente de prueba.
6. Validar en `testing15` que los avances existentes no bajan incorrectamente.

## Referencias oficiales

- Frappe Framework Guides: https://docs.frappe.io/framework/user/en/guides
- Migrations / patches: https://docs.frappe.io/framework/user/en/guides/deployment/migrations
- bench migrate: https://docs.frappe.io/framework/user/en/bench/reference/migrate
- Exporting customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- Client Script: https://docs.frappe.io/framework/user/en/desk/scripting/client-script
- Server Script: https://docs.frappe.io/framework/user/en/desk/scripting/server-script
