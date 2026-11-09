# CSCI502 Project 2

Adds NASA Earthdata access (`earthaccess`) on top of the shared `gds-base:latest`
base image.

Lives at `OneDrive\Desktop\CSCI502\Project2\` alongside the other course
projects (moved from `C:\CSCI502\Projects\CSCI502_Project2\` on 2026-11-08).
`data/` is pinned "Always keep on this device" so the devcontainer's bind mount
never reads a cloud-only OneDrive placeholder.

```
docker build -t gds-base:latest ./gds-base
docker build -t gds-project2 .devcontainer
```

## Why `gds-base` and not `gds-qgis`

This base is `darribas/gds` **without** QGIS — it was removed deliberately
(commit `311b0bb`), since Project 2 works through rasterio/geopandas and never
calls PyQGIS. The coursework folder
(`OneDrive\Desktop\CSCI502\docker\gds-qgis\`) builds a *different* image that does
include QGIS and the `qgis-py3` Jupyter kernel, for the exercises in
`docs/HOW_TO_RUN_QGIS_DOCKER.md`.

Both used to build to the tag `gds-qgis:latest`, so whichever was built last
won, and `import qgis` would fail in the exercises for no visible reason.
Different names now, no collision.
