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

## Automated validation and controlled build

The lightweight CI now uses pinned kas 5.5 to parse the real kas YAML, in addition to host code tests. This catches malformed kas schema before an expensive image build. It does **not** validate BitBake recipes.

A separate `AION Edge self-hosted build` workflow is strictly manual (`workflow_dispatch`) and runs only on a Linux x86-64 self-hosted runner. The `validate` mode checks the manifest without building; the `build` mode requires at least 120 GiB free disk and 16 GiB RAM and is subject to a 240-minute cap. This workflow has not been triggered and does not mean a runner is currently available.

For build evidence, inspect its artifacts and actual BitBake logs. Never claim Raspberry Pi boot PASS before a separately recorded physical serial-console test.

## BitBake parse gate

The self-hosted workflow now supports three *manually selected* modes:

| Mode | Expected work | Minimum resources |
|---|---|---|
| `validate` | parse kas YAML and validate pinned revisions; no layer clone | 1 GiB free and 1 GiB RAM |
| `parse` | checkout upstream layers, run `bitbake -p`, then evaluate `bitbake -e aion-edge-image` | 30 GiB free and 8 GiB RAM |
| `build` | perform the same metadata parse, then compile the target image | 120 GiB free and 16 GiB RAM |

These are preliminary admission limits, not promised sufficient resources for every build host. A parse PASS proves recipe metadata resolves under the selected Yocto toolchain; it does **not** produce an image or establish bootability. The runner must already exist in this repository with labels `self-hosted`, `linux`, `x64`; this connection cannot confirm runner registration or remotely dispatch this workflow.

Do not use the GPIO Raspberry Pi or a production server for the full build without isolating capacity. Workflow artifacts omit large images and raw BitBake logs; preserve reviewed diagnostic logs privately when investigating failures.

## Mandatory post-build artifact acceptance

The workflow now treats full BitBake success as **necessary but not sufficient**. A build PASS also requires `tests/verify_edge_artifacts.py` to find **one distinct fresh, non-empty** `aion-edge-image-*.wic.bz2` in the expected deploy folder, plus a fresh image package manifest explicitly containing `aion-health`. Stale images, missing manifests, ambiguous outputs and symlinks escaping the deployment tree are rejected.

If accepted, it creates `aion-image-evidence.json` containing image and manifest SHA256, size and scope. This is an inventory checksum, not a cryptographic signature or proof of physical boot. No artifact is automatically flashed. Test images must still boot on the Pi 4B before T007 or AT-01 is accepted.

## Layer parser regression correction (2026-11-13)

A source audit discovered that `BBFILE_PATTERN_aion` was assigned with the deferred operator `=`. Because BitBake's `LAYERDIR` variable changes while parsing subsequent layers, the expression could be evaluated against another layer's directory, so the AION recipe files could fail to be assigned to the `aion` collection. It now uses immediate `:=` expansion and explicitly declares `LAYERDEPENDS_aion = "core"`. This follows the Yocto layer configuration recommendation. The host regression test checks this assignment; real `bitbake -p` confirmation still remains pending.
