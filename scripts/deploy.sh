#!/usr/bin/env bash
# Rebuild and restart Tapwise on the Pi with the latest code.
# Secrets come from ~/tapwise.env (outside the repo, never committed):
#   ADMIN_PASSWORD=...
#   ANTHROPIC_API_KEY=...      (optional: AI first review of visitor ideas)
# Port 8080 is for the home network and Tailscale only: Tapwise stays private (see CLAUDE.md).
set -euo pipefail
cd "$(dirname "$0")/.."

ENV_FILE="${TAPWISE_ENV:-$HOME/tapwise.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE. Create it once with ADMIN_PASSWORD=... (and ANTHROPIC_API_KEY=...), then chmod 600 it." >&2
  exit 1
fi

git pull --ff-only
docker build -q -t tapwise .
docker rm -f tapwise >/dev/null 2>&1 || true
docker run -d --name tapwise --restart unless-stopped \
  -p 8080:8000 \
  -v tapwise_data:/srv/app/data \
  --env-file "$ENV_FILE" \
  tapwise >/dev/null

for _ in $(seq 1 15); do
  if curl -fsS -o /dev/null http://localhost:8080/; then echo "Tapwise is up on :8080"; exit 0; fi
  sleep 1
done
echo "Tapwise didn't come up. Logs:" >&2
docker logs --tail 30 tapwise >&2
exit 1
