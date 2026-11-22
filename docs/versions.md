# Versions and the update policy

Cascade reaches one engine through two doors — the official `relate` binary
and the embedded Python client (`relate_db`). This page records what the
repository is tested against and the only supported way to move to a newer
release. `make check-claims` enforces the pin below, so this page cannot
drift away from the Makefile unnoticed.

## What is pinned

| Component | Version | Where it lives |
| --- | --- | --- |
| Embedded engine (`relate_db`, PyPI) | **1.2.0** — `relate_db==1.2.0` | `RELATE_DB_VERSION` in the `Makefile`; installed by `make venv` |
| Official `relate` binary | not pinned by design | installed by the user with `install.sh`; `bin/relate` prefers it whenever the CPU supports it (AVX2) |
| Python (local build machine) | 3.14 | the machine that builds `store/catalog.rl` |
| Python (CI) | 3.12 | `.github/workflows/ci.yml` — the wheel is `cp39-abi3`, `Requires-Python >=3.9` |
| Browser engine (`@relate/relate-wasm`) | deferred with M3 | recorded when the live viewer lands |

The **contract is behavior, not the version number**: `make verify` (11 gates
plus the committed-store precheck), `make golden` (byte-exact demo/report/verify
outputs) and `make check-claims` are what proves a release works here. A newer
official binary on a judge's machine is acceptable as long as those gates pass
— which is exactly why they run on every push and pull request.

## Updating the engine

1. Bump `RELATE_DB_VERSION` in the `Makefile`.
2. Recreate the environment: `rm -rf .venv && make venv`.
3. Run the **full** battery on the new version — twice, because a single run
   can hit the documented transient class:
   `make verify` ×2, `make golden` ×2, `make check-claims`.
4. If an output changed **on purpose**, refresh the fixtures in the same
   commit (`make golden-update`, then review `git diff tests/golden`).
   If it changed **by accident**, that is a regression — do not refresh.
5. Update the table above with the new version; until the Makefile pin, this
   page and `.venv` agree, `check-claims` fails.
6. Push and wait for CI to be green **on the same commit**.

A dependency change and a feature change must stay separable in the history:
never bump the pin inside a commit that also changes behavior.
