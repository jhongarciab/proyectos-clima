# MP2 — Ítem 2 (estado)

## Avance realizado
1. Se definió formalmente la fuente ERA5 y el dataset mensual de niveles de superficie.
2. Se codificó script de descarga reproducible con request persistente en JSON.
3. Se fijaron variables y dominio en archivo de configuración central.

## Pendiente para cerrar el ítem 2
Ejecutar descarga con credenciales activas de Copernicus CDS (`~/.cdsapirc`) para generar:
- `data/raw/era5_surface_monthly_2015_2024.nc`

## Nota
En este entorno aún no existe `~/.cdsapirc`, por lo que la descarga automática no se ejecuta hasta configurar acceso CDS.
