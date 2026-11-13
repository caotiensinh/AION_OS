SUMMARY = "AION OS Edge experimental ARM64 image"
DESCRIPTION = "Minimal offline-first image with local boot-time health snapshot, no AI runtime."
LICENSE = "MIT"
require recipes-core/images/core-image-minimal.bb
IMAGE_INSTALL:append = " aion-health"
IMAGE_FEATURES:remove = "debug-tweaks empty-root-password allow-empty-password allow-root-login"
