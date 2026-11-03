# AusCoast_ENSO

ENSO effects on Australian shelf SST and marine heatwaves from OISST v2.1 (ia39 copy, 1982–2024).

All choices are in `notebooks/ausenso.py`. Run the notebooks in order on ARE, using the **Python (mhw3d)** kernel and storage `gdata/ia39+gdata/xp65+scratch/m35`.

| Notebook | Does | Main output (in `/scratch/m35/$USER/AusCoast_ENSO`) |
|---|---|---|
| 00_subset_oisst | Australian-domain subset and Niño3.4/DMI box means | `oisst_aus_daily.zarr`, `index_boxes_daily.nc` |
| 01_enso_index | ENSO/IOD classification of Jun–May years | `enso_years.csv` |
| 02_masks_regions | ETOPO 2022 (60″) → shelf/slope masks and regions on the OISST grid | `masks.nc` |
| 03_climatology_anomalies | `mhw3d.legacy` seas/thresh (1982–2011), T_anom, severity | `clim_thresh_*.nc`, `anom_severity_daily_*.zarr` |
| 04_mhw_detection | Events, daily MHW mask, monthly MHW metrics | `mhw_events_*.nc`, `mhw_monthly_*.nc` |
| 05_composites_sst | SST composites, maps and regional lag curves | figures + `composites_sst_*.nc` |
| 06_composites_mhw | MHW-metric composites | figures + `composites_*_maps.nc` |

Before running 02, download the ETOPO 2022 60″ subset to `BATHY_FILE` (see the wget command at the top of notebook 02).

Files on `/scratch` are purged when unused, so copy the final outputs to `/g/data` once you're done.
