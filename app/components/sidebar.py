import pendulum
import streamlit as st
import datetime


def render_sidebar():
    """
    Renderiza la barra lateral de la aplicación, permitiendo al usuario seleccionar la región y el rango de fechas para la consulta de datos de demanda eléctrica.

    Returns:
        tuple: Contiene los valores seleccionados por el usuario:
            - geo_name (str): Región seleccionada.
            - start_date (datetime.date): Fecha de inicio seleccionada.
            - end_date (datetime.date): Fecha de fin seleccionada.
    """
    with st.sidebar:
        st.title("Control de Parámetros")
        st.caption("Filtros y parametros operativos")
        st.divider()

        # ---------------------------------------------------------
        # 1. Rango Temporal
        # ---------------------------------------------------------
        st.subheader("📅 Período de Análisis")
        start_date = st.date_input(
            "Fecha de inicio",
            value=pendulum.now().subtract(months=1).to_date_string(),
        )

        end_date = st.date_input(
            "Fecha de fin",
            value=pendulum.now().to_date_string(),
        )

        granularity = st.selectbox(
            "Agrupar por",
            options=["Hora", "Dia", "Trimestre", "Mes"],
            index=0 # Set default to "Hora"
        )
        # ---------------------------------------------------------
        # 2. Selección de Región
        # ---------------------------------------------------------
        geo_name = st.selectbox(
            "Selecciona la región",
            options=["Península","España"],
            index=0
        )

        agg_func = st.selectbox(
            "Función de Agregación",
            options=["Promedio", "Suma", "Máximo", "Mínimo"],
            index=0 # Set default to "Promedio"
            )
        agg_functions = {
            "Promedio": "mean",
            "Suma": "sum",
            "Máximo": "max",
            "Mínimo": "min"
        }
        # ---------------------------------------------------------
        # 3. Selección de Tipo de Medición
        # ---------------------------------------------------------
        measurement_type = st.multiselect(
            "Tipo de Medición",
            options=["Real", "Forecast", "Scheduled"],
            default=["Real", "Forecast", "Scheduled"]
        )

    return {
        "geo_name": geo_name,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "agg_func": agg_functions[agg_func],
        "measurement_type": measurement_type,
    }

