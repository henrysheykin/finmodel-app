#!/usr/bin/env bash
# Container entry point for Railway (or any Docker host): one container runs
# migrations, the build worker and the web server. If either process exits, the
# container exits and the host restarts it.
set -euo pipefail
cd /srv/app

STORAGE_DIR="${STORAGE_DIR:-/data/storage}"
export STORAGE_DIR

if [ "$(id -u)" = "0" ]; then
  # Volumes are mounted owned by root. Hand the storage folder to the app user, then drop root.
  if [ "${STORAGE_BACKEND:-local}" = "local" ]; then
    mkdir -p "$STORAGE_DIR"
    chown -R app:app "$STORAGE_DIR"
  fi
  export HOME=/home/app
  exec setpriv --reuid=app --regid=app --init-groups "$0" "$@"
fi

python -m app.manage check
# go-live readiness in the deploy log; informational, never stops the container
python -m app.manage preflight || true
python -m app.manage migrate
# privacy policy retention (unpaid orders, old sign-in records); never stops the container
python -m app.manage purge || true

trap 'kill 0' TERM INT

python -m worker.main &
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" \
  --proxy-headers --forwarded-allow-ips='*' --no-server-header &

status=0
wait -n || status=$?
echo "a process exited (status $status); stopping the container" >&2
kill 0 2>/dev/null || true
exit "$status"
