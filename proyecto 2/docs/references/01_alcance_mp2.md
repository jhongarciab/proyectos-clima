# MP2 — Alcance técnico definido (Fase A)

## Estado
**Aprobado** para iniciar desarrollo.

## Región de estudio (caja rectangular)
- Latitud: **4.0°N a 5.5°N**
- Longitud: **-76.5° a -75.0°**

## Fuente de datos
- **ERA5** (ECMWF/Copernicus Climate Data Store)

## Ventana temporal
- **1996–2025** (30 años)

## Variables objetivo
### Superficie (ítems 2, 3 y 4)
- `2m_temperature` (T2m)
- `surface_pressure` (sp)
- `10m_u_component_of_wind` (u10)
- `10m_v_component_of_wind` (v10)

### Vertical (ítem 5)
- `temperature` (niveles de presión)
- `geopotential` (niveles de presión)

## Nota de metodología
El ítem 1 (atmósfera estándar) se desarrolla de forma independiente del reanálisis, y se
usará luego como referencia para comparación con el perfil vertical regional del ítem 5.
