#!/usr/bin/env bash
# Install a long-running raw CAN recorder for the ESPHome Trane device on the
# kitchen panel Pi. It connects to the ESP32 over the ESPHome API (read-only,
# alongside Home Assistant) and writes hourly JSONL chunks plus daily .tar.gz
# archives, using uncharted9898's trane_log_collector.py (MIT), pinned below.
#
#   bash pi_trane_capture_install.sh [esp-address] [api-key]   # install + start (default 10.70.1.94)
#   bash pi_trane_capture_install.sh --status        # service state + data size
#   bash pi_trane_capture_install.sh --undo          # stop + remove service (keeps data)
#
# Run as kitchen-panel-pi; it asks for sudo only to install the systemd unit.
# Requires firmware profile CB1 (the device must log TRANE_CAN_LIVE lines).
# api-key: the device's `api: encryption: key:` value, if encryption is on.
# It is stored in ~/trane-capture/api.env (mode 600), not in the unit file.
set -euo pipefail

BASE="$HOME/trane-capture"
UNIT=/etc/systemd/system/trane-capture.service
PIN=3e5eee8a6b18fee0b758f6c4566b53ad44443ee7
URL="https://raw.githubusercontent.com/uncharted9898/esphome-trane/$PIN/tools/trane_log_collector.py"
SHA=d22d79721a6ce78bb4be3648d8ffe7ec581b78f54ec6aea51543c240d7e7aec5
MIN_FREE_MB=2048

status() {
  systemctl --no-pager status trane-capture.service 2>/dev/null | head -12 || echo "service not installed"
  echo "--- data"
  du -sh "$BASE/data" 2>/dev/null || echo "no data yet"
  latest=$(ls -1t "$BASE"/data/*.jsonl 2>/dev/null | head -1 || true)
  if [ -n "$latest" ]; then
    echo "current chunk: $latest"
    echo "CAN frames in it: $(grep -c '"type":"can"' "$latest" || true)"
    echo "JSON messages in it: $(grep -c '"type":"trane_json"' "$latest" || true)"
  fi
  df -h "$HOME" | tail -1
}

case "${1:-}" in
  --status) status; exit 0 ;;
  --undo)
    sudo systemctl disable --now trane-capture.service 2>/dev/null || true
    sudo rm -f "$UNIT"
    sudo systemctl daemon-reload
    echo "Service removed. Data kept in $BASE/data (delete with: rm -rf $BASE)"
    exit 0 ;;
esac

ESP="${1:-10.70.1.94}"
KEY="${2:-}"

# Reject typos such as "10.70.1.94E": an IPv4 address or a host name only.
if ! [[ "$ESP" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ || "$ESP" =~ ^[A-Za-z][A-Za-z0-9.-]*$ ]] \
   || [[ "$ESP" =~ ^[0-9.]+[A-Za-z] ]]; then
  echo "'$ESP' is not a valid IP address or host name." >&2
  exit 1
fi

free_mb=$(df -Pm "$HOME" | awk 'NR==2 {print $4}')
if [ "$free_mb" -lt "$MIN_FREE_MB" ]; then
  echo "Only ${free_mb} MB free; need ${MIN_FREE_MB} MB (about 80-100 MB per day compressed, more while the day is open)." >&2
  exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1 || ! python3 -c 'import ensurepip' 2>/dev/null; then
  echo "Installing python3-venv (sudo)..."
  sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv
fi

mkdir -p "$BASE/bin" "$BASE/data"
# Only set the variable when a key is given: an empty value would still be
# read as an (invalid) key by the collector.
( umask 077; if [ -n "$KEY" ]; then printf 'ESPHOME_NOISE_PSK=%s\n' "$KEY"; fi > "$BASE/api.env" )
curl -fsSL "$URL" -o "$BASE/bin/trane_log_collector.py.new"
got=$(sha256sum "$BASE/bin/trane_log_collector.py.new" | cut -d' ' -f1)
if [ "$got" != "$SHA" ]; then
  echo "Collector checksum mismatch ($got); not installing." >&2
  rm -f "$BASE/bin/trane_log_collector.py.new"; exit 1
fi
mv "$BASE/bin/trane_log_collector.py.new" "$BASE/bin/trane_log_collector.py"

[ -x "$BASE/venv/bin/python" ] || python3 -m venv "$BASE/venv"
"$BASE/venv/bin/pip" install -q --upgrade pip aioesphomeapi

sudo tee "$UNIT" >/dev/null <<EOF
[Unit]
Description=ESPHome Trane raw CAN recorder ($ESP)
After=network-online.target
Wants=network-online.target

[Service]
User=$(id -un)
WorkingDirectory=$BASE
EnvironmentFile=$BASE/api.env
ExecStart=$BASE/venv/bin/python $BASE/bin/trane_log_collector.py $ESP -o $BASE/data/trane.jsonl
Restart=always
RestartSec=15
Nice=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable trane-capture.service
# restart (not just start) so a re-run always applies the new address/key
sudo systemctl restart trane-capture.service
echo "Started. Checking in 30 s..."
sleep 30
status
echo
echo "If 'CAN frames' is 0: check the log with  journalctl -u trane-capture -n 30"
echo "  (an encryption/handshake error means the api key is missing or wrong)."
echo "Check again any time:  bash $0 --status"
echo "Remove:                bash $0 --undo"
