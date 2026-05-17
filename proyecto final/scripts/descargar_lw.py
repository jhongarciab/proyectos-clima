import cdsapi
import os

c = cdsapi.Client()
output_dir = "datos/ERA5"

for year in range(1980, 2024):
    output_file = f"{output_dir}/era5_surface_thermal_radiation_downwards_{year}.nc"
    if os.path.exists(output_file):
        print(f"Ya existe {output_file}, saltando.")
        continue

    print(f"Descargando LW {year}...")
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": "surface_thermal_radiation_downwards",
            "year": str(year),
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