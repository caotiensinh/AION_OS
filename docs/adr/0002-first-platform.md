# ADR-0002: First executable platform targets

**Status:** Accepted for planning · 2026-11-13

## Decision
First physical Edge target is Raspberry Pi 4B (ARM64), built as a pinned Yocto-based embedded Linux image. Tiny will target one *explicitly selected* Cortex-M development board running Zephyr.

## Rationale
The Pi is broadly accessible and allows serial-console, networking, watchdog, resource and power-recovery testing without a proprietary BSP. Zephyr is suited to constrained real-time MCUs, but its exact board, flash and SRAM budget must be confirmed before choosing a port.

## Consequences
Linux and MCU variants have **different kernels** and separately validated update mechanisms. No default claim that a Raspberry Pi offers hardware-rooted secure boot, anti-rollback or A/B recovery. Evidence of real board capabilities is a prerequisite for such claims.
