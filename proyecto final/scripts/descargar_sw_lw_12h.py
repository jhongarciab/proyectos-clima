import cdsapi
import os

c = cdsapi.Client()
output_dir = "datos/ERA5"

for var in ["surface_solar_radiation_downwards", "surface_thermal_radiation_downwards"]:
    output_file = f"{output_dir}/era5_{var}_1980_2023.nc"
    if os.path.exists(output_file):
        print(f"Ya existe {output_file}, saltando.")
        continue

    print(f"Descargando {var}...")
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": var,
            "year": [str(y) for y in range(1980, 2024)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": "12:00",
            "area": [8, -82, 0, -75],
            "format": "netcdf",
        },
        output_file,
    )
    print(f"  -> {output_file}")