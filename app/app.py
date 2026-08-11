import streamlit as st
import pandas as pd
import requests
from config.settings import API_DEMAND_URL
import datetime

# Configuracion inicial de la pagina
st.set_page_config(
    page_title="Dashboard Demanda Electrica", 
    page_icon="⚡", 
    layout="wide"
)

st.title("Dashboard Demanda Electrica")
st.markdown("Visualizacion de los datos de demanda electrica servidos por la API de ESIOS")

st.sidebar.header("Parametros de consulta")

geo_name = st.sidebar.selectbox(
    "Selecciona una región",
    options=["Península"]
)

measurement_type = st.sidebar.multiselect(
    "Tipo de Medición",
    options=["Real", "Forecast", "Scheduled"],
    default=["Real", "Forecast", "Scheduled"]
)

granularity = st.sidebar.selectbox(
    "Agrupar por",
    options=["Hora", "Dia", "Trimestre", "Mes"],
    index=0 # Set default to "Hora"
)

agg_func = st.sidebar.selectbox(
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

# today = datetime.date.today()
# one_week_ago = today - datetime.timedelta(days=7)



start_date = st.sidebar.date_input(
    "Fecha de inicio",
    value=datetime.date(2026, 7, 1),
)

end_date = st.sidebar.date_input(
    "Fecha de fin",
    value=datetime.date(2026, 7, 10)
)

@st.cache_data(ttl=300) # Cache the data for 5 minutes
def fetch_demand_data(
    geo_name:str, 
    start_date:datetime.date, 
    end_date:datetime.date,
    measurement_type: str | None = None,
)->pd.DataFrame:
    """
    Carga los datos de demanda electrica desde la API para la región y tipo de medición especificados, dentro del rango de fechas proporcionado.

    Args:
        geo_name (str): Región para la cual se desea obtener la demanda.
        measurement_type (str): Tipo de medición ("Real", "Forecast", "Scheduled").
        start_date (datetime.date): Fecha de inicio del rango de consulta.
        end_date (datetime.date): Fecha de fin del rango de consulta.

    Returns:
        pd.DataFrame: DataFrame con los datos de demanda electrica.
    """
    try:
        params = {
            "geo_name": geo_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        if measurement_type:
            params["measurement_type"] = measurement_type
            
        response = requests.get(
            url=API_DEMAND_URL,
            params=params
        )
        response.raise_for_status()
        data = response.json()

        df = pd.json_normalize(data)

        return df 

    except requests.RequestException as e:
        st.error(f"Error de conexión con la API: {e}")
        return pd.DataFrame()

# Cargar los datos de demanda electrica
frames = []
for m_type in measurement_type:
    df_tmp = fetch_demand_data(
        geo_name=geo_name,
        start_date=start_date,
        end_date=end_date,
        measurement_type=m_type
    )
    if not df_tmp.empty:
        frames.append(df_tmp)

df_demand = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

if not df_demand.empty:
    df_demand.rename(columns={"time.datetime_utc": "datetime_utc"}, inplace=True)
    df_demand["datetime_utc"] = pd.to_datetime(df_demand["datetime_utc"], errors="coerce")
    df_demand = df_demand.dropna(subset=["datetime_utc", "demand_mwh", "measurement_type"])

    if granularity == "Hora":
        df_demand["bucket_time"] = df_demand["datetime_utc"].dt.floor("h")
    elif granularity == "Dia":
        df_demand["bucket_time"] = df_demand["datetime_utc"].dt.floor("d")
    elif granularity == "Mes":
        df_demand["bucket_time"] = df_demand["datetime_utc"].dt.to_period("M")
    elif granularity == "Trimestre":
        # Mes inicial del trimestre: 1, 4, 7, 10
        q_start_month = (df_demand["time.quarter"] - 1) * 3 + 1
        df_demand["bucket_time"] = pd.to_datetime(
            dict(
                year=df_demand["time.year"],
                month=q_start_month,
                day=1,
            ),
            errors="coerce",
            utc=True
        )

    df_plot = (
        df_demand
        .groupby(["bucket_time","measurement_type"], as_index=False)["demand_mwh"]
        .agg(agg_functions[agg_func])
        .pivot_table(
            index="bucket_time",
            columns="measurement_type",
            values="demand_mwh"
        )
        .sort_index()
    )

    # Fila de métricas clave (KPIs)
    col1, col2, col3 = st.columns(3)

    last_record = df_demand["demand_mwh"].iloc[-1]
    col1.metric("Último valor de Demanda (MWh)", f"{last_record:.2f} MWh")

    avg_demand = df_demand["demand_mwh"].mean()
    col2.metric("Demanda Promedio (MWh)", f"{avg_demand:.2f} MWh")

    max_demand = df_demand["demand_mwh"].max()
    col3.metric("Pico Máximo (MWh)", f"{max_demand:.2f} MWh")

    st.divider()

    # Grafico de series temporales de demanda electrica
    st.subheader("Demanda Electrica a lo largo del tiempo")
    st.line_chart(df_plot, width='stretch')

    # Boton para descargar los datos en formato CSV
    csv = df_demand.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar datos en CSV",
        data=csv,
        file_name='demanda_electrica.csv',
        mime='text/csv',
    )

else:
    st.info("No se encontraron datos para los parámetros seleccionados.")