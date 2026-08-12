COLOR_MAP = {
    # ☀️ Energías Solares (Gama Cálida/Amarillos)
    "Solar fotovoltaica": "#FFC107",  # Amarillo solar brillante (reemplaza al azul dominante)
    "Solar": "#FFD54F",  # Amarillo suave
    "Solar térmica": "#FF7043",  # Naranja cálido térmico
    # 💨 Viento y Agua
    "Eólica": "#7E57C2",  # Púrpura (mantiene el tono distinctivo de tu gráfica)
    "Hidráulica": "#03A9F4",  # Azul agua / Cyan claro
    # 🏭 Térmicas y Fósiles
    "Ciclo combinado": "#FF9800",  # Naranja ámbar
    "Nuclear": "#E65100",  # Naranja oscuro / Terracota
    "Carbón": "#37474F",  # Gris carbón / Pizarra oscuro
    "Fuel-gas": "#E53935",  # Rojo vivo
    "Generación T.Real Turbina de vapor": "#8D6E63",  # Marrón térmico
    # 🌐 Red e Interconexiones
    "Intercambios": "#009688",  # Verde turquesa / Teal
    "Resto generación": "#9E9E9E",  # Gris neutro
}

PLOT_LAYOUT_DEFAULTS = dict(
    font=dict(family="Arial, sans-serif", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode="x unified",
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
    ),
)