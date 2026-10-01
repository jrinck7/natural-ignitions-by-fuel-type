# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: gds
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Project 2: Launch

# %% [markdown]
# ## Research Question: 
# Between 2018 and 2020, does the rate at which lightning strikes convert into wildfire ignitions vary by fuel type across the ecoregions of the contiguous United States, independent of raw lightning exposure?
#
# ##### Revised Research Question:
# Between 1992 and 2024, how are naturally occuring wildfires distributed across ecoregions and what fuel-types during this time period account for the most natural ignitions? 

# %% [markdown]
# # Data:
#
# 1. [Spatial wildfire occurrence data for the United States, 1992-2020 (7th Edition)(USFS)](https://www.fs.usda.gov/rds/archive/catalog/RDS-2013-0009.7)
#    - Federal, State and Local fire data aggreagated
#    - Discovery date, final fire size, point location (1 sq mile accuracy), wildfire-cause
#    - 2.3 million geo-referenced wildfire records
# 2. [Combined Geostationary Lightning Mapper (GLM) Hourly Thunder Hour Data Product (NASA)](https://search.earthdata.nasa.gov/search/granules/collection-details?p=C3894650367-GHRC_DAAC&pg[0][v]=f&pg[0][gsk]=-start_date&q=Lightning%20Mapper&lat=40.780546668112606&long=-83.81276234265948&zoom=3.990854889796647)
#    - 2019 - 2025
#    - Two sattelites GOES-18 (west) and GOES-19 (east)
#    - Thunder hour: an hour with detected lightning at a location - a frequency-based storm-activity metric, less biased by a sensor's geographic detection-sensitivity variation than raw flash counts
#    - Resolution: 5 km 
# 3. [LANDFIRE's 40 Scott and Burgan Fire Behavior Fuel Model (FBFM40), CONUS raster (USFS & USGS](https://www.sciencebase.gov/catalog/item/6a1602c7b66b013d45990b82)
#    - 40 fuel models classifying surface fuel loading by type (grass, brush, timber, slash), size class, bed depth, and moisture of extinction
#    - Fuel assignments aren't static - herbaceous fuels shift between live and dead through the growing season, and burned or otherwise disturbed areas are updated to reflect estimated recovery through 2022
# 4. [Level III Ecoregions of the Conterminous United States (EPA)](https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states)
#     - Ecoregions mark areas of broadly similar ecosystems - a spatial framework for managing and comparing environmental resources across agencies
#     - Delineated from patterns across multiple factors (geology, vegetation, climate, soils, land use, wildlife, hydrology), weighted differently region to region
#     - Four Levels: Level I (15 regions, North America) → Level II (50) → Level III (85 in the conterminous US) → Level IV (further subdivisions)
# 5. [Backup Wildfire Data: Interagency Fire Occurrence Reporting Modules (InFORM](https://in-form-nifc.hub.arcgis.com/pages/in-form-faqs)
#     - Ongling incorporation of historic data across other agencies is still in progress
#     - Data still needs to be backfilled

# %% [markdown]
# ## Data Processing:
# 1. CRS
#    - Albers Equal Area Conic
#         - Preserves area calculation accuracy
#         - Minimal distortion for CONUS
# 2.  Zonal Statistics at CONUS Scale for LANDFIRE Raster
#     - Windowed (chunked) reads for the raster data set to avoid memory issues in Docker
# 3. Lightning Data Cropping to CONUS
# 5. LANDFIRE Attribute Table
#     - Translate values to fuel model classes
# 6. Categorize Fuel Types
#    - Single majority class per eco region?
#    - Proportions of fuel class per eco region?
#    - Lightning strikes per fuel class

# %% [markdown]
# ## Analysis Methods:
#
# ### Spatial joins and overlays
#
# - Fire points joined to ecoregion polygons (point-in-polygon)
# - Fire points sampled against the fuel raster (tagging each ignition with its fuel class)
# - Lightning grid cells overlaid on the fuel raster to assign each cell a majority fuel class
# - Statistics of the fuel raster within ecoregion polygons (raster clipped by polygon)
#
# ### Attribute filtering and aggregation
#
# - Filtering fire records to NWCG_CAUSE == "Natural" and to the date range February 2019–December 2020
# - Lightning will use the combined Monthly Thunder Hour product for 2019 and 2020 to summ across CONUS to get a per grid cell count 
#     - Monthly Thunder Hour: did lightning happen in this cell during this hour, yes or no?
# - Aggregating fuel pixel counts within each ecoregion into classes
#
# ### Choropleth mapping and advanced visualization
#
# - Fuel map colored by their ignition-to-thunder-hour ratio
# - Ecoregions colored by their ignition-to-thunder-hour ratio
# - Create a map that displays the areas with the most lightning cause wildfire ignitions 

# %%
# import libraries

import os
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from IPython.display import display
from rasterio.transform import from_origin
from rasterio.warp import reproject
from rasterio.enums import Resampling
from libpysal import weights
import matplotlib.pyplot as plt


from pathlib import Path
DATA_DIR = Path("../data")


# %% [markdown]
# ## Reprojections for Analysis and Geographic Alignment 
#
# ##### Projection: EPSG:5070 — NAD83 / Conus Albers Equal Area Conic
# - Albers is an equal-area projection that preserves area accuarcy for CONUS
# - Minimal distortion for CONUS
# - Well-suited for regional comparisons
#

# %%
# Fire occurrence (7th edition, reprojected to Albers)
# Cache paths so we don't have to recompute everytime we open a the notebook
fire_cache_path = DATA_DIR / "processed/fire_occurrence_7th_albers.gpkg"

if fire_cache_path.exists():
    # Only load the columns the analysis uses (all 38 columns take ~4 GB of memory)
    fire = gpd.read_file(fire_cache_path, engine="pyogrio", columns=[
        "FIRE_YEAR", "DISCOVERY_DATE", "NWCG_CAUSE_CLASSIFICATION",
        "NWCG_GENERAL_CAUSE", "FIRE_SIZE", "STATE"])
else:
    fire = gpd.read_file(DATA_DIR / "FPA_FOD/FPA_FOD_20260615.gpkg")
    fire = fire.to_crs("EPSG:5070")
    fire.to_file(fire_cache_path, driver="GPKG")

# Smaller dtypes: repeated strings become categories, numbers get narrower types
fire = fire.astype({"NWCG_CAUSE_CLASSIFICATION": "category",
                    "NWCG_GENERAL_CAUSE": "category", "STATE": "category",
                    "FIRE_YEAR": "int16", "FIRE_SIZE": "float32"})

# Fuel type raster (already in EPSG:5070 — no reprojection needed)
fuelClass = rasterio.open(DATA_DIR / "LF2020_FBFM40_CONUS/Tif/LF2020_FBFM40_CONUS.tif")

# Ecoregions (reprojected + dissolved to one polygon per ecoregion)
# Dissolve ecoregions because the downloaded shapefiles split ecoregion polygons at state-lines
ecoregion_cache_path = DATA_DIR / "processed/ecoregions_l3_albers_nb.gpkg"

if ecoregion_cache_path.exists():
    ecoregion = gpd.read_file(ecoregion_cache_path)
else:
    ecoregion = gpd.read_file(DATA_DIR / "ecoregions/us_eco_l3_state_boundaries.shp")
    ecoregion = ecoregion.to_crs("EPSG:5070")
    # Dissolve on the ecoregion identifier
    ecoregion = ecoregion.dissolve(by="US_L3CODE", as_index=False)
    ecoregion.to_file(ecoregion_cache_path, driver="GPKG")

# %%
# Look at the datasets to identify what needs to be cleaned
print("Fire Occurrence")
pd.set_option('display.max_columns', None)
display(fire.head(10))

print("Ecoregions")
display(ecoregion.head(10))

print("Fuel Model Classes (LANDFIRE attribute table)")
fuel_lookup = pd.read_csv(DATA_DIR / "LF2020_FBFM40_CONUS/CSV_Data/LF2020_FBFM40.csv")
display(fuel_lookup.head(10))

# %%
# Check each dataset for empty/NaN values
print(fire.isnull().sum())
print(ecoregion.isnull().sum())
print(fuel_lookup.isnull().sum())

# %%
# Simplify the Fire Occurance Dataset to suit the needs of the analysis
# Cleaned data is free of empty/NaN values
fire_clean = fire  # already limited to these columns at load

# Look at new dataframe
display(fire_clean.head(10))


# %%
fire_fuel_cache_path = DATA_DIR / "processed/natural_fire_fuel_ecoregion.gpkg"

if fire_fuel_cache_path.exists():
    # Only the ecoregion and fuel columns are used below, so skip the rest and the geometry
    fire_fuel = gpd.read_file(fire_fuel_cache_path, engine="pyogrio", ignore_geometry=True,
        columns=["US_L3NAME", "US_L3CODE", "FUEL_CLASS"]).astype({"FUEL_CLASS": "int16"})
# Only look at naturally caused fires
else:
    natural_fire = fire[fire["NWCG_CAUSE_CLASSIFICATION"] == "Natural"].copy()

    # Build a list of x,y pairs of point geom for natural fires
    coords = [(geom.x, geom.y) for geom in natural_fire.geometry]
    # Look up the rasters pixel by coords (val[0] removes the raterio wrapper and returns an int to the new col FUEL_CLASS to natural_fire
    natural_fire["FUEL_CLASS"] = [val[0] for val in fuelClass.sample(coords)]

    # Spatial join tags each fire WITHIN its containing ecoregion
    # geopandas spatial join matches rows based on geom
    fire_fuel = gpd.sjoin(natural_fire, ecoregion, how="left", predicate="within")

    fire_fuel.to_file(fire_fuel_cache_path, driver="GPKG")
    del natural_fire, coords

# Clip fire points to the lower 48
# The fire data covers all of the US, but the ecoregions only cover the lower 48.
# The left join in the fire_fuel cell kept every fire, so fires outside the
# ecoregions have NaN in the ecoregion columns. Keeping only rows with an ecoregion name.
fire_fuel = fire_fuel[fire_fuel["US_L3NAME"].notna()].copy()

# Raw ignition counts per ecoregion / fuel type combination
counts = fire_fuel.groupby(["US_L3NAME", "FUEL_CLASS"]).size().reset_index(name="ignition_count")
print(counts)

# Free the full fire table now that fire_fuel is built
import gc
del fire, fire_clean
gc.collect()

# %%
# ---- Majority fuel class per grid cell ----
# Builds a coarse grid over CONUS where each cell stores the most common fuel class
# found inside it, so density values can later be grouped by fuel class.

cell_size = 10_000  # grid cell width/height in meters (EPSG:5070 units) - I don't know if this is the right size...we could definitely adjust this

# Grid extent = bounding box of the ecoregions (i.e., CONUS)
xmin, ymin, xmax, ymax = ecoregion.total_bounds

# Columns/rows needed to cover that box; ceil so the far edges aren't cut off
ncols = int(np.ceil((xmax - xmin) / cell_size))
nrows = int(np.ceil((ymax - ymin) / cell_size))

# Affine transform: ties grid row/column positions to real-world coordinates.
grid_transform = from_origin(xmin, ymax, cell_size, cell_size)

# Cell size is in the filename, so changing it never reuses a stale cached array
fuel_mode_cache_path = DATA_DIR / f"processed/fuel_mode_{cell_size // 1000}km.npy"

if fuel_mode_cache_path.exists():
    fuel_mode = np.load(fuel_mode_cache_path)  # reuse the saved array
else:
    # Empty grid to fill, pre-set to the nodata value
    fuel_mode = np.full((nrows, ncols), -9999, dtype="int16")

    # Resample the 30 m fuel raster onto the coarse grid.
    # Resampling.mode: each cell gets the most common fuel code among the pixels inside it
    reproject(
        source=rasterio.band(fuelClass, 1),  # band 1 = fuel model codes
        destination=fuel_mode,               # array the results are written into
        dst_transform=grid_transform,        # where the grid sits in the world
        dst_crs="EPSG:5070",                 # same CRS as the source: regridding only, no reprojection
        src_nodata=-9999,                    # ignore nodata pixels in the source
        dst_nodata=-9999,                    # cells with no valid pixels stay -9999
        resampling=Resampling.mode,
    )
    np.save(fuel_mode_cache_path, fuel_mode)  # slow step runs once, then it's cached

# %% [markdown]
# ## Where we are at:
#
# #### Spatial Joins and Overlays
# - fire points joined to ecoregion polygons, fuel raster sampled at each fire, fuel raster resampled onto the 10 km grid
# - To Do: overlay the density grid on the fuel grid, then draw ecoregion boundaries over the surface
#
# #### Attribute filtering and aggregation
# - filtered to natural fires, dissolved ecoregions by code, ignition counts per ecoregion and fuel class, majority fuel class per grid cell
# - To Do: mean density per fuel class. Normalizing counts by how much of each fuel exists?
#
# #### Choropleth and advanced visualization
# - To Do: choropleth of ignition counts (or the normalized rate) per ecoregion
# - To Do: density surface with ecoregion outlines on top
# - To Do (optional): one density map per fuel class
#
# Additionally: How do we want to use patial weights (queen contiguity weights)?
# I was thinking we could compare compare fire occurrence across ecoregions, then use spatial weights (and maybe Moran's I) to find clusters of neighboring ecoregions with similarly high or low ignition rates. Thoughts? (see below).

# %%
# Neighbors = ecoregions 
w = weights.Queen.from_dataframe(ecoregion)
w.transform = "R"   # Row-standardizing divides each weight by that row's total, so every row sums to 1

print("Ecoregions:", w.n)
print("Neighbors per ecoregion (min / mean / max):",
      w.min_neighbors, round(w.mean_neighbors, 1), w.max_neighbors)
print("Islands (no neighbors):", w.islands)

# %%
# Natural ignitions per ecoregion
ignitions = fire_fuel.groupby("US_L3CODE").size()
# Create a new col of ignitions per ecoregion
ecoregion["ignitions"] = ecoregion["US_L3CODE"].map(ignitions).fillna(0)

# .area is in meters squared - divide by 1e9 to get per 1,000 km squared
# Create a new col that contains the normalized ignition data 
ecoregion["ign_per_1000km2"] = ecoregion["ignitions"] / (ecoregion.area / 1e9)

# Plot the data
fig, ax = plt.subplots(figsize=(12, 8))
ecoregion.plot(column="ign_per_1000km2", cmap="YlOrRd", scheme="quantiles", k=7,
               edgecolor="0.4", linewidth=0.3, legend=True,
               legend_kwds={"title": "Natural ignitions per 1,000 km²", "loc": "lower left"},
               ax=ax)
ax.set_title("Natural wildfire ignitions per 1,000 km² by ecoregion, 1992–2024")
ax.set_axis_off()
plt.show()

# %% [markdown]
# ![](../images/Project2_OverviewofData_FirebyFuelClass.png)

# %% [markdown]
# ![](../images/Project2_OverviewofData_Legend.png)

# %%
# ============================================================
# LIGHTNING DATA — on hold and ready to uncomment when revisited
# ============================================================

# --- Acquisition (already run once; files already exist locally) ---
# # %pip install earthaccess
# import earthaccess

# earthaccess.login(strategy="interactive", persist=True)

# results = earthaccess.search_data(
#     short_name="glmmth",
#     temporal=("2019-01-01", "2024-12-31"),
# )
# files = earthaccess.download(results, "work/Project2/data")

# --- Processing: crop each file to CONUS, sum 12 months, sum both years ---
# import glob
# import xarray as xr

# files = sorted(glob.glob(str(DATA_DIR / "glmmth/GLMc_th_*.nc")))

# def load_and_crop(path):
#     ds = xr.open_dataset(path)
#     ds = ds.assign_coords(lat=("nlat", ds.lat.values), lon=("nlon", ds.lon.values))
#     ds = ds.swap_dims({"nlat": "lat", "nlon": "lon"})
#     lat_vals = ds.lat.values
#     lat_slice = slice(24, 50) if lat_vals[0] < lat_vals[-1] else slice(50, 24)
#     return ds.sel(lat=lat_slice, lon=slice(-125, -66))

# datasets = [load_and_crop(f) for f in files]
# lightning = sum(ds.thunder_hours.sum(dim="nmon") for ds in datasets)
