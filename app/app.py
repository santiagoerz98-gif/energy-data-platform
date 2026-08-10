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

measurement_type = st.sidebar.radio(
    "Tipo de Medición",
    options=["Real", "Forecast", "Scheduled"]
)

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
    measurement_type:str, 
    start_date:datetime.date, 
    end_date:datetime.date
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
        response = requests.get(
            url=API_DEMAND_URL,
            params={
                "geo_name": geo_name,
                "measurement_type": measurement_type,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        response.raise_for_status()
        data = response.json()

        df = pd.json_normalize(data)

        return df 

    except requests.RequestException as e:
        st.error(f"Error de conexión con la API: {e}")
        return pd.DataFrame()

# Cargar los datos de demanda electrica
df_demand = fetch_demand_data(
    geo_name=geo_name,
    measurement_type=measurement_type,
    start_date=start_date,
    end_date=end_date
)

if not df_demand.empty:
    df_demand.rename(columns={"time.datetime_utc": "datetime_utc"}, inplace=True)
    df_demand["datetime_utc"] = pd.to_datetime(df_demand["datetime_utc"], errors="coerce")
    df_demand = df_demand.dropna(subset=["datetime_utc", "demand_mwh"])
    df_demand = df_demand.sort_values("datetime_utc")
    df_demand = df_demand.set_index("datetime_utc")

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
    st.line_chart(df_demand["demand_mwh"], use_container_width=True)

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