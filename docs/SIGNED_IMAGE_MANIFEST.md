# Signed AION Edge image manifests (experimental)

AION provides an **offline detached Ed25519 signature** over a canonical JSON manifest describing a WIC image. It is not secure boot, no bootloader verifies it yet, it does not install or flash firmware and it has no anti-rollback protection. The signer accepts a private key **supplied outside Git**; the verifier requires an explicitly trusted public key. **Never commit production keys**.

## Image artifact fields

`schema_version=1`, `algorithm=Ed25519`, `board=raspberrypi4-64`, semantic version, image filename, image size, SHA256, source Git commit SHA and signer ID. Unknown fields, duplicate JSON keys, unsupported boards and noncanonical encodings are rejected.

## Example: local test keys only

```sh
mkdir -p .local-test-keys
openssl genpkey -algorithm ed25519 -out .local-test-keys/dev-private.pem
openssl pkey -in .local-test-keys/dev-private.pem -pubout -out .local-test-keys/dev-public.pem

python3 tools/aion_image_manifest.py sign \
  --image /path/to/aion-edge-image-raspberrypi4-64.wic.bz2 \
  --version 0.1.0 --build-sha "$(git rev-parse HEAD)" \
  --signer aion-dev --private-key .local-test-keys/dev-private.pem \
  --manifest /tmp/aion-image.manifest.json \
  --signature /tmp/aion-image.manifest.sig

python3 tools/aion_image_manifest.py verify \
  --image /path/to/aion-edge-image-raspberrypi4-64.wic.bz2 \
  --expected-signer aion-dev --expected-board raspberrypi4-64 \
  --public-key .local-test-keys/dev-public.pem \
  --manifest /tmp/aion-image.manifest.json \
  --signature /tmp/aion-image.manifest.sig
```

Delete the development key after testing; use a separately managed, protected production signing system. CI generates only ephemeral test keys and must never use real signing secrets or claim a release is securely booted.

## Acceptance boundary

A passing `test_signed_manifest.py` demonstrates file integrity and detached signature verification with temporary keys. It does **not** establish the identity of a deployed board, secure update staging, post-boot attestation, recovery, anti-rollback or Pi image acceptance. **T006 is partial pending release integration; T007/AT-01..04 remain TODO.**
