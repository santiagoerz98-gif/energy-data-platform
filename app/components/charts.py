import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app_config import PLOT_LAYOUT_DEFAULTS, COLOR_MAP


# -----------------------------------------------------------------------------
# 1. GRÁFICO DE DEMANDA ELÉCTRICA (LÍNEAS)
# -----------------------------------------------------------------------------

def plot_demand_comparison(df_plot_demand: pd.DataFrame):
    """Genera un gráfico de líneas comparando Demanda Real, Programada y Pronosticada.

    Args:
        df_plot_demand (pd.DataFrame): Debe contener columnas ['timestamp', 'Real',
          'Forecast', 'Scheduled'] con los datos de demanda.

    Returns:
        go.Figure: Objeto Plotly con la curva de demanda.
    """

    fig = go.Figure()

    if 'Real' in df_plot_demand.columns:
        fig.add_trace(go.Scatter(
            x=df_plot_demand.index,
            y=df_plot_demand['Real'],
            mode='lines',
            name='Demanda Real',
            line=dict(color="#1E88E5", width=3)
        ))

    if 'Forecast' in df_plot_demand.columns:
        fig.add_trace(go.Scatter(
            x=df_plot_demand.index,
            y=df_plot_demand['Forecast'],
            mode='lines',
            name='Demanda Pronosticada',
            line=dict(color="#E53935", width=3, dash='dash')
        )) 

    if 'Scheduled' in df_plot_demand.columns:
        fig.add_trace(go.Scatter(
            x=df_plot_demand.index,
            y=df_plot_demand['Scheduled'],
            mode='lines',
            name='Demanda Programada',
            line=dict(color="#757575", width=3, dash='dot')
        ))

    fig.update_layout(
        title="Comparación de Demanda Eléctrica",
        xaxis_title='Fecha/Hora',
        yaxis_title='Demanda (MWh)',
        **PLOT_LAYOUT_DEFAULTS
    )

    return fig

# -----------------------------------------------------------------------------
# 2. GRÁFICO DE GENERACIÓN POR FUENTE (ÁREA APILADA)
# -----------------------------------------------------------------------------
def plot_generation_mix_timeline(df_generation: pd.DataFrame) -> go.Figure:
    """Genera un gráfico de área apilada mostrando la evolución temporal de la generación eléctrica por fuente.

    Args:
        df_generation (pd.DataFrame): Debe contener columnas ['timestamp', "energy_source", "value"] con los datos de generación por fuente.

    Returns:
        go.Figure: Objeto Plotly con la curva de generación por fuente.
    """

    if df_generation.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de generación disponibles para el período seleccionado.", 
            showarrow=False, 
            font=dict(size=16)
        )
        return fig

    fig = px.area(
        df_generation,
        x='time.datetime_utc',
        y='generation_mwh',
        color='energy_source.technology_name',
        color_discrete_map=COLOR_MAP,
        labels={
            "time.datetime_utc": "Fecha y Hora (UTC)",
            "generation_mwh": "Generación (MWh)",
            "energy_source.technology_name": "Tecnología",
        },
    )

    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>"
        + "📅 Fecha: %{x|%d/%m/%Y %H:%M}<br>"
        + "⚡ Generación: <b>%{y:,.2f} MWh</b>"
        + "<extra></extra>"  # Elimina la etiqueta secundaria gris de la derecha
    )
    
    fig.update_layout(
        **PLOT_LAYOUT_DEFAULTS
    )
    return fig

# 2. Mix Energético Instantáneo (Dona)
def plot_generation_mix(df_generation: pd.DataFrame) -> go.Figure:
    """Genera un gráfico de barras mostrando la distribución de la generación eléctrica por fuente dentro del rango temporal seleccionado.

    Args:
        df_generation (pd.DataFrame): Debe contener columnas ['timestamp', "energy_source", "value"] con los datos de generación por fuente.

    Returns:
        go.Figure: Objeto Plotly con la distribución dentro del rango temporal seleccionado de la generación por fuente.
    """

    if df_generation.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de generación disponibles para el período seleccionado.", 
            showarrow=False, 
            font=dict(size=16)
        )
        return fig

    df_summary = df_generation.groupby('energy_source.technology_name', as_index=False)['generation_mwh'].sum()
    df_summary = df_summary.sort_values(by='generation_mwh', ascending=False)

    fig = px.bar(
        df_summary,
        x='energy_source.technology_name',
        y='generation_mwh',
        title=f"<b>Mix Energético en el período seleccionado</b>",
        labels={
            "energy_source.technology_name": "Fuente de Energía",
            "generation_mwh": "Generación (MWh)",
        },
        color='energy_source.technology_name',
    )

    fig.update_traces(
        textposition='auto',
        hovertemplate='%{x}: %{y} MWh'
    )

    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    
    return fig

# Renovables vs no renovables 
def plot_current_renewables_vs_nonrenewables(df_generation: pd.DataFrame) -> go.Figure:
    """Genera un gráfico de dona comparando la generación de fuentes renovables y no renovables.

    Args:
        df_generation (pd.DataFrame): Debe contener columnas ['time.datetime_utc', "energy_source.renewable", "generation_mwh"] con los datos de generación por fuente.
        Se utilizará el resumen del rango temporal seleccionado.

    Returns:
        go.Figure: Objeto Plotly con la comparación de generación renovable vs no renovable.
    """

    if df_generation.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de generación disponibles para el período seleccionado.", 
            showarrow=False, 
            font=dict(size=16)
        )
        return fig

    df_generation['type'] = df_generation['energy_source.renewable'].apply(
        lambda x: 'Renovables' if x else 'No Renovables'
    )

    df_summary = df_generation.groupby('type', as_index=False)['generation_mwh'].sum()



    fig = px.pie(
        df_summary,
        names='type',
        values='generation_mwh',
        hole=0.45,
        color='type',
        color_discrete_map={'Renovables': "#1EE588", 'No Renovables': '#E53935'},
        title=f"Comparación de Generación Renovable vs No Renovable",
        )

    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='%{label}: %{value} MW (%{percent})'
    )

    fig.update_layout(showlegend=False, **PLOT_LAYOUT_DEFAULTS)
    
    return fig