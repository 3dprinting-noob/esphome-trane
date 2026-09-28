#!/usr/bin/env bash
# Package the last N hours of the Trane raw capture for upload.
#
#   bash pi_trane_capture_pack.sh [hours]   # default 24
#
# Collects the hourly JSONL chunks (and any finished daily .tar.gz) modified in
# the last N hours into ~/trane-capture/upload/trane-capture-<stamp>-<N>h.tar.gz
# and prints the command to copy it to a Mac. Does not stop the recorder.
set -euo pipefail

HOURS="${1:-24}"
BASE="$HOME/trane-capture"
OUT="$BASE/upload"
mkdir -p "$OUT"

mapfile -t files < <(find "$BASE/data" -maxdepth 1 -type f \
  \( -name '*.jsonl' -o -name '*.tar.gz' \) -mmin "-$((HOURS * 60))" -printf '%f\n' | sort)
if [ "${#files[@]}" -eq 0 ]; then
  echo "No capture files from the last $HOURS h in $BASE/data." >&2
  exit 1
fi

name="trane-capture-$(date +%Y%m%d-%H%M)-${HOURS}h.tar.gz"
# The recorder is still appending to the current hour's chunk; tar a snapshot
# copy so it does not fail with "file changed as we read it".
snap=$(mktemp -d "$OUT/.snap.XXXXXX")
trap 'rm -rf "$snap"' EXIT
for f in "${files[@]}"; do cp -p "$BASE/data/$f" "$snap/$f"; done
tar -czf "$OUT/$name" -C "$snap" "${files[@]}"
tar -tzf "$OUT/$name" >/dev/null   # archive integrity check

echo "files: ${#files[@]}"
ls -lh "$OUT/$name"
sha256sum "$OUT/$name"
ip=$(hostname -I | awk '{print $1}')
echo
echo "On your Mac (Terminal):"
echo "  scp $(id -un)@$ip:$OUT/$name ~/Downloads/"
echo "Then attach ~/Downloads/$name in the chat, with the sha256 line above."
