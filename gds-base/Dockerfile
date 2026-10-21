# Pinned by digest so the build is reproducible. `latest` is a floating tag:
# it currently resolves to this same image (10.0, published 2023-10-19), but the
# upstream maintainer has newer images published (11.0gc, 2026-02-23_amd64) and
# could repoint `latest` at any time, silently changing this build.
# To upgrade deliberately: pick a tag, look up its digest, update both halves here.
FROM darribas/gds:10.0@sha256:3d1ea1df436f0790052cd768838e82b1b5c7e8f659e0bf9e9e78d10ea12f6419

USER root

# The gds kernel.json launches /opt/conda/envs/gds/bin/python directly via
# ipykernel_launcher, bypassing `conda activate`. That means the
# PROJ_DATA/PROJ_NETWORK env vars normally set by
# /opt/conda/envs/gds/etc/conda/activate.d/proj4-activate.sh are never
# applied to the kernel process, so GDAL/OGR's linked libproj falls back to
# a path that fails to open ("PROJ: proj_create_from_database: Open of
# .../share/proj failed") even though pyproj resolves the same directory
# fine on its own. Pin the env vars directly in the kernel spec so every
# gds-kernel notebook process gets them regardless of shell activation.
RUN python3 -c "\
import json; \
path = '/home/jovyan/.local/share/jupyter/kernels/gds/kernel.json'; \
spec = json.load(open(path)); \
spec['env'] = {'PROJ_DATA': '/opt/conda/envs/gds/share/proj', 'PROJ_NETWORK': 'ON'}; \
json.dump(spec, open(path, 'w'), indent=1)"

# uv/uvx launch the QGIS MCP server (`claude mcp add qgis -- uvx ...`), which
# talks to the QGIS plugin on the Windows host via host.docker.internal:9876.
# The MCP registration itself lives in ~/.claude, a persistent volume; only
# the uvx binary needs baking in. Pinned to match the rest of this file.
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /usr/local/bin/

USER jovyan

EXPOSE 8888