frappe.pages["dashboard-obra"].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "Dashboard de Obra",
        single_column: true,
    });

    let proyecto_field = page.add_field({
        fieldname: "proyecto",
        label: __("Proyecto"),
        fieldtype: "Link",
        options: "Proyectos",
        change() { load_data(); },
    });

    page.add_button(__("Actualizar"), load_data, { icon: "refresh" });

    // ── Estilos ──────────────────────────────────────────────────────
    frappe.dom.set_style(`
        .ob-wrap { padding: 16px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }

        .ob-kpi-row { display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin-bottom:18px; }
        .ob-kpi { background:#fff; border-radius:10px; padding:14px 16px; box-shadow:0 2px 8px rgba(0,0,0,.06); border-left:4px solid #2563eb; }
        .ob-kpi .lbl { font-size:11px; color:#6b7280; font-weight:600; text-transform:uppercase; letter-spacing:.4px; }
        .ob-kpi .val { font-size:26px; font-weight:700; color:#111827; margin-top:2px; }
        .ob-kpi .sub { font-size:11px; color:#9ca3af; margin-top:1px; }
        .ob-kpi.green  { border-left-color:#16a34a; }
        .ob-kpi.blue   { border-left-color:#2563eb; }
        .ob-kpi.orange { border-left-color:#f59e0b; }
        .ob-kpi.red    { border-left-color:#dc2626; }
        .ob-kpi.gray   { border-left-color:#9ca3af; }
        .ob-kpi.purple { border-left-color:#7c3aed; }

        .ob-section { background:#fff; border-radius:10px; padding:16px 18px; box-shadow:0 2px 8px rgba(0,0,0,.06); margin-bottom:16px; }
        .ob-section h3 { font-size:14px; color:#111827; font-weight:700; margin-bottom:12px; padding-bottom:8px;
            border-bottom:2px solid #f3f4f6; display:flex; justify-content:space-between; align-items:center; }
        .ob-section h3 .accent { font-size:11px; color:#6b7280; font-weight:500; }

        .ob-legend { display:flex; gap:12px; flex-wrap:wrap; font-size:12px; color:#374151; margin-bottom:10px; }
        .ob-legend span { display:inline-flex; align-items:center; gap:5px; }
        .ob-legend i { width:13px; height:13px; border-radius:3px; display:inline-block; }

        .ob-filters { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
        .ob-filters button { background:#f3f4f6; border:1px solid #e5e7eb; color:#374151; padding:5px 12px;
            border-radius:20px; font-size:12px; cursor:pointer; transition:all .15s; }
        .ob-filters button:hover { background:#e5e7eb; }
        .ob-filters button.active { background:#2563eb; color:#fff; border-color:#2563eb; }

        .ob-mosaic-wrap { display:grid; grid-template-columns:2fr 1fr; gap:16px; align-items:flex-start; }
        .ob-mosaic { display:flex; flex-direction:column; gap:14px; }
        .ob-bloque-title { font-size:12px; font-weight:700; color:#1f2937; margin-bottom:6px; display:flex; justify-content:space-between; }
        .ob-bloque-title .cnt { color:#6b7280; font-weight:500; font-size:11px; }
        .ob-lots { display:flex; flex-wrap:wrap; gap:6px; }
        .ob-lot { width:58px; height:40px; border-radius:6px; display:flex; flex-direction:column;
            align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#fff;
            cursor:pointer; border:2px solid transparent; transition:transform .12s, box-shadow .12s;
            text-shadow:0 1px 1px rgba(0,0,0,.25); }
        .ob-lot small { font-size:9px; font-weight:600; opacity:.9; margin-top:1px; }
        .ob-lot:hover { transform:translateY(-2px) scale(1.06); box-shadow:0 6px 12px rgba(0,0,0,.18); z-index:5; }
        .ob-lot.selected { border-color:#111827 !important; box-shadow:0 0 0 3px rgba(17,24,39,.2); }
        .ob-lot.dimmed { opacity:.15; pointer-events:none; }

        .ob-detail { background:linear-gradient(180deg,#f9fafb 0%,#fff 100%); border-radius:10px;
            padding:16px; border:1px solid #e5e7eb; min-height:380px; }
        .ob-detail h4 { font-size:12px; color:#6b7280; text-transform:uppercase; letter-spacing:.5px; margin-bottom:8px; }
        .ob-detail .lot-id { font-size:28px; font-weight:800; color:#111827; }
        .ob-detail .det-row { display:flex; justify-content:space-between; padding:7px 0;
            border-bottom:1px dashed #e5e7eb; font-size:12.5px; }
        .ob-detail .det-row span:first-child { color:#6b7280; }
        .ob-detail .det-row span:last-child { color:#111827; font-weight:600; }
        .ob-detail .prog-bar { height:16px; background:#f3f4f6; border-radius:8px; overflow:hidden; margin-top:6px; position:relative; }
        .ob-detail .prog-bar > div { height:100%; border-radius:8px; transition:width .4s ease; }
        .ob-detail .prog-bar span { position:absolute; left:50%; transform:translateX(-50%);
            top:0; line-height:16px; font-size:11px; font-weight:700; color:#fff; text-shadow:0 1px 1px rgba(0,0,0,.3); }

        .ob-row3 { display:grid; gap:16px; margin-bottom:16px; }
        .ob-row3.cols3 { grid-template-columns:1fr 1fr 1fr; }
        .ob-row3.cols2 { grid-template-columns:1.5fr 1fr; }
        .ob-row3.cols2eq { grid-template-columns:1fr 1fr; }
        .ob-chart-box { height:240px; }
        .ob-chart-tall { height:320px; }
        .ob-empty-chart { display:flex; align-items:center; justify-content:center; height:100%;
            color:#9ca3af; font-size:13px; }
        .ob-badge { display:inline-block; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; color:#fff; }
        .ob-empty { text-align:center; color:#9ca3af; padding:60px 20px; font-size:14px; }

        @media (max-width:1100px) {
            .ob-kpi-row { grid-template-columns:repeat(3,1fr); }
            .ob-row3.cols3, .ob-row3.cols2, .ob-row3.cols2eq { grid-template-columns:1fr 1fr; }
            .ob-mosaic-wrap { grid-template-columns:1fr; }
        }
        @media (max-width:700px) {
            .ob-kpi-row { grid-template-columns:repeat(2,1fr); }
            .ob-row3.cols3, .ob-row3.cols2, .ob-row3.cols2eq { grid-template-columns:1fr; }
        }
    `);

    // ── HTML ──────────────────────────────────────────────────────────
    $(wrapper).find(".page-content").html(`
        <div class="ob-wrap">
            <div class="ob-kpi-row" id="ob-kpis"></div>

            <div class="ob-section" id="ob-mosaic-card">
                <h3>Mapa Interactivo de Lotes <span class="accent" id="ob-mosaic-subtitle"></span></h3>
                <div class="ob-legend">
                    <span><i style="background:#16a34a"></i>Entregada</span>
                    <span><i style="background:#2563eb"></i>Terminada</span>
                    <span><i style="background:#f59e0b"></i>En Proceso</span>
                    <span><i style="background:#dc2626"></i>Atrasada</span>
                    <span><i style="background:#9ca3af"></i>Pendiente</span>
                </div>
                <div class="ob-filters" id="ob-filters">
                    <button data-f="all" class="active">Todos</button>
                    <button data-f="Entregada">Entregadas</button>
                    <button data-f="Terminada">Terminadas</button>
                    <button data-f="En Proceso">En Proceso</button>
                    <button data-f="atrasada">Atrasadas</button>
                    <button data-f="Pendiente">Pendientes</button>
                </div>
                <div class="ob-mosaic-wrap">
                    <div class="ob-mosaic" id="ob-mosaic"></div>
                    <div class="ob-detail" id="ob-detail">
                        <h4>Detalle del Lote</h4>
                        <p style="color:#9ca3af;font-size:13px;margin-top:60px;text-align:center;">
                            Haz clic en un lote para ver su detalle.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Fila 1: Mix Modelos · Contratista · Bancos -->
            <div class="ob-row3 cols3">
                <div class="ob-section">
                    <h3>Mix de Modelos <span class="accent">distribución</span></h3>
                    <div class="ob-chart-box" id="chart-modelos"></div>
                </div>
                <div class="ob-section">
                    <h3>Por Contratista</h3>
                    <div class="ob-chart-box" id="chart-contratista"></div>
                </div>
                <div class="ob-section">
                    <h3>Cartera por Banco <span class="accent">cartas activas</span></h3>
                    <div class="ob-chart-box" id="chart-banco"></div>
                </div>
            </div>

            <!-- Fila 2: Avance por unidad · Estado por bloque -->
            <div class="ob-row3 cols2">
                <div class="ob-section">
                    <h3>Avance por Unidad <span class="accent">% construcción</span></h3>
                    <div class="ob-chart-box ob-chart-tall" id="chart-avance"></div>
                </div>
                <div class="ob-section">
                    <h3>Estado por Bloque</h3>
                    <div class="ob-chart-box ob-chart-tall" id="chart-bloque"></div>
                </div>
            </div>

            <!-- Fila 3: Pre-entregas por mes · Tasa de éxito -->
            <div class="ob-row3 cols2eq">
                <div class="ob-section">
                    <h3>Pre-Entregas por Mes <span class="accent">histórico</span></h3>
                    <div class="ob-chart-box" id="chart-entregas"></div>
                </div>
                <div class="ob-section">
                    <h3>Tasa de Éxito en Entregas <span class="accent">a tiempo vs desfase</span></h3>
                    <div class="ob-chart-box" id="chart-exito"></div>
                </div>
            </div>
        </div>
    `);

    let _current_filter = "all";
    let _current_data = [];

    // ── Filtros mosaico ───────────────────────────────────────────────
    $("#ob-filters").on("click", "button", function () {
        _current_filter = $(this).data("f");
        $("#ob-filters button").removeClass("active");
        $(this).addClass("active");
        apply_lot_filter(_current_filter);
    });

    // ── Cargar datos ──────────────────────────────────────────────────
    function load_data() {
        frappe.call({
            method: "urbanizacion.urbanizacion.page.dashboard_obra.dashboard_obra.get_dashboard_data",
            args: { proyecto: proyecto_field.get_value() || null },
            callback: function (r) {
                const msg = r.message || {};
                const seguimientos = msg.seguimientos || [];
                const bancos = msg.bancos || [];
                if (seguimientos.length) {
                    _current_data = seguimientos;
                    render_dashboard(seguimientos, bancos);
                } else {
                    $("#ob-kpis").html('<div class="ob-empty">No hay datos de seguimiento de obra.</div>');
                    $("#ob-mosaic").html("");
                }
            },
        });
    }

    function render_dashboard(data, bancos) {
        render_kpis(data);
        render_mosaic(data);
        render_charts(data, bancos);
    }

    // ── KPI Cards ─────────────────────────────────────────────────────
    function render_kpis(data) {
        const total     = data.length;
        const entregadas = data.filter(r => r.estado_obra === "Entregada").length;
        const terminadas = data.filter(r => r.estado_obra === "Terminada").length;
        const en_proceso = data.filter(r => r.estado_obra === "En Proceso").length;
        const atrasadas  = data.filter(r => r.estado_obra === "En Proceso" && r.dias_restantes < 0).length;
        const avg = total ? (data.reduce((s, r) => s + (r.porcentaje_avance || 0), 0) / total).toFixed(1) : 0;

        $("#ob-kpis").html(`
            <div class="ob-kpi blue">  <div class="lbl">Total</div><div class="val">${total}</div><div class="sub">unidades</div></div>
            <div class="ob-kpi green"> <div class="lbl">Entregadas</div><div class="val">${entregadas}</div><div class="sub">completadas</div></div>
            <div class="ob-kpi blue">  <div class="lbl">Terminadas</div><div class="val">${terminadas}</div><div class="sub">listas para entrega</div></div>
            <div class="ob-kpi orange"><div class="lbl">En Proceso</div><div class="val">${en_proceso}</div><div class="sub">en construcción</div></div>
            <div class="ob-kpi red">   <div class="lbl">Atrasadas</div><div class="val">${atrasadas}</div><div class="sub">vencidas</div></div>
            <div class="ob-kpi purple"><div class="lbl">Avance Prom.</div><div class="val">${avg}%</div><div class="sub">construcción</div></div>
        `);
    }

    // ── Colores ───────────────────────────────────────────────────────
    const STATUS_COLOR = { "Entregada":"#16a34a","Terminada":"#2563eb","En Proceso":"#f59e0b","Pendiente":"#9ca3af" };

    function lot_color(row) {
        if (row.estado_obra === "En Proceso" && row.dias_restantes < 0) return "#dc2626";
        return STATUS_COLOR[row.estado_obra] || "#9ca3af";
    }
    function lot_status_key(row) {
        return (row.estado_obra === "En Proceso" && row.dias_restantes < 0) ? "atrasada" : row.estado_obra;
    }

    // ── Mosaico ───────────────────────────────────────────────────────
    function render_mosaic(data) {
        const by_bloque = {};
        data.forEach(r => {
            if (!by_bloque[r.bloque]) by_bloque[r.bloque] = [];
            by_bloque[r.bloque].push(r);
        });
        const bloques = Object.keys(by_bloque).sort();
        $("#ob-mosaic-subtitle").text(`${data.length} unidades · ${bloques.length} bloques`);

        let html = "";
        bloques.forEach(b => {
            const lots = by_bloque[b].sort((a, z) => {
                return (parseInt((a.lote||"").split("-").pop())||0) - (parseInt((z.lote||"").split("-").pop())||0);
            });
            html += `<div>
                <div class="ob-bloque-title"><span>Bloque ${b}</span><span class="cnt">${lots.length} unidades</span></div>
                <div class="ob-lots" data-bloque="${b}">${lots.map(r => lot_tile(r)).join("")}</div>
            </div>`;
        });
        $("#ob-mosaic").html(html);

        $("#ob-mosaic").on("click", ".ob-lot", function () {
            const row = _current_data.find(r => r.lote === $(this).data("lote"));
            if (row) {
                $(".ob-lot.selected").removeClass("selected");
                $(this).addClass("selected");
                render_detail(row);
            }
        });
        apply_lot_filter(_current_filter);
    }

    function lot_tile(row) {
        const num   = (row.lote || "").split("-").pop();
        const pct   = row.porcentaje_avance || 0;
        const color = lot_color(row);
        const key   = lot_status_key(row);
        return `<div class="ob-lot" data-lote="${row.lote}" data-status="${key}" style="background:${color}"
                    title="${row.lote} · ${row.estado_obra} · ${pct}%${row.contratista ? " · " + row.contratista : ""}">
                    ${num}<small>${pct}%</small></div>`;
    }

    function apply_lot_filter(f) {
        $(".ob-lot").each(function () {
            $(this).toggleClass("dimmed", f !== "all" && $(this).data("status") !== f);
        });
    }

    // ── Detalle lote ──────────────────────────────────────────────────
    function render_detail(row) {
        const pct   = row.porcentaje_avance || 0;
        const color = lot_color(row);
        const dias  = row.dias_restantes;
        const dias_txt   = dias < 0 ? `${Math.abs(dias)} días vencido` : `${dias} días restantes`;
        const dias_color = dias < 0 ? "#dc2626" : dias <= 30 ? "#f59e0b" : "#16a34a";
        const fmtDate    = d => d ? frappe.datetime.str_to_user(d) : "—";
        const badge_color = STATUS_COLOR[row.estado_obra] || "#9ca3af";

        $("#ob-detail").html(`
            <h4>Detalle del Lote</h4>
            <div class="lot-id">${row.lote || "—"}</div>
            ${row.modelo ? `<div style="display:inline-block;margin:4px 0 12px;padding:3px 10px;border-radius:12px;background:#3b82f6;color:#fff;font-size:12px;font-weight:700">${row.modelo}</div>` : ""}
            <div class="det-row"><span>Estado</span><span><span class="ob-badge" style="background:${badge_color}">${row.estado_obra||"—"}</span></span></div>
            <div class="det-row"><span>Proyecto</span><span>${row.proyecto||"—"}</span></div>
            <div class="det-row"><span>Contratista</span><span>${row.contratista||"—"}</span></div>
            <div class="det-row"><span>Avance</span><span>${pct}%</span></div>
            <div class="prog-bar"><div style="width:${pct}%;background:${color}"></div><span>${pct}%</span></div>
            <div class="det-row" style="margin-top:10px"><span>Fecha Inicio</span><span>${fmtDate(row.fecha_inicio)}</span></div>
            <div class="det-row"><span>Entrega Estimada</span><span>${fmtDate(row.fecha_entrega_estimada)}</span></div>
            <div class="det-row"><span>Pre-Entrega</span><span>${fmtDate(row.fecha_pre_entrega)}</span></div>
            <div class="det-row"><span>Entrega Cliente</span><span>${fmtDate(row.fecha_entrega_cliente)}</span></div>
            <div class="det-row"><span>Cronograma</span><span style="color:${dias_color};font-weight:600">${dias_txt}</span></div>
            ${row.contrato ? `<div class="det-row"><span>Contrato</span><span><a href="/app/contratoventa/${encodeURIComponent(row.contrato)}" target="_blank" title="${row.contrato}">Ver contrato →</a></span></div>` : ""}
        `);
    }

    // ── Helper chart ──────────────────────────────────────────────────
    function draw(id, config) {
        try { new frappe.Chart(id, config); }
        catch(e) { $(id).html(`<div class="ob-empty-chart">Sin datos</div>`); }
    }

    // ── Gráficas ──────────────────────────────────────────────────────
    function render_charts(data, bancos) {

        // 1. Mix de Modelos (barras verticales)
        const modelo_cnt = {};
        data.forEach(r => { const k = r.modelo || "Sin Modelo"; modelo_cnt[k] = (modelo_cnt[k]||0)+1; });
        const m_labels = Object.keys(modelo_cnt).sort();
        draw("#chart-modelos", {
            type: "bar",
            data: { labels: m_labels, datasets: [{ name: "Unidades", values: m_labels.map(k => modelo_cnt[k]) }] },
            colors: ["#f59e0b","#3b82f6","#ef4444","#10b981","#7c3aed","#ec4899"],
            height: 220,
        });

        // 2. Por Contratista (barras horizontales — más legible con muchos contratistas)
        const cont_cnt = {};
        data.forEach(r => { const k = r.contratista || "Sin Asignar"; cont_cnt[k] = (cont_cnt[k]||0)+1; });
        const c_sorted = Object.entries(cont_cnt).sort((a, z) => z[1] - a[1]);
        draw("#chart-contratista", {
            type: "bar",
            data: { labels: c_sorted.map(e => e[0]), datasets: [{ name: "Unidades", values: c_sorted.map(e => e[1]) }] },
            colors: ["#2563eb","#f97316","#16a34a","#7c3aed","#f59e0b","#ec4899","#06b6d4"],
            height: 220,
            barOptions: { spaceRatio: 0.3 },
        });

        // 3. Cartera por Banco (barras verticales)
        if (bancos && bancos.length) {
            const banco_palette = ["#f97316","#fbbf24","#facc15","#10b981","#3b82f6","#6366f1","#9ca3af","#ec4899"];
            draw("#chart-banco", {
                type: "bar",
                data: { labels: bancos.map(b => b.banco), datasets: [{ name: "Cartas", values: bancos.map(b => b.total) }] },
                colors: banco_palette,
                height: 220,
            });
        } else {
            $("#chart-banco").html('<div class="ob-empty-chart">Sin cartas de reserva activas</div>');
        }

        // 4. Avance por Unidad (barras por lote, ordenado por bloque)
        const sorted_lots = [...data].sort((a, z) => {
            const bc = (a.bloque||"").localeCompare(z.bloque||"");
            return bc !== 0 ? bc : (parseInt((a.lote||"").split("-").pop())||0) - (parseInt((z.lote||"").split("-").pop())||0);
        });
        draw("#chart-avance", {
            type: "bar",
            data: {
                labels: sorted_lots.map(r => r.lote),
                datasets: [{ name: "Avance %", values: sorted_lots.map(r => r.porcentaje_avance || 0) }],
            },
            colors: ["#2563eb"],
            height: 300,
            axisOptions: { yAxisMode: "span", yMinInterval: 20 },
            barOptions: { spaceRatio: 0.2 },
        });

        // 5. Estado por Bloque (barras apiladas)
        const bloques = [...new Set(data.map(r => r.bloque).filter(Boolean))].sort();
        const estados_stack = ["Entregada","Terminada","En Proceso","Pendiente"];
        const stack_colors  = ["#16a34a","#2563eb","#f59e0b","#9ca3af"];
        draw("#chart-bloque", {
            type: "bar",
            data: {
                labels: bloques.map(b => `Bloque ${b}`),
                datasets: estados_stack.map(e => ({
                    name: e,
                    values: bloques.map(b => data.filter(r => r.bloque === b && r.estado_obra === e).length),
                })),
            },
            colors: stack_colors,
            height: 300,
            barOptions: { stacked: 1 },
        });

        // 6. Pre-Entregas por Mes (línea)
        const meses = {};
        data.forEach(r => {
            if (!r.fecha_pre_entrega) return;
            const d = new Date(r.fecha_pre_entrega);
            if (isNaN(d)) return;
            const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
            meses[key] = (meses[key]||0)+1;
        });
        const mes_sorted = Object.keys(meses).sort();
        if (mes_sorted.length) {
            const mes_labels = mes_sorted.map(k => {
                const [y, m] = k.split("-");
                return new Date(+y, +m-1).toLocaleDateString("es", { month:"short", year:"2-digit" });
            });
            draw("#chart-entregas", {
                type: "line",
                data: { labels: mes_labels, datasets: [{ name: "Pre-Entregas", values: mes_sorted.map(k => meses[k]) }] },
                colors: ["#2563eb"],
                height: 220,
                lineOptions: { regionFill: 1, hideDots: 0 },
            });
        } else {
            $("#chart-entregas").html('<div class="ob-empty-chart">Sin fechas de pre-entrega registradas</div>');
        }

        // 7. Tasa de Éxito (donut — fecha_entrega_cliente vs fecha_entrega_estimada)
        const con_ambas = data.filter(r => r.fecha_entrega_cliente && r.fecha_entrega_estimada);
        const a_tiempo  = con_ambas.filter(r => r.fecha_entrega_cliente <= r.fecha_entrega_estimada).length;
        const desfase   = con_ambas.filter(r => r.fecha_entrega_cliente >  r.fecha_entrega_estimada).length;
        if (a_tiempo + desfase > 0) {
            const pct_t = Math.round(a_tiempo / (a_tiempo + desfase) * 100);
            // Mostrar stats sobre el gráfico via HTML para evitar truncamiento de leyenda
            $("#chart-exito").before(`
                <div style="display:flex;gap:20px;justify-content:center;margin-bottom:8px;font-size:13px">
                    <span style="color:#16a34a;font-weight:700">&#9632; A Tiempo: ${a_tiempo} (${pct_t}%)</span>
                    <span style="color:#dc2626;font-weight:700">&#9632; Con Desfase: ${desfase} (${100-pct_t}%)</span>
                </div>
            `);
            draw("#chart-exito", {
                type: "donut",
                data: {
                    labels: ["A Tiempo", "Con Desfase"],
                    datasets: [{ values: [a_tiempo, desfase] }],
                },
                colors: ["#16a34a","#dc2626"],
                height: 180,
            });
        } else {
            $("#chart-exito").html('<div class="ob-empty-chart">Sin entregas registradas</div>');
        }
    }

    load_data();
};
