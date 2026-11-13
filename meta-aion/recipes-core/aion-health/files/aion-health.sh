#!/bin/sh
# Offline, unprivileged, one-shot diagnostic. No network or serial/secret collection.
set -eu
if [ ! -r /proc/uptime ] || [ ! -r /proc/meminfo ]; then
    echo 'aion_health status=unavailable reason=procfs_missing'
    exit 1
fi
uptime_seconds=$(cut -d' ' -f1 /proc/uptime)
mem_total_kib=$(awk '$1 == "MemTotal:" {print $2; exit}' /proc/meminfo)
mem_available_kib=$(awk '$1 == "MemAvailable:" {print $2; exit}' /proc/meminfo)
if [ -z "$uptime_seconds" ] || [ -z "$mem_total_kib" ] || [ -z "$mem_available_kib" ]; then
    echo 'aion_health status=unavailable reason=metrics_missing'
    exit 1
fi
printf 'aion_health status=ok uptime_seconds=%s mem_total_kib=%s mem_available_kib=%s\n' \
    "$uptime_seconds" "$mem_total_kib" "$mem_available_kib"
