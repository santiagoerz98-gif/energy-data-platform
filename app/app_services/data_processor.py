import pandas as pd
from typing import Dict, Any

def prepare_demand_plot_df(raw_df:pd.DataFrame, filters:Dict[str,Any]):
    """
    Prepara el DataFrame para la visualización de la demanda electrica, aplicando filtros y agregaciones según los parámetros proporcionados.

    Args:
        raw_df (pd.DataFrame): DataFrame crudo con los datos de demanda electrica.
        filters (Dict[str, Any]): Diccionario con los filtros y parámetros seleccionados por el usuario.

    Returns:
        pd.DataFrame: DataFrame preparado para la visualización de la demanda electrica.
    """

    if raw_df.empty:
        return pd.DataFrame()  # Retorna un DataFrame vacío si no hay datos

    df_demand = raw_df.copy()

    df_demand.rename(columns={"time.datetime_utc": "datetime_utc"}, inplace=True)
    df_demand["datetime_utc"] = pd.to_datetime(df_demand["datetime_utc"], errors="coerce")
    df_demand = df_demand.dropna(subset=["datetime_utc", "demand_mwh", "measurement_type"])

    if filters["granularity"] == "Hora":
        df_demand["bucket_time"] = df_demand["datetime_utc"].dt.floor("h")
    elif filters["granularity"] == "Dia":
        df_demand["bucket_time"] = df_demand["datetime_utc"].dt.floor("d")
    elif filters["granularity"] == "Mes":
        df_demand["bucket_time"] = df_demand["datetime_utc"].dt.to_period("M")
    elif filters["granularity"] == "Trimestre":
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
        .agg(filters["agg_func"])
        .pivot_table(
            index="bucket_time",
            columns="measurement_type",
            values="demand_mwh"
        )
        .sort_index()
    )

    return df_plot

