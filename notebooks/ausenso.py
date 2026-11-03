"""
ausenso.py — shared configuration and helpers for the AusCoast_ENSO notebooks.

Edit the CONFIG block below; every notebook imports from here so the choices
(baseline, end date, thresholds, regions) live in one place.
Paths can be overridden with environment variables (used for testing).
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

# =============================================================================
# CONFIG
# =============================================================================
USER = os.environ.get("USER", "nm5072")

# --- input ---
OISST_DIR = Path(os.environ.get(
    "AUSENSO_OISST_DIR", "/g/data/ia39/aus-ref-clim-data-nci/oisst/data/yearly"))
OISST_PATTERN = "oisst-avhrr-v02r01_{year}.nc"
BATHY_FILE = Path(os.environ.get(
    "AUSENSO_BATHY", f"/scratch/m35/{USER}/AusCoast_ENSO/bathy/etopo2022_60s_aus.nc"))
BATHY_VAR = os.environ.get("AUSENSO_BATHY_VAR", "z")   # ETOPO 2022 ERDDAP: z (m, +ve up); GEBCO: elevation

# --- output ---
OUT = Path(os.environ.get("AUSENSO_OUT", f"/scratch/m35/{USER}/AusCoast_ENSO"))
# figures go in the repo (tracked by git) rather than on /scratch
FIG = Path(os.environ.get("AUSENSO_FIG", Path(__file__).resolve().parent.parent / "figures"))

# --- time ---
YEAR_START, YEAR_END = 1982, 2024   # data read (1981 is a partial year; ia39 ends ~Dec 2024)
BASELINE = (1982, 2011)             # climatologyPeriod for mhw3d.legacy (fixed baseline)
ENSO_YEARS = (1982, 2023)           # Jun(Y)–May(Y+1); last = Jun 2023–May 2024

# --- domain (OISST lon is 0–360) ---
DOMAIN = dict(lat=(-48.0, -5.0), lon=(105.0, 165.0))

# --- climate-index boxes (area-weighted SST means) ---
INDEX_BOXES = {
    "nino34": dict(lat=(-5.0, 5.0),   lon=(190.0, 240.0)),   # 170W–120W
    "dmi_w":  dict(lat=(-10.0, 10.0), lon=(50.0, 70.0)),
    "dmi_e":  dict(lat=(-10.0, 0.0),  lon=(90.0, 110.0)),
    "trop":   dict(lat=(-20.0, 20.0), lon=(0.0, 360.0)),     # tropical-mean SST for the relative index
}

# --- ENSO / IOD classification ---
# BoM relative Niño3.4 (BoM "About climate indices", adopted Sep 2025):
#   RN34 = S * [(N34 - N34clim) - (TropMean - TropMeanclim)],  TropMean = 20S–20N mean SST,
#   anomalies vs 1991–2020, S scales RN34 to the variance of the traditional index,
#   El Niño / La Niña typical when sustained monthly values > +0.8 / < -0.8 °C.
# Here computed from OISST (BoM does not name its SST dataset on that page).
INDEX_BASELINE = (1991, 2020)   # BoM climatology for the indices (separate from the MHW BASELINE)
SCALE_PERIOD = (1991, 2020)     # period over which S matches variances (BoM does not state one)
ENSO_SMOOTH = 1          # months of running mean before thresholding (1 = monthly values, as BoM)
ENSO_THRESH = 0.8        # |RN34| threshold (°C), BoM
ENSO_MIN_MONTHS = 5      # consecutive months beyond threshold = "sustained" (BoM gives no number — our choice)
STRONG_THRESH = 1.5      # event peak RN34 for a "strong" El Niño (°C) — our choice, BoM defines none
INDEX_DETREND = False    # linear detrend of DMI anomalies (RN34 is never detrended; the tropical-mean
                         # subtraction already removes the warming trend)
IOD_THRESH = 0.4         # SON-mean DMI threshold (°C) for flagging +/-IOD years — set to your preferred definition

# --- shelf mask ---
SHELF_DEPTH = 200.0      # m
SHELF_FRAC = 0.5         # OISST cell is "shelf" if >= this fraction of its area is 0–SHELF_DEPTH m
SLOPE_DEPTH = 2000.0     # offshore contrast band: mean depth SHELF_DEPTH–SLOPE_DEPTH and not shelf

# Regional boxes, intersected with the shelf mask. First match wins (dict order).
REGIONS = {
    "NW Shelf":      dict(lat=(-23.0, -12.0), lon=(113.0, 129.0)),
    "North":         dict(lat=(-17.0, -8.0),  lon=(129.0, 142.0)),   # Arafura / Gulf of Carpentaria
    "GBR":           dict(lat=(-25.0, -9.0),  lon=(142.0, 155.0)),
    "SEQ-NSW":       dict(lat=(-37.5, -25.0), lon=(149.0, 156.0)),
    "Bass-Tasmania": dict(lat=(-44.5, -37.5), lon=(140.0, 151.0)),
    "SA-GAB":        dict(lat=(-40.0, -31.0), lon=(125.0, 140.0)),
    "SW WA":         dict(lat=(-36.0, -23.0), lon=(110.0, 125.0)),
}

# --- MHW detection ---
MAX_EVT = 400            # event slots per cell (mhw3d default 200); checked for saturation in 04

# --- composites ---
COMPOSITE_DETREND = True  # remove linear trend across ENSO years from each per-year field before
                          # compositing (strong El Niños cluster early in the record)
N_BOOT = 2000
ALPHA_FDR = 0.10          # Wilks (2016): alpha_FDR = 2 x alpha_global for alpha_global = 0.05
SEED = 42

# --- dask chunking for the domain arrays ---
CHUNKS_SPACE = {"lat": 43, "lon": 60}
CHUNKS_CLIM = {"lat": 22, "lon": 20}   # smaller for legacy.compute_threshold (pools ~330 samples/DOY)

# Seasons within an ENSO year (Jun(0)..May(+1)); values are emonth indices 0..11
SEASONS = {"JJA(0)": [0, 1, 2], "SON(0)": [3, 4, 5], "DJF": [6, 7, 8], "MAM(+1)": [9, 10, 11]}
EMONTH_LABELS = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"]

# --- output file names ---
F_SST = OUT / "oisst_aus_daily.zarr"
F_INDICES_DAILY = OUT / "index_boxes_daily.nc"
F_ENSO_TABLE = OUT / "enso_years.csv"
F_INDICES_MONTHLY = OUT / "indices_monthly.nc"
F_MASKS = OUT / "masks.nc"
F_CLIM = OUT / f"clim_thresh_{BASELINE[0]}-{BASELINE[1]}.nc"
F_SEV = OUT / f"anom_severity_daily_{BASELINE[0]}-{BASELINE[1]}.zarr"
F_SST_MONTHLY = OUT / f"sst_anom_monthly_{BASELINE[0]}-{BASELINE[1]}.nc"
F_EVENTS = OUT / f"mhw_events_{BASELINE[0]}-{BASELINE[1]}.nc"
F_MHW_DAILY = OUT / f"mhw_daily_{BASELINE[0]}-{BASELINE[1]}.zarr"
F_MHW_MONTHLY = OUT / f"mhw_monthly_{BASELINE[0]}-{BASELINE[1]}.nc"


# =============================================================================
# I/O helpers
# =============================================================================
def oisst_files(years=None):
    years = range(YEAR_START, YEAR_END + 1) if years is None else years
    files = [OISST_DIR / OISST_PATTERN.format(year=y) for y in years]
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        raise FileNotFoundError(f"Missing OISST files: {missing}")
    return files


def preprocess_oisst(ds):
    """Keep sst, drop zlev, normalise time to 00:00 (files are stamped at 12:00)."""
    ds = ds[["sst"]]
    if "zlev" in ds.dims:
        ds = ds.squeeze("zlev", drop=True)
    return ds.assign_coords(time=ds.time.dt.floor("D"))


def sel_box(da, box):
    return da.sel(lat=slice(*box["lat"]), lon=slice(*box["lon"]))


def area_weights(lat):
    return np.cos(np.deg2rad(lat))


def box_mean(da, box=None, mask=None):
    """Area-weighted (cos lat) mean over a lat/lon box and/or boolean mask."""
    if box is not None:
        da = sel_box(da, box)
    if mask is not None:
        da = da.where(mask)
    return da.weighted(area_weights(da.lat).fillna(0)).mean(("lat", "lon"))


def ensure_dirs():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)


def start_client(memory_fraction=0.9):
    """LocalCluster sized to the ARE allocation (process-based; mhw3d's apply_ufunc
    with vectorize=True is GIL-bound, so threads_per_worker=1)."""
    from dask.distributed import Client, LocalCluster
    try:
        ncpu = len(os.sched_getaffinity(0))
    except AttributeError:
        ncpu = os.cpu_count()
    mem = os.environ.get("PBS_VMEM") or os.environ.get("PBS_MEM")
    kw = {}
    if mem:
        kw["memory_limit"] = f"{int(int(mem) * memory_fraction / ncpu)}B"
    cluster = LocalCluster(n_workers=ncpu, threads_per_worker=1, **kw)
    return Client(cluster)


# =============================================================================
# ENSO-year bookkeeping
# =============================================================================
def add_enso_coords(da):
    """Add enso_year (Jun–May year labelled by its June) and emonth (0=Jun..11=May)."""
    m = da.time.dt.month
    y = da.time.dt.year
    return da.assign_coords(enso_year=("time", xr.where(m >= 6, y, y - 1).data),
                            emonth=("time", ((m - 6) % 12).data))


def to_enso_year_month(monthly):
    """Monthly (time, ...) -> (enso_year, emonth, ...) restricted to ENSO_YEARS."""
    da = add_enso_coords(monthly)
    da = da.set_index(time=["enso_year", "emonth"]).unstack("time")
    return da.sel(enso_year=slice(*ENSO_YEARS))


def to_seasons(ym, how="mean"):
    """(enso_year, emonth, ...) -> (enso_year, season, ...)."""
    out = []
    for name, idx in SEASONS.items():
        sub = ym.isel(emonth=idx)
        out.append(getattr(sub, how)("emonth", skipna=False).expand_dims(season=[name]))
    return xr.concat(out, "season").transpose("enso_year", "season", ...)


def load_enso_table():
    return pd.read_csv(F_ENSO_TABLE, index_col="enso_year")


def phase_years(table):
    """Dict of composite name -> list of ENSO years."""
    return {
        "El Niño": table.index[table.phase == "EN"].tolist(),
        "Strong El Niño": table.index[table.strong_EN].tolist(),
        "Moderate El Niño": table.index[(table.phase == "EN") & ~table.strong_EN].tolist(),
        "La Niña": table.index[table.phase == "LN"].tolist(),
        "Neutral": table.index[table.phase == "N"].tolist(),
    }


# =============================================================================
# Compositing and significance
# =============================================================================
def detrend_years(per_year):
    """Remove a linear trend along enso_year, keeping the all-year mean."""
    fit = per_year.polyfit("enso_year", deg=1, skipna=True)
    trend = xr.polyval(per_year.enso_year, fit.polyfit_coefficients)
    return per_year - trend + trend.mean("enso_year")


def composite_bootstrap(per_year, years, n_boot=N_BOOT, seed=SEED, detrend=COMPOSITE_DETREND):
    """
    Composite anomaly (mean over `years` minus mean over all years) and a two-sided
    p-value from a resampling null: n_boot random draws (without replacement) of
    len(years) ENSO years from the full set.

    per_year : DataArray with an 'enso_year' dim (any other dims), loaded in memory.
    Returns Dataset(comp, pval, null_lo, null_hi) — null_lo/hi = 2.5/97.5 % of the null.
    """
    py = detrend_years(per_year) if detrend else per_year
    py = py.load()
    clim = py.mean("enso_year")
    anom = (py - clim).transpose("enso_year", ...)
    arr = anom.values
    sel = np.isin(anom.enso_year.values, years)
    n = int(sel.sum())
    comp = np.nanmean(arr[sel], axis=0)

    rng = np.random.default_rng(seed)
    ny = arr.shape[0]
    exceed = np.zeros_like(comp)
    null = np.empty((n_boot,) + comp.shape, dtype=np.float32) if comp.size * n_boot < 2e8 else None
    for b in range(n_boot):
        idx = rng.choice(ny, size=n, replace=False)
        c = np.nanmean(arr[idx], axis=0)
        exceed += np.abs(c) >= np.abs(comp)
        if null is not None:
            null[b] = c
    pval = (exceed + 1) / (n_boot + 1)

    dims, coords = anom.dims[1:], {k: v for k, v in anom.coords.items() if "enso_year" not in v.dims}
    ds = xr.Dataset({"comp": (dims, comp), "pval": (dims, pval)}, coords=coords)
    if null is not None:
        ds["null_lo"] = (dims, np.nanpercentile(null, 2.5, axis=0))
        ds["null_hi"] = (dims, np.nanpercentile(null, 97.5, axis=0))
    ds.attrs.update(n_years=n, years=str(list(years)), n_boot=n_boot, detrended=int(detrend))
    return ds


def fdr_mask(pval, alpha=ALPHA_FDR):
    """Benjamini–Hochberg FDR (Wilks 2016). True where locally significant after control.
    Applied over all non-NaN points of `pval` jointly (call per map)."""
    p = np.asarray(pval)
    flat = p[np.isfinite(p)]
    if flat.size == 0:
        return xr.zeros_like(pval, dtype=bool)
    ps = np.sort(flat)
    k = np.arange(1, ps.size + 1)
    ok = ps <= alpha * k / ps.size
    p_crit = ps[ok].max() if ok.any() else 0.0
    return pval <= p_crit


# =============================================================================
# Plotting
# =============================================================================
def map_axes(nrows, ncols, figsize=None, ocean=None, coast=False):
    """Map grid over DOMAIN. Land is shaded from the OISST `ocean` mask if given (works offline);
    coast=True adds cartopy coastlines (needs Natural Earth data available locally)."""
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    figsize = figsize or (3.6 * ncols, 3.0 * nrows)
    fig, axs = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False,
                            subplot_kw=dict(projection=ccrs.PlateCarree()),
                            constrained_layout=True)
    for ax in axs.flat:
        ax.set_extent([DOMAIN["lon"][0], DOMAIN["lon"][1], DOMAIN["lat"][0], DOMAIN["lat"][1]],
                      crs=ccrs.PlateCarree())
        if ocean is not None:
            ax.contourf(ocean.lon, ocean.lat, (~ocean.astype(bool)).astype(float), levels=[0.5, 1.5],
                        colors="0.75", transform=ccrs.PlateCarree(), zorder=0.5)
        if coast:
            ax.coastlines(resolution="50m", lw=0.5)
    return fig, axs


def plot_composite_maps(results, label, vmax, cmap="RdBu_r", masks=None, every=2, title=""):
    """results: {composite name: Dataset(comp, pval) with dims (season, lat, lon)}.
    Rows = composites, cols = seasons; stippling = FDR-significant; grey contour = shelf edge."""
    import cartopy.crs as ccrs
    names = list(results)
    seasons = list(results[names[0]].season.values)
    fig, axs = map_axes(len(names), len(seasons), ocean=None if masks is None else masks.ocean)
    for i, nm in enumerate(names):
        r = results[nm]
        for j, s in enumerate(seasons):
            ax = axs[i, j]
            c = r.comp.sel(season=s)
            if masks is not None:
                c = c.where(masks.ocean)
            pm = ax.pcolormesh(c.lon, c.lat, c, vmin=-vmax, vmax=vmax, cmap=cmap,
                               transform=ccrs.PlateCarree(), shading="auto")
            stipple(ax, fdr_mask(r.pval.sel(season=s)) & c.notnull(), every=every)
            if masks is not None:
                ax.contour(masks.lon, masks.lat, masks.shelf.astype(float), levels=[0.5],
                           colors="0.3", linewidths=0.5, transform=ccrs.PlateCarree())
            ax.set_title(f"{nm} (n={r.attrs['n_years']}) {s}" if j == 0 else s, fontsize=8)
    fig.colorbar(pm, ax=axs, shrink=0.6, label=label)
    if title:
        fig.suptitle(title)
    return fig


def plot_regional_lags(results, label, region_names, individual=None):
    """results: {composite name: Dataset(comp, null_lo, null_hi) dims (region, emonth)}.
    individual: optional DataArray (region, enso_year, emonth) of anomalies to overlay per-year lines
    for the years in individual.attrs['years']."""
    import matplotlib.pyplot as plt
    nreg = len(region_names)
    ncol = 4
    nrow = int(np.ceil(nreg / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(3.4 * ncol, 2.6 * nrow), sharex=True,
                            squeeze=False, constrained_layout=True)
    x = np.arange(12)
    colors = {"El Niño": "C3", "Strong El Niño": "darkred", "Moderate El Niño": "salmon",
              "La Niña": "C0", "Neutral": "0.5"}
    for k, reg in enumerate(region_names):
        ax = axs.flat[k]
        if individual is not None:
            for y in individual.attrs.get("years", []):
                ax.plot(x, individual.sel(enso_year=y).isel(region=k), color="darkred", lw=0.6,
                        ls="--", alpha=0.6)
        for nm, r in results.items():
            c = r.comp.isel(region=k)
            ax.plot(x, c, color=colors.get(nm), lw=1.6,
                    label=f"{nm} (n={r.attrs['n_years']})" if k == 0 else None)
            sig = (r.pval.isel(region=k) < 0.05).values
            ax.plot(x[sig], c.values[sig], "o", ms=3.5, color=colors.get(nm))
        ax.axhline(0, color="k", lw=0.5)
        ax.set_title(reg, fontsize=9)
        ax.set_xticks(x[::2], EMONTH_LABELS[::2])
    for ax in axs.flat[nreg:]:
        ax.axis("off")
    axs.flat[0].set_ylabel(label)
    fig.legend(loc="lower right", fontsize=8)
    return fig


def regional_means(da, masks):
    """Area-weighted means over each shelf region -> new 'region' dim."""
    names = masks.attrs["region_names"].split(";")
    out = [box_mean(da, mask=(masks.region == i)) for i in range(len(names))]
    return xr.concat(out, "region").assign_coords(region=names)


def stipple(ax, sig, every=2, **kw):
    """Dot significant cells (subsampled every `every` cells for legibility)."""
    import cartopy.crs as ccrs
    s = sig.isel(lat=slice(None, None, every), lon=slice(None, None, every))
    yy, xx = np.meshgrid(s.lat, s.lon, indexing="ij")
    m = s.values.astype(bool)
    ax.scatter(xx[m], yy[m], s=kw.pop("s", 0.4), c=kw.pop("c", "k"),
               transform=ccrs.PlateCarree(), **kw)
