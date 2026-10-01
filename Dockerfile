# Project 2 image: the gds-qgis environment plus NASA Earthdata access.
#
# Built FROM the local gds-qgis image rather than duplicating its build, so this
# only adds a ~100 MB layer instead of a second 15.7 GB image. The trade-off is
# that `gds-qgis:latest` is a floating local tag: rebuilding gds-qgis changes
# this image's base the next time this is rebuilt. Rebuild both together if
# you ever change the base.
#
# Requires gds-qgis:latest to exist locally. Build it first:
#   docker build -t gds-qgis:latest ./gds-qgis
FROM gds-qgis:latest

# --- Norton TLS interception workaround (optional, OFF by default) ---
# Only needed on a machine running Norton Web/Mail Shield, which MITM-
# intercepts TLS: it re-signs https connections with its own root, so
# pypi.org (and any other https host) presents a Norton-issued cert inside
# the container. Without this, that machine's pip/earthaccess calls fail with:
#   SSLError: certificate verify failed: unable to get local issuer certificate
#
# Teammates without Norton do not need this - leave NORTON_TLS_FIX unset and
# the block below is a no-op. See README.md for how to enable it.
#
# This trusts an interception root, so a build with this enabled must never
# be pushed to a shared registry.
ARG NORTON_TLS_FIX=false
USER root
# The bracket glob makes this COPY a no-op when the file isn't present, so
# builds without a local norton-root-ca.crt (i.e. everyone but its owner)
# still succeed. norton-root-ca.crt is gitignored - it is never committed.
COPY norton-root-ca.cr[t] /usr/local/share/ca-certificates/norton-root-ca.crt
# The sed and the leading newline are both load-bearing. The cert is exported
# from the Windows store, so it arrives CRLF, and appending it unnormalised
# glues "-----END CERTIFICATE-----" onto the bundle's last line and silently
# invalidates the whole append - pip then still fails with the same error.
# Norton's root is added to BOTH trust stores, which fixes two separate things:
#   - /usr/local/share/ca-certificates -> the system store, used by apt/curl
#   - certifi's cacert.pem             -> what pip AND earthaccess actually use
# The certifi half matters at RUNTIME, not just build time: earthaccess pulls
# granules over https from NASA Earthdata, and it would hit the same error.
RUN if [ "$NORTON_TLS_FIX" = "true" ]; then \
        sed -i 's/\r$//' /usr/local/share/ca-certificates/norton-root-ca.crt && \
        update-ca-certificates && \
        CERTIFI="$(/opt/conda/envs/gds/bin/python -c 'import certifi; print(certifi.where())')" && \
        printf '\n' >> "$CERTIFI" && \
        cat /usr/local/share/ca-certificates/norton-root-ca.crt >> "$CERTIFI"; \
    fi

USER jovyan

# earthaccess (NASA Earthdata search/download) goes into the conda `gds` env --
# the env behind the default `gds` Jupyter kernel, not the system Python that
# backs the QGIS kernel.
#
# numpy has to be pinned in the same command. earthaccess's own floor is
# numpy>=1.24, which is above the 1.23.4 the base image ships, so installing it
# unpinned drags in numpy 2.x. The pandas 2.1.1 and pyarrow 10.0.1 in that env
# are conda builds compiled against the numpy 1.x C ABI, and numpy 2 breaks
# them at import time:
#   ValueError: numpy.dtype size changed, may indicate binary incompatibility.
#              Expected 96 from C header, got 88 from PyObject
#
# The upper bound is <1.25, not <2, because numba 0.57.1 refuses to import on
# anything newer ("Numba needs NumPy 1.24 or less"). Between earthaccess's
# >=1.24 floor and numba's <1.25 ceiling, 1.24.x is the only window that
# satisfies both; it resolves to 1.24.4.
#
# --cert is required, not belt-and-braces: pip does NOT use the environment's
# certifi, it uses its own vendored copy at pip/_vendor/certifi/cacert.pem.
# Patching the env certifi above fixes earthaccess at runtime but leaves pip
# itself still failing, so pip is pointed at the system bundle that
# update-ca-certificates just refreshed.
RUN /opt/conda/envs/gds/bin/python -m pip install --no-cache-dir \
        --cert /etc/ssl/certs/ca-certificates.crt \
        "numpy>=1.24,<1.25" \
        earthaccess \
        jupytext

# Lets Start-Project2 supply Earthdata credentials from the host without baking
# them into the image (see the script for why it is a copy, not a direct mount).
USER root
COPY 10-earthdata-netrc.sh /usr/local/bin/before-notebook.d/10-earthdata-netrc.sh
RUN sed -i 's/\r$//' /usr/local/bin/before-notebook.d/10-earthdata-netrc.sh && \
    chmod 0755 /usr/local/bin/before-notebook.d/10-earthdata-netrc.sh

# Pre-create the Claude Code config dir so a fresh named volume mounted here
# inherits jovyan ownership instead of root.
RUN mkdir -p /home/jovyan/.claude && chown jovyan:users /home/jovyan/.claude

USER jovyan

EXPOSE 8888
