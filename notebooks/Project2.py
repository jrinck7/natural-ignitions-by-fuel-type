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
# # Project 2: Natural Wildfire Ignition Frequency by Fuel Type Across CONUS Ecoregions, 1992–2024
#
# **Names:** Jansen Rinck, Benjamin Barlog, Jianru Shen 
#
# **Class:** CSCI 502: Geospatial Data Science  
#
# **Date:** 10/6/2026

# %% [markdown]
# ## Introduction
#
# Natural wildfire ignitions are not evenly distributed across the contiguous United States (CONUS), and the fuels present on the landscape are one factor shaping where they occur. By comparing ignition rates across fuel types and ecoregions, this analysis examines how fuels and fire interact, and how those interactions vary from region to region. The results can help fire and forest managers understand the spatial patterns of natural ignitions. This is increasingly important as ecosystems, especially post-fire landscapes with limited forest regeneration, shift away from historical vegetation structure. Analyses like this one can help assess the fire-regime shifts that may follow.

# %% [markdown]
# ## Research Question: 
# Between 2018 and 2020, does the rate at which lightning strikes convert into wildfire ignitions vary by fuel type across the ecoregions of the contiguous United States, independent of raw lightning exposure?
#
# ##### Revised Research Question:
# Between 1992 and 2024, how are naturally occurring wildfires distributed across ecoregions and which fuel types have the highest natural ignition rates relative to the area they cover? 

# %% [markdown]
# ### Hypothesis:
#
# Between 1992 and 2024, natural wildfire ignitions are not distributed randomly across CONUS ecoregions. They cluster by ecoregion and neighboring ecoregions will have similar ignition rates. Fuel types impact the rate of ignition - grass and grass-shrub fuels will be the most susceptible to natural ignitions relative to the area they cover.

# %% [markdown]
# # Data:
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
from matplotlib.colors import ListedColormap, LogNorm, to_rgb
from matplotlib.patches import Patch, Polygon, Rectangle

DATA_DIR = Path("../data")


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
# Simplify the Fire Occurance Dataset to suit the needs of the analysis
# Cleaned data is free of empty/NaN values
fire_clean = fire  # already limited to these columns at load

# Look at new dataframe
display(fire_clean.head(10))


# %%
natural_ignitions_cache_path = DATA_DIR / "processed/natural_fire_fuel_ecoregion.gpkg"

if natural_ignitions_cache_path.exists():
    # Only the ecoregion and fuel columns are used below, plus the point geometry for gridding
    natural_ignitions = gpd.read_file(natural_ignitions_cache_path, engine="pyogrio",
        columns=["US_L3NAME", "US_L3CODE", "FUEL_CLASS"]).astype({"FUEL_CLASS": "int16"})
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
# ### Data Cleaning Discussion:
#
# **Fire Occurance Data** 
#
# - Filtered to NWCG_Cause_Classification == "Natural"
# - Clipped to CONUS through spatial join (point-in-polygon)
# - Fire tagged with fuel class (30 m pixel) at its location
# - Removed fires that were tagged with (NB1), snow/ice (NB2), water (NB8), barren (NB9), slash-blowdown (SB1–SB4) or no-data fuel
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
# **View.** **TO DO**

# %% [markdown]
# ### Discussion - Overview
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
#
# **TO DO**

# %% [markdown]
# ## Iteration 1: Natural Ignitions per 1,000 km² by Ecoregion

# %%
# Natural ignitions per ecoregion
ignitions = natural_ignitions.groupby("US_L3CODE").size()
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


def add_scalebar(ax, x0, y0, length_km=500, n_segments=4, height_km=30):
    """Alternating black/white scale bar, drawn in map units (meters), lower-left corner at (x0, y0)."""
    seg = length_km * 1000 / n_segments                       # one segment's length in meters
    for i in range(n_segments):
        ax.add_patch(Rectangle((x0 + i * seg, y0), seg, height_km * 1000,
                               facecolor="black" if i % 2 == 0 else "white",   # alternate colors
                               edgecolor="black", linewidth=0.8, zorder=5))
    # Labels centered under the start, middle and end of the bar
    for km in (0, length_km / 2, length_km):
        ax.text(x0 + km * 1000, y0 - height_km * 1000 * 0.5, f"{km:g}",
                ha="center", va="top", fontsize=9, zorder=5)
    # "km" right after the end number, on the same line. It's offset in points (not meters) from the
    # bar's end: about half the width of the end number + a small gap, so "500" stays centered on its tick
    end_label = f"{length_km:g}"
    ax.annotate("km", xy=(x0 + length_km * 1000, y0 - height_km * 1000 * 0.5),
                xytext=(0.3 * 9 * len(end_label) + 2.5, 0), textcoords="offset points",
                ha="left", va="top", fontsize=9, zorder=5)

def add_compass(ax, cx, cy, radius_km=90, style="arrow"):
    """North indicator centered at (cx, cy) in map units.
    style="arrow":   simple arrowhead, half black / half white, with N above it
    style="compass": 4-point compass rose, each point half black / half white
    """
    r = radius_km * 1000          # length of each point
    w = r * 0.22                  # half-width of each point at its base
    if style == "arrow":
        # One tall arrowhead: tip at the top, notched base so it reads as an arrow, not a triangle
        tip, base_y, notch = (cx, cy + r), cy - r, (cx, cy - r * 0.55)
        w = r * 0.4
        ax.add_patch(Polygon([tip, (cx - w, base_y), notch], facecolor="black", edgecolor="black", lw=0.8, zorder=5))
        ax.add_patch(Polygon([tip, (cx + w, base_y), notch], facecolor="white", edgecolor="black", lw=0.8, zorder=5))
    else:
        # Each point = two triangles from the center: (tip, side) gives one half of the point
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:          # N, E, S, W
            tip = (cx + dx * r, cy + dy * r)
            left = (cx - dy * w, cy + dx * w)                       # perpendicular offsets at the base
            right = (cx + dy * w, cy - dx * w)
            ax.add_patch(Polygon([(cx, cy), left, tip], facecolor="black", edgecolor="black", lw=0.8, zorder=5))
            ax.add_patch(Polygon([(cx, cy), right, tip], facecolor="white", edgecolor="black", lw=0.8, zorder=5))
    ax.text(cx, cy + r * 1.1, "N", ha="center", va="bottom", fontsize=13, fontweight="bold", zorder=5)

# Place both in the lower right, using the plotted map's extent (meters, EPSG:5070)
# (In Albers, true north tilts slightly away from "up" far from the -96° central meridian)
x_lo, x_hi = ax.get_xlim()
y_lo, y_hi = ax.get_ylim()
bar_x = x_lo + 0.84 * (x_hi - x_lo)          # scale bar starts 84% of the way across (east of Florida)
bar_y = y_lo + 0.05 * (y_hi - y_lo)          # and 5% up from the bottom
add_scalebar(ax, bar_x, bar_y, length_km=500)
add_compass(ax, bar_x + 250_000, bar_y + 0.08 * (y_hi - y_lo))   # centered right above the bar's midpoint

ax.set_axis_off()
plt.show()

# %% [markdown]
# **View.** **TO DO**

# %% [markdown]
# ### Discussion – First Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
# **TO DO**

# %% [markdown]
# ## Iteration 2: Spatial Weights & Moran's I

# %%
# Queen contiguity: ecoregions are neighbors if they share any edge or corner
w = weights.Queen.from_dataframe(ecoregion, use_index=False)
w.transform = "R"   # row-standardize: each ecoregion's neighbor weights sum to 1

# Number of neighbors for each ecoregion
ecoregion["n_neighbors"] = pd.Series(w.cardinalities)

# Ecoregions with one or two neighbors.
few = ecoregion[ecoregion["n_neighbors"] <= 2]
for i, row in few.iterrows():
    neighbor_names = ecoregion.loc[w.neighbors[i], "US_L3NAME"].tolist()
    print(row["US_L3NAME"], "has", row["n_neighbors"], "neighbor(s):", neighbor_names)

# Draw the contiguity graph
fig, ax = plt.subplots(figsize=(12, 8))
ecoregion.plot(ax=ax, facecolor="whitesmoke", edgecolor="0.6", linewidth=0.3)
w.plot(ecoregion, ax=ax,
       edge_kws={"color": "tab:blue", "linewidth": 0.6},
       node_kws={"color": "tab:red", "s": 8})
ax.set_title("Queen contiguity between Level III ecoregions")
ax.set_axis_off()
plt.show()

# %%
# Spatial lag of the ignition rate
# Row standardized weights times the rate gives, for each ecoregion, the mean rate of its neighbors.
ecoregion["lag_rate"] = weights.lag_spatial(w, ecoregion["ign_per_1000km2"].values)

# Use the same 7 quantile breaks from the observed rate on both maps so the colors are comparable
import mapclassify
bins = mapclassify.Quantiles(ecoregion["ign_per_1000km2"], k=7).bins

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

ecoregion.plot(column="ign_per_1000km2", cmap="YlOrRd",
               scheme="user_defined", classification_kwds={"bins": bins},
               edgecolor="0.4", linewidth=0.3, legend=True,
               legend_kwds={"title": "Ignitions per 1,000 km²", "loc": "lower left"},
               ax=axes[0])
axes[0].set_title("Observed rate")
axes[0].set_axis_off()

ecoregion.plot(column="lag_rate", cmap="YlOrRd",
               scheme="user_defined", classification_kwds={"bins": bins},
               edgecolor="0.4", linewidth=0.3, legend=False,
               ax=axes[1])
axes[1].set_title("Spatial lag: mean rate of Queen neighbors (same classes)")
axes[1].set_axis_off()

plt.show()

# %% [markdown]
# **View. TO DO** 

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

# %%
# Moran scatterplot for the log rate
# x axis: standardized log rate of each ecoregion
# y axis: spatial lag of that value
# With row standardized weights the slope of the line through the origin equals Moran's I.
z = (log_rate - log_rate.mean()) / log_rate.std()
lag_z = weights.lag_spatial(w, z)
ecoregion["z_log_rate"] = z
ecoregion["lag_z_log_rate"] = lag_z

fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(z, lag_z, s=25, color="tab:red", edgecolor="0.3", linewidth=0.3)
x_line = np.array([z.min(), z.max()])
ax.plot(x_line, mi_log.I * x_line, color="0.2", linewidth=1.5)
ax.axhline(0, color="0.5", linewidth=0.8, linestyle="--")
ax.axvline(0, color="0.5", linewidth=0.8, linestyle="--")

# Name the ecoregions that sit far from the rest
for i in range(len(z)):
    if abs(z[i]) > 2 or abs(lag_z[i]) > 1.5:
        ax.annotate(ecoregion["US_L3NAME"].iloc[i], (z[i], lag_z[i]),
                    fontsize=7, xytext=(3, 3), textcoords="offset points")

# Quadrant labels
ax.text(0.98, 0.98, "High-High", transform=ax.transAxes, ha="right", va="top")
ax.text(0.02, 0.98, "Low-High", transform=ax.transAxes, ha="left", va="top")
ax.text(0.02, 0.02, "Low-Low", transform=ax.transAxes, ha="left", va="bottom")
ax.text(0.98, 0.02, "High-Low", transform=ax.transAxes, ha="right", va="bottom")

ax.set_xlabel("Standardized log ignition rate")
ax.set_ylabel("Spatial lag of standardized log ignition rate")
ax.set_title(f"Moran scatterplot, I = {mi_log.I:.3f}, p = {mi_log.p_sim}")
plt.show()

# %% [markdown]
# **Figure.** **TO DO**

# %% [markdown]
# ### Discussion – Second Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
# **TO DO**

# %% [markdown]
# ## Iteration 3: Natural Ignition Density by Fuel Group

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
                                       # 68% of each fire's weight stays within ~5 km of it and about 95% within ~10 km

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
fig.colorbar(im, ax=ax, shrink=0.6, label="Natural ignitions per km² (1992–2024)")
ax.set_title(f"Kernel density of natural ignitions (Gaussian, σ = {bandwidth / 1000:.1f} km)")
ax.set_axis_off()
plt.show()



# %% [markdown]
# **View.** **TO DO**

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

fig, axes = plt.subplots(2, 3, figsize=(16, 8))   # 6 groups -> 2 rows x 3 columns
for ax, g in zip(axes.flat, groups):
    im = ax.imshow(density_by_group[g], extent=extent, cmap="YlOrRd", norm=norm)
    ecoregion.boundary.plot(ax=ax, color="0.4", linewidth=0.2)
    ax.set_title(f"{names[g]} ({(natural_ignitions['FUEL_GROUP'] == g).sum():,} fires)")
    ax.set_axis_off()
fig.colorbar(im, ax=axes, shrink=0.6, label="Natural ignitions per km² (1992–2024)")
fig.suptitle(f"Kernel density of natural ignitions by fuel group (σ = {bandwidth / 1000:.1f} km)")
plt.show()


# %% [markdown]
# **View.** **TO DO**

# %% [markdown]
# ### Discussion – Third Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
#
# **Fuel Grouping**
#
# - Extracted fuel groups (GR, GS, SH, TU, TL, NB3) by their two letter prefix
#
# **Kernel Density**
#
# - Created a 1km grid over CONUS which is close to the 1 mi² accuracy of the Fire Occurance Data so a finer resolution wouldn't have added more detail 
# - Summed all fires in each 1 km cell and used to Gaussian KDE to smoothed the data relative to cell cebtroids
# - Crossvalidation with 5 k-fold shuffling to find the optimal bandwidth (sigma) for the Gaussian kernel

# %% [markdown]
# ## Iteration 4: Dominant Fuel Group by Ignition Density

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

bg = "#333333"   # dark grey background
fig, ax = plt.subplots(figsize=(12, 8), facecolor=bg)   # axis is turned off, so the figure color is what shows
ax.imshow(dominant_masked, extent=extent, cmap=ListedColormap(colors),
          vmin=-0.5, vmax=len(groups) - 0.5, interpolation="nearest")
# White outlines: no fuel group color is near-white, so they stand out from both the grey and the cells
ecoregion.boundary.plot(ax=ax, color="white", linewidth=0.6)
leg = ax.legend(handles=[Patch(color=c, label=names[g]) for c, g in zip(colors, groups)],
                loc="lower left", title="Dominant fuel group",
                facecolor=bg, edgecolor="0.6", labelcolor="white")
leg.get_title().set_color("white")
ax.set_title(f"Fuel group with the highest ignition density (σ = {bandwidth / 1000:.1f} km)", color="white")
ax.set_axis_off()
plt.show()


# %% [markdown]
# **View.** **TO DO**

# %% [markdown]
# ### Discussion – Fourth Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
# **TO DO**

# %% [markdown]
# ## Iteration 5: Ignition Rate by Fuel Group

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

# Sanity check: the total should be close to the area of CONUS (~8.1 million km²)
print(f"Total area counted: {fuel_area['area_km2'].sum():,.0f} km²")
print(fuel_area.groupby("FUEL_GROUP")["area_km2"].sum().sort_values(ascending=False).round(0))


# %% [markdown]
# ### Which fuels are most receptive to ignition?
#
# Ignition rate = natural ignitions on a fuel group ÷ area of that fuel group ÷ number of years, expressed as ignitions per 1,000 km² of fuel per year. This normalizes ignitions by how much of each fuel exists across CONUS, so a fuel isn't rewarded just for covering a lot of ground.

# %%
# Now that we have the area of each fuel type (per ecoregion, summed here across CONUS),
# we can normalize: ignitions on each fuel type ÷ area of that fuel type ÷ years
# = ignitions per 1,000 km² of fuel per year, so fuels that cover more ground aren't favored

n_years = 2024 - 1992 + 1 

# Ignitions per fuel group (natural_ignitions exclude urban, snow/ice, water, barren, no-data)
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
ax.set_title(f"Ignition rate by fuel group, CONUS {1992}–{2024}")
ax.spines[["top", "right"]].set_visible(False)            
plt.tight_layout()
plt.show()


# %% [markdown]
# **Figure.** **TO DO**

# %% [markdown]
# ### Discussion – Final Iteration
# **TO DO**

# %% [markdown]
# ### Data Processing & Visualization
# **TO DO**

# %% [markdown]
# ### Conclusion
# **TO DO**

# %% [markdown]
# ### Future Work
# **TO DO**

# %% [markdown]
# ### AI Appendix
# **TO DO**
