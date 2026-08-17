import streamlit as st
import pandas as pd
from components.sidebar import render_sidebar
from components.charts import (
    plot_demand_comparison, 
    plot_generation_mix, 
    plot_generation_mix_timeline, 
    plot_current_renewables_vs_nonrenewables
)
from app_services.data_processor import prepare_demand_plot_df
from app_services.data_loader import fetch_demand_data, fetch_generation_data
from config.settings import API_BASE_URL


# Configuracion inicial de la pagina
st.set_page_config(
    page_title="Dashboard Demanda y Generación de la Red Eléctrica Española", 
    page_icon="⚡", 
    layout="wide"
)

st.title("Dashboard Demanda y Generación de la Red Eléctrica Española")
st.markdown("Visualización de los datos de demanda y generación eléctrica en España, incluyendo la evolución de la generación por fuente y la comparación de demanda real, programada y pronosticada. Fuente de datos: [Red Eléctrica de España](https://www.esios.ree.es/es).")

filters = render_sidebar()

# today = datetime.date.today()
# one_week_ago = today - datetime.timedelta(days=7)

# Cargar los datos de generacion
df_generation = fetch_generation_data(
    geo_name=filters["geo_name"],
    start_date=filters["start_date"],
    end_date=filters["end_date"]
)


# Cargar los datos de demanda electrica
frames = []
for m_type in filters["measurement_type"]:
    df_tmp = fetch_demand_data(
        geo_name=filters["geo_name"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        measurement_type=m_type
    )
    if not df_tmp.empty:
        frames.append(df_tmp)

df_demand = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

df_plot = prepare_demand_plot_df(df_demand, filters)

if not df_plot.empty:
    # Grafico de series temporales de demanda electrica
    st.subheader("Demanda Electrica a lo largo del tiempo")
    fig_demand = plot_demand_comparison(df_plot)
    st.plotly_chart(fig_demand, width='stretch')


else:
    st.info("No se encontraron datos para los parámetros seleccionados.")

st.divider()

st.subheader("Evolución de la generación eléctrica por fuente")
fig_generation_mix_timeline = plot_generation_mix_timeline(df_generation)
st.plotly_chart(fig_generation_mix_timeline, width='stretch', key='generation_mix_timeline_chart')

col1, col2 = st.columns(2)

with col2:
    st.subheader("Comparacion de la generacion de fuentes renovables vs no renovables")
    fig_current_renewables_vs_nonrenewables = plot_current_renewables_vs_nonrenewables(df_generation)
    st.plotly_chart(fig_current_renewables_vs_nonrenewables, width='stretch', key='renewable_vs_nonrenewable_chart')

with col1:
    st.subheader("Distribución de la generación eléctrica por fuente")
    fig_current_generation_mix = plot_generation_mix(df_generation)
    st.plotly_chart(fig_current_generation_mix, width='stretch', key='generation_mix_chart')
