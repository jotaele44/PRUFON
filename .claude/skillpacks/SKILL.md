---
name: ovnis-pr-unified-live-skillpack
description: "Compiled non-activating dispatch contract for shared and ovnis-pr capabilities."
version: 1.0.0
compatibility: claude
repository: ovnis-pr
---

# ovnis-pr Unified Live Skillpack

Pinned base: `400994dcc4e0e752c6ead984b0956f65adb0e153`.

## Execution contract

- Exact capability identifiers only; unknown identifiers fail closed.
- Runtime activation, automatic dispatch, live polling, notifications, external writes, promotion, control actions, merge, and release are disabled.
- Source module semantics remain cryptographically bound in `MANIFEST.json`; this file is the compiled live dispatcher.
- Repository-specific authority overrides shared defaults.

## Capability dispatch

| Capability | Module | Status | Preserved responsibility |
|---|---|---|---|
| `repo-state-reader` | `repository-governance` | `` |  |
| `repo-identity-guard` | `repository-governance` | `` |  |
| `branch-guard` | `repository-governance` | `` |  |
| `task-scope-guard` | `repository-governance` | `` |  |
| `git-action-guard` | `repository-governance` | `` |  |
| `skill-authoring-template` | `skill-lifecycle` | `` |  |
| `skill-package-builder` | `skill-lifecycle` | `` |  |
| `validation-gate-runner` | `validation-and-recovery` | `` |  |
| `failure-packet-builder` | `validation-and-recovery` | `` |  |
| `delta-reporter` | `reporting-and-receipts` | `` |  |
| `status-writer` | `reporting-and-receipts` | `` |  |
| `foia-correspondence-manager` | `foia-operations` | `` |  |
| `foia-request-sender` | `foia-operations` | `` |  |
| `ovnis-operator` | `orchestration-and-intake` | `` |  |
| `ovnis-case-intake` | `orchestration-and-intake` | `` |  |
| `ovnis-ledger-validator` | `evidence-integrity` | `` |  |
| `ovnis-case-deduplicator` | `evidence-integrity` | `` |  |
| `ovnis-provenance-reconstructor` | `evidence-integrity` | `` |  |
| `ovnis-evidence-tier-review` | `evidence-integrity` | `` |  |
| `ovnis-gap-sweep` | `gap-analysis` | `` |  |
| `ovnis-federation-export` | `federation-export` | `` |  |

## Required output fields

Every execution receipt must include `capability_id`, `repository`, `pinned_base_commit`, `inputs`, `outputs`, `validation`, `limitations`, `authority`, and `next_action`.

## Non-activation boundary

This binding does not invoke repository code. A later runtime adapter requires separate design, tests, review, and explicit authorization.
