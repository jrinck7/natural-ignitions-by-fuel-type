# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: gds
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Project 2: Natural Wildfire Ignition Frequency by Fuel Type Across CONUS Ecoregions, 1992–2024
#
# **Names:** Jansen Rinck, Benjamin Barlog, Jianru Shen 
#
# **Class:** CSCI 502: Geospatial Data Science  
#
# **Date:** 10/12/2026

# %% [markdown]
# ## Introduction
#
# Natural wildfire ignitions are not evenly distributed across the contiguous United States (CONUS), and the fuels present on the landscape are one factor shaping where they occur. By comparing ignition rates across fuel types and ecoregions, this analysis examines how fuels and fire interact, and how those interactions vary from region to region. The results can help fire and forest managers understand the spatial patterns of natural ignitions. This is increasingly important as ecosystems, especially post-fire landscapes with limited forest regeneration, shift away from historical vegetation structure. Analyses like this one can help assess the fire-regime shifts that may follow.

# %% [markdown]
# ## Research Question: 
# Between 2018 and 2020, does the rate at which lightning strikes convert into wildfire ignitions vary by fuel type across the ecoregions of the contiguous United States, independent of raw lightning exposure?
#
# ##### Revised Research Question:
# Between 1992 and 2024, how are natural wildfire ignitions distributed across fuel types in CONUS, which fuel types are most susceptible to natural ignitions relative to the area they cover, and how does each ecoregion's mix of fuels explain differences in ignition density between ecoregions?

# %% [markdown]
# ##### Revised Hypothesis:
#
# Between 1992 and 2024, natural wildfire ignitions across CONUS are not distributed randomly - they are concentrated in specific fuel types. Timber-understory fuels, which combine forest litter with grass and shrubs in the understory, will be the most susceptible to natural ignitions relative to the area they cover. Differences in ignition density between ecoregions will be driven mainly by the mix of fuels each ecoregion contains.

# %% [markdown]
# ## Data:
#
# 1. [Spatial wildfire occurrence data for the United States, 1992-2024 (7th Edition)(USFS)](https://www.fs.usda.gov/rds/archive/catalog/RDS-2013-0009.7)
#    - Federal, State and Local fire data aggregated
#    - Discovery date, final fire size, point location (1 sq mile accuracy), wildfire-cause
#    - 2.3 million geo-referenced wildfire records
# 2. [LANDFIRE's 40 Scott and Burgan Fire Behavior Fuel Model (FBFM40), CONUS raster (USFS & USGS)](https://www.sciencebase.gov/catalog/item/6a1602c7b66b013d45990b82)
#    - 40 fuel models classifying surface fuel loading by type (grass, brush, timber, slash), size class, bed depth, and moisture of extinction
#    - Fuel assignments aren't static - herbaceous fuels shift between live and dead through the growing season, and burned or otherwise disturbed areas are updated to reflect estimated recovery through 2022
# 3. [Level III Ecoregions of the Conterminous United States (EPA)](https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states)
#     - Ecoregions mark areas of broadly similar ecosystems - a spatial framework for managing and comparing environmental resources across agencies
#     - Delineated from patterns across multiple factors (geology, vegetation, climate, soils, land use, wildlife, hydrology), weighted differently region to region
#     - Four Levels: Level I (15 regions, North America) → Level II (50) → Level III (85 in the conterminous US) → Level IV (further subdivisions)
#
# ## Data for Further Analysis 
# 4. [Combined Geostationary Lightning Mapper (GLM) Hourly Thunder Hour Data Product (NASA)](https://search.earthdata.nasa.gov/search/granules/collection-details?p=C3894650367-GHRC_DAAC&pg[0][v]=f&pg[0][gsk]=-start_date&q=Lightning%20Mapper&lat=40.780546668112606&long=-83.81276234265948&zoom=3.990854889796647)
#    - 2019 - 2025
#    - Two satellites GOES-18 (west) and GOES-19 (east)
#    - Thunder hour: an hour with detected lightning at a location - a frequency-based storm-activity metric, less biased by a sensor's geographic detection-sensitivity variation than raw flash counts
#    - Resolution: 5 km 

# %% [markdown]
# ## Definitions: Scott and Burgan Fuel Models (FBFM40)
#
# Scott and Burgan (2005) group their 40 fire behavior fuel models (plus 5 nonburnable models) by the fuel that primarily carries fire. Values in parentheses are the codes used in the LANDFIRE FBFM40 raster.
#
# | Group | Primary carrier of fire |
# |---|---|
# | NB – Nonburnable | No fuel load; fire will not spread |
# | GR – Grass | Grass |
# | GS – Grass-Shrub | Grass and shrubs combined |
# | SH – Shrub | Shrub twigs, foliage, and shrub litter |
# | TU – Timber-Understory | Forest litter with herbaceous or shrub fuels |
# | TL – Timber Litter | Dead and down woody fuel |
# | SB – Slash-Blowdown | Activity fuel or blowdown |
#
# **Nonburnable (NB):** There is no fuel load, so wildland fire will not spread.
#
# | Code (value) | Name | Description |
# |---|---|---|
# | NB1 (91) | Urban/Developed | Urban and suburban development that does not support wildland fire spread |
# | NB2 (92) | Snow/Ice | Land covered by permanent snow or ice |
# | NB3 (93) | Agricultural | Agricultural land maintained in a nonburnable condition (e.g., irrigated annual crops, mowed or tilled orchards) |
# | NB8 (98) | Open Water | Open bodies of water such as lakes, rivers, and oceans |
# | NB9 (99) | Bare Ground | Land without enough fuel to support fire spread (e.g., gravel pits, sparse arid desert, sand dunes, rock outcrops, beaches) |
#
# **Grass (GR):** The primary carrier of fire is grass, ranging from heavily grazed stubble or sparse natural grass to dense grass more than 6 feet tall. All GR models are dynamic: live herbaceous fuel shifts from live to dead as it dries.
#
# | Code (value) | Name | Description |
# |---|---|---|
# | GR1 (101) | Short, Sparse Dry Climate Grass | Short, sparse grass (naturally or from grazing) that may be discontinuous |
# | GR2 (102) | Low Load, Dry Climate Grass | Grass with more load than GR1; fuelbed may be more continuous |
# | GR3 (103) | Low Load, Very Coarse, Humid Climate Grass | Continuous, coarse, humid-climate grass; light load, about 2 ft deep |
# | GR4 (104) | Moderate Load, Dry Climate Grass | Continuous dry-climate grass; more load and depth than GR2, about 2 ft deep |
# | GR5 (105) | Low Load, Humid Climate Grass | Humid-climate grass; more load than GR3, 1–2 ft deep |
# | GR6 (106) | Moderate Load, Humid Climate Grass | Continuous humid-climate grass; more load than GR5 and less coarse |
# | GR7 (107) | High Load, Dry Climate Grass | Continuous dry-climate grass about 3 ft tall |
# | GR8 (108) | High Load, Very Coarse, Humid Climate Grass | Continuous, very coarse humid-climate grass; spread and flame length can be extreme when cured |
# | GR9 (109) | Very High Load, Humid Climate Grass | Dense humid-climate grass about 6 ft tall; spread and flame length can be extreme when cured |
#
# **Grass-Shrub (GS):** The primary carrier of fire is grass and shrubs combined; both determine fire behavior. All GS models are dynamic.
#
# | Code (value) | Name | Description |
# |---|---|---|
# | GS1 (121) | Low Load, Dry Climate Grass-Shrub | Shrubs about 1 ft high, low grass load; moderate spread, low flame length |
# | GS2 (122) | Moderate Load, Dry Climate Grass-Shrub | Shrubs 1–3 ft high, moderate grass load; high spread, moderate flame length |
# | GS3 (123) | Moderate Load, Humid Climate Grass-Shrub | Moderate grass/shrub load under 2 ft deep; high spread, moderate flame length |
# | GS4 (124) | High Load, Humid Climate Grass-Shrub | Heavy grass/shrub load over 2 ft deep; high spread, very high flame length |
#
# **Shrub (SH):** The primary carrier of fire is live and dead shrub twigs and foliage together with dead and down shrub litter. SH1 and SH9 are dynamic.
#
# | Code (value) | Name | Description |
# |---|---|---|
# | SH1 (141) | Low Load Dry Climate Shrub | Low shrub load about 1 ft deep, some grass; very low spread and flame length |
# | SH2 (142) | Moderate Load Dry Climate Shrub | Moderate load about 1 ft deep, no grass; low spread and flame length |
# | SH3 (143) | Moderate Load, Humid Climate Shrub | Moderate shrub load, possibly under pine overstory, 2–3 ft deep; low spread and flame length |
# | SH4 (144) | Low Load, Humid Climate Timber-Shrub | Low to moderate shrub and litter load, possibly under pine overstory, about 3 ft deep; high spread, moderate flame length |
# | SH5 (145) | High Load, Dry Climate Shrub | Heavy shrub load 4–6 ft deep; very high spread and flame length |
# | SH6 (146) | Low Load, Humid Climate Shrub | Dense shrubs, little or no herbaceous fuel, about 2 ft deep; high spread and flame length |
# | SH7 (147) | Very High Load, Dry Climate Shrub | Very heavy shrub load 4–6 ft deep; high spread, very high flame length |
# | SH8 (148) | High Load, Humid Climate Shrub | Dense shrubs, little or no herbaceous fuel, about 3 ft deep; high spread and flame length |
# | SH9 (149) | Very High Load, Humid Climate Shrub | Dense, finely branched shrubs 4–6 ft tall with much fine dead fuel; high spread, very high flame length |
#
# **Timber-Understory (TU):** The primary carrier of fire is forest litter combined with herbaceous or shrub fuels. TU1 and TU3 are dynamic.
#
# | Code (value) | Name | Description |
# |---|---|---|
# | TU1 (161) | Low Load Dry Climate Timber-Grass-Shrub | Low load of grass and/or shrub with litter; low spread and flame length |
# | TU2 (162) | Moderate Load, Humid Climate Timber-Shrub | Moderate litter load with a shrub component; moderate spread, low flame length |
# | TU3 (163) | Moderate Load, Humid Climate Timber-Grass-Shrub | Moderate forest litter with grass and shrubs; high spread, moderate flame length |
# | TU4 (164) | Dwarf Conifer With Understory | Short conifer trees with a grass or moss understory; moderate spread and flame length |
# | TU5 (165) | Very High Load, Dry Climate Timber-Shrub | Heavy forest litter with a shrub or small-tree understory; moderate spread and flame length |
#
# **Timber Litter (TL):** The primary carrier of fire is dead and down woody fuel. Live fuel, if present, has little effect on fire behavior.
#
# | Code (value) | Name | Description |
# |---|---|---|
# | TL1 (181) | Low Load Compact Conifer Litter | Compact forest litter 1–2 in deep; can represent recently burned forest; very low spread and flame length |
# | TL2 (182) | Low Load Broadleaf Litter | Low load, compact broadleaf (hardwood) litter; very low spread and flame length |
# | TL3 (183) | Moderate Load Conifer Litter | Moderate conifer litter with a light load of coarse fuels; very low spread, low flame length |
# | TL4 (184) | Small Downed Logs | Moderate fine litter and coarse fuels, including small-diameter downed logs; low spread and flame length |
# | TL5 (185) | High Load Conifer Litter | High conifer litter load with light slash or mortality fuel; low spread and flame length |
# | TL6 (186) | Moderate Load Broadleaf Litter | Moderate broadleaf litter, less compact than TL2; moderate spread, low flame length |
# | TL7 (187) | Large Downed Logs | Heavy forest litter including larger-diameter downed logs; low spread and flame length |
# | TL8 (188) | Long-Needle Litter | Moderate long-needle pine litter, possibly with some herbaceous fuel; moderate spread, low flame length |
# | TL9 (189) | Very High Load Broadleaf Litter | Very high load, fluffy broadleaf litter (or heavy needle-drape); moderate spread and flame length |
#
# **Slash-Blowdown (SB):** The primary carrier of fire is activity fuel or blowdown. Forested areas with heavy mortality may also be modeled with SB.
#
# | Code (value) | Name | Description |
# |---|---|---|
# | SB1 (201) | Low Load Activity Fuel | Light dead and down activity fuel under 1 ft deep; moderate spread, low flame length |
# | SB2 (202) | Moderate Load Activity Fuel or Low Load Blowdown | Moderate dead and down activity fuel or light blowdown, about 1 ft deep |
# | SB3 (203) | High Load Activity Fuel or Moderate Load Blowdown | Heavy dead and down activity fuel or moderate blowdown, more than 1 ft deep |
# | SB4 (204) | High Load Blowdown | Heavy, uncompacted blowdown with foliage and fine fuel still attached; very high spread and flame length |
#
# *Source: Scott, J. H., & Burgan, R. E. (2005). Standard fire behavior fuel models: A comprehensive set for use with Rothermel's surface fire spread model (Gen. Tech. Rep. RMRS-GTR-153, pp. 19–70). USDA Forest Service, Rocky Mountain Research Station.*

# %%
# Import libraries

# Standard library
import gc
from pathlib import Path

# Data handling
import numpy as np
import pandas as pd
from IPython.display import display

# Geospatial
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.windows import Window
from rasterio.windows import bounds as window_bounds
from shapely.geometry import box
from libpysal import weights

# Statistics / KDE
from scipy.ndimage import gaussian_filter
from scipy.stats import chi2
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.neighbors import KernelDensity

# Plotting
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LogNorm, Normalize, to_hex, to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon, Rectangle

# Interactive plotting (Bokeh: interactions run in the browser, so they also work in a saved HTML file)
from bokeh.io import output_notebook, save, show
from bokeh.layouts import column, row
from bokeh.models import (ColorBar, ColumnDataSource, CustomJS, Div, FactorRange, HoverTool,
                          LinearColorMapper, LogColorMapper, NumeralTickFormatter, Select, Slider)
from bokeh.plotting import figure

DATA_DIR = Path("../data")
OUTPUT_DIR = Path("../outputs")


# %% [markdown]
# ## Reprojections for Analysis and Geographic Alignment 
#
# ##### Projection: EPSG:5070 — NAD83 / Conus Albers Equal Area Conic
# - Albers is an equal-area projection that preserves area accuracy for CONUS
# - Minimal distortion for CONUS
# - Well-suited for regional comparisons
#

# %%
# Fire occurrence (7th edition, reprojected to Albers)
# Cache paths so we don't have to recompute every time we open the notebook
fire_cache_path = DATA_DIR / "processed/fire_occurrence_7th_albers.gpkg"
# The cache folder is gitignored, so a fresh clone doesn't have it yet
fire_cache_path.parent.mkdir(parents=True, exist_ok=True)

# Only load the columns the analysis uses (all 38 columns take ~4 GB of memory)
fire_columns = ["FIRE_YEAR", "DISCOVERY_DATE", "NWCG_CAUSE_CLASSIFICATION",
                "NWCG_GENERAL_CAUSE", "FIRE_SIZE", "STATE"]

if fire_cache_path.exists():
    fire = gpd.read_file(fire_cache_path, engine="pyogrio", columns=fire_columns)
else:
    # The GeoPackage also holds a reporting-unit table, so name the fire layer explicitly
    fire = gpd.read_file(DATA_DIR / "FPA_FOD/FPA_FOD_20260615.gpkg", layer="Fires",
                         engine="pyogrio", columns=fire_columns)
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

# %% [markdown]
# ## Data Exploration and Cleaning

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
# Simplify the Fire Occurrence Dataset to suit the needs of the analysis
# Cleaned data is free of empty/NaN values
fire_clean = fire  # already limited to these columns at load

# Look at new dataframe
display(fire_clean.head(10))


# %%
natural_ignitions_cache_path = DATA_DIR / "processed/natural_fire_fuel_ecoregion.gpkg"

if natural_ignitions_cache_path.exists():
    # Ecoregion and fuel columns, plus year/date/size for the interactive summaries, plus the point geometry for gridding
    natural_ignitions = gpd.read_file(natural_ignitions_cache_path, engine="pyogrio",
        columns=["US_L3NAME", "US_L3CODE", "FUEL_CLASS", "FIRE_YEAR", "DISCOVERY_DATE", "FIRE_SIZE"]
    ).astype({"FUEL_CLASS": "int16", "FIRE_YEAR": "int16", "FIRE_SIZE": "float32"})
# Only look at naturally caused fires
else:
    natural_fire = fire[fire["NWCG_CAUSE_CLASSIFICATION"] == "Natural"].copy()

    # Build a list of x,y pairs of point geom for natural fires
    coords = [(geom.x, geom.y) for geom in natural_fire.geometry]
    # Look up the rasters pixel by coords (val[0] removes the rasterio wrapper and returns an int to the new col FUEL_CLASS to natural_fire
    natural_fire["FUEL_CLASS"] = [val[0] for val in fuelClass.sample(coords)]

    # Spatial join tags each fire WITHIN its containing ecoregion
    # Geopandas spatial join matches rows based on geom
    natural_ignitions = gpd.sjoin(natural_fire, ecoregion, how="left", predicate="within")

    natural_ignitions.to_file(natural_ignitions_cache_path, driver="GPKG")
    del natural_fire, coords

# Clip fire points to the lower 48
# The fire data covers all of the US, but the ecoregions only cover the lower 48.
# The left join in the natural_ignitions cell kept every fire, so fires outside the
# ecoregions have NaN in the ecoregion columns. Keeping only rows with an ecoregion name.
natural_ignitions = natural_ignitions[natural_ignitions["US_L3NAME"].notna()].copy()

# Raw ignition counts per ecoregion / fuel type combination
counts = natural_ignitions.groupby(["US_L3NAME", "FUEL_CLASS"]).size().reset_index(name="ignition_count")
print(counts)

# Free the full fire table now that natural_ignitions is built
del fire, fire_clean
gc.collect()

# %%
# Remove fires that fall in NB1 Urban/developed and the unburnable fuel types
# NB9 Barren, NB8 Open water, & NB2 Snow/ice, -9999 Fill-NoData
# Also remove SB1–SB4 Slash-blowdown: it covers only ~300 km² of CONUS (24 fires), too little data to analyze

# look up each fuel class that is unburnable (plus urban/developed and slash-blowdown)
is_unburnable = (fuel_lookup["FBFM40"].isin(["NB1", "NB2", "NB8", "NB9", "Fill-NoData"])
                 | fuel_lookup["FBFM40"].str.startswith("SB"))
# Assign the values of the unburnable fuel classes to unburnable
unburnable = fuel_lookup.loc[is_unburnable, "VALUE"]

# Drop unburnable fuel classes in the natural_ignitions df
dropped = natural_ignitions["FUEL_CLASS"].isin(unburnable)

# How many fires were dropped?
print(f"Dropping {dropped.sum():,} of {len(natural_ignitions):,} fires ({dropped.mean():.1%}) "
      "on urban, snow/ice, water, barren, slash-blowdown, or no-data fuel")
print(natural_ignitions.loc[dropped, "FUEL_CLASS"].value_counts())

# This keeps the fires that were not flagged to be dropped and flips 
# every true to false and false to true so true means keep (~ means not)
natural_ignitions = natural_ignitions[~dropped].copy()

# %% [markdown]
# ### Fuel availability: area of each fuel type in each ecoregion 
#
# Ignition counts alone favor fuels that cover a lot of ground. To identify which fuels are most
# receptive to ignition, we need the area of each fuel class inside each ecoregion to create a normalized scale. Then
# compare ignitions to that area (ignitions per km² of fuel).
#
# The 30 m fuel raster has far too many pixels to load at once so we will batch process them,
# For each batch:
# 1. read the fuel codes
# 2. turn the ecoregion polygons into a matching array, so every pixel has a tag that corresponds to its ecoregion
# 3. count every (ecoregion, fuel class) pair and add it to a running total

# %%
# Before we normalize we need to count the number of fuel-type pixels that fall within each ecoregion. This is what 
# we will do below

# Lookup from fuel code to its FBFM40 label (e.g. 102 -> "GR2"), used to group fuel classes
code_to_label = dict(zip(fuel_lookup["VALUE"], fuel_lookup["FBFM40"]))

fuel_area_cache_path = DATA_DIR / "processed/fuel_area_by_ecoregion.csv"

if fuel_area_cache_path.exists():
    fuel_area = pd.read_csv(fuel_area_cache_path)
else:
    window_size = 4096  

    # Ecoregion codes are stored as text and rasterize needs numbers, so convert text to ints
    eco_codes = ecoregion["US_L3CODE"].astype(int)

    # Create a running totals array that has space for each ecoregion/fuel pair
    pair_totals = np.zeros(256 * 256, dtype="int64")

    # Create a double for-loop to step through the fuel-class raster one window (4096 x 4096 pixels) at a time
    for row_off in range(0, fuelClass.height, window_size):
        for col_off in range(0, fuelClass.width, window_size):
            # Window(col_off, row_off, width, height); min() trims the last windows at the right/bottom edges
            window = Window(col_off, row_off,
                            min(window_size, fuelClass.width - col_off),
                            min(window_size, fuelClass.height - row_off))

            # Window_bounds converts the pixels into geographic coordinates in meters
            window_box = box(*window_bounds(window, fuelClass.transform))
            # Which ecoregions overlap this window? Returns T/F for each ecoregion
            overlapping = ecoregion.geometry.intersects(window_box)
            if not overlapping.any():
                continue   # window is entirely ocean / Canada / Mexico: nothing to count, skip the read

            # 1. Fuel codes for this window (int16 array, -9999 = no data)
            fuel = fuelClass.read(1, window=window)

            # 2. Ecoregion code for each pixel in the same window (0 = outside every ecoregion)
            #  Converts polygons into a grid of pixels. Input = geom and value, return = array where every pixel falling
            # within that shape is assigned the shape's value
            eco = rasterize(zip(ecoregion.geometry[overlapping], eco_codes[overlapping]),
                            out_shape=fuel.shape,
                            transform=fuelClass.window_transform(window),
                            fill=0, dtype="uint8")

            # 3. Keep pixels that are inside an ecoregion and have fuel data, then count each pair
            valid = (eco > 0) & (fuel != -9999)
            keys = eco[valid].astype("int32") * 256 + fuel[valid]
            pair_totals += np.bincount(keys, minlength=pair_totals.size)   # bincount = how many times each key appears

    # Turn the non-zero slots back into a table: key // 256 = ecoregion, key % 256 = fuel class
    keys = np.nonzero(pair_totals)[0]
    fuel_area = pd.DataFrame({"US_L3CODE": keys // 256,
                              "FUEL_CLASS": keys % 256,
                              "pixels": pair_totals[keys]})
    fuel_area.to_csv(fuel_area_cache_path, index=False)   # slow step runs once, then it's cached

# Each pixel is 30 m x 30 m = 900 m² = 0.0009 km²
fuel_area["area_km2"] = fuel_area["pixels"] * 900 / 1e6

# Same fuel grouping as the fires: two-letter FBFM40 prefix (fuel-class group)
# other non-burnable classes (urban, snow/ice, water, barren) get no group
fuel_labels = fuel_area["FUEL_CLASS"].map(code_to_label)
fuel_area["FUEL_GROUP"] = fuel_labels.str[:2].replace({"NB": None})
fuel_area.loc[fuel_labels == "NB3", "FUEL_GROUP"] = "Ag"

# Sanity check: the total should be close to the area of CONUS minus the Great Lakes, which the
# ecoregions leave out (~8.1 million km² - ~0.24 million km² ≈ 7.8 million km²)
print(f"Total area counted: {fuel_area['area_km2'].sum():,.0f} km²")
print(fuel_area.groupby("FUEL_GROUP")["area_km2"].sum().sort_values(ascending=False).round(0))


# %% [markdown]
# ### Data Cleaning Discussion:
#
# **Fire Occurrence Data** 
#
# - Filtered to NWCG_Cause_Classification == "Natural"
# - Clipped to CONUS through spatial join (point-in-polygon)
# - Fire tagged with fuel class (30 m pixel) at its location
# - Removed fires that were tagged with urban (NB1), snow/ice (NB2), water (NB8), barren (NB9), slash-blowdown (SB1–SB4) or no-data fuel
#
# **Ecoregions (EPA Level III)**
#
# - Dissolved on the US_L3CODE field because original dataset split polygons at state lines

# %% [markdown]
# ## Overview: Natural Ignitions by Fuel Class

# %% [markdown]
# ![](../images/Project2_OverviewofData_FirebyFuelClass.png)

# %% [markdown]
# ![](../images/Project2_OverviewofData_Legend.png)

# %% [markdown]
# **View 1.** Natural-cause wildfire ignitions across CONUS, before non-burnable and slash-blowdown fires were removed. Each point is one ignition, colored by the LANDFIRE FBFM40 fuel class at its location. White lines are EPA Level III ecoregion boundaries.

# %% [markdown]
# ### Discussion – Overview
# This preliminary visualization shows only broad trends in ignitions by fuel type across CONUS. The sheer number of points makes it difficult to see patterns finer than the landscape scale. As expected, ignitions are concentrated in the West, specifically the Great Basin, the Northern and Middle Rockies, the Colorado Plateau, and the Arizona/New Mexico mountains, and they taper off toward the Midwest. Interestingly, Florida stands out as a hotspot in the East, possibly because of frequent lightning producing many small fires. Fuel classes at ignition points change clearly across ecoregions and often line up with ecoregion boundaries, which supports comparing ignitions by ecoregion. However, raw ignition counts can make a fuel type look dominant simply because it covers more area than other fuels, which shows the need to normalize ignition rates by fuel area. Finally, some ignitions fall on non-burnable fuel types, likely reflecting the ~1 mi² location accuracy of the fire records. Those records were removed during data cleaning.

# %% [markdown]
# ## Iteration 1: Kernel Density of Natural Ignitions

# %%
# ---- Map elements used on the maps: scale bar, north arrow, projection / data sources box ----
# All positions are in map units (meters, EPSG:5070) unless noted.

def add_scalebar(ax, x0, y0, length_km=500, n_segments=4, height_km=30,
                 label_every_segment=False, labels_above=False, fill=("black", "white"), color="black"):
    """Alternating black/white scale bar, lower-left corner at (x0, y0).
    label_every_segment=True labels every segment boundary (0, 250, 500, ...) like the overview map;
    otherwise only the start, middle and end. labels_above=True puts the labels above the bar.
    fill: the two alternating segment colors; color: outline and label color (for dark maps)."""
    seg = length_km * 1000 / n_segments                       # one segment's length in meters
    for i in range(n_segments):
        ax.add_patch(Rectangle((x0 + i * seg, y0), seg, height_km * 1000,
                               facecolor=fill[i % 2],                         # alternate colors
                               edgecolor=color, linewidth=0.8, zorder=5))
    # Where the labels go: every segment boundary, or start / middle / end
    if label_every_segment:
        ticks = [i * length_km / n_segments for i in range(n_segments + 1)]
    else:
        ticks = [0, length_km / 2, length_km]
    # Labels sit just above or just below the bar
    if labels_above:
        label_y, va = y0 + height_km * 1000 * 1.5, "bottom"
    else:
        label_y, va = y0 - height_km * 1000 * 0.5, "top"
    for km in ticks:
        ax.text(x0 + km * 1000, label_y, f"{km:,g}", ha="center", va=va, fontsize=9, color=color, zorder=5)
    # "km" right after the end number, on the same line. It's offset in points (not meters) from the
    # bar's end: about half the width of the end number + a small gap, so the number stays centered on its tick
    end_label = f"{length_km:,g}"
    ax.annotate("km", xy=(x0 + length_km * 1000, label_y),
                xytext=(0.3 * 9 * len(end_label) + 2.5, 0), textcoords="offset points",
                ha="left", va=va, fontsize=9, color=color, zorder=5)

def add_compass(ax, cx, cy, radius_km=90, style="arrow", fg="black", bg="white"):
    """North indicator centered at (cx, cy) in map units.
    style="arrow":   simple arrowhead, half black / half white, with N above it
    style="compass": 4-point compass rose, each point half black / half white
    fg / bg replace black / white (fg also colors the outline and the N), e.g. for dark maps.
    """
    r = radius_km * 1000          # length of each point
    w = r * 0.22                  # half-width of each point at its base
    if style == "arrow":
        # One tall arrowhead: tip at the top, notched base so it reads as an arrow, not a triangle
        tip, base_y, notch = (cx, cy + r), cy - r, (cx, cy - r * 0.55)
        w = r * 0.4
        ax.add_patch(Polygon([tip, (cx - w, base_y), notch], facecolor=fg, edgecolor=fg, lw=0.8, zorder=5))
        ax.add_patch(Polygon([tip, (cx + w, base_y), notch], facecolor=bg, edgecolor=fg, lw=0.8, zorder=5))
    else:
        # Each point = two triangles from the center: (tip, side) gives one half of the point
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:          # N, E, S, W
            tip = (cx + dx * r, cy + dy * r)
            left = (cx - dy * w, cy + dx * w)                       # perpendicular offsets at the base
            right = (cx + dy * w, cy - dx * w)
            ax.add_patch(Polygon([(cx, cy), left, tip], facecolor=fg, edgecolor=fg, lw=0.8, zorder=5))
            ax.add_patch(Polygon([(cx, cy), right, tip], facecolor=bg, edgecolor=fg, lw=0.8, zorder=5))
    ax.text(cx, cy + r * 1.1, "N", ha="center", va="bottom", fontsize=13, fontweight="bold", color=fg, zorder=5)

def add_projection_box(ax, sources=None, x=0.0, y=-0.02, color="black", facecolor="white"):
    """Projection (and optional data sources) box, same wording as the overview map.
    x, y are in axes fractions (0–1); the default hangs the box just below the map's lower-left corner.
    sources: list of "Label: citation" strings; leave out to show only the projection.
    color: text color; facecolor: box fill (for dark maps)."""
    lines = [r"$\bf{Projection}$",
             "North American Datum of 1983 / Conus Albers Equal Area Conic",
             "Standard parallels 29.5° N, 45.5° N • Central meridian 96° W • Latitude of origin 23° N •",
             "Units: meters"]
    if sources:
        lines += ["", r"$\bf{Data\ sources}$"] + sources
    return ax.text(x, y, "\n".join(lines), transform=ax.transAxes, ha="left", va="top", fontsize=8,
                   color=color, linespacing=1.4,
                   bbox=dict(facecolor=facecolor, edgecolor="0.5", boxstyle="square,pad=0.8"))

# %%
# Cross-validate KDE bandwidth (σ)
# For each candidate σ, fit a Gaussian KDE on 4/5 of the fires and score how well it predicts
# too small overfits individual fires, too large smooths away patterns.
# Uses all fires because the best σ shrinks as the number of points grows.

# Pull out the natural_ignitions coordinates in meters. The KDE needs projected coordinates (meters), not lat/lon
fire_xy = np.column_stack([natural_ignitions.geometry.x, natural_ignitions.geometry.y])   # EPSG:5070 meters

# Create a cross-validation bandwidth function that uses grid search to find the optimal sigma
def cv_bandwidth(candidates):
    search = GridSearchCV(
        KernelDensity(kernel="gaussian", rtol=1e-4),   
        {"bandwidth": candidates},                      # σ values to try, in meters
        # 5 folds, shuffled: the file is ordered by agency/region, so shuffling keeps
        # the folds from being grouped by region
        cv=KFold(n_splits=5, shuffle=True, random_state=0),
        n_jobs=-1,                                      # use all CPU cores
    )
    search.fit(fire_xy)
    return search.best_params_["bandwidth"], search.cv_results_["mean_test_score"]

# 2-stage coarse search over 2–30 km, then a finer search around the optimal sigma
# Makes 12 bandwidths from 2-30km
coarse = np.geomspace(2_000, 30_000, 12)
# Runs the cross-validation on all 12 values and returns the best σ and the average score for each one
best, scores = cv_bandwidth(coarse)
# Returns the position of the highest score
i = int(np.argmax(scores))
# Use i for the fine search to make 7 candidates evenly spaced around the optimal sigma's two neighbors
fine = np.linspace(coarse[max(i - 1, 0)], coarse[min(i + 1, len(coarse) - 1)], 7)
# Return the best σ from the fine cv
best_bandwidth, _ = cv_bandwidth(fine)

print(f"Cross-validated bandwidth: {best_bandwidth / 1000:.1f} km")

# %%
# Step 1: 1 km grid over CONUS
# Fires are counted per cell on this grid, then smoothed into density surfaces (KDE).
# 1 km keeps local variation in ignitions; FPA FOD locations are only accurate to ~1 sq mi,
# so going finer would add memory without adding real detail.

cell_size = 1_000  # grid cell width/height in meters (EPSG:5070 units)

# Grid extent = bounding box of the ecoregions (i.e., CONUS)
xmin, ymin, xmax, ymax = ecoregion.total_bounds

# Columns/rows needed to cover that box; ceil so the far edges aren't cut off
ncols = int(np.ceil((xmax - xmin) / cell_size))
nrows = int(np.ceil((ymax - ymin) / cell_size))

# Affine transform: ties grid row/column positions to real-world coordinates.
grid_transform = from_origin(xmin, ymax, cell_size, cell_size)

# CONUS mask: True for cells inside an ecoregion, False for ocean/Canada/Mexico
# all_touched=True keeps coastal/border cells that are only partly inside, so no fires get masked out
conus_mask = rasterize(ecoregion.geometry, out_shape=(nrows, ncols), transform=grid_transform,
                       fill=0, default_value=1, dtype="uint8", all_touched=True).astype(bool)

# Each fire's grid cell: x counts columns right from xmin, y counts rows down from ymax
natural_ignitions["COL"] = ((natural_ignitions.geometry.x - xmin) // cell_size).astype("int32")
natural_ignitions["ROW"] = ((ymax - natural_ignitions.geometry.y) // cell_size).astype("int32")

print(f"Grid: {nrows:,} rows x {ncols:,} cols = {nrows * ncols / 1e6:.1f}M cells "
      f"({conus_mask.sum() / 1e6:.1f}M inside CONUS)")

# Step 2: Count fires per 1 km cell
# Each fire adds 1 to the cell it falls in (np.add.at handles many fires in the same cell)
fire_counts = np.zeros((nrows, ncols), dtype="int32")
np.add.at(fire_counts, (natural_ignitions["ROW"].to_numpy(), natural_ignitions["COL"].to_numpy()), 1)

print(f"Total fires counted: {fire_counts.sum():,} (should equal {len(natural_ignitions):,})")
print(f"Cells with at least one fire: {(fire_counts > 0).sum():,}")
print(f"Most fires in one cell: {fire_counts.max()}")


# Step 3: Gaussian KDE of natural ignitions on the 1 km grid
bandwidth = round(best_bandwidth, -2)  # kernel standard deviation (σ) in meters, from cross-validation
sigma_cells = bandwidth / cell_size    # gaussian_filter works in cells, not meters -> 5.1 cells
                                       # in 2-D, about 39% of each fire's weight stays within 1σ (~5 km) of it and about 86% within 2σ (~10 km)

density = gaussian_filter(
    fire_counts.astype("float32"),     # input grid (must be float)
    sigma=sigma_cells,                 # width of the Gaussian, in cells
    mode="constant",                   # treat everything beyond the grid edge as zero fires
    cval=0.0,                       
    truncate=4.0,                      # ignore cells farther than 4σ
)

# Each cell is 1 km², so the value is already fires per km² (1992–2024)
density[~conus_mask] = np.nan          # blank out ocean / Canada / Mexico (~ = not in)

print(f"Total before: {fire_counts.sum():,}  after: {np.nansum(density):,.0f}")

# Create a plot
fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(density, extent=(xmin, xmin + ncols * cell_size, ymax - nrows * cell_size, ymax),
               cmap="YlOrRd", norm=LogNorm(vmin=1e-3, vmax=np.nanmax(density)))
ecoregion.boundary.plot(ax=ax, color="0.3", linewidth=0.3)
cbar = fig.colorbar(im, ax=ax, shrink=0.6, label="Natural ignitions per km² (1992–2024)")
ax.set_title(f"Kernel Density of Natural Ignitions, 1992–2024 (Gaussian, σ = {bandwidth / 1000:.1f} km)", fontsize=16)

# Map elements laid out like the overview map: 1,000 km scale bar (labels above) in the lower left
# with the projection box below it, north arrow below the colorbar in the bottom-right corner
x_lo, x_hi = ax.get_xlim()
y_lo, y_hi = ax.get_ylim()
add_scalebar(ax, x_lo + 0.02 * (x_hi - x_lo), y_lo + 0.04 * (y_hi - y_lo), length_km=1000,
             n_segments=4, height_km=25, label_every_segment=True, labels_above=True)
add_projection_box(ax)

# North arrow: its own small axes centered under the colorbar (positions in figure fractions)
fig.canvas.draw()                     # settle the layout so the colorbar's final position is known
cb = cbar.ax.get_position()
arrow_ax = fig.add_axes([cb.x0 + cb.width / 2 - 0.03, cb.y0 - 0.16, 0.06, 0.11])
arrow_ax.set_xlim(-150_000, 150_000)
arrow_ax.set_ylim(-100_000, 150_000)
arrow_ax.set_aspect("equal")
add_compass(arrow_ax, 0, 0)
arrow_ax.set_axis_off()

ax.set_axis_off()
plt.show()



# %% [markdown]
# **View 2.** Kernel density of natural-cause wildfire ignitions across CONUS. Colors show natural ignitions per km² on a log scale. Grey lines are EPA Level III ecoregion boundaries.

# %% [markdown]
# ### Discussion – First Iteration
#
# Wildfire ignitions are heavily concentrated, with clear boundaries in particular ecoregions in the West and Southeast. About half of the 319,148 natural ignitions (~159,500) fall within just 401,247 km², or 5.1% of CONUS, and 80% (~255,300) fall within 1,237,645 km², or 15.8% of CONUS. The highest mean density of ignitions is in the Southwest, in the Arizona/New Mexico Mountains ecoregion (Upper Gila Mountains Level II ecoregion), with nearly 0.3 ignitions/km². High-density bands closely follow ecoregion boundaries in the Cascades, Sierra Nevada, Blue Mountains, Idaho Batholith, and Northern Rockies - all five lie within the same Western Cordillera Level II ecoregion. These regions share forest fuel types in elevated terrain that sees frequent summer thunderstorms. Also noteworthy, Florida is an outlier compared to its East Coast neighbors, and a clear hotspot exists in the Black Hills of South Dakota (Middle Rockies ecoregion). Raw density doesn't tell us enough about fuel groups to draw any definitive conclusions - although we can see that many of the western hotspots are in areas dominated by the timber understory and timber litter fuel groups.

# %% [markdown]
# ### Data Processing & Visualization
#
# **Kernel Density & Rasterizing**
#
# Creating a rasterized map of natural wildfire ignitions from point features first requires smoothing the data and taking it from discrete to continuous data. Choosing a function and the appropriate bandwidth to use in the KDE are the two most important design features when implementing a KDE. A Gaussian curve is a function that generally works well with a variety of data. The bandwidth to choose for the Gaussian is less straightforward and requires its own analysis. Using grid search cross-validation to find the optimal bandwidth is one approach to optimizing this value. For each candidate bandwidth (σ), cross-validation splits the fires into 5 random groups (folds) and fits a Gaussian KDE on 4 of the 5 groups, holding out the 5th for validation. It scores the bandwidth on the held-out fold by comparing the density of the KDE to where the validation group's fires actually fall, using log-likelihood. Higher scores correspond to KDEs that capture the distribution more accurately. This process repeats 5 times so each group is held out once, then the log-likelihood scores are averaged. This approach penalizes bandwidths that are too small because the Gaussian is a narrow spike over each fire occurrence - held-out fires that fall outside the spikes are given a density of ~0. The log of a density close to 0 is a large negative value - a few fires in the gaps between the curves drag the average score way down. This results in the KDE memorizing the training data and overfitting. On the contrary, a very large bandwidth over each fire occurrence doesn't capture areas where hotspots exist because the peaks have been flattened - resulting in a blurred distribution and underfitting. Grid search is implemented twice in conjunction with cross-validation - first, 12 values from 2 - 30 km were tested, then 7 values around the winner of the first grid search - the result was a 5.1 km bandwidth.
#
# After the optimal bandwidth was found, a 1 km grid over CONUS was created and all fires within each cell were summed. The KDE was then run with the optimal bandwidth across the centroid of each grid cell and its corresponding fire occurrence count. The optimal bandwidth was chosen from each fire occurrence rather than the sum of fires per 1 km grid cell - summing fires per cell shifts each fire to the center of its cell, which is a very small shift compared to the 5 km width of the Gaussian. This results in a map that is only slightly smoother than one built from each fire occurrence, so the difference is negligible. Also, by summing fire counts per pixel we aren't losing any nuance in the fire occurrence dataset because the points within that dataset are only accurate within ~1 mi². The resulting KDE is much less expensive to rasterize than if it were smoothed over each fire occurrence point.

# %% [markdown]
# ## Iteration 2: Natural Ignitions per 1,000 km² of Fuel by Ecoregion

# %%
# Natural ignitions per ecoregion
ignitions = natural_ignitions.groupby("US_L3CODE").size()
# Create a new col of ignitions per ecoregion
ecoregion["ignitions"] = ecoregion["US_L3CODE"].map(ignitions).fillna(0)

# Normalize by fuel area, not total ecoregion area: only the fuel types kept in the analysis
# (GR, GS, SH, TU, TL, Ag) count, so urban, water, barren, snow/ice and slash-blowdown land
# doesn't dilute the rate of ecoregions that contain a lot of it
fuel_km2 = (fuel_area[fuel_area["FUEL_GROUP"].isin(["GR", "GS", "SH", "TU", "TL", "Ag"])]
            .groupby("US_L3CODE")["area_km2"].sum())
ecoregion["fuel_km2"] = ecoregion["US_L3CODE"].astype(int).map(fuel_km2)

# Create a new col that contains the normalized ignition data: ignitions per 1,000 km² of fuel
ecoregion["ign_per_1000km2"] = ecoregion["ignitions"] / (ecoregion["fuel_km2"] / 1_000)

# Class breaks: the rates span 0.3–316, so each class covers roughly 2–3x the one below,
# with 4 of the 7 classes above 50 to show detail where ignitions occur. Every break falls in a
# natural gap between ecoregion rates (e.g. 150 sits in the 141 -> 188 gap).
# The last break is the maximum rate so every ecoregion falls in a class
rate_bins = [5, 15, 50, 100, 150, 200, ecoregion["ign_per_1000km2"].max()]

# Colors: one continuous yellow-to-red scale, one color per class
rate_cmap = ListedColormap(plt.get_cmap("YlOrRd")(np.linspace(0.08, 1, len(rate_bins))))

# Whole-number legend labels like "100–150" (the first class starts at 0)
rate_labels = [f"{lo:.0f}–{hi:.0f}" for lo, hi in zip([0] + rate_bins[:-1], rate_bins)]

def relabel_legend(ax, labels):
    """Replace a geopandas legend's default "100.00, 150.00" labels with our own."""
    for text, label in zip(ax.get_legend().get_texts(), labels):
        text.set_text(label)

# Plot the data
fig, ax = plt.subplots(figsize=(12, 8))
ecoregion.plot(column="ign_per_1000km2", cmap=rate_cmap,
               scheme="user_defined", classification_kwds={"bins": rate_bins},
               edgecolor="0.4", linewidth=0.3, legend=True,
               # Legend placed outside the map on the right, like the colorbar on the KDE map: its
               # lower-left corner sits just past the axes' right edge, low in the frame above the north
               # arrow (bbox_to_anchor is in axes fractions), so it can't overlap the CONUS polygons.
               # "\n" wraps the title onto two lines; alignment="left" left-aligns the title with the entries
               # fontsize / title_fontsize / markerscale enlarge the legend text and color dots
               legend_kwds={"title": "Natural ignitions per\n1,000 km² of fuel", "alignment": "left",
                            "loc": "lower left", "bbox_to_anchor": (1.01, 0.1),
                            "fontsize": 12, "title_fontsize": 13, "markerscale": 1.4},
               ax=ax)
relabel_legend(ax, rate_labels)
ax.set_title("Natural Wildfire Ignitions per 1,000 km² of Fuel by Ecoregion, 1992–2024", fontsize=16)

# Map elements laid out like the KDE map: 1,000 km scale bar (labels above) in the lower left
# with the projection box below it, north arrow below the legend in the bottom-right corner
x_lo, x_hi = ax.get_xlim()
y_lo, y_hi = ax.get_ylim()
add_scalebar(ax, x_lo + 0.02 * (x_hi - x_lo), y_lo + 0.04 * (y_hi - y_lo), length_km=1000,
             n_segments=4, height_km=25, label_every_segment=True, labels_above=True)
proj_box = add_projection_box(ax)

# North arrow: its own small axes centered under the legend, bottom level with the bottom of the
# projection box, so it sits in the figure's bottom-right corner (positions in figure fractions)
fig.canvas.draw()                     # settle the layout so the legend and box positions are known
to_fig = fig.transFigure.inverted()
leg = ax.get_legend().get_window_extent().transformed(to_fig)
box_bottom = proj_box.get_bbox_patch().get_window_extent().transformed(to_fig).y0
arrow_ax = fig.add_axes([leg.x0 + leg.width / 2 - 0.03, box_bottom, 0.06, 0.11])
arrow_ax.set_xlim(-150_000, 150_000)
arrow_ax.set_ylim(-100_000, 150_000)
arrow_ax.set_aspect("equal")
add_compass(arrow_ax, 0, 0)
arrow_ax.set_axis_off()

ax.set_axis_off()
plt.show()

# %% [markdown]
# **View 3.** Natural-cause wildfire ignitions per 1,000 km² of fuel for each EPA Level III ecoregion, 1992–2024. Only the fuel types kept in the analysis (grass, grass-shrub, shrub, timber-understory, timber litter and agriculture) count toward each ecoregion's fuel area. Classes are weighted toward the high end of the data.

# %% [markdown]
# ### Discussion – Second Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
# **TO DO**

# %% [markdown]
# ## Iteration 3: Spatial Weights & Moran's I

# %% [markdown]
# Do ecoregions with a lot of natural ignitions sit next to each other, or is the pattern on the map just noise?
#
# The first step is to define who is next to whom. We use Queen contiguity on the 85 ecoregions, so two ecoregions are neighbors if they share any part of a boundary. The check below confirms there are no islands and that the average ecoregion has about five neighbors.

# %%
# Queen contiguity: ecoregions are neighbors if they share any edge or corner
w = weights.Queen.from_dataframe(ecoregion, use_index=False)
w.transform = "R"   # row-standardize: each ecoregion's neighbor weights sum to 1

# Number of neighbors for each ecoregion
ecoregion["n_neighbors"] = pd.Series(w.cardinalities)

# How the neighbor counts are distributed across the 85 ecoregions
print(ecoregion["n_neighbors"].value_counts().sort_index())
print()

# Ecoregions with one or two neighbors.
few = ecoregion[ecoregion["n_neighbors"] <= 2]
for i, row in few.iterrows():
    neighbor_names = ecoregion.loc[w.neighbors[i], "US_L3NAME"].tolist()
    print(row["US_L3NAME"], "has", row["n_neighbors"], "neighbor(s):", neighbor_names)

# %% [markdown]
# The five ecoregions with only one or two neighbors are either enclosed by a single ecoregion or sit on the coast or the Canadian border, where neighbors outside the data are missing. With row standardized weights, an ecoregion with one neighbor is compared to that single neighbor's rate, which matters later for Southern Florida.
#
# The weights are row standardized, so each ecoregion is compared to the average of its neighbors. That average is the spatial lag, computed below.

# %%
# Spatial lag of the ignition rate
# Row standardized weights times the rate gives, for each ecoregion, the mean rate of its neighbors.
ecoregion["lag_rate"] = weights.lag_spatial(w, ecoregion["ign_per_1000km2"].values)

# Each ecoregion's own rate next to the mean rate of its neighbors
display(ecoregion[["US_L3NAME", "n_neighbors", "ign_per_1000km2", "lag_rate"]].head(10))

# Use the same class breaks as the Iteration 2 map (rate_bins) on both maps so the colors are comparable

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

ecoregion.plot(column="ign_per_1000km2", cmap=rate_cmap,
               scheme="user_defined", classification_kwds={"bins": rate_bins},
               edgecolor="0.4", linewidth=0.3, legend=True,
               # Legend outside the map so it doesn't overlap the CONUS polygons
               legend_kwds={"title": "Ignitions per\n1,000 km² of fuel", "alignment": "left",
                            "loc": "lower right", "bbox_to_anchor": (0.12, 0.0)},
               ax=axes[0])
relabel_legend(axes[0], rate_labels)
axes[0].set_title("Observed Rate")
axes[0].set_axis_off()

ecoregion.plot(column="lag_rate", cmap=rate_cmap,
               scheme="user_defined", classification_kwds={"bins": rate_bins},
               edgecolor="0.4", linewidth=0.3, legend=False,
               ax=axes[1])
axes[1].set_title("Spatial Lag: Mean Rate of Queen Neighbors (Same Classes)")
axes[1].set_axis_off()

plt.show()

# %% [markdown]
# **View 4.** Observed ignition rate per 1,000 km² of fuel for each ecoregion (left) next to its spatial lag, the mean rate of its Queen contiguity neighbors (right). Both maps use the same classes and colors as View 3.

# %% [markdown]
# Next, global Moran's I. The rate is very skewed, from under one to over three hundred, so it is run on the log of the rate. The raw rate is run as well to check that the answer does not depend on the transform.

# %%
# Global Moran's I on the natural ignition rate
from esda.moran import Moran

rate = ecoregion["ign_per_1000km2"].values
print("Smallest rate:", round(rate.min(), 2), " largest rate:", round(rate.max(), 2))

# The rate is heavily skewed, run Moran's I on the log rate,
log_rate = np.log(rate)

np.random.seed(12345)
mi_log = Moran(log_rate, w, permutations=999)
mi_raw = Moran(rate, w, permutations=999)

print("Moran's I, log rate:", round(mi_log.I, 3),
      " expected under no autocorrelation:", round(mi_log.EI, 3),
      " z:", round(mi_log.z_sim, 2),
      " p (999 permutations):", mi_log.p_sim)
print("Moran's I, raw rate:", round(mi_raw.I, 3),
      " expected under no autocorrelation:", round(mi_raw.EI, 3),
      " z:", round(mi_raw.z_sim, 2),
      " p (999 permutations):", mi_raw.p_sim)

# %% [markdown]
# Global Moran's I only says clustering exists. Local Moran's I says where. Each ecoregion is tested against its own neighbors, and the ones that are significant at 0.05 keep their quadrant label.

# %%
# Local Moran's I tests each ecoregion against its own neighbors.
from esda.moran import Moran_Local

lisa = Moran_Local(log_rate, w, permutations=999, seed=12345)

# lisa.q gives the Moran quadrant: 1 High-High, 2 Low-High, 3 Low-Low, 4 High-Low
# lisa.p_sim is the permutation pseudo p value for each ecoregion
ecoregion["lisa_I"] = lisa.Is
ecoregion["lisa_p"] = lisa.p_sim
ecoregion["lisa_q"] = lisa.q

# An ecoregion significant at alpha keeps its quadrant label, the rest are Not significant
alpha = 0.05
labels = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
ecoregion["lisa_cluster"] = "Not significant"
sig = ecoregion["lisa_p"] < alpha
ecoregion.loc[sig, "lisa_cluster"] = ecoregion.loc[sig, "lisa_q"].map(labels)

# How many ecoregions fall in each cluster type
print(ecoregion["lisa_cluster"].value_counts())
print()

# Table of the significant ecoregions, grouped by cluster type and sorted by local I
lisa_table = ecoregion.loc[sig, ["US_L3CODE", "US_L3NAME", "ign_per_1000km2", "lag_rate",
                                 "lisa_I", "lisa_p", "lisa_cluster"]]
lisa_table = lisa_table.sort_values(["lisa_cluster", "lisa_I"], ascending=[True, False])
display(lisa_table)

# %% [markdown]
# Nineteen ecoregions come out High-High, and they form one block across the interior West, from the Cascades and the Northern Rockies down to the Colorado Plateau and the Mojave. Fifteen come out Low-Low across the Corn Belt and the central plains. The Sonoran desert is the one Low-High, a low spot inside the western cluster. No ecoregion is High-Low.

# %% [markdown]
# ### Discussion – Third Iteration
# The spatial statistics confirm what the choropleth suggests by eye. Natural ignition rates are not scattered at random across ecoregions. Global Moran's I on the log of the rate is 0.616 with a permutation p value of 0.001, and the local results put 19 ecoregions in one High-High block across the interior West and 15 in a Low-Low block across the Corn Belt and the central plains. For the research question this means the distribution of natural fires is organized at a scale larger than a single ecoregion. Neighboring ecoregions tend to share the same fire regime, which points to drivers that cross ecoregion boundaries, such as summer lightning and terrain, rather than something unique to each region.
#
# A few limits matter for reading these results. The analysis works at the ecoregion level, so it says nothing about variation inside an ecoregion, and ecoregions differ greatly in size, which is a modifiable areal unit problem. The weights stop at the national border, so ecoregions on the coast or along Canada have fewer neighbors than they really do. Southern Florida shows this clearly. It has one of the highest rates in the East but only one neighbor, so the local test has almost no power there and it is not flagged. With 85 local tests at a cutoff of 0.05 a few of the significant ecoregions are expected to be false positives, and a couple of the High-High members, such as the Columbia Plateau, are in the cluster because of their neighbors rather than their own rate.

# %% [markdown]
# ## Iteration 4: Natural Ignition Density by Fuel Group

# %%
# Fuel group = first two letters of the FBFM40 code (GR, GS, SH, TU, TL); NB3 agriculture -> "Ag"
# Create a dictionary of fuel class and the corresponding label
code_to_label = dict(zip(fuel_lookup["VALUE"], fuel_lookup["FBFM40"]))
# Replace each fires numeric code with its fuel-type label
labels = natural_ignitions["FUEL_CLASS"].map(code_to_label)
# Group each fuel class by fuel group (drop the third char from the Scott and Burgan labels (GR1, GR2 to GR))
natural_ignitions["FUEL_GROUP"] = labels.str[:2].replace({"NB": None})
# Any NB3 label becomes Ag
natural_ignitions.loc[labels == "NB3", "FUEL_GROUP"] = "Ag"

# Create an empty dictionary to store density grid by fuel-class
density_by_group = {}
# groupby splits the table by FUEL_GROUP. Each pass through the loop gives you group and fires
for group, fires in natural_ignitions.groupby("FUEL_GROUP"):
    # Blank 1km grid is created (nrows and ncols come from step 1 when creating grid)
    counts_g = np.zeros((nrows, ncols), dtype="float32")
    # Adds 1 to the cell of every fire in this group
    np.add.at(counts_g, (fires["ROW"].to_numpy(), fires["COL"].to_numpy()), 1)
    # Smooths the counts into a density surface
    dens = gaussian_filter(counts_g, sigma=sigma_cells, mode="constant", cval=0.0)
    # Blanks out cells outside CONUS so they don't get counted
    dens[~conus_mask] = np.nan
    # Saves the group's surface in the dictionary under its name
    density_by_group[group] = dens
    
    print(f"{group}: {len(fires):,} fires")


# %%
groups = ["GR", "GS", "SH", "TU", "TL", "Ag"]
names = {"GR": "Grass", "GS": "Grass-shrub", "SH": "Shrub", "TU": "Timber-understory",
         "TL": "Timber litter", "Ag": "Agriculture"}
extent = (xmin, xmin + ncols * cell_size, ymax - nrows * cell_size, ymax)
norm = LogNorm(vmin=1e-3, vmax=max(np.nanmax(d) for d in density_by_group.values()))

# Densities below 0.001 per km² (including zero) are drawn transparent so the grey CONUS fill
# underneath shows through: grey = (almost) no ignitions, pale yellow = few ignitions
panel_cmap = plt.get_cmap("YlOrRd").copy()
panel_cmap.set_under("none")

# 6 groups -> 2 rows x 3 columns. Figure size and small gaps are chosen so the wide CONUS maps
# fill their panels; right=0.9 leaves room for the colorbar
fig, axes = plt.subplots(2, 3, figsize=(15, 7))
fig.subplots_adjust(left=0.01, right=0.9, top=0.87, bottom=0.03, wspace=0.03, hspace=0.2)
for ax, g, letter in zip(axes.flat, groups, "abcdef"):
    # zorder stacks the layers: grey CONUS fill, then density, then light, thin ecoregion lines
    ecoregion.plot(ax=ax, color="0.88", linewidth=0, zorder=1)
    im = ax.imshow(density_by_group[g], extent=extent, cmap=panel_cmap, norm=norm, zorder=2)
    ecoregion.boundary.plot(ax=ax, color="0.6", linewidth=0.12, zorder=3)
    # Panel letter and group name, with the fire count on a smaller second line just below it
    ax.set_title(f"({letter}) {names[g]}", fontsize=12, pad=14)
    ax.text(0.5, 1.0, f"{(natural_ignitions['FUEL_GROUP'] == g).sum():,} fires", transform=ax.transAxes,
            ha="center", va="bottom", fontsize=9, color="0.35")
    ax.set_axis_off()
fig.suptitle(f"Kernel Density of Natural Ignitions by Fuel Group, 1992–2024 (σ = {bandwidth / 1000:.1f} km)",
             fontsize=16)

# One set of map elements for the whole figure: scale bar below the maps in the bottom-left corner
# with the projection box under it, colorbar the full height of both rows, north arrow below the colorbar
fig.canvas.draw()                     # settle the layout so the panel positions are known
to_fig = fig.transFigure.inverted()

# The scale bar gets its own strip of axes just below panel (d), with the same width and x/y limits
# per figure fraction as the panel, so 1,000 km on the bar is 1,000 km on the maps
panel = axes[1, 0].get_position()
x_lo, x_hi = axes[1, 0].get_xlim()
y_lo, y_hi = axes[1, 0].get_ylim()
strip_h = 0.05                                                   # strip height in figure fractions
sb_ax = fig.add_axes([panel.x0, panel.y0 - strip_h, panel.width, strip_h])
sb_ax.set_xlim(x_lo, x_hi)
sb_ax.set_ylim(0, strip_h * (y_hi - y_lo) / panel.height)        # same meters per figure fraction as the map
sb_ax.set_axis_off()
# Labels only at 0 / 500 / 1,000 km: every segment boundary is too crowded at panel size
add_scalebar(sb_ax, x_lo + 0.02 * (x_hi - x_lo), 0.15 * strip_h * (y_hi - y_lo) / panel.height,
             length_km=1000, n_segments=4, height_km=25, labels_above=True)
proj_box = add_projection_box(sb_ax, y=-0.35)                   # hangs just below the scale bar strip
fig.canvas.draw()                     # settle again so the projection box position is known
top_panel, bottom_panel = axes[0, 2].get_position(), axes[1, 2].get_position()
cax = fig.add_axes([top_panel.x1 + 0.015, bottom_panel.y0, 0.012, top_panel.y1 - bottom_panel.y0])
cbar = fig.colorbar(im, cax=cax, label="Natural ignitions per km² (1992–2024)")

# North arrow: its own small axes centered under the colorbar, bottom level with the bottom of the
# projection box, so it sits in the figure's bottom-right corner (positions in figure fractions)
cb = cax.get_position()
box_bottom = proj_box.get_bbox_patch().get_window_extent().transformed(to_fig).y0
# min() drops the arrow further if needed so its "N" clears the colorbar's bottom tick label
arrow_ax = fig.add_axes([cb.x0 + cb.width / 2 - 0.03, min(box_bottom, cb.y0 - 0.13), 0.06, 0.09])
arrow_ax.set_xlim(-150_000, 150_000)
arrow_ax.set_ylim(-100_000, 150_000)
arrow_ax.set_aspect("equal")
add_compass(arrow_ax, 0, 0)
arrow_ax.set_axis_off()
plt.show()


# %% [markdown]
# **View 5.** Kernel density of natural-cause wildfire ignitions for each fuel group, using the same cross-validated bandwidth as View 2. All panels share one log color scale, so the same color means the same density in every panel. Grey areas have fewer than 0.001 natural ignitions per km². Grey lines are EPA Level III ecoregion boundaries.

# %% [markdown]
# ### Discussion – Fourth Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
#
# **Fuel Grouping**
#
# - Extracted fuel groups (GR, GS, SH, TU, TL) by their two letter prefix; NB3 (agriculture) became its own group, Ag


# %% [markdown]
# ## Iteration 5: Dominant Fuel Group by Ignition Density

# %%
# Track the highest-density group in each cell, one group at a time (saves memory vs. stacking)
best = np.zeros((nrows, ncols), dtype="float32")
dominant = np.full((nrows, ncols), -1, dtype="int8")
for i, g in enumerate(groups):
    d = np.nan_to_num(density_by_group[g])
    higher = d > best
    best[higher], dominant[higher] = d[higher], i

dominant = np.where(best >= 1e-3, dominant, -1)   # blank cells with almost no ignitions
dominant_masked = np.ma.masked_equal(dominant, -1)

colors = ["#e6c84f", "#9cc97a", "#c8743c", "#4fa3a0", "#2f5d3a", "#f2a7b8"]

# Styled like the overview map: dark grey background, bold white title, light map elements
bg = "#333333"   # dark grey background
fg = "0.92"      # near-white for text, outlines and map elements
fig, ax = plt.subplots(figsize=(12, 8), facecolor=bg)   # axis is turned off, so the figure color is what shows
ax.imshow(dominant_masked, extent=extent, cmap=ListedColormap(colors),
          vmin=-0.5, vmax=len(groups) - 0.5, interpolation="nearest")
# White outlines: no fuel group color is near-white, so they stand out from both the grey and the cells
ecoregion.boundary.plot(ax=ax, color="white", linewidth=0.6)
ax.set_title(f"Fuel Group with the Highest Ignition Density, 1992–2024 (σ = {bandwidth / 1000:.1f} km)",
             color="white", fontsize=18, fontweight="bold", pad=16)

# Legend low on the right, just outside the map so it doesn't cover the Southeast: circle markers
# for each fuel group plus an outlined box for the ecoregion boundaries, like the overview map
handles = [Line2D([], [], marker="o", linestyle="none", markersize=13, markerfacecolor=c,
                  markeredgecolor="none", label=names[g]) for c, g in zip(colors, groups)]
handles.append(Patch(facecolor="none", edgecolor="white", label="Level III ecoregion"))
leg = ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(1.01, 0.1), title="Dominant fuel group",
                fontsize=12, title_fontsize=13, alignment="left", labelspacing=0.9,
                facecolor=bg, edgecolor="0.6", labelcolor=fg, framealpha=1, fancybox=False)
leg.get_title().set_color(fg)

# Map elements: 1,000 km scale bar (labels above) in the lower left with the projection box below it
x_lo, x_hi = ax.get_xlim()
y_lo, y_hi = ax.get_ylim()
add_scalebar(ax, x_lo + 0.02 * (x_hi - x_lo), y_lo + 0.04 * (y_hi - y_lo), length_km=1000,
             n_segments=4, height_km=25, label_every_segment=True, labels_above=True,
             fill=(fg, bg), color=fg)
proj_box = add_projection_box(ax, color=fg, facecolor=bg)

# North arrow: its own small axes centered under the legend, bottom level with the bottom of the
# projection box, so it sits in the figure's bottom-right corner (positions in figure fractions)
fig.canvas.draw()                     # settle the layout so the legend and box positions are known
to_fig = fig.transFigure.inverted()
leg_box = leg.get_window_extent().transformed(to_fig)
box_bottom = proj_box.get_bbox_patch().get_window_extent().transformed(to_fig).y0
arrow_ax = fig.add_axes([leg_box.x0 + leg_box.width / 2 - 0.03, box_bottom, 0.06, 0.11])
arrow_ax.set_xlim(-150_000, 150_000)
arrow_ax.set_ylim(-100_000, 150_000)
arrow_ax.set_aspect("equal")
add_compass(arrow_ax, 0, 0, fg=fg, bg=bg)
arrow_ax.set_axis_off()
ax.set_axis_off()
plt.show()


# %% [markdown]
# **View 6.** Fuel group with the highest natural ignition density in each 1 km cell, based on the fuel-group surfaces in View 5. Cells with almost no ignitions are left blank. White lines are EPA Level III ecoregion boundaries.

# %% [markdown]
# ### Discussion – Fifth Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
# **TO DO**

# %% [markdown]
# ## Iteration 6: Ignition Rate by Fuel Group

# %% [markdown]
# ### Which fuels are most receptive to ignition?
#
# Ignition rate = natural ignitions on a fuel group ÷ area of that fuel group ÷ number of years, expressed as ignitions per 1,000 km² of fuel per year. This normalizes ignitions by how much of each fuel exists across CONUS, so a fuel that covers a greater area isn't favored.

# %%
# Now that we have the area of each fuel type (per ecoregion, summed here across CONUS),
# we can normalize: ignitions on each fuel type ÷ area of that fuel type ÷ years
# = ignitions per 1,000 km² of fuel per year, so fuels that cover more ground aren't favored

n_years = 2024 - 1992 + 1 

# Ignitions per fuel group (natural_ignitions exclude urban, snow/ice, water, barren, slash-blowdown, no-data)
ignitions_by_group = natural_ignitions.groupby("FUEL_GROUP").size()

# Fuel area per fuel group, summed over all ecoregions (km²)
area_by_group = fuel_area.groupby("FUEL_GROUP")["area_km2"].sum()

# Create a table, one row per group; only groups in `groups` (same order/colors as the maps)
receptivity = pd.DataFrame({"ignitions": ignitions_by_group, "area_km2": area_by_group}).loc[groups]

# Rate: ignitions / area gives per km² over all years
receptivity["rate"] = receptivity["ignitions"] / receptivity["area_km2"] * 1_000 / n_years

# 95% confidence interval for the rate: we are 95% confident that the true ignition rate on each
# fuel type falls within this interval (natural ignitions per 1,000 km² of that fuel per year).
# It reflects random variation in the fire counts.
n = receptivity["ignitions"]
scale = 1_000 / (receptivity["area_km2"] * n_years)
# lower limit
receptivity["rate_low"] = chi2.ppf(0.025, 2 * n) / 2 * scale
# upper limit 
receptivity["rate_high"] = chi2.ppf(0.975, 2 * n + 2) / 2 * scale

plot_df = receptivity.sort_values("rate")   # sorted so the most receptive bar is on top

print(receptivity.round(3))

# Horizontal bar chart: one bar per fuel group, colored like the maps, with 95% CI error bars
group_color = dict(zip(groups, colors))
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh([names[g] for g in plot_df.index],              
        plot_df["rate"],                                
        xerr=[plot_df["rate"] - plot_df["rate_low"],    
              plot_df["rate_high"] - plot_df["rate"]],    
        color=[group_color[g] for g in plot_df.index],
        edgecolor="0.3", capsize=3)
ax.set_xlabel("Natural ignitions per 1,000 km² of fuel per year")
ax.set_title("Ignition Rate by Fuel Group, CONUS 1992–2024")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.show()


# %% [markdown]
# **Figure 1.** Natural ignitions per 1,000 km² of fuel per year for each fuel group across CONUS, 1992–2024. Error bars show exact Poisson 95% confidence intervals.

# %% [markdown]
# ### Discussion – Final Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
# **TO DO**


# %% [markdown]
# ## Summary tables for the interactive visuals
#
# The interactive charts only need counts, not every fire, so everything below is built from three small tables:
# - `fire_summary`: natural ignitions counted by ecoregion × fuel group × year × month × fire size class.
#   Yearly trends, seasonality, and size breakdowns are all a `groupby` of this table.
# - `eco_fuel`: one row per ecoregion × fuel group with ignitions, fuel area, ignition rate (95% CI),
#   and each fuel's share of the ecoregion's ignitions and fuel area
# - `eco_summary`: one row per ecoregion with its totals, overall ignition rate, and the fuel group with the most ignitions
#
# **Relative rate** = share of the ecoregion's ignitions ÷ share of its fuel area. Above 1 means that fuel
# ignites more than its area alone would predict *within that ecoregion*; below 1 means less.

# %%
# NWCG fire size classes (acres): A < 0.25, B 0.25–9.9, C 10–99.9, D 100–299, E 300–999, F 1,000–4,999, G 5,000+
size_bins = [0, 0.25, 10, 100, 300, 1_000, 5_000, np.inf]

# One row per fire with only the attributes the summaries need
fire_attrs = pd.DataFrame({
    "US_L3CODE": natural_ignitions["US_L3CODE"].astype(int),
    "FUEL_GROUP": natural_ignitions["FUEL_GROUP"],
    "FIRE_YEAR": natural_ignitions["FIRE_YEAR"],
    "MONTH": pd.to_datetime(natural_ignitions["DISCOVERY_DATE"]).dt.month.astype("int8"),
    "SIZE_CLASS": pd.cut(natural_ignitions["FIRE_SIZE"], size_bins, labels=list("ABCDEFG"), right=False),
    "FIRE_SIZE": natural_ignitions["FIRE_SIZE"],
})

# Table 1: counts and acres burned per ecoregion / fuel group / year / month / size class
# observed=True keeps only combinations that actually have fires (SIZE_CLASS is categorical)
fire_summary = (fire_attrs
                .groupby(["US_L3CODE", "FUEL_GROUP", "FIRE_YEAR", "MONTH", "SIZE_CLASS"], observed=True)
                .agg(ignitions=("FIRE_SIZE", "size"), acres_burned=("FIRE_SIZE", "sum"))
                .reset_index())

# Ecoregion names and Level I region (title case reads better than the shapefile's ALL CAPS)
eco_info = pd.DataFrame({"US_L3CODE": ecoregion["US_L3CODE"].astype(int),
                         "US_L3NAME": ecoregion["US_L3NAME"],
                         "NA_L1NAME": ecoregion["NA_L1NAME"].str.title()}).set_index("US_L3CODE").sort_index()

# Table 2: every ecoregion × fuel group pair, including pairs with no fires or no fuel (filled with 0)
pairs = pd.MultiIndex.from_product([eco_info.index, groups], names=["US_L3CODE", "FUEL_GROUP"])
eco_fuel = pd.DataFrame({
    "ignitions": fire_summary.groupby(["US_L3CODE", "FUEL_GROUP"])["ignitions"].sum(),
    "area_km2": fuel_area.groupby(["US_L3CODE", "FUEL_GROUP"])["area_km2"].sum(),
}).reindex(pairs).fillna(0).astype({"ignitions": "int64"})

# Ignition rate and 95% CI, same method as the CONUS-wide bar chart above.
# Area of 0 becomes NaN so pairs where the fuel doesn't exist get a NaN rate instead of dividing by zero
n = eco_fuel["ignitions"]
scale = 1_000 / (eco_fuel["area_km2"].where(eco_fuel["area_km2"] > 0) * n_years)
eco_fuel["rate"] = n * scale
eco_fuel["rate_low"] = np.where(n > 0, chi2.ppf(0.025, 2 * n) / 2, 0) * scale   # lower limit is 0 when there are no fires
eco_fuel["rate_high"] = chi2.ppf(0.975, 2 * n + 2) / 2 * scale

# Each fuel's share of its ecoregion's ignitions and fuel area, and their ratio (relative rate)
eco_totals = eco_fuel.groupby(level="US_L3CODE")[["ignitions", "area_km2"]].transform("sum")
eco_fuel["ign_share"] = eco_fuel["ignitions"] / eco_totals["ignitions"]
eco_fuel["area_share"] = eco_fuel["area_km2"] / eco_totals["area_km2"]
eco_fuel["rel_rate"] = eco_fuel["ign_share"] / eco_fuel["area_share"]

# Table 3: one row per ecoregion
eco_summary = eco_info.assign(
    ignitions=eco_fuel.groupby(level="US_L3CODE")["ignitions"].sum(),
    burnable_km2=eco_fuel.groupby(level="US_L3CODE")["area_km2"].sum(),
)
eco_summary["rate"] = eco_summary["ignitions"] / eco_summary["burnable_km2"] * 1_000 / n_years
eco_summary["top_fuel_group"] = eco_fuel["ignitions"].unstack()[groups].idxmax(axis=1)

# Sanity check: every fire should be counted exactly once
print(f"Fires in fire_summary: {fire_summary['ignitions'].sum():,} (should equal {len(natural_ignitions):,})")
print(f"Fires in eco_fuel:     {eco_fuel['ignitions'].sum():,}")
display(fire_summary.head())
display(eco_fuel.head(6).round(3))
display(eco_summary.sort_values("rate", ascending=False).head().round(2))


# %% [markdown]
# ## Interactive heatmap + map: ignition rate by ecoregion and fuel group
#
# Each heatmap cell is one fuel group inside one ecoregion. Hover over a cell for its counts, area, rate, and confidence interval.
# - **Color by** switches between the ignition rate, relative rate, shares, and raw counts (heatmap and map together)
# - **Sort ecoregions by** reorders the rows, e.g. by the rate on one fuel group to see where that fuel burns most
# - **The slider** greys out cells where the fuel covers too little area for the rate to be trustworthy
#   (a few fires on a tiny patch of fuel give a huge but meaningless rate).
#
# The map beside it shows **one fuel group at a time** in the same colors, so you can see whether high/low values cluster in space.
# - **Click a heatmap cell**: the map switches to that cell's fuel group and outlines that ecoregion
# - **Click an ecoregion on the map**: its row is highlighted in the heatmap. Click empty space to clear.
# - Pan and zoom the map with the toolbar (useful for the small eastern ecoregions)
#
# Everything is also saved as a standalone HTML file in `outputs/`. It works without Jupyter, so it can be shared or linked from the PDF.

# %%
output_notebook(hide_banner=True)

MIN_FUEL_KM2 = 100           # default cut-off for "too little fuel to trust the rate"
NO_FUEL = "#f0f0f0"          # fuel group doesn't exist in this ecoregion
LOW_AREA = "#bdbdbd"         # fuel exists, but covers less than the slider's area

# One row per cell, with the ecoregion's names attached
hm = eco_fuel.reset_index().join(eco_info, on="US_L3CODE")
hm["fuel_name"] = hm["FUEL_GROUP"].map(names)
reliable = hm["area_km2"] >= MIN_FUEL_KM2

# Color scale bounds come from the 2nd–98th percentile of the trustworthy cells, so a few extreme cells don't wash out the rest
def bounds(col):
    vals = hm.loc[reliable & (hm[col] > 0), col]
    return vals.quantile(0.02), vals.quantile(0.98)

rate_lo, rate_hi = bounds("rate")
rel_lo, rel_hi = bounds("rel_rate")
rel_max = max(1 / rel_lo, rel_hi)    # symmetric around 1 on a log scale, so 1 is the neutral middle color
count_lo, count_hi = bounds("ignitions")

# metric -> (label, matplotlib colormap, normalization)
metrics = {
    "rate":       ("Ignition rate (ignitions per 1,000 km² of fuel per year)", "YlOrRd", LogNorm(rate_lo, rate_hi)),
    "rel_rate":   ("Relative rate (share of ignitions ÷ share of fuel area)", "RdBu_r", LogNorm(1 / rel_max, rel_max)),
    "ign_share":  ("Share of the ecoregion's ignitions", "Purples", Normalize(0, 1)),
    "area_share": ("Share of the ecoregion's fuel area", "Greens", Normalize(0, 1)),
    "ignitions":  ("Ignition count, 1992–2024", "YlOrRd", LogNorm(max(count_lo, 1), count_hi)),
}

# Pre-compute every cell's color for every metric (one column each); the browser just swaps columns
mappers = {}
for key, (label, cmap_name, norm) in metrics.items():
    cmap = plt.get_cmap(cmap_name)
    values = hm[key].to_numpy(dtype=float)
    rgba = cmap(norm(np.clip(values, norm.vmin, norm.vmax)))
    hm[f"c_{key}"] = np.where(np.isnan(values), NO_FUEL, [to_hex(c) for c in rgba])
    # Matching Bokeh color mapper so the color bar uses the same colors and range
    palette = [to_hex(c) for c in cmap(np.linspace(0, 1, 256))]
    Mapper = LogColorMapper if isinstance(norm, LogNorm) else LinearColorMapper
    mappers[key] = Mapper(palette=palette, low=norm.vmin, high=norm.vmax)

def cell_colors(metric, min_area):
    """Same rule as the JavaScript callback below: no fuel -> light grey, too little fuel -> grey, else the metric color."""
    return np.where(hm["area_km2"] == 0, NO_FUEL,
                    np.where(hm["area_km2"] < min_area, LOW_AREA, hm[f"c_{metric}"]))

hm["fill"] = cell_colors("rate", MIN_FUEL_KM2)

# Row orders for the sort menu. Rate sorts use only trustworthy cells; the rest go to the bottom.
rate_wide = hm.pivot(index="US_L3NAME", columns="FUEL_GROUP", values="rate")
area_wide = hm.pivot(index="US_L3NAME", columns="FUEL_GROUP", values="area_km2")
orders = {
    "Overall ignition rate (high → low)": eco_summary.sort_values("rate", ascending=False)["US_L3NAME"].tolist(),
    "Level I region, then name": eco_info.sort_values(["NA_L1NAME", "US_L3NAME"])["US_L3NAME"].tolist(),
    "Ecoregion code": eco_info["US_L3NAME"].tolist(),
    "Name (A–Z)": sorted(eco_info["US_L3NAME"]),
}
for g in groups:
    rate_g = rate_wide[g].where(area_wide[g] >= MIN_FUEL_KM2)
    orders[f"{names[g]} rate (high → low)"] = rate_g.sort_values(ascending=False, na_position="last").index.tolist()
# Bokeh draws the first category at the bottom, so reverse each list to put the first ecoregion on top
orders = {k: v[::-1] for k, v in orders.items()}
default_sort = "Overall ignition rate (high → low)"

# Position of each cell's ecoregion (row in eco_info) and fuel group (in `groups`), so the browser can
# find "the cell for ecoregion j and fuel group k" as index j * len(groups) + k (hm is ecoregion-major)
hm["eco_pos"] = hm["US_L3CODE"].map({code: j for j, code in enumerate(eco_info.index)})
hm["fuel_pos"] = hm["FUEL_GROUP"].map({g: k for k, g in enumerate(groups)})
assert (hm.index == hm["eco_pos"] * len(groups) + hm["fuel_pos"]).all()

source = ColumnDataSource(hm.drop(columns="FUEL_GROUP"))

hover_rows = [
    ("Ecoregion", "@US_L3NAME (@US_L3CODE)"),
    ("Level I region", "@NA_L1NAME"),
    ("Fuel group", "@fuel_name"),
    ("Ignitions", "@ignitions{0,0}"),
    ("Fuel area", "@area_km2{0,0} km²"),
    ("Ignition rate", "@rate{0.00} per 1,000 km²/yr (95% CI @rate_low{0.00}–@rate_high{0.00})"),
    ("Share of ignitions", "@ign_share{0.0%}"),
    ("Share of fuel area", "@area_share{0.0%}"),
    ("Relative rate", "@rel_rate{0.00}×"),
]

def make_color_bar():
    return ColorBar(color_mapper=mappers["rate"], title=metrics["rate"][0], orientation="horizontal",
                    width=420, height=12, location=(0, 0), padding=10,
                    formatter=NumeralTickFormatter(format="0.[00]"))   # plain numbers instead of 10⁰, 10¹ on log scales

# --- Heatmap ---
p = figure(x_range=[names[g] for g in groups], y_range=FactorRange(factors=orders[default_sort]),
           width=820, height=16 * len(eco_info) + 150, x_axis_location="above",
           tools="tap", toolbar_location=None)
# Selected cells (a clicked ecoregion's row) stay solid, everything else fades
p.rect(x="fuel_name", y="US_L3NAME", width=0.96, height=0.9, source=source,
       fill_color="fill", line_color=None,
       selection_line_color="black", selection_line_width=1.5, nonselection_fill_alpha=0.35)
p.add_tools(HoverTool(tooltips=hover_rows))
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.grid.grid_line_color = None
p.yaxis.major_label_text_font_size = "9pt"
p.xaxis.major_label_text_font_size = "9pt"
heat_bar = make_color_bar()
p.add_layout(heat_bar, "above")

# --- Choropleth ---
# Simplify the outlines (1 km tolerance) so the saved HTML stays small; invisible at this map size
eco_geoms = ecoregion.set_index(ecoregion["US_L3CODE"].astype(int)).geometry.simplify(1_000).loc[eco_info.index]

def rings(geom):
    """Bokeh multi_polygons format: a list of polygons, each a list of rings (exterior first, then holes)."""
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    xs = [[np.round(ring.xy[0]).tolist() for ring in (poly.exterior, *poly.interiors)] for poly in polys]
    ys = [[np.round(ring.xy[1]).tolist() for ring in (poly.exterior, *poly.interiors)] for poly in polys]
    return xs, ys

# One row per ecoregion (same order as eco_info), starting on the first fuel group.
# The browser copies the chosen fuel group's columns from the heatmap's source into this one.
map_df = hm[hm["FUEL_GROUP"] == groups[0]].drop(columns="FUEL_GROUP").reset_index(drop=True)
map_df["xs"], map_df["ys"] = zip(*(rings(geom) for geom in eco_geoms))
map_source = ColumnDataSource(map_df)

m = figure(width=640, height=430, match_aspect=True, tools="pan,wheel_zoom,reset,tap",
           toolbar_location="below", title=f"Map: {names[groups[0]]}")
m.multi_polygons(xs="xs", ys="ys", source=map_source, fill_color="fill",
                 line_color="white", line_width=0.4,
                 selection_line_color="black", selection_line_width=2.5,
                 nonselection_fill_alpha=1, nonselection_line_color="white")
m.add_tools(HoverTool(tooltips=hover_rows))
m.axis.visible = False
m.grid.grid_line_color = None
m.outline_line_color = None
map_bar = make_color_bar()
m.add_layout(map_bar, "above")

# --- Widgets ---
metric_select = Select(title="Color by", value="rate", width=380,
                       options=[(k, label) for k, (label, _, _) in metrics.items()])
sort_select = Select(title="Sort ecoregions by", value=default_sort, options=list(orders), width=300)
area_slider = Slider(title="Grey out fuels covering less than (km²)", start=0, end=2_000, step=50,
                     value=MIN_FUEL_KM2, width=380)
map_fuel = Select(title="Fuel group shown on map", value=groups[0], width=300,
                  options=[(g, names[g]) for g in groups])
grey_key = Div(text=f"<span style='background:{NO_FUEL};padding:0 8px'>&nbsp;</span> fuel group absent &nbsp; "
               f"<span style='background:{LOW_AREA};padding:0 8px'>&nbsp;</span> too little fuel area to trust the rate")

# Columns copied from the heatmap's source onto the map for the chosen fuel group (colors + hover values)
map_columns = ["fill", "fuel_name", "ignitions", "area_km2", "rate", "rate_low", "rate_high",
               "ign_share", "area_share", "rel_rate"]

# Runs in the browser whenever a widget changes: recolor cells and map, swap the color bars, reorder rows
update = CustomJS(
    args=dict(source=source, map_source=map_source, metric=metric_select, sort=sort_select,
              slider=area_slider, map_fuel=map_fuel, color_bars=[heat_bar, map_bar], map_fig=m,
              mappers=mappers, orders=orders, y_range=p.y_range, map_columns=map_columns,
              titles={k: label for k, (label, _, _) in metrics.items()},
              fuel_names=names, groups=groups, no_fuel=NO_FUEL, low_area=LOW_AREA),
    code="""
    const d = source.data;
    const colors = d["c_" + metric.value];
    for (let i = 0; i < d.fill.length; i++) {
        d.fill[i] = d.area_km2[i] == 0 ? no_fuel : (d.area_km2[i] < slider.value ? low_area : colors[i]);
    }
    source.change.emit();

    // Map: ecoregion j takes the values of heatmap cell j * n_groups + k
    const k = groups.indexOf(map_fuel.value);
    const md = map_source.data;
    for (const col of map_columns) {
        for (let j = 0; j < md[col].length; j++) {
            md[col][j] = d[col][j * groups.length + k];
        }
    }
    map_source.change.emit();
    map_fig.title.text = "Map: " + fuel_names[map_fuel.value];

    for (const bar of color_bars) {
        bar.color_mapper = mappers[metric.value];
        bar.title = titles[metric.value];
    }
    y_range.factors = orders[sort.value];
""")
for widget in (metric_select, sort_select, area_slider, map_fuel):
    widget.js_on_change("value", update)

# Linking clicks. Selecting one side updates the other; the equality checks stop the two from
# endlessly re-triggering each other.
# Heatmap click: select the clicked cell's whole row, show its fuel group on the map, outline the ecoregion
heat_click = CustomJS(args=dict(source=source, map_source=map_source, map_fuel=map_fuel, groups=groups), code="""
    const sel = source.selected.indices;
    const n = groups.length;
    if (sel.length == 0) {
        if (map_source.selected.indices.length > 0) map_source.selected.indices = [];
        return;
    }
    const j = source.data.eco_pos[sel[0]];
    const row = Array.from({length: n}, (_, k) => j * n + k);
    if (sel.length == 1) {
        map_fuel.value = groups[source.data.fuel_pos[sel[0]]];   // a single clicked cell (not a whole row from the map)
    }
    if (sel.length != n || sel[0] != row[0]) source.selected.indices = row;
    if (map_source.selected.indices[0] != j) map_source.selected.indices = [j];
""")
source.selected.js_on_change("indices", heat_click)

# Map click: highlight that ecoregion's row in the heatmap
map_click = CustomJS(args=dict(source=source, map_source=map_source, groups=groups), code="""
    const sel = map_source.selected.indices;
    const n = groups.length;
    if (sel.length == 0) {
        if (source.selected.indices.length > 0) source.selected.indices = [];
        return;
    }
    const j = sel[0];
    if (source.selected.indices[0] != j * n || source.selected.indices.length != n) {
        source.selected.indices = Array.from({length: n}, (_, k) => j * n + k);
    }
""")
map_source.selected.js_on_change("indices", map_click)

# The map panel sticks to the top of the window while you scroll down the (tall) heatmap
map_panel = column(map_fuel, m, styles={"position": "sticky", "top": "0px", "align-self": "flex-start"})
dashboard = column(row(metric_select, sort_select), area_slider, grey_key, row(p, map_panel))
show(dashboard)

OUTPUT_DIR.mkdir(exist_ok=True)
save(dashboard, filename=OUTPUT_DIR / "ecoregion_fuel_dashboard.html",
     title="Natural ignitions by ecoregion and fuel group")


# %% [markdown]
# ### Conclusion
#
# Spatial analysis of the raw ignition distribution and the by-fuel-type distribution shows that natural ignitions are highly concentrated, with hotspots in the forested regions of the Western US and in the Southern Coastal Plain. Six of the top seven ecoregions lie in the same Western Cordillera Level II ecoregion, which is characterized by rugged mountain ranges, mostly mixed-coniferous forest ecosystems, and climates with winter snow and warm, dry summers that experience convective thunderstorms bringing lightning. The Arizona/New Mexico Mountains are alone at the top, about 23% above the next highest ecoregion. Interestingly, the ignitions in this region are different from the other top ecoregions in the West - they are dominated by the timber-litter and grass fuel groups, not timber-understory like the other ecoregions. This points to driving factors other than fuel type, like intense summer monsoonal lightning. It also suggests that it might not be appropriate to compare fuel types across ecoregions, but rather within ecoregions, which points out the importance of scale within the analysis.
#
# Hotspots cluster with their neighbors - the spatial lag and Moran's I (I = 0.616 on the log rate, p = 0.001) analysis shows this, but I doubt the driving force behind it is fuel characteristics. Ecoregions show drastically different fuel types - while grass and timber can both burn, it doesn't mean these two are somehow related. It's fair to say the clustering here is most likely driven by climate and regional weather patterns.
#
# The Southeast is a separate hotspot that warrants a closer look - particularly the Southern Coastal Plain and Southern Florida Coastal Plain. These regions are flat but experience a high degree of lightning strikes - the Southern Coastal Plain's ignitions are mostly timber fuels (timber litter 34%, timber-understory 32%), while the Southern Florida Coastal Plain's are mostly grass (54%), dominated by high-load humid-climate grasses like sawgrass. The two Southeast hotspots have different dominant fuel types and both have high ignition densities, which points to a driver other than fuel type, like lightning and climate.
#
# Fuel type is only part of the pattern we can draw conclusions from in this spatial analysis. While timber-understory has the highest ignition rate nationally and dominates ignitions in hotspots like the Northern Rockies (48%) and Sierra Nevada (43%), the Arizona/New Mexico Mountains and the Southeast show that other driving factors like lightning frequency and regional climate shape where ignition density falls.
#
# Overall, it is safe to say that ignitions concentrate where receptive fuels overlap with lightning, but the nuances within that overlap still need to be explored with further analysis and additional datasets (lightning) to draw any further conclusions.

# %% [markdown]
# ### Future Work
#
# Grouping the 40 Scott and Burgan fuel models into broad fuel groups made the patterns easier to see, but it also hides differences between individual fuel classes. For example, a low-load dry-climate grass (GR1) and a high-load humid-climate grass (GR8) may respond to ignition very differently. Future work will compare ignition rates for the individual fuel classes within each group to find trends that the grouped analysis misses.
#
# Lightning exposure is the other major gap. The ignition rates in this analysis don't account for where lightning actually strikes, so a fuel may look receptive simply because it grows in storm-prone regions. Adding the GOES Geostationary Lightning Mapper (GLM) thunder-hour data would let us map lightning activity across CONUS and model ignitions as a function of both fuel and lightning. That would answer our original research question: whether some fuels convert lightning into ignitions more readily than others, independent of how much lightning they receive.

# %% [markdown]
# ### AI Appendix
#
# **Prompts:**
#
# 1. I have three geospatial datasets: Spatial wildfire occurrence data for the United States, 1992–2020 (7th Edition) (USFS); LANDFIRE's 40 Scott and Burgan Fire Behavior Fuel Models (FBFM40) CONUS raster (USFS & USGS); and Level III Ecoregions of the Conterminous United States (EPA). Give me guidance on how to analyze these datasets to answer my research question: how are natural wildfire ignitions distributed across ecoregions, and which fuel types have the highest ignition rates relative to the area they cover?
# 2. Guide me through creating a grid for a KD-Trees kernel density algorithm using fuel type from the fuelClass dataset (LANDFIRE), so each grid cell contains the majority fuel class.
# 3. Give me the common libraries geospatial data scientists use to implement KDEs. I am going to implement a KDE on my fire-point-by-fuel-type dataset using a Gaussian function.
# 4. What is a more feasible computational approach: keep the same cell size and count per point using a smaller bandwidth, or drop the cell size and sum the counts in each cell? Explain the tradeoffs of these two approaches.
# 5. Now that I have my grid constructed and have summed the number of fires per grid cell, help me implement the suggested KDE. Walk through each step so I understand the code and the arguments being passed into the KDE function.
# 6. Give me the typical libraries geospatial data scientists use to rasterize KDEs. Tell me about the methods and what to take into account when rasterizing point density data.
#
# **Reflection:** These prompts were pivotal in implementing my KDE, and they even pointed me toward using cross-validation (with sklearn) to find the optimal bandwidth for my Gaussian kernel. I found that chatting with GenAI, while taking the time to comment the code and ask about lines I didn't understand, helped me get further than I otherwise would have. I love seeing which libraries exist for what I'm trying to implement and getting a breakdown of each one, so I can find the one that best suits my needs. Learning to cache data on disk and to use `engine="pyogrio"` to read in large datasets was also extremely helpful for speeding up this notebook, as was figuring out the most feasible computational approach to rasterizing KDE data.
