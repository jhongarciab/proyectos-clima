# descargar_era5.py
import cdsapi

c = cdsapi.Client()

variables = {
    "total_precipitation": "era5_precip_ejc.nc",
    "2m_temperature":      "era5_t2m_ejc.nc",
}

for var, filename in variables.items():
    print(f"Descargando {var}...")
    c.retrieve(
        "reanalysis-era5-single-levels-monthly-means",
        {
            "product_type": "monthly_averaged_reanalysis",
            "variable":     var,
            "year":  [str(y) for y in range(1950, 2024)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "time":  "00:00",
            "area":  [7, -77, 3, -73],   # N, W, S, E
            "format": "netcdf",
        },
        f"datos/crudos/era5/{filename}",
    )
    print(f"  -> guardado: datos/crudos/era5/{filename}")
