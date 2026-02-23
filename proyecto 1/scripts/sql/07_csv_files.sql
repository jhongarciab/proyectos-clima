-- CSV Files

\copy (SELECT * FROM gold.ideam_daily_filled) TO './data/processed/ideam_daily.csv' WITH (FORMAT csv, HEADER true);
\copy (SELECT * FROM gold.nasa_daily) TO './data/processed/nasa_daily.csv' WITH (FORMAT csv, HEADER true);