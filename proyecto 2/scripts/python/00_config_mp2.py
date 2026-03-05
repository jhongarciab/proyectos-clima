"""Configuración central del MP2."""

# Región aprobada (N, W, S, E) para CDS/ERA5
AREA = [5.5, -76.5, 4.0, -75.0]

# Período aprobado
YEAR_START = 2015
YEAR_END = 2024
YEARS = [str(y) for y in range(YEAR_START, YEAR_END + 1)]

# Variables de superficie (ERA5 monthly means)
ERA5_SURFACE_VARIABLES = [
    "2m_temperature",
    "surface_pressure",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
]

# Variables en niveles de presión (para ítem 5; no se descargan en script de ítem 2)
ERA5_PRESSURE_LEVEL_VARIABLES = [
    "temperature",
    "geopotential",
]

PRESSURE_LEVELS_HPA = [
    "1000", "925", "850", "700", "600", "500", "400", "300", "250", "200", "150", "100",
]
