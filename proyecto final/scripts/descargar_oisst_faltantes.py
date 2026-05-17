import xarray as xr
import os
import calendar

output_dir = "datos/OISST"
base_url = "https://www.ncei.noaa.gov/thredds/dodsC/OisstBase/NetCDF/V2.1/AVHRR"

for year in [2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    output_file = f"{output_dir}/oisst_{year}.nc"
    if os.path.exists(output_file):
        print(f"Ya existe {output_file}, saltando.")
        continue

    print(f"Descargando OISST {year}...")
    datasets = []

    for month in range(1, 13):
        days_in_month = calendar.monthrange(year, month)[1]
        for day in range(1, days_in_month + 1):
            url = (
                f"{base_url}/{year}{month:02d}/"
                f"oisst-avhrr-v02r01.{year}{month:02d}{day:02d}.nc"
            )
            try:
                ds = xr.open_dataset(url)
                sub = ds["sst"][:, :, 360:393, 1111:1140].load()
                datasets.append(sub)
                ds.close()
            except Exception as e:
                print(f"  Error {year}-{month:02d}-{day:02d}: {e}")

    if datasets:
        year_da = xr.concat(datasets, dim="time")
        year_da.to_netcdf(output_file)
        print(f"  -> {output_file}")

print("Listo.")