# Hardware and contract acceptance matrix

**Default verdict for all rows: TODO.** No device-level test has been executed.

| ID | Acceptance condition | Environment | Status |
|---|---|---|---|
| AT-01 | ARM64 image boots, produces serial evidence and valid manifest | Pi 4B | TODO |
| AT-02 | Offline boot supports essential I/O and logging | Pi 4B | TODO |
| AT-03 | Repeatedly crash AI service; core stays alive | Pi 4B | TODO |
| AT-04 | Malformed/missing model enters safe fallback | QEMU + Pi | TODO |
| AT-05 | Denied proposal causes zero executor calls | unit + Pi | TODO |
| AT-06 | Expired, replayed, mismatched device denied | unit + Pi | TODO |
| AT-07 | Authorized bounded proposal executes with verified postcondition | Pi | TODO |
| AT-08 | Unknown action/oversized payload rejected | fuzz + Pi | TODO |
| AT-09 | Audit and diagnostics contain no secrets | static + Pi | TODO |
| AT-10 | Over-budget inference request rejected | stress + Pi | TODO |
| AT-11 | Admission flood respects queue/RSS and control latency | stress + Pi | TODO |
| AT-12 | Restart inference under load; base services survive | Pi | TODO |
| AT-13 | Edge agent idle RSS <=80MiB and CPU <=3%/core averaged 15min | Pi | TODO |
| AT-14 | Tiny platform runtime SRAM <=64KiB, flash <=256KiB excluding OS/model | MCU | TODO |
| AT-15 | Signed update installs and confirms correct slot | Pi | TODO |
| AT-16 | Bad signature/board mismatch rejected before write | Pi | TODO |
| AT-17 | 10/10 interrupted updates recover known-good boot | Pi | TODO |
| AT-18 | Failed health check rolls back | Pi | TODO |
| AT-19 | Model digest/signature mismatch refuses load | unit + Pi | TODO |
| AT-20 | Downgrade protections accurately reflect board capability | Pi / MCU | TODO |
| AT-21 | Tiny/Edge capability fixtures match schema | MCU + Pi | TODO |
| AT-22 | Missing feature explicitly UNSUPPORTED | MCU + Pi | TODO |
| AT-23 | Tiny sensor path works without gateway | MCU | TODO |
| AT-24 | ISR never blocks on AI/transport | MCU | TODO |
| AT-25 | Pinned dependencies/source SHA records | build | TODO |
| AT-26 | SBOM/licenses/image checksum artifacts | build | TODO |
| AT-27 | Positive, negative and boundary contract suites | CI | TODO |
| AT-28 | 72-hour soak, no unexplained reset, logs retained | Pi | TODO |

Every PASS requires Git revision, board revision, toolchain, exact command, timestamp, logs, metrics, artifacts and reviewer. Host-side policy tests are preliminary evidence for AT-05/06/08 only; they cannot close those cross-environment tests.
