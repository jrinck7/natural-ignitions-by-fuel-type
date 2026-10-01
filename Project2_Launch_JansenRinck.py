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

# %% [markdown]
# # Data:
#
# 1. [Spatial wildfire occurrence data for the United States, 1992-2020 (6th Edition)(USFS)](https://www.fs.usda.gov/rds/archive/catalog/RDS-2013-0009.6)
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

# %% [markdown]
# ![](images/Project2_OverviewofData.png)

# %%
# # %pip install earthaccess
# import earthaccess
#import glob

#files = sorted(glob.glob("data/glmmth/GLMc_th_*.nc"))
# earthaccess.login(strategy="interactive", persist=True)

# results = earthaccess.search_data(
#     short_name="glmmth",   
#     temporal=("2019-01-01", "2020-12-31"),
# )
# files = earthaccess.download(results, "work/Project2/data")

# %%
# For each file, promotes lat/lon to real coordinates and crops to CONUS, then sums each year's 12 monthly slices and adds both years together into 
# one cumulative thunder-hours grid

# Gridded because "thunder hour" is a binning concept by definition, and because it merges detections from instruments with different viewing geometries 
# (both satellites, and more broadly ground networks) onto one common reference frame

# lat is 520 values, lon is 1180 values, and total is 1180×520 — like a spreadsheet: lat gives the row headers, lon gives the column headers, and cell 
# total[i, j] is the thunder-hour count

import glob
import xarray as xr

files = sorted(glob.glob("data/glmmth/GLMc_th_*.nc"))
assert files, "No GLM thunder-hour files found - check the data path"

def load_and_crop(path):
    ds = xr.open_dataset(path)
    # lat/lon are plain data variables here, not indexed coordinates —
    # promote them so .sel() can crop by actual lat/lon values
    ds = ds.assign_coords(lat=("nlat", ds.lat.values), lon=("nlon", ds.lon.values))
    ds = ds.swap_dims({"nlat": "lat", "nlon": "lon"})

    # handle either latitude ordering (ascending or descending)
    lat_vals = ds.lat.values
    lat_slice = slice(24, 50) if lat_vals[0] < lat_vals[-1] else slice(50, 24)

    return ds.sel(lat=lat_slice, lon=slice(-125, -66))

datasets = [load_and_crop(f) for f in files]

# If range assumptions above don't match this file and need adjusting
print("Cropped shape:", datasets[0].thunder_hours.shape)

# sum each file's 12 months, then sum both years together
total = sum(ds.thunder_hours.sum(dim="nmon") for ds in datasets)

print(total)

# %%
# counts of each fuel class per polygon
import os
import geopandas as gpd
import pandas as pd

cache_path = "data/processed/fire_natural_2019_2020.gpkg"

if os.path.exists(cache_path):
    fire = gpd.read_file(cache_path)
else:
    fire = gpd.read_file("data/processed/fire_occurrence_7th_albers.gpkg")

    fire["DISCOVERY_DATE"] = pd.to_datetime(fire["DISCOVERY_DATE"])
    fire = fire[
        (fire["NWCG_CAUSE_CLASSIFICATION"] == "Natural")
        & (fire["DISCOVERY_DATE"] >= "2019-02-12")
        & (fire["DISCOVERY_DATE"] <= "2020-12-31")
    ]

    fire.to_file(cache_path, driver="GPKG")

# %%
print(fire.head())
