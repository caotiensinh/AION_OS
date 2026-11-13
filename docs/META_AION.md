# meta-aion — first-party Edge layer (unbooted)

This first-party Wrynose-compatible Yocto layer defines the experimental `aion-edge-image` and a local one-shot health reporter. **No BitBake parse, image build, ARM boot or hardware acceptance has passed.** This is not a secure production OS.

The reporter runs once at boot as an unprivileged systemd service, reads only `/proc/uptime` and selected memory metrics, prints a diagnostic and exits. There is no networking, LLM, permanent agent or privileged actuator.

## Build in an isolated self-hosted Linux workspace

From the AION_OS repository checkout root, with a compatible kas/Yocto host environment and ample free disk:

```sh
python3 -m unittest discover -s tests -p 'test_meta_aion.py' -v
export KAS_WORK_DIR="$(pwd)"
kas checkout bsp/raspberrypi4-64.yml
kas build bsp/raspberrypi4-64.yml
```

Check that the local `meta-aion` layer resolves to the checkout and that BitBake sees `aion-edge-image`. Review all source hashes and build logs; the upstream source pinning is not yet complete provenance. Never flash an active drive: use a spare microSD, inspect the device node, record SHA256 of image, serial output and target board revision.

Target acceptance: repeat cold boots offline, verify `journalctl -u aion-health`, test missing procfs fallback, measure RSS/CPU and confirm AI-disabled behavior. Identity, watchdog supervision, signed updates and hardware root of trust are NOT implemented.
