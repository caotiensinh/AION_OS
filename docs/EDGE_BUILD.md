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

## Lightweight real metadata parse on a standard public runner

A dedicated [G1 BitBake metadata parse](../.github/workflows/g1-bitbake-parse.yml) workflow on ordinary `ubuntu-22.04` is triggered only by pull requests changing BSP/Yocto layer metadata or via explicit dispatch. Standard GitHub-hosted runners are free for public repositories (not larger runners). The job has a 25-minute timeout, does **not** build an image and refuses to proceed if it lacks 8 GiB free disk or 4 GiB RAM.

It installs the pinned `kas==5.5`, checks out pinned upstream layers, executes `bitbake -p`, evaluates `aion-health` and `aion-edge-image` metadata, and checks the fully expanded `IMAGE_INSTALL` includes `aion-health`. Record its actual Actions run status; workflow source alone is **not** proof of BitBake parse PASS. Physical boot and image artifact gates remain separate.

### Metadata parse failure diagnosed on Yocto 6.0

The first **real** metadata run reached BitBake on Ubuntu 22.04 but failed when parsing `aion-health_0.1.0.bb`: `Using S = ${WORKDIR} is no longer supported`. This is an actual recipe defect exposed by BitBake (not by kas dump). Replaced `S` with `"${UNPACKDIR}"` and moved both installed source paths to `"${S}/..."` in accordance with Yocto's single-file recipe guidance. A host regression assertion prevents reintroducing `S = ${WORKDIR}`. The fix was validated by a subsequent actual BitBake parse on commit `4f93ba67c3994627db8aa944b1e6fb9ec94c6d37`, run `43394533686` (PASS).

### Verified G1 metadata outcome

Real BitBake ran on a free standard Ubuntu 22.04 runner at PR #9. It successfully parsed **2,052 recipes**, discovered **3,575 targets**, and reported **0 parse errors**; `IMAGE_INSTALL="packagegroup-core-boot  aion-health"` was confirmed. [GitHub Actions run 43394533686](https://github.com/caotiensinh/AION_OS/actions/runs/43394533686). See [durable evidence](../specs/001-ai-native-platform/evidence/G1-metadata-2026-11-13.md). **No image binary or Pi boot was produced.**

## Controlled full-image experiment on a free public runner

A [G1 hosted image build workflow](../.github/workflows/g1-hosted-image.yml) performs a **real** `kas build` on a standard Ubuntu 22.04 runner in this public repository. For resource containment the Yocto manifest limits BitBake tasks and Make jobs to 2 and enables `rm_work`; full build is denied below 75 GiB free or 12 GiB RAM. This is an experiment, **not a supported build environment or guaranteed resource budget**.

Unlike earlier metadata-only jobs, this workflow invokes the target image compilation, then requires a fresh non-empty `aion-edge-image-*.wic.bz2` and a matching package manifest with `aion-health`. If both pass it uploads the actual compressed image (seven-day retention) and JSON SHA256 evidence. A failed or timed-out job is **not** T007 PASS; read logs and fix the root cause. Even a successful build is not hardware AT-01: physical Raspberry Pi serial-console boot remains independent.

A single integration pull request on branch `feat/g1-hosted-image-build` triggers the experimental hosted build; later invocations must be manually dispatched. The workflow has no flash or destructive disk-write commands. Do not confuse GitHub Actions artifact storage with a permanent release or secure update channel.
