# AION Edge G1 — reproducible inputs / unverified image

**State:** source revisions selected and manifest validated; **no image has been built or booted**. The manifest now selects the experimental first-party `aion-edge-image`; no image build or boot has been verified.

## Hardware and release
- Raspberry Pi 4B, 64-bit (`raspberrypi4-64`).
- Yocto 6.0 Wrynose LTS series with separate source repos for BitBake 2.18, OpenEmbedded-Core, meta-yocto, meta-openembedded and meta-raspberrypi.
- Every source repo uses a 40-character Git commit pin in [`bsp/raspberrypi4-64.yml`](../bsp/raspberrypi4-64.yml), checked against the respective public upstream GitHub repo on 2026-11-13.
- The layers are not submodules and are not copied into this repository. Build tooling fetches them at the pinned revisions.
- **Important:** pinned Git layer commits do not automatically pin every recipe source download, compiler binary, model or firmware artifact. Verify `bitbake -e`, downloaded checksums, `buildhistory`, SBOM and full image provenance before declaring T005/AT-25 passed.

## Host preconditions
Use an isolated, **self-hosted Ubuntu Linux builder** with adequate disk/RAM, network access to upstream, and a compatible supported host distribution. Do not run a large BitBake build inside a busy production application runner. Confirm available resources first; a full clean Yocto build can use many tens of GB.

Install a supported `kas` version in a dedicated virtual environment. Review the requirements of the selected kas/Yocto versions; don't run build scripts as root. Avoid paid runners and hosted image builds.

## Build (not executed as part of this repository change)

```sh
python3 -m unittest discover -s tests -p 'test_edge_build_config.py' -v
kas checkout bsp/raspberrypi4-64.yml
kas build bsp/raspberrypi4-64.yml
```

Capture the resolved layer revisions, bitbake version, distro, `MACHINE`, `DISTRO`, compiler version, buildhistory and hashes of the produced artifacts. Output paths can vary with kas build configuration; examine the actual `tmp/deploy/images/raspberrypi4-64/` tree after build. The requested `wic.bz2` output must be independently verified before flashing.

## First device test (future, not completed)

1. Use a **spare** microSD; check target block device twice. **Never** flash an active disk or overwrite existing data automatically.
2. Record board revision, power supply, kernel/firmware versions and serial console output.
3. Validate boot offline, repeat three cold boots, confirm boot logs and absence of default remote access. AION agent, watchdog policy and updater are **not yet included**.
4. Save SHA256 hashes of image and test logs with the Git commit; reviewers must sign off AT-01..04 separately.

## Next integration
A first-party `meta-aion` image recipe and offline one-shot health script are included. BitBake parsing/build and Pi boot remain unverified; device identity, full health service and AI agent remain future work. No signing, secure boot or rollback is claimed at this point.
