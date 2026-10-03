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
# 1. [Spatial wildfire occurrence data for the United States, 1992-2024 (7th Edition)(USFS)](https://www.fs.usda.gov/rds/archive/catalog/RDS-2013-0009.7)
#    - Federal, State and Local fire data aggreagated
#    - Discovery date, final fire size, point location (1 sq mile accuracy), wildfire-cause
#    - 2.3 million geo-referenced wildfire records
# 2. [LANDFIRE's 40 Scott and Burgan Fire Behavior Fuel Model (FBFM40), CONUS raster (USFS & USGS](https://www.sciencebase.gov/catalog/item/6a1602c7b66b013d45990b82)
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
#    - Two sattelites GOES-18 (west) and GOES-19 (east)
#    - Thunder hour: an hour with detected lightning at a location - a frequency-based storm-activity metric, less biased by a sensor's geographic detection-sensitivity variation than raw flash counts
#    - Resolution: 5 km 

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
    # Look up the rasters pixel by coords (val[0] removes the raterio wrapper and returns an int to the new col FUEL_CLASS to natural_fire
    natural_fire["FUEL_CLASS"] = [val[0] for val in fuelClass.sample(coords)]

    # Spatial join tags each fire WITHIN its containing ecoregion
    # geopandas spatial join matches rows based on geom
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
# ![](../images/Project2_OverviewofData_FirebyFuelClass.png)

# %% [markdown]
# ![](../images/Project2_OverviewofData_Legend.png)

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
# Cross-validate KDE bandwidth (σ)
# For each candidate σ, fit a Gaussian KDE on 4/5 of the fires and score how well it predicts
# too small overfits individual fires, too large smooths away patterns.
# Uses all fires because the best σ shrinks as the number of points grows.

# Pull out the natural_ignitions coordinates in meters. KDE's do not work with coordinates
fire_xy = np.column_stack([natural_ignitions.geometry.x, natural_ignitions.geometry.y])   # EPSG:5070 meters

# Create a cross-validation bandwidth function that uses grid search to find the optimal sigma
def cv_bandwidth(candidates):
    search = GridSearchCV(
        KernelDensity(kernel="gaussian", rtol=1e-4),   
        {"bandwidth": candidates},                      # σ values to try, in meters
        # 5 folds, shuffled: the file is ordered by agency/region, so unshuffled folds
        # aren't grouped by region and are truly random
        cv=KFold(n_splits=5, shuffle=True, random_state=0),
        n_jobs=-1,                                      # use all CPU cores
    )
    search.fit(fire_xy)
    return search.best_params_["bandwidth"], search.cv_results_["mean_test_score"]

# 2-stage coarse search over 2–30 km, then a finer search around the optimal sigma
# Makes 12 bandwidths from 2-30km
coarse = np.geomspace(2_000, 30_000, 12)
# Runs the cross-validation on all 12 valuesand returns the best σ and the average score for each one
best, scores = cv_bandwidth(coarse)
# Returns the position of the highest score
i = int(np.argmax(scores))
# Use i for the fine search to make 7 candidates evenly spaced around the optimal sigma's two neightbors
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
sigma_cells = bandwidth / cell_size    # gaussian_filter works in cells, not meters -> 3 cells
                                       # 68% of each fire's weight stays within 3 km of it and about 95% within 6 km

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


# %%
# Save the dominant fuel group map as a GeoTIFF (for QGIS)
# Raster values: 1–7 = fuel group (in the order of `groups`), 0 = no data (outside CONUS / almost no ignitions)
# uint8 is needed for an embedded color table, and 0 as nodata keeps the groups starting at 1


dominant_out = np.where(dominant >= 0, dominant + 1, 0).astype("uint8")
dominant_tif_path = DATA_DIR / f"processed/dominant_fuel_group_{bandwidth / 1000:.1f}km_sigma.tif"

with rasterio.open(
    dominant_tif_path, "w",
    driver="GTiff",
    height=nrows, width=ncols,      # same shape as the grid
    count=1,                        # one band
    dtype="uint8",
    crs="EPSG:5070",                # same CRS as everything else
    transform=grid_transform,       # ties pixels to real-world coordinates
    nodata=0,
    compress="deflate",             # mostly empty cells, so this shrinks the file a lot
) as dst:
    dst.write(dominant_out, 1)
    # Color table so QGIS shows the same colors as the matplotlib map (paletted renderer)
    dst.write_colormap(1, {i + 1: tuple(int(v * 255) for v in to_rgb(c)) + (255,)
                           for i, c in enumerate(colors)})
    # Record what each value means inside the file itself
    dst.update_tags(1, **{str(i + 1): names[g] for i, g in enumerate(groups)})
    dst.set_band_description(1, "Fuel group with highest natural ignition density")

print(f"Saved {dominant_tif_path}")
print({i + 1: names[g] for i, g in enumerate(groups)})


# %% [markdown]
# ## Fuel availability: proportion of fuel per area in each ecoregion 
#
# Ignition counts alone favor fuels that cover a lot of ground. To idetify which fuels are most
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

    # Create a double for-loop to step through the fuel-class raster one pixel at a time
    for row_off in range(0, fuelClass.height, window_size):
        for col_off in range(0, fuelClass.width, window_size):
            # Window(col_off, row_off, width, height); min() trims the last windows at the right/bottom edges
            window = Window(col_off, row_off,
                            min(window_size, fuelClass.width - col_off),
                            min(window_size, fuelClass.height - row_off))

            # Window_bounds converts the pixels into geographic coordinates in meters
            window_box = box(*window_bounds(window, fuelClass.transform))
            # Which eco region does this pixel fall in? Returns T/F
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
# ## Which fuels are most receptive to ignition?
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
