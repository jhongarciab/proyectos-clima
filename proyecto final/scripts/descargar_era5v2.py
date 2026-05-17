import cdsapi
import os

c = cdsapi.Client()
output_dir = "datos/ERA5"

# Bloques de 2 años, de mas reciente a mas antiguo
years = list(range(1980, 2024))
bloques = [years[i:i+2] for i in range(0, len(years), 2)]
bloques = list(reversed(bloques))

for bloque in bloques:
    year_str = "_".join(str(y) for y in bloque)
    output_file = f"{output_dir}/era5_surface_thermal_radiation_downwards_{year_str}.nc"
    if os.path.exists(output_file):
        print(f"Ya existe {output_file}, saltando.")
        continue

    # Saltar años que ya descargó el script individual
    ya_existen = all(
        os.path.exists(f"{output_dir}/era5_surface_thermal_radiation_downwards_{y}.nc")
        for y in bloque
    )
    if ya_existen:
        print(f"Ya existen archivos individuales para {bloque}, saltando.")
        continue

    print(f"Descargando LW {bloque}...")
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": "surface_thermal_radiation_downwards",
            "year": [str(y) for y in bloque],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": ["00:00", "03:00", "06:00", "09:00",
                     "12:00", "15:00", "18:00", "21:00"],
            "area": [8, -82, 0, -75],
            "format": "netcdf",
        },
        output_file,
    )
    print(f"  -> {output_file}")