# CSCI502 Project 2

Adds NASA Earthdata access (`earthaccess`) on top of the shared `gds-qgis:latest`
base image.

```
docker build -t gds-qgis:latest ./gds-qgis
docker build -t gds-project2 .
```

## Troubleshooting: pip/earthaccess SSL errors (Norton only)

If your build or the running container fails with:

```
SSLError: certificate verify failed: unable to get local issuer certificate
```

this means something on your machine is intercepting TLS traffic (commonly
Norton's Web/Mail Shield). It re-signs `https` connections with its own root
certificate, which the container doesn't trust by default.

This is **not** something most teammates will hit, so it's off by default,
and the certificate itself is gitignored - it's specific to your machine and
is never committed.

1. Export your interceptor's root CA certificate as `norton-root-ca.crt`
   (PEM format) into this folder.
2. Build with the workaround turned on:
   ```
   docker build --build-arg NORTON_TLS_FIX=true -t gds-project2 .
   ```

Do not push an image built this way to a shared registry — it trusts a
TLS-interception root that only makes sense on the machine that generated it.
