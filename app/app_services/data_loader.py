import pandas as pd
import streamlit as st
import datetime
from config.settings import API_BASE_URL
import requests

@st.cache_data(ttl=300,show_spinner="Cargando datos de demanda...") # Cache the data for 5 minutes
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
    returns:
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
            url=f"{API_BASE_URL}/demand",
            params=params
        )
        response.raise_for_status()
        data = response.json()

        df = pd.json_normalize(data)

        return df 

    except requests.RequestException as e:
        st.error(f"Error de conexión con la API: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300,show_spinner="Cargando datos de generación...") # Cache the data for 5 minutes
def fetch_generation_data(
    geo_name:str, 
    start_date:datetime.date, 
    end_date:datetime.date,
)->pd.DataFrame:
    """
    Carga los datos de generación electrica desde la API para la región especificada, dentro del rango de fechas proporcionado.

    Args:
        geo_name (str): Región para la cual se desea obtener la generación.
        start_date (datetime.date): Fecha de inicio del rango de consulta.
        end_date (datetime.date): Fecha de fin del rango de consulta.
    returns:
        pd.DataFrame: DataFrame con los datos de generación electrica.
    """
    try:
        params = {
            "geo_name": geo_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
            
        response = requests.get(
            url=f"{API_BASE_URL}/generation",
            params=params
        )
        response.raise_for_status()
        data = response.json()

        df = pd.json_normalize(data)

        return df 

    except requests.RequestException as e:
        st.error(f"Error de conexión con la API: {e}")
        return pd.DataFrame()