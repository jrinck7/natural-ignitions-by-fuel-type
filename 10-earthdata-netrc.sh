# Sourced by the docker-stacks entrypoint (start.sh runs everything in
# /usr/local/bin/before-notebook.d before JupyterLab launches).
#
# Start-Project2 bind-mounts the host's .netrc read-only at /run/secrets/netrc.
# It cannot be mounted straight to ~/.netrc: a Windows bind mount lands as
# root-owned mode 777, and Python's netrc module hard-rejects that with
#   NetrcParseError: ~/.netrc file owner (root) does not match current user
# So copy it into place as the notebook user and tighten the mode instead.
#
# No mount -> no-op, and earthaccess just prompts interactively as usual.
if [ -r /run/secrets/netrc ]; then
    cp /run/secrets/netrc "${HOME}/.netrc"
    chmod 600 "${HOME}/.netrc"
    echo "earthdata: credentials installed from mounted .netrc"
fi
