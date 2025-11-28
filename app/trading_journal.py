import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from pathlib import Path

# =========================================================
# CONFIG BÁSICA
# =========================================================
st.set_page_config(
    page_title="Trading Journal",
    layout="wide"
)

FILE_PATH = "trading_journal.csv"

if "tema" not in st.session_state:
    st.session_state.tema = "oscuro"
if "num_confirmaciones" not in st.session_state:
    st.session_state.num_confirmaciones = 1

# ---------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------
DARK_CSS = """
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #151b2f 0, #050711 45%, #02030a 100%);
    color: #E5E9F0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b14 0%, #050711 100%);
    border-right: 1px solid rgba(82, 97, 154, 0.6);
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
h1, h2, h3, h4 {
    color: #E5E9F0;
}
.card-block h3, .card-block h4 {
    font-size: 1.12rem;
}
.card-block {
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.0rem;
    border-radius: 1rem;
    background: radial-gradient(circle at top left, rgba(18,27,63,0.96), rgba(7,11,30,0.96));
    border: 1px solid rgba(78,96,160,0.95);
    box-shadow: 0 16px 40px rgba(0,0,0,0.55);
}
.metric-card {
    padding: 1rem 1.5rem;
    border-radius: 1rem;
    background: radial-gradient(circle at top left, rgba(25, 39, 85, 0.85), rgba(8, 12, 28, 0.95));
    border: 1px solid rgba(88, 96, 150, 0.7);
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.55);
    margin-bottom: 1rem;
}
.metric-title {
    font-size: 0.85rem;
    color: #9CA3AF;
    margin-bottom: 0.25rem;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #F9FAFB;
}
.metric-sub {
    font-size: 0.8rem;
    color: #9CA3AF;
}

/* Botones generales (guardar, etc.) */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #0061ff, #00c2ff);
    color: white;
    border-radius: 999px;
    border: none;
    font-weight: 600;
    padding: 0.4rem 1.3rem;
}
div.stButton > button:hover {
    filter: brightness(1.1);
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput input,
.stDateInput input,
.stTimeInput input,
textarea {
    background: rgba(7, 13, 30, 0.95) !important;
    color: #E5E9F0 !important;
    border-radius: 0.6rem !important;
}
.stSelectbox > div > div,
.stMultiselect > div > div {
    background: rgba(7, 13, 30, 0.95) !important;
    border-radius: 0.6rem !important;
}

.sidebar-title {
    font-size: 0.9rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

/* Tabla historial */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.styled-table thead th {
    background: #0b1020;
    color: #e5e7eb;
    padding: 6px 8px;
    text-align: left;
    border-bottom: 1px solid #1f2937;
}
.styled-table tbody td {
    padding: 6px 8px;
    border-bottom: 1px solid rgba(31,41,55,0.7);
}
.tag-long {
    display:inline-block;
    padding:2px 8px;
    border-radius:999px;
    background:rgba(22,163,74,0.2);
    color:#bbf7d0;
}
.tag-short {
    display:inline-block;
    padding:2px 8px;
    border-radius:999px;
    background:rgba(239,68,68,0.25);
    color:#fecaca;
}
.tag-estado {
    display:inline-block;
    padding:2px 8px;
    border-radius:999px;
    background:rgba(59,130,246,0.2);
    color:#bfdbfe;
}
.tag-estrategia {
    display:inline-block;
    padding:2px 8px;
    border-radius:999px;
    background:rgba(59,130,246,0.18);
    color:#bfdbfe;
}
.rating-label {
    text-align:center;
    font-size:0.9rem;
    color:#e5e7eb;
    margin-bottom:0.25rem;
}

/* 🔷 BOTÓN ESPECIAL: AGREGAR CONFIRMACIÓN (Glass Blue sólido, opción C) */
.agregar-conf-btn button {
    background: rgba(40, 90, 255, 0.55) !important;
    border: 1px solid rgba(120, 160, 255, 0.90) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 10px !important;
    padding: 0.25rem 1.1rem !important;
    font-weight: 500 !important;
    color: #ffffff !important;
    box-shadow: 0 10px 26px rgba(15, 23, 42, 0.6);
}
.agregar-conf-btn button:hover {
    background: rgba(60, 120, 255, 0.85) !important;
    border-color: rgba(160, 190, 255, 1.0) !important;
    box-shadow: 0 14px 32px rgba(15,23,42,0.9);
}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES AUX
# ---------------------------------------------------------
def cargar_datos():
    if Path(FILE_PATH).exists():
        try:
            df = pd.read_csv(FILE_PATH)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    # Asegurar columna ID
    if not df.empty:
        if "ID" not in df.columns:
            df.insert(0, "ID", range(1, len(df) + 1))
            df.to_csv(FILE_PATH, index=False)
    return df


def guardar_df(df: pd.DataFrame):
    df.to_csv(FILE_PATH, index=False)


def guardar_operacion(registro: dict):
    df = cargar_datos()
    if not df.empty and "ID" in df.columns:
        next_id = int(df["ID"].max()) + 1
    else:
        next_id = 1
        df = pd.DataFrame()

    registro["ID"] = next_id
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)

    cols = ["ID"] + [c for c in df.columns if c != "ID"]
    df = df[cols]

    guardar_df(df)


def calcular_pnl(tipo, precio_entrada, precio_cierre, tamanio_posicion, apalancamiento):
    if (
        tipo not in ["LONG", "SHORT"] or
        precio_entrada is None or precio_entrada <= 0 or
        precio_cierre is None or precio_cierre <= 0 or
        tamanio_posicion is None or tamanio_posicion <= 0 or
        apalancamiento is None or apalancamiento <= 0
    ):
        return None, None

    if tipo == "LONG":
        cambio_precio_pct = (precio_cierre - precio_entrada) / precio_entrada
    else:
        cambio_precio_pct = (precio_entrada - precio_cierre) / precio_entrada

    pnl_pct = cambio_precio_pct * apalancamiento * 100
    pnl_usd = tamanio_posicion * cambio_precio_pct * apalancamiento
    return pnl_pct, pnl_usd


def clasificar_resultado(pnl_usd):
    if pnl_usd is None:
        return ""
    if pnl_usd > 0:
        return "Ganado"
    elif pnl_usd < 0:
        return "Perdido"
    else:
        return "Break-even"


def preparar_df_numerico(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    if "Fecha" in df.columns:
        df["Fecha_dt"] = pd.to_datetime(df["Fecha"], errors="coerce")
    else:
        df["Fecha_dt"] = pd.NaT

    for col in ["Resultado (USD)", "Resultado (%)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def stats_por(df: pd.DataFrame, modo: str) -> pd.DataFrame:
    if df.empty or "Fecha_dt" not in df.columns:
        return pd.DataFrame()

    temp = df.dropna(subset=["Fecha_dt"]).copy()

    if modo == "dia":
        temp["Grupo"] = temp["Fecha_dt"].dt.date.astype(str)
    elif modo == "semana":
        temp["Grupo"] = temp["Fecha_dt"].dt.to_period("W").astype(str)
    elif modo == "mes":
        temp["Grupo"] = temp["Fecha_dt"].dt.to_period("M").astype(str)
    else:
        return pd.DataFrame()

    def agg_func(x):
        n_trades = len(x)
        ganados = (x["Resultado trade"] == "Ganado").sum() if "Resultado trade" in x.columns else 0
        winrate = (ganados / n_trades * 100) if n_trades > 0 else 0
        pnl_usd = x["Resultado (USD)"].sum(skipna=True) if "Resultado (USD)" in x.columns else 0
        pnl_pct_prom = x["Resultado (%)"].mean(skipna=True) if "Resultado (%)" in x.columns else 0
        return pd.Series({
            "Nº trades": n_trades,
            "Winrate (%)": round(winrate, 2),
            "PnL USD": round(pnl_usd, 2),
            "PnL % promedio": round(pnl_pct_prom, 2),
        })

    res = temp.groupby("Grupo").apply(agg_func).reset_index()
    nombre_col = {"dia": "Fecha", "semana": "Semana", "mes": "Mes"}[modo]
    res = res.rename(columns={"Grupo": nombre_col})
    return res


def panel_superior(df_num, pnl_total_usd):
    if "capital_inicial" not in st.session_state:
        st.session_state.capital_inicial = 1000.0

    col_capital, col_res_global = st.columns([1, 2])

    with col_capital:
        st.markdown("#### ⚙️ Configuración de cuenta")
        capital_inicial = st.number_input(
            "Capital inicial (USD)",
            min_value=0.0,
            step=100.0,
            value=st.session_state.capital_inicial
        )
        st.session_state.capital_inicial = capital_inicial

    capital_actual = st.session_state.capital_inicial + pnl_total_usd
    total_trades = len(df_num) if not df_num.empty else 0
    total_ganados = (df_num["Resultado trade"] == "Ganado").sum() if not df_num.empty else 0
    winrate_global = (total_ganados / total_trades * 100) if total_trades > 0 else 0.0

    with col_res_global:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">Capital actual</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">${capital_actual:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-sub">Inicial: ${st.session_state.capital_inicial:,.2f}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">PnL acumulado</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{pnl_total_usd:+.2f} USD</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-sub">En {total_trades} trades</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">Winrate global</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{winrate_global:.2f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-sub">Ganados / totales</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


def render_historial_table(df_today: pd.DataFrame):
    if df_today.empty:
        st.info("Hoy todavía no hay operaciones registradas.")
        return

    df_show = df_today.copy()
    for c in ["Par / Token", "Tipo", "Estado operación", "Razón entrada", "Resultado (USD)", "Fecha_dt"]:
        if c not in df_show.columns:
            df_show[c] = ""

    rows_html = ""
    for _, row in df_show.iterrows():
        token = row["Par / Token"]
        tipo = row["Tipo"]
        estado = row["Estado operación"]
        operacion = (row["Razón entrada"] or "")[:30]
        fecha = row["Fecha_dt"].strftime("%Y-%m-%d") if pd.notna(row["Fecha_dt"]) else ""
        pnl_usd = row["Resultado (USD)"]

        try:
            pnl_usd_f = float(pnl_usd)
            pnl_str = f"{pnl_usd_f:+.2f}"
        except Exception:
            pnl_str = str(pnl_usd)

        if tipo == "LONG":
            tipo_html = '<span class="tag-long">Long (Compra)</span>'
        else:
            tipo_html = '<span class="tag-short">Short (Venta)</span>'

        estado_html = f'<span class="tag-estado">{estado}</span>'
        estrategia_html = '<span class="tag-estrategia">Estrategia</span>'

        rows_html += f"""
        <tr>
            <td>{operacion}</td>
            <td>{token}</td>
            <td>{fecha}</td>
            <td>{tipo_html}</td>
            <td>{estado_html}</td>
            <td>{estrategia_html}</td>
            <td>{pnl_str}</td>
        </tr>
        """

    table_html = f"""
    <table class="styled-table">
        <thead>
            <tr>
                <th>Operación</th>
                <th>Par / Activo</th>
                <th>Fecha</th>
                <th>Dirección</th>
                <th>Estado</th>
                <th>Estrategia</th>
                <th>PnL (USD)</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">Trading Journal</div>', unsafe_allow_html=True)
    vista = st.radio(
        "Vista",
        options=["🏠 Home", "📊 Stats", "📅 Calendario"],
        index=0
    )
    st.markdown("---")
    st.caption("Dashboard para tu diario de operaciones de trading.")

# =========================================================
# DATOS
# =========================================================
df_raw = cargar_datos()
df_num = preparar_df_numerico(df_raw)
pnl_total_usd = df_num["Resultado (USD)"].sum(skipna=True) if not df_num.empty else 0.0

# =========================================================
# HOME
# =========================================================
if vista == "🏠 Home":
    st.title("✨ Trading Journal – Home")

    panel_superior(df_num, pnl_total_usd)
    st.markdown("---")
    st.subheader("📝 Trading journal – nueva entrada")

    with st.form("trade_form"):
        # FECHA
        fecha = st.date_input("Fecha", value=date.today())

        # Hora estilo iPhone (hora, minuto, AM/PM)
        now = datetime.now()
        hour_24 = now.hour
        am_default = "AM" if hour_24 < 12 else "PM"
        hour_12_default = hour_24 % 12
        if hour_12_default == 0:
            hour_12_default = 12

        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            hora_12 = st.selectbox(
                "Hora",
                options=list(range(1, 13)),
                index=list(range(1, 13)).index(hour_12_default)
            )
        with col_h2:
            minutos_opciones = [f"{m:02d}" for m in range(60)]
            minuto_default = f"{now.minute:02d}"
            minuto = st.selectbox(
                "Minutos",
                options=minutos_opciones,
                index=minutos_opciones.index(minuto_default)
            )
        with col_h3:
            ampm = st.selectbox(
                "AM / PM",
                options=["AM", "PM"],
                index=["AM", "PM"].index(am_default)
            )

        minuto_int = int(minuto)
        if ampm == "AM":
            hour_24_final = 0 if hora_12 == 12 else hora_12
        else:
            hour_24_final = 12 if hora_12 == 12 else hora_12 + 12
        hora = time(hour_24_final, minuto_int, 0)

        st.markdown("---")

        # ---------- BLOQUE 1: INFO POSICIÓN ----------
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown("#### Información de la posición")

        c1, c2, c3 = st.columns(3)

        with c1:
            par_token = st.text_input("Par / Token", value="", placeholder="Ej. BTCUSDT, SUIUSDT")

            direccion_label = st.selectbox(
                "Dirección",
                ["Long (Compra)", "Short (Venta)"]
            )
            tipo = "LONG" if direccion_label.startswith("Long") else "SHORT"

            senal_de_simple = st.selectbox(
                "Señal de",
                ["Análisis propio", "Bot", "Consejo"]
            )

        with c2:
            tamanio_posicion = st.number_input(
                "Tamaño posición (USD)",
                min_value=0.0,
                step=10.0,
                value=0.0
            )

            apalancamiento = st.number_input(
                "Apalancamiento (x)",
                min_value=1.0,
                step=1.0,
                value=10.0
            )

            estado_operacion = st.selectbox(
                "Estado de la operación",
                [
                    "Operación puesta (esperando entrada)",
                    "Corriendo",
                    "Cerrada - Ganadora",
                    "Cerrada - Perdedora",
                    "Cerrada - Break-even"
                ]
            )

        with c3:
            precio_entrada = st.number_input(
                "Precio de entrada",
                min_value=0.0,
                step=0.0001,
                format="%.4f"
            )
            stop_loss = st.number_input(
                "Stop Loss",
                min_value=0.0,
                step=0.0001,
                format="%.4f"
            )
            take_profit_1 = st.number_input(
                "Take Profit 1",
                min_value=0.0,
                step=0.0001,
                format="%.4f"
            )
            take_profit_2 = st.number_input(
                "Take Profit 2",
                min_value=0.0,
                step=0.0001,
                format="%.4f"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # ---------- BLOQUE 2: CHECKLIST / CONFIRMACIONES ----------
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown("#### Checklist / Confirmaciones")

        estrategias_usadas = []
        rating_label = ""
        rating_value = ""
        confirmaciones_resumen = []
        comentario_estrategia = ""

        opciones_tf = ["1M", "5M", "15M", "30M", "1H", "4H", "Diario", "Semanal", "Mensual"]
        opciones_estrategias = [
            "Patrones de velas",
            "Medias móviles",
            "MACD",
            "RSI",
            "Fibonacci",
            "Estructura de mercado / S-R",
            "Order blocks / SMC",
            "Volumen / Delta",
            "Zonas de liquidez / FVG",
        ]

        if senal_de_simple == "Análisis propio":
            izquierda, derecha = st.columns([2, 1])
            with izquierda:
                st.markdown("##### Estrategia general")
                estrategias_usadas = st.multiselect(
                    "Estrategias principales usadas en el set-up",
                    opciones_estrategias
                )
            with derecha:
                st.markdown("##### Calificación del análisis")
                rating_options = [
                    "⭐ (1/5) Muy pobre",
                    "⭐⭐ (2/5) Pobre",
                    "⭐⭐⭐ (3/5) Aceptable",
                    "⭐⭐⭐⭐ (4/5) Bueno",
                    "⭐⭐⭐⭐⭐ (5/5) Excelente",
                ]
                rating_label = st.select_slider(
                    "",
                    options=rating_options,
                    value=rating_options[3]
                )
                rating_value = rating_options.index(rating_label) + 1

            header_col, btn_col = st.columns([3, 1])
            with header_col:
                st.markdown("##### Confirmaciones por temporalidad")
            with btn_col:
                st.markdown('<div class="agregar-conf-btn">', unsafe_allow_html=True)
                add_conf_clicked = st.form_submit_button("➕ Agregar confirmación")
                st.markdown("</div>", unsafe_allow_html=True)
                if add_conf_clicked:
                    st.session_state.num_confirmaciones += 1

            st.caption(f"Confirmaciones configuradas: {st.session_state.num_confirmaciones}")

            for i in range(st.session_state.num_confirmaciones):
                st.markdown(f"**Confirmación #{i+1}**")
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    tf = st.selectbox(
                        f"Temporalidad #{i+1}",
                        opciones_tf,
                        key=f"tf_conf_{i}"
                    )
                with cc2:
                    estrategias_tf = st.multiselect(
                        "Estrategias usadas",
                        opciones_estrategias,
                        key=f"estr_conf_{i}"
                    )
                with cc3:
                    comentario_conf = st.text_input(
                        f"Comentario confirmación #{i+1}",
                        key=f"coment_conf_{i}",
                        placeholder="Ej. ruptura de estructura + retesteo."
                    )

                resumen = f"{tf}: {', '.join(estrategias_tf) if estrategias_tf else 'Sin estrategias marcadas'} – {comentario_conf}"
                confirmaciones_resumen.append(resumen)

            comentario_estrategia = st.text_area(
                "Comentario general de la estrategia / set-up",
                placeholder="Describe en pocas palabras el set-up completo."
            )

            confirmaciones_estructuradas = " | ".join(
                [x for x in confirmaciones_resumen if x.strip()]
            )

            detalle_senal = (
                f"Tipo: Análisis técnico; "
                f"Estrategias globales: {', '.join(estrategias_usadas) if estrategias_usadas else 'N/A'}; "
                f"Calificación: {rating_label}; "
                f"Comentario: {comentario_estrategia}"
            )

        else:
            if senal_de_simple == "Bot":
                st.info("Esta operación viene de un **Bot**, solo se guardarán notas generales.")
            else:
                st.info("Esta operación viene de un **Consejo**, solo se guardarán notas generales.")

            comentario_estrategia = st.text_area(
                "Notas o comentarios sobre esta señal",
                placeholder="Por qué decidiste seguir esta señal, qué viste, etc."
            )

            confirmaciones_estructuradas = ""
            detalle_senal = (
                f"Tipo: {senal_de_simple}; "
                f"Notas: {comentario_estrategia}"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # ---------- BLOQUE 3: CIERRE Y PSICO ----------
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown("#### Cierre y psicología")

        b1, b2 = st.columns(2)

        with b1:
            modo_cierre = st.selectbox(
                "Modo de cierre",
                ["SL", "TP1", "TP2", "Manual"]
            )

            precio_cierre_manual = None
            if modo_cierre == "Manual":
                precio_cierre_manual = st.number_input(
                    "Precio de cierre (Manual)",
                    min_value=0.0,
                    step=0.0001,
                    format="%.4f"
                )

            razon_entrada = st.text_area(
                "Razón de la entrada",
                placeholder="Por qué entraste en este trade..."
            )

            confirmaciones_texto = st.text_area(
                "Resumen rápido de confirmaciones",
                placeholder="Liquidez, FVG, estructura, news, sesión, etc."
            )

        with b2:
            emocion_opcion = st.selectbox(
                "Emoción durante el trade",
                [
                    "Calmado",
                    "Confiado",
                    "Ansioso",
                    "Con miedo",
                    "FOMO",
                    "Eufórico",
                    "Frustrado",
                    "Irritado",
                    "Otra (manual)",
                ]
            )
            emocion_durante = emocion_opcion
            if emocion_opcion == "Otra (manual)":
                emocion_durante = st.text_input(
                    "Describe tu emoción durante el trade",
                    placeholder="Ej. nervioso pero controlado..."
                )

            emocion_final_opcion = st.selectbox(
                "Emoción al finalizar el trade",
                [
                    "Satisfecho",
                    "Molesto",
                    "Neutral",
                    "Eufórico",
                    "Con FOMO",
                    "Otra (manual)",
                ]
            )
            emocion_final = emocion_final_opcion
            if emocion_final_opcion == "Otra (manual)":
                emocion_final = st.text_input(
                    "Describe tu emoción final",
                    placeholder="Ej. frustrado por salir antes del movimiento..."
                )

            notas_adicionales = st.text_area(
                "Notas adicionales",
                placeholder="Cualquier cosa que quieras recordar de este trade."
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # -------- Cálculo PnL --------
        precio_cierre = None
        if modo_cierre == "Manual":
            if precio_cierre_manual and precio_cierre_manual > 0:
                precio_cierre = precio_cierre_manual
        elif modo_cierre == "SL" and stop_loss > 0:
            precio_cierre = stop_loss
        elif modo_cierre == "TP1" and take_profit_1 > 0:
            precio_cierre = take_profit_1
        elif modo_cierre == "TP2" and take_profit_2 > 0:
            precio_cierre = take_profit_2

        pnl_pct, pnl_usd = calcular_pnl(
            tipo=tipo,
            precio_entrada=precio_entrada,
            precio_cierre=precio_cierre,
            tamanio_posicion=tamanio_posicion,
            apalancamiento=apalancamiento
        )
        resultado_trade = clasificar_resultado(pnl_usd)

        st.markdown("---")
        st.subheader("🔍 Resumen del cálculo (previo a guardar)")

        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(
                "Precio de cierre usado",
                value=f"{precio_cierre:.4f}" if precio_cierre else "N/A"
            )
        with col_res2:
            st.metric(
                "Resultado (%)",
                value=f"{pnl_pct:.2f} %" if pnl_pct is not None else "N/A"
            )
        with col_res3:
            st.metric(
                "Resultado (USD)",
                value=f"{pnl_usd:.2f} $" if pnl_usd is not None else "N/A"
            )

        submitted = st.form_submit_button("💾 Guardar operación")

        if submitted:
            registro = {
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Hora": hora.strftime("%H:%M:%S"),
                "Par / Token": par_token,
                "Tipo": tipo,
                "Tamaño posición (USD)": tamanio_posicion,
                "Apalancamiento (x)": apalancamiento,
                "Señal de (simple)": senal_de_simple,
                "Estado operación": estado_operacion,
                "Precio entrada": precio_entrada,
                "Stop Loss": stop_loss,
                "Take Profit 1": take_profit_1,
                "Take Profit 2": take_profit_2,
                "Modo cierre": modo_cierre,
                "Precio cierre": precio_cierre if precio_cierre else "",
                "Resultado trade": resultado_trade,
                "Resultado (%)": pnl_pct if pnl_pct is not None else "",
                "Resultado (USD)": pnl_usd if pnl_usd is not None else "",
                "Origen señal (detalle)": detalle_senal,
                "Confirmaciones estructuradas": confirmaciones_estructuradas,
                "Razón entrada": razon_entrada,
                "Confirmaciones (texto)": confirmaciones_texto,
                "Emoción durante": emocion_durante,
                "Emoción final": emocion_final,
                "Notas adicionales": notas_adicionales,
                "Calificación numérica": rating_value if senal_de_simple == "Análisis propio" else "",
            }

            guardar_operacion(registro)
            st.success("✅ Operación guardada en trading_journal.csv")

    # Historial del día actual
    st.markdown("---")
    st.header("📅 Historial de operaciones del día")

    df_raw = cargar_datos()
    df_num = preparar_df_numerico(df_raw)

    if not df_num.empty:
        hoy = date.today()
        df_today = df_num[df_num["Fecha_dt"].dt.date == hoy]
        render_historial_table(df_today)
    else:
        st.info("Aún no hay operaciones registradas.")

# =========================================================
# STATS
# =========================================================
elif vista == "📊 Stats":
    st.title("📊 Estadísticas y gráficas")

    df_raw = cargar_datos()
    df_num = preparar_df_numerico(df_raw)
    pnl_total_usd = df_num["Resultado (USD)"].sum(skipna=True) if not df_num.empty else 0.0
    panel_superior(df_num, pnl_total_usd)

    if df_num.empty:
        st.info("Aún no hay datos para mostrar estadísticas.")
    else:
        st.markdown("---")
        modo = st.radio(
            "Agrupar estadísticas por:",
            ["Día", "Semana", "Mes"],
            horizontal=True
        )
        modo_map = {"Día": "dia", "Semana": "semana", "Mes": "mes"}
        modo_id = modo_map[modo]

        df_stats = stats_por(df_num, modo_id)
        if df_stats.empty:
            st.info("No se pudieron calcular estadísticas con los datos actuales.")
        else:
            st.subheader(f"Resumen por {modo.lower()}")
            st.dataframe(df_stats, use_container_width=True)

            col_name = {"dia": "Fecha", "semana": "Semana", "mes": "Mes"}[modo_id]
            chart_data = df_stats.set_index(col_name)[["PnL USD"]]

            st.subheader("Evolución de PnL (USD)")
            st.bar_chart(chart_data)

        # ------- EDICIÓN / BORRADO DE TRADES -------
        st.markdown("---")
        st.subheader("✏️ Editar o borrar trades")

        df_all = df_raw.copy()
        if df_all.empty:
            st.info("No hay trades para editar.")
        else:
            # Asegurar ID
            if "ID" not in df_all.columns:
                df_all.insert(0, "ID", range(1, len(df_all) + 1))
                guardar_df(df_all)

            # ---- Filtros avanzados ----
            with st.expander("Filtros de búsqueda", expanded=False):
                colf1, colf2, colf3 = st.columns(3)
                with colf1:
                    filtro_par = st.text_input(
                        "Par / Token contiene",
                        value=""
                    )
                with colf2:
                    filtro_tipo = st.multiselect(
                        "Tipo",
                        ["LONG", "SHORT"],
                        default=[]
                    )
                with colf3:
                    estados_posibles = [
                        "Operación puesta (esperando entrada)",
                        "Corriendo",
                        "Cerrada - Ganadora",
                        "Cerrada - Perdedora",
                        "Cerrada - Break-even",
                    ]
                    filtro_estado = st.multiselect(
                        "Estado de la operación",
                        estados_posibles,
                        default=[]
                    )

                usar_rango = st.checkbox("Filtrar por rango de fechas", value=False)
                fecha_desde = None
                fecha_hasta = None
                if usar_rango and "Fecha" in df_all.columns:
                    fechas_validas = pd.to_datetime(df_all["Fecha"], errors="coerce").dropna()
                    if not fechas_validas.empty:
                        min_fecha = fechas_validas.min().date()
                        max_fecha = fechas_validas.max().date()
                        colfd, colfh = st.columns(2)
                        with colfd:
                            fecha_desde = st.date_input(
                                "Desde",
                                value=min_fecha,
                                min_value=min_fecha,
                                max_value=max_fecha
                            )
                        with colfh:
                            fecha_hasta = st.date_input(
                                "Hasta",
                                value=max_fecha,
                                min_value=min_fecha,
                                max_value=max_fecha
                            )

            # Aplicar filtros a copia filtrada
            df_filtered = df_all.copy()

            if filtro_par:
                df_filtered = df_filtered[
                    df_filtered["Par / Token"].astype(str).str.contains(filtro_par, case=False, na=False)
                ]
            if filtro_tipo:
                df_filtered = df_filtered[df_filtered["Tipo"].isin(filtro_tipo)]
            if filtro_estado:
                df_filtered = df_filtered[df_filtered["Estado operación"].isin(filtro_estado)]
            if usar_rango and fecha_desde and fecha_hasta and "Fecha" in df_filtered.columns:
                fechas_tmp = pd.to_datetime(df_filtered["Fecha"], errors="coerce")
                mask = (fechas_tmp.dt.date >= fecha_desde) & (fechas_tmp.dt.date <= fecha_hasta)
                df_filtered = df_filtered[mask]

            if df_filtered.empty:
                st.info("No hay trades que coincidan con los filtros seleccionados.")
            else:
                opciones = [
                    f"{int(row.ID)} – {row.get('Fecha', '')} {row.get('Par / Token', '')} ({row.get('Tipo', '')})"
                    for _, row in df_filtered.iterrows()
                ]
                ids = [int(row.ID) for _, row in df_filtered.iterrows()]

                seleccionado = st.selectbox("Selecciona un trade", opciones)
                idx = opciones.index(seleccionado)
                trade_id = ids[idx]

                fila = df_all[df_all["ID"] == trade_id].iloc[0]

                st.write("Vista rápida del trade seleccionado:")
                st.json(fila.to_dict())

                with st.form("edit_trade_form"):
                    col_e1, col_e2, col_e3 = st.columns(3)
                    with col_e1:
                        nueva_fecha = st.date_input(
                            "Fecha",
                            value=pd.to_datetime(fila.get("Fecha", date.today())).date()
                        )
                        nuevo_par = st.text_input(
                            "Par / Token",
                            value=str(fila.get("Par / Token", ""))
                        )
                    with col_e2:
                        nuevo_tipo_label = st.selectbox(
                            "Dirección",
                            ["Long (Compra)", "Short (Venta)"],
                            index=0 if fila.get("Tipo", "LONG") == "LONG" else 1
                        )
                        nuevo_tipo = "LONG" if nuevo_tipo_label.startswith("Long") else "SHORT"

                        nuevo_estado = st.selectbox(
                            "Estado de la operación",
                            [
                                "Operación puesta (esperando entrada)",
                                "Corriendo",
                                "Cerrada - Ganadora",
                                "Cerrada - Perdedora",
                                "Cerrada - Break-even"
                            ],
                            index=0
                            if fila.get("Estado operación", "") not in [
                                "Corriendo",
                                "Cerrada - Ganadora",
                                "Cerrada - Perdedora",
                                "Cerrada - Break-even",
                            ]
                            else [
                                "Operación puesta (esperando entrada)",
                                "Corriendo",
                                "Cerrada - Ganadora",
                                "Cerrada - Perdedora",
                                "Cerrada - Break-even",
                            ].index(fila.get("Estado operación", "Operación puesta (esperando entrada)"))
                        )
                    with col_e3:
                        nuevo_pnl_usd = st.number_input(
                            "Resultado (USD)",
                            value=float(fila.get("Resultado (USD)", 0.0))
                            if str(fila.get("Resultado (USD)", "")).strip() != ""
                            else 0.0,
                            step=1.0
                        )

                    nuevas_notas = st.text_area(
                        "Notas adicionales",
                        value=str(fila.get("Notas adicionales", "")),
                    )

                    guardar_cambios = st.form_submit_button("💾 Guardar cambios")

                if guardar_cambios:
                    df_all.loc[df_all["ID"] == trade_id, "Fecha"] = nueva_fecha.strftime("%Y-%m-%d")
                    df_all.loc[df_all["ID"] == trade_id, "Par / Token"] = nuevo_par
                    df_all.loc[df_all["ID"] == trade_id, "Tipo"] = nuevo_tipo
                    df_all.loc[df_all["ID"] == trade_id, "Estado operación"] = nuevo_estado
                    df_all.loc[df_all["ID"] == trade_id, "Resultado (USD)"] = nuevo_pnl_usd
                    df_all.loc[df_all["ID"] == trade_id, "Notas adicionales"] = nuevas_notas

                    guardar_df(df_all)
                    st.success("✅ Cambios guardados correctamente.")

                eliminar = st.button("🗑️ Borrar trade seleccionado")
                if eliminar:
                    df_all = df_all[df_all["ID"] != trade_id]
                    guardar_df(df_all)
                    st.success("🗑️ Trade eliminado.")

# =========================================================
# CALENDARIO
# =========================================================
elif vista == "📅 Calendario":
    st.title("📅 Calendario de rendimiento")

    df_num = preparar_df_numerico(df_raw)
    pnl_total_usd = df_num["Resultado (USD)"].sum(skipna=True) if not df_num.empty else 0.0
    panel_superior(df_num, pnl_total_usd)

    if df_num.empty:
        st.info("Aún no hay datos para el calendario.")
    else:
        st.markdown("---")
        st.subheader("PnL por día")

        df_daily = stats_por(df_num, "dia")
        if df_daily.empty:
            st.info("No hay datos diarios para mostrar.")
        else:
            st.dataframe(df_daily, use_container_width=True)

            chart_data = df_daily.set_index("Fecha")[["PnL USD"]]
            st.subheader("PnL diario")
            st.bar_chart(chart_data)
