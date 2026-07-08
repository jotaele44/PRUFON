"""Repo-specific maintenance adapter for ovnis-pr.

The generic maintenance core (models/state/detect/corrections/quarantine/report/
runner) now lives in the shared `prii_maintenance` package
(thehub-pr/packages/prii_maintenance, pinned via federation.json's setup
command). Only `adapters/local.py` — the ovnis-specific checks — stays
vendored here; it is passed into
`prii_maintenance.run_maintenance(..., local_checks=local.run_checks)`.
Run via ``python3 scripts/run_maintenance.py --repo ovnis-pr --mode audit``.
"""
