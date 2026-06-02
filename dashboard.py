import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Dashboard Inventario AB",
    layout="wide"
)

# ==========================================
# CARGA DE DATOS
# ==========================================

@st.cache_data
def cargar_datos():
    df = pd.read_excel("TRAZABILIDAD AB.xlsx")

    df["Fecha Salida"] = pd.to_datetime(
        df["Fecha Salida"],
        dayfirst=True,
        errors="coerce"
    )

    return df

df = cargar_datos()
# ==========================================
# TITULO PRINCIPAL
# ==========================================

st.title("📦 Dashboard Inventario AB")

st.caption(
    "Análisis de ventas, transferencias, clasificación ABC y pronósticos de demanda"
)
# ==========================================
# MENÚ LATERAL
# ==========================================

st.sidebar.title("📦 Dashboard Inventario")

menu = st.sidebar.radio(
    "Seleccione una opción",
    [
        "Resumen Ejecutivo",
        "Ventas",
        "Transferencias",
        "ABC",
        "Producto",
        "Pronóstico",
        "Planeamiento",
        "Top Ventas Mensual",
        "Inventario Inteligente",
        "Rotación de Productos"
    ]
)

# ==========================================
# RESUMEN EJECUTIVO
# ==========================================

if menu == "Resumen Ejecutivo":

    st.title("📊 Resumen Ejecutivo")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Registros",
        f"{len(df):,}"
    )

    c2.metric(
        "Productos",
        df["Código Artículo"].nunique()
    )

    c3.metric(
        "Transacciones",
        df["NOMBRE DE TRANSACCION"].nunique()
    )

    c4.metric(
        "Cantidad Vendida",
        f"{df['CANTIDAD VENDIDA'].sum():,.0f}"
    )

    ranking = (
        df.groupby("NOMBRE DE TRANSACCION")
        ["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .sort_values(
            "CANTIDAD VENDIDA",
            ascending=False
        )
    )

    ranking["Participacion"] = (
        ranking["CANTIDAD VENDIDA"]
        / ranking["CANTIDAD VENDIDA"].sum()
        * 100
    )

    fig = px.bar(
        ranking,
        x="Participacion",
        y="NOMBRE DE TRANSACCION",
        orientation="h",
        text=ranking["Participacion"].round(2)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================
# VENTAS
# ==========================================

if menu == "Ventas":

    st.title("📈 Ventas")

    df_ventas = df[
        df["NOMBRE DE TRANSACCION"] == "SALIDA POR VENTAS"
    ]

    años = sorted(
        df_ventas["Fecha Salida"]
        .dt.year
        .dropna()
        .unique()
    )

    año = st.selectbox(
        "Seleccione Año",
        años,
        key="ventas_anio"
    )

    df_ventas = df_ventas[
        df_ventas["Fecha Salida"].dt.year == año
    ]

    top10 = (
        df_ventas
        .groupby(
            ["Código Artículo", "Artículo"]
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .sort_values(
            "CANTIDAD VENDIDA",
            ascending=False
        )
        .head(10)
    )

    st.subheader("Top 10 Productos Más Vendidos")

    st.dataframe(
        top10,
        use_container_width=True
    )

    fig = px.bar(
        top10,
        x="CANTIDAD VENDIDA",
        y="Artículo",
        orientation="h",
        text="CANTIDAD VENDIDA"
    )

    fig.update_layout(
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# TRANSFERENCIAS
# ==========================================

if menu == "Transferencias":

    st.title("🚚 Transferencias")

    df_trans = df[
        df["NOMBRE DE TRANSACCION"]
        == "SALIDA POR TRANSFERENCIA"
    ]

    años = sorted(
        df_trans["Fecha Salida"]
        .dt.year
        .dropna()
        .unique()
    )

    año = st.selectbox(
        "Seleccione Año",
        años,
        key="transferencia_anio"
    )

    df_trans = df_trans[
        df_trans["Fecha Salida"].dt.year == año
    ]

    top10 = (
        df_trans
        .groupby(
            ["Código Artículo", "Artículo"]
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .sort_values(
            "CANTIDAD VENDIDA",
            ascending=False
        )
        .head(10)
    )

    st.subheader("Top 10 Productos Más Transferidos")

    st.dataframe(
        top10,
        use_container_width=True
    )

    fig = px.bar(
        top10,
        x="CANTIDAD VENDIDA",
        y="Artículo",
        orientation="h",
        text="CANTIDAD VENDIDA"
    )

    fig.update_layout(
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# ABC AUTOMÁTICO
# ==========================================

if menu == "ABC":

    st.title("📊 Clasificación ABC")

    df_abc = df[
        df["NOMBRE DE TRANSACCION"] == "SALIDA POR VENTAS"
    ]

    abc = (
        df_abc
        .groupby(
            ["Código Artículo", "Artículo"]
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .sort_values(
            "CANTIDAD VENDIDA",
            ascending=False
        )
    )

    abc["Participacion"] = (
        abc["CANTIDAD VENDIDA"]
        / abc["CANTIDAD VENDIDA"].sum()
    )

    abc["Acumulado"] = abc["Participacion"].cumsum()

    def clasificar(x):
        if x <= 0.80:
            return "A"
        elif x <= 0.95:
            return "B"
        else:
            return "C"

    abc["ABC"] = abc["Acumulado"].apply(clasificar)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Productos A",
        len(abc[abc["ABC"] == "A"])
    )

    c2.metric(
        "Productos B",
        len(abc[abc["ABC"] == "B"])
    )

    c3.metric(
        "Productos C",
        len(abc[abc["ABC"] == "C"])
    )

    st.subheader("Clasificación ABC")

    st.dataframe(
        abc,
        use_container_width=True
    )

    resumen_abc = (
        abc.groupby("ABC")
        .size()
        .reset_index(name="Cantidad")
    )

    fig = px.pie(
        resumen_abc,
        names="ABC",
        values="Cantidad",
        title="Distribución ABC"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# ANALISIS POR PRODUCTO
# ==========================================

if menu == "Producto":

    st.title("🔎 Análisis por Producto")

    codigo = st.selectbox(
        "Seleccione Código",
        sorted(
            df["Código Artículo"]
            .astype(str)
            .unique()
        ),
        key="producto_codigo"
    )

    prod = df[
        df["Código Artículo"]
        .astype(str)
        == codigo
    ].copy()

    if len(prod) == 0:
        st.warning("No hay información.")
        st.stop()

    nombre_producto = (
        prod["Artículo"]
        .iloc[0]
    )

    st.subheader(nombre_producto)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Movimientos",
        len(prod)
    )

    c2.metric(
        "Cantidad Total",
        round(
            prod["CANTIDAD VENDIDA"].sum(),
            2
        )
    )

    c3.metric(
        "Máximo Movimiento",
        round(
            prod["CANTIDAD VENDIDA"].max(),
            2
        )
    )

    c4.metric(
        "Promedio",
        round(
            prod["CANTIDAD VENDIDA"].mean(),
            2
        )
    )

    historial = (
        prod.groupby(
            prod["Fecha Salida"]
            .dt.to_period("M")
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
    )

    historial["Fecha Salida"] = (
        historial["Fecha Salida"]
        .astype(str)
    )

    st.subheader(
        "Histórico Mensual"
    )

    fig = px.line(
        historial,
        x="Fecha Salida",
        y="CANTIDAD VENDIDA",
        markers=True
    )

    fig.update_traces(
        text=historial["CANTIDAD VENDIDA"],
        textposition="top center"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Detalle Histórico"
    )

    st.dataframe(
        historial,
        use_container_width=True
    )

# ==========================================
# PRONÓSTICO
# ==========================================

if menu == "Pronóstico":

    st.title("🔮 Pronóstico de Demanda")

    codigo = st.selectbox(
        "Seleccione Código",
        sorted(
            df["Código Artículo"]
            .astype(str)
            .unique()
        ),
        key="pronostico_codigo"
    )

    prod = df[
        (df["Código Artículo"].astype(str) == codigo)
        &
        (df["NOMBRE DE TRANSACCION"] == "SALIDA POR VENTAS")
    ].copy()

    serie = (
        prod.groupby(
            prod["Fecha Salida"]
            .dt.to_period("M")
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
    )

    if len(serie) < 6:

        st.warning(
            "Se requieren al menos 6 meses de datos para un análisis más confiable."
        )

    else:

        serie["Periodo"] = range(len(serie))

        X = serie[["Periodo"]]
        y = serie["CANTIDAD VENDIDA"]

        modelo = LinearRegression()
        modelo.fit(X, y)

        futuro = pd.DataFrame({
            "Periodo": range(
                len(serie),
                len(serie) + 6
            )
        })

        pronostico = modelo.predict(futuro)

        resultado = pd.DataFrame({
            "Mes Futuro": [
                "Mes +1",
                "Mes +2",
                "Mes +3",
                "Mes +4",
                "Mes +5",
                "Mes +6"
            ],
            "Pronóstico":
            pronostico.round(2)
        })

        st.subheader(
            "Pronóstico Próximos 6 Meses"
        )

        st.dataframe(
            resultado,
            use_container_width=True
        )

        historico = serie[
            ["Periodo", "CANTIDAD VENDIDA"]
        ].copy()

        historico["Tipo"] = "Histórico"

        futuro_plot = pd.DataFrame({
            "Periodo": futuro["Periodo"],
            "CANTIDAD VENDIDA": pronostico
        })

        futuro_plot["Tipo"] = "Pronóstico"

        grafico = pd.concat(
            [historico, futuro_plot]
        )

        fig = px.line(
            grafico,
            x="Periodo",
            y="CANTIDAD VENDIDA",
            color="Tipo",
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ==========================================
# PLANEAMIENTO
# ==========================================

if menu == "Planeamiento":

    st.title("📊 Planeamiento de Demanda")

    ventas = df[
        df["NOMBRE DE TRANSACCION"]
        == "SALIDA POR VENTAS"
    ].copy()

    ventas = ventas[
        ventas["CLASIFICACION"].isin(["A", "B"])
    ]
    total_a = ventas[
        ventas["CLASIFICACION"] == "A"
    ]["CANTIDAD VENDIDA"].sum()

    total_b = ventas[
        ventas["CLASIFICACION"] == "B"
    ]["CANTIDAD VENDIDA"].sum()

    prod_a = ventas[
        ventas["CLASIFICACION"] == "A"
    ]["Código Artículo"].nunique()

    prod_b = ventas[
        ventas["CLASIFICACION"] == "B"
    ]["Código Artículo"].nunique()

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Productos A",
        prod_a
    )

    c2.metric(
        "Productos B",
        prod_b
    )

    c3.metric(
        "Venta Clase A",
        f"{total_a:,.0f}"
    )

    c4.metric(
        "Venta Clase B",
        f"{total_b:,.0f}"
    )
    comparativo = pd.DataFrame({
        "Clasificacion": ["A","B"],
        "Cantidad": [total_a,total_b]
    })

    fig = px.bar(
        comparativo,
        x="Clasificacion",
        y="Cantidad",
        text="Cantidad",
        title="Participación A vs B"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader("🏆 Top 10 Productos Clase A")

    top_a = (
        ventas[
            ventas["CLASIFICACION"] == "A"
        ]
        .groupby(
            ["Código Artículo","Artículo"]
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .sort_values(
            "CANTIDAD VENDIDA",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_a,
        use_container_width=True
    )
    st.subheader("🥈 Top 10 Productos Clase B")

    top_b = (
        ventas[
            ventas["CLASIFICACION"] == "B"
        ]
        .groupby(
            ["Código Artículo","Artículo"]
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .sort_values(
            "CANTIDAD VENDIDA",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_b,
        use_container_width=True
    )
    st.subheader(
        "📈 Tendencia por Producto"
    )

    clase = st.radio(
        "Clasificación",
        ["A","B"]
    )
    lista = (
        ventas[
            ventas["CLASIFICACION"] == clase
        ]
        ["Código Artículo"]
        .astype(str)
        .unique()
    )

    codigo = st.selectbox(
        "Seleccione Código",
        sorted(lista)
    )
    producto = ventas[
        ventas["Código Artículo"]
        .astype(str)
        == codigo
    ]
    historico = (
        producto.groupby(
            producto["Fecha Salida"]
            .dt.to_period("M")
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
    )

    historico["Fecha Salida"] = (
        historico["Fecha Salida"]
        .astype(str)
    )
    fig = px.line(
        historico,
        x="Fecha Salida",
        y="CANTIDAD VENDIDA",
        markers=True,
        title=f"Tendencia Producto {codigo}"
    )

    fig.update_traces(
        text=historico["CANTIDAD VENDIDA"],
        textposition="top center"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
# ==========================================
# TOP VENTAS MENSUAL
# ==========================================

if menu == "Top Ventas Mensual":

    st.title("🏆 Top Ventas por Mes")

    ventas = df[
        df["NOMBRE DE TRANSACCION"]
        == "SALIDA POR VENTAS"
    ].copy()

    # -----------------------
    # Filtros
    # -----------------------

    años = sorted(
        ventas["Fecha Salida"]
        .dt.year
        .dropna()
        .unique()
    )

    año = st.selectbox(
        "Seleccione Año",
        años
    )

    meses = {
        1:"Enero",
        2:"Febrero",
        3:"Marzo",
        4:"Abril",
        5:"Mayo",
        6:"Junio",
        7:"Julio",
        8:"Agosto",
        9:"Septiembre",
        10:"Octubre",
        11:"Noviembre",
        12:"Diciembre"
    }

    mes_nombre = st.selectbox(
        "Seleccione Mes",
        list(meses.values())
    )

    mes_num = list(meses.keys())[
        list(meses.values()).index(mes_nombre)
    ]

    clasificacion = st.selectbox(
        "Clasificación",
        ["TODAS","A","B","C"]
    )

    filtro = ventas[
        (ventas["Fecha Salida"].dt.year == año)
        &
        (ventas["Fecha Salida"].dt.month == mes_num)
    ]

    if clasificacion != "TODAS":

        filtro = filtro[
            filtro["CLASIFICACION"]
            == clasificacion
        ]

    # -----------------------
    # KPIs
    # -----------------------

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Cantidad Vendida",
        f"{filtro['CANTIDAD VENDIDA'].sum():,.0f}"
    )

    c2.metric(
        "Productos",
        filtro["Código Artículo"].nunique()
    )

    c3.metric(
        "Registros",
        len(filtro)
    )

    # -----------------------
    # Top 10
    # -----------------------

    top10 = (
        filtro
        .groupby(
            ["Código Artículo","Artículo"]
        )["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .sort_values(
            "CANTIDAD VENDIDA",
            ascending=False
        )
        .head(10)
    )

    st.subheader(
        "🏆 Top 10 Productos"
    )

    st.dataframe(
        top10,
        use_container_width=True
    )

    fig = px.bar(
        top10,
        x="CANTIDAD VENDIDA",
        y="Artículo",
        orientation="h",
        text="CANTIDAD VENDIDA"
    )

    fig.update_layout(
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------
    # Comparativo Año Anterior
    # -----------------------

    año_anterior = año - 1

    actual = filtro[
        "CANTIDAD VENDIDA"
    ].sum()

    anterior = ventas[
        (ventas["Fecha Salida"].dt.year == año_anterior)
        &
        (ventas["Fecha Salida"].dt.month == mes_num)
    ]

    if clasificacion != "TODAS":

        anterior = anterior[
            anterior["CLASIFICACION"]
            == clasificacion
        ]

    anterior_total = anterior[
        "CANTIDAD VENDIDA"
    ].sum()

    if anterior_total > 0:

        variacion = (
            (
                actual
                -
                anterior_total
            )
            /
            anterior_total
        ) * 100

        st.subheader(
            "📈 Comparativo Año Anterior"
        )

        c1,c2,c3 = st.columns(3)

        c1.metric(
            f"{año_anterior}",
            f"{anterior_total:,.0f}"
        )

        c2.metric(
            f"{año}",
            f"{actual:,.0f}"
        )

        c3.metric(
            "Variación %",
            f"{variacion:,.2f}%"
        )

    # -----------------------
    # Top Crecimiento
    # -----------------------

    st.subheader(
        "🚀 Productos con Mayor Crecimiento"
    )

    actual_cod = (
        filtro
        .groupby("Código Artículo")
        ["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "CANTIDAD VENDIDA":"Actual"
            }
        )
    )

    anterior_cod = (
        anterior
        .groupby("Código Artículo")
        ["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "CANTIDAD VENDIDA":"Anterior"
            }
        )
    )

    crecimiento = pd.merge(
        actual_cod,
        anterior_cod,
        on="Código Artículo",
        how="inner"
    )

    crecimiento = crecimiento[
        crecimiento["Anterior"] > 0
    ]

    crecimiento["Variacion %"] = (
        (
            crecimiento["Actual"]
            -
            crecimiento["Anterior"]
        )
        /
        crecimiento["Anterior"]
    ) * 100

    crecimiento = crecimiento.sort_values(
        "Variacion %",
        ascending=False
    ).head(10)

    st.dataframe(
        crecimiento,
        use_container_width=True
    )
# ==========================================
# INVENTARIO INTELIGENTE
# ==========================================

if menu == "Inventario Inteligente":

    st.title("📦 Inventario Inteligente")

    dias = st.selectbox(
        "Seleccione período sin movimiento",
        [90, 180, 365]
    )

    ventas = df[
        df["NOMBRE DE TRANSACCION"]
        == "SALIDA POR VENTAS"
    ].copy()

    ultima_fecha = ventas["Fecha Salida"].max()

    ultimo_movimiento = (
        ventas
        .groupby(
            ["Código Artículo", "Artículo", "CLASIFICACION"]
        )["Fecha Salida"]
        .max()
        .reset_index()
    )

    ultimo_movimiento["Dias Sin Movimiento"] = (
        ultima_fecha -
        ultimo_movimiento["Fecha Salida"]
    ).dt.days

    sin_movimiento = ultimo_movimiento[
        ultimo_movimiento["Dias Sin Movimiento"] >= dias
    ]

    # KPI

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Productos Sin Movimiento",
        len(sin_movimiento)
    )

    c2.metric(
        "Productos Clase A",
        len(
            sin_movimiento[
                sin_movimiento["CLASIFICACION"] == "A"
            ]
        )
    )

    c3.metric(
        "Productos Clase B",
        len(
            sin_movimiento[
                sin_movimiento["CLASIFICACION"] == "B"
            ]
        )
    )

    st.subheader(
        f"Productos sin movimiento por más de {dias} días"
    )

    st.dataframe(
        sin_movimiento.sort_values(
            "Dias Sin Movimiento",
            ascending=False
        ),
        use_container_width=True
    )
st.markdown("---")

st.subheader(
        "🚚 Ratio Transferencia / Venta"
    )

ventas_tot = (
        df[
            df["NOMBRE DE TRANSACCION"]
            == "SALIDA POR VENTAS"
        ]
        .groupby("Código Artículo")
        ["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "CANTIDAD VENDIDA":"Ventas"
            }
        )
    )

transf_tot = (
        df[
            df["NOMBRE DE TRANSACCION"]
            == "SALIDA POR TRANSFERENCIA"
        ]
        .groupby("Código Artículo")
        ["CANTIDAD VENDIDA"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "CANTIDAD VENDIDA":"Transferencias"
            }
        )
    )

ratio = pd.merge(
        ventas_tot,
        transf_tot,
        on="Código Artículo",
        how="inner"
    )

ratio = ratio[
        ratio["Ventas"] > 0
    ]

ratio["Ratio %"] = (
        ratio["Transferencias"]
        /
        ratio["Ventas"]
    ) * 100

ratio = ratio.sort_values(
        "Ratio %",
        ascending=False
    )

st.dataframe(
        ratio.head(20),
        use_container_width=True
    )
st.markdown("---")

st.subheader(
        "⚠ Alertas Logísticas"
    )

alertas = ratio[
        ratio["Ratio %"] > 80
    ]

st.write(
        f"Productos con ratio mayor a 80%: {len(alertas)}"
    )

st.dataframe(
        alertas.head(20),
        use_container_width=True
    )
# ==========================================
# ROTACION DE PRODUCTOS (V7)
# ==========================================

if menu == "Rotación de Productos":

    st.title("📈 Rotación de Productos")

    clasificacion = st.selectbox(
        "Clasificación",
        ["TODAS", "A", "B", "C"]
    )

    df_rot = df.copy()

    if clasificacion != "TODAS":
        df_rot = df_rot[
            df_rot["CLASIFICACION"] == clasificacion
        ]

    codigo = st.selectbox(
        "Seleccione Código",
        sorted(
            df_rot["Código Artículo"]
            .astype(str)
            .unique()
        ),
        key="rotacion_codigo"
    )

    producto = df_rot[
        df_rot["Código Artículo"].astype(str) == codigo
    ].copy()

    # Solo ventas
    producto = producto[
        producto["NOMBRE DE TRANSACCION"]
        == "SALIDA POR VENTAS"
    ]

    if len(producto) == 0:

        st.warning(
            "No existen ventas para este producto."
        )

else:

        # =========================
        # RESUMEN
        # =========================

    total_vendido = producto[
            "CANTIDAD VENDIDA"
        ].sum()

    ultimo_mes = (
            producto["Fecha Salida"]
            .max()
        )

    ult_3m = producto[
            producto["Fecha Salida"] >=
            (ultimo_mes - pd.DateOffset(months=3))
        ]["CANTIDAD VENDIDA"].sum()

    ult_6m = producto[
            producto["Fecha Salida"] >=
            (ultimo_mes - pd.DateOffset(months=6))
        ]["CANTIDAD VENDIDA"].sum()

    ult_12m = producto[
            producto["Fecha Salida"] >=
            (ultimo_mes - pd.DateOffset(months=12))
        ]["CANTIDAD VENDIDA"].sum()

    promedio_mensual = (
            producto
            .groupby(
                producto["Fecha Salida"]
                .dt.to_period("M")
            )["CANTIDAD VENDIDA"]
            .sum()
            .mean()
        )

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric(
            "Venta Total",
            f"{total_vendido:,.0f}"
        )

    c2.metric(
            "Promedio Mensual",
            f"{promedio_mensual:,.0f}"
        )

    c3.metric(
            "Últimos 3 Meses",
            f"{ult_3m:,.0f}"
        )

    c4.metric(
            "Últimos 6 Meses",
            f"{ult_6m:,.0f}"
        )

    c5.metric(
            "Últimos 12 Meses",
            f"{ult_12m:,.0f}"
        )

    st.markdown("---")

    # =========================
    # VENTAS POR AÑO
    # =========================

    st.subheader("📊 Ventas por Año")

    ventas_anuales = (
            producto
            .groupby(
                producto["Fecha Salida"].dt.year
            )["CANTIDAD VENDIDA"]
            .sum()
            .reset_index()
        )

    ventas_anuales.columns = [
            "Año",
            "Cantidad"
        ]

    st.dataframe(
            ventas_anuales,
            use_container_width=True
        )

    fig = px.bar(
            ventas_anuales,
            x="Año",
            y="Cantidad",
            text="Cantidad"
        )

    st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

        # =========================
        # TABLA MENSUAL
        # =========================

    st.subheader(
            "📅 Comportamiento Mensual"
        )

    producto["Año"] = (
            producto["Fecha Salida"]
            .dt.year
        )

    producto["Mes"] = (
            producto["Fecha Salida"]
            .dt.month_name()
        )

    tabla = pd.pivot_table(
            producto,
            values="CANTIDAD VENDIDA",
            index="Año",
            columns="Mes",
            aggfunc="sum",
            fill_value=0
        )

    orden = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

    columnas_existentes = [
            c for c in orden
            if c in tabla.columns
        ]

    tabla = tabla[
            columnas_existentes
        ]

    st.dataframe(
            tabla,
            use_container_width=True
        )

    st.markdown("---")

    # =========================
    # TENDENCIA MENSUAL
    # =========================

    st.subheader(
            "📈 Tendencia Mensual"
        )

    tendencia = (
            producto
            .groupby(
                producto["Fecha Salida"]
                .dt.to_period("M")
            )["CANTIDAD VENDIDA"]
            .sum()
            .reset_index()
        )

    tendencia["Fecha"] = (
            tendencia["Fecha Salida"]
            .astype(str)
        )

    fig = px.line(
            tendencia,
            x="Fecha",
            y="CANTIDAD VENDIDA",
            markers=True
        )

    fig.update_traces(
            text=tendencia[
                "CANTIDAD VENDIDA"
            ],
            textposition="top center"
        )

    st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =========================
        # SEMAFORO
        # =========================

        st.markdown("---")

        st.subheader(
            "🚦 Estado de Rotación"
        )
if promedio_mensual >= 100:
            st.success(
                "🟢 Alta Rotación"
            )

elif promedio_mensual >= 20:
            st.warning(
                "🟡 Rotación Media"
            )

else:
            st.error(
                "🔴 Baja Rotación"
            )
