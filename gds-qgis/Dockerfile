# Pinned by digest so the build is reproducible. `latest` is a floating tag:
# it currently resolves to this same image (10.0, published 2023-10-19), but the
# upstream maintainer has newer images published (11.0gc, 2026-02-23_amd64) and
# could repoint `latest` at any time, silently changing this build.
# To upgrade deliberately: pick a tag, look up its digest, update both halves here.
FROM darribas/gds:10.0@sha256:3d1ea1df436f0790052cd768838e82b1b5c7e8f659e0bf9e9e78d10ea12f6419

USER root

RUN apt-get update && apt-get install -y \
    qgis python3-qgis python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# QGIS's Python bindings are installed against the system Python (apt),
# not the conda env Jupyter normally uses (different Python versions,
# so the compiled bindings can't be imported across envs). Register the
# system Python as its own Jupyter kernel instead.
RUN /usr/bin/python3 -m pip install --no-cache-dir ipykernel && \
    /usr/bin/python3 -m ipykernel install --prefix=/usr/local \
        --name qgis-py3 --display-name "Python 3 (QGIS)"

# The base image's JupyterLab config hardcodes a kernel whitelist that
# would otherwise hide qgis-py3 from the kernel picker.
RUN sed -i \
    "s/c.KernelSpecManager.whitelist = {'gds', 'ir'}/c.KernelSpecManager.whitelist = {'gds', 'ir', 'qgis-py3'}/" \
    /home/jovyan/.jupyter/jupyter_lab_config.py

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

USER jovyan

EXPOSE 8888