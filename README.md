# Urbanizacion

Aplicación Frappe/ERPNext v15 para gestionar el flujo comercial y operativo de urbanizaciones en Inversiones BEL.

## Proposito

`urbanizacion` modela y controla el ciclo de vida de lotes y ventas:

- Catalogo de modelos de vivienda
- Proyectos de urbanizacion
- Lotes por proyecto
- Cartas de reserva
- Contratos de venta
- Adendums
- Seguimiento de obra
- Cambio de lote

Tambien incluye una pagina interna de importacion de lotes para uso operativo desde Desk (`/app/importar-lotes`).

## Compatibilidad y Dependencias

- Frappe Framework: v15
- ERPNext: v15 (entorno objetivo)
- Python: `>=3.10`
- App name: `urbanizacion`
- Modulo funcional: `Urbanizacion`

Dependencias Python externas:

- No requiere paquetes adicionales declarados en `pyproject.toml`.
- La dependencia de Frappe la gestiona Bench.

## Estructura Funcional

DocTypes principales (no child table):

- `Proyectos`
- `CatalogoModelos`
- `Lotes`
- `CartaReserva`
- `ContratoVenta`
- `Adendum`
- `SeguimientoObra`
- `CambioLote`

DocTypes child table:

- `AdendumExtra`
- `ActividadObra`
- `FotoAvance`

Workspace:

- `Urbanizacion` (publico en Desk, controlado por roles)

Pagina interna de Desk:

- `importar-lotes` (ruta: `/app/importar-lotes`)

## Configuracion Tecnica Relevante

La app usa `fixtures` para versionar configuracion de sitio en codigo:

- `DocType`
- `Workspace`
- `Client Script`
- `Server Script`
- `Property Setter`
- `Workflow`
- `Notification`
- `Print Format`
- `DocType Link`
- `Web Page` (pagina base `importar-lotes` no publica)
- `Role`

### Dashboards / Conexiones

La app incluye overrides para conexiones en formularios:

- `Proyectos` muestra relacion con `Lotes`
- `Lotes` muestra referencia interna a `Proyectos`

Archivos:

- `urbanizacion/urbanizacion/dashboard/proyectos_dashboard.py`
- `urbanizacion/urbanizacion/dashboard/lotes_dashboard.py`

## Seguridad

### Pagina de importacion de lotes

Se despublico la ruta web publica y se expone solo por Desk:

- Web Page `importar-lotes`: `published = 0`
- Acceso operativo por Desk: `/app/importar-lotes`
- Metodo backend valida permiso `read` sobre `Lotes`

Archivo backend:

- `urbanizacion/urbanizacion/page/importar_lotes/importar_lotes.py`

### Scripts de negocio

La logica operativa esta en:

- `Client Script` (UX, automatizaciones de formulario)
- `Server Script` (validaciones y reglas server-side)

Ambos quedaron versionados en fixtures para que viajen con `install-app`.

## Roles

Roles versionados por la app:

- `Urbanizacion Manager`
- `Urbanizacion Operador`
- `Urbanizacion Consulta`
- `Urbanizacion Vendedor`

Adicionalmente, `System Manager` mantiene acceso administrativo.

### Matriz base aplicada

`Urbanizacion Vendedor` (actual):

- Edicion/creacion: `CartaReserva`, `ContratoVenta`, `Adendum`
- Solo lectura: `Lotes`, `CatalogoModelos`, `Proyectos`, `SeguimientoObra`, `CambioLote`
- Sin `delete`, sin `export`, sin `share`

`importar-lotes` (Page interna):

- Roles permitidos en archivo de pagina:
  - `System Manager`
  - `Urbanizacion Manager`
  - `Urbanizacion Operador`
  - `Urbanizacion Vendedor`

## Instalacion

En un bench con Frappe/ERPNext v15:

```bash
cd /home/frappe/frappe-bench
bench get-app https://github.com/berroteran/erpnext-bel-urbanizacion.git --branch master
bench --site <tu-sitio> install-app urbanizacion
bench --site <tu-sitio> migrate
```

## Actualizacion / Despliegue

Cuando haya cambios en el repo:

```bash
cd /home/frappe/frappe-bench/apps/urbanizacion
git pull origin master
cd /home/frappe/frappe-bench
bench --site <tu-sitio> migrate
```

Para multi-sitio, repetir `migrate` por cada site destino.

## Entorno de Referencia (actual)

- Servidor: Ubuntu en AWS EC2
- Bench principal: `/home/frappe/frappe-bench`
- Sitio testing usado para construir la app: `testing15.inversionesbel.com`
- Apps instaladas en testing: `frappe`, `erpnext`, `hrms`, `urbanizacion`

## Desarrollo

Lint/format configurado en el proyecto:

- Ruff
- ESLint
- Prettier
- PyUpgrade

Activacion de pre-commit:

```bash
cd /home/frappe/frappe-bench/apps/urbanizacion
pre-commit install
```

## Recomendaciones Operativas

- Tratar `fixtures` como fuente de verdad para configuracion funcional.
- Evitar cambios manuales persistentes solo en BD sin re-exportar fixtures.
- Desplegar primero en testing y luego en produccion con `migrate` controlado.
- Mantener control de acceso por roles de negocio (no dar `System Manager` para operacion diaria).

## Licencia

MIT
