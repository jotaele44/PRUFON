---
name: ovnis-pr-unified-live-skillpack
description: "Compiled non-activating dispatch contract."
version: 1.0.1
compatibility: claude
repository: ovnis-pr
---

# ovnis-pr Unified Live Skillpack

Pinned base: `400994dcc4e0e752c6ead984b0956f65adb0e153`.

## Execution contract

- Exact identifiers only; unknown identifiers fail closed.
- Runtime activation, automatic dispatch, polling, notifications, writes, promotion, control, merge, and release are disabled.
- Module and package hashes remain in `MANIFEST.json`.

## Capability dispatch

| Capability | Module | Status | Preserved responsibility |
|---|---|---|---|
<a id="capability-repo-state-reader"></a>| `repo-state-reader` | `repository-governance` | `preserved-active-contract` | Preserve `repo-state-reader` under `repository-governance`. |
<a id="capability-repo-identity-guard"></a>| `repo-identity-guard` | `repository-governance` | `preserved-active-contract` | Preserve `repo-identity-guard` under `repository-governance`. |
<a id="capability-branch-guard"></a>| `branch-guard` | `repository-governance` | `preserved-active-contract` | Preserve `branch-guard` under `repository-governance`. |
<a id="capability-task-scope-guard"></a>| `task-scope-guard` | `repository-governance` | `preserved-active-contract` | Preserve `task-scope-guard` under `repository-governance`. |
<a id="capability-git-action-guard"></a>| `git-action-guard` | `repository-governance` | `preserved-active-contract` | Preserve `git-action-guard` under `repository-governance`. |
<a id="capability-skill-authoring-template"></a>| `skill-authoring-template` | `skill-lifecycle` | `preserved-active-contract` | Preserve `skill-authoring-template` under `skill-lifecycle`. |
<a id="capability-skill-package-builder"></a>| `skill-package-builder` | `skill-lifecycle` | `preserved-active-contract` | Preserve `skill-package-builder` under `skill-lifecycle`. |
<a id="capability-validation-gate-runner"></a>| `validation-gate-runner` | `validation-and-recovery` | `preserved-active-contract` | Preserve `validation-gate-runner` under `validation-and-recovery`. |
<a id="capability-failure-packet-builder"></a>| `failure-packet-builder` | `validation-and-recovery` | `preserved-active-contract` | Preserve `failure-packet-builder` under `validation-and-recovery`. |
<a id="capability-delta-reporter"></a>| `delta-reporter` | `reporting-and-receipts` | `preserved-active-contract` | Preserve `delta-reporter` under `reporting-and-receipts`. |
<a id="capability-status-writer"></a>| `status-writer` | `reporting-and-receipts` | `preserved-active-contract` | Preserve `status-writer` under `reporting-and-receipts`. |
<a id="capability-foia-correspondence-manager"></a>| `foia-correspondence-manager` | `foia-operations` | `preserved-active-contract` | Preserve `foia-correspondence-manager` under `foia-operations`. |
<a id="capability-foia-request-sender"></a>| `foia-request-sender` | `foia-operations` | `preserved-active-contract` | Preserve `foia-request-sender` under `foia-operations`. |
<a id="capability-ovnis-operator"></a>| `ovnis-operator` | `orchestration-and-intake` | `preserved-active-contract` | Preserve `ovnis-operator` under `orchestration-and-intake`. |
<a id="capability-ovnis-case-intake"></a>| `ovnis-case-intake` | `orchestration-and-intake` | `preserved-active-contract` | Preserve `ovnis-case-intake` under `orchestration-and-intake`. |
<a id="capability-ovnis-ledger-validator"></a>| `ovnis-ledger-validator` | `evidence-integrity` | `preserved-active-contract` | Preserve `ovnis-ledger-validator` under `evidence-integrity`. |
<a id="capability-ovnis-case-deduplicator"></a>| `ovnis-case-deduplicator` | `evidence-integrity` | `preserved-active-contract` | Preserve `ovnis-case-deduplicator` under `evidence-integrity`. |
<a id="capability-ovnis-provenance-reconstructor"></a>| `ovnis-provenance-reconstructor` | `evidence-integrity` | `preserved-active-contract` | Preserve `ovnis-provenance-reconstructor` under `evidence-integrity`. |
<a id="capability-ovnis-evidence-tier-review"></a>| `ovnis-evidence-tier-review` | `evidence-integrity` | `preserved-active-contract` | Preserve `ovnis-evidence-tier-review` under `evidence-integrity`. |
<a id="capability-ovnis-gap-sweep"></a>| `ovnis-gap-sweep` | `gap-analysis` | `preserved-active-contract` | Preserve `ovnis-gap-sweep` under `gap-analysis`. |
<a id="capability-ovnis-federation-export"></a>| `ovnis-federation-export` | `federation-export` | `preserved-active-contract` | Preserve `ovnis-federation-export` under `federation-export`. |

## Required receipt fields

`capability_id`, `repository`, `pinned_base_commit`, `inputs`, `outputs`, `validation`, `limitations`, `authority`, and `next_action`.

## Non-activation boundary

This binding does not invoke repository code. Runtime adapters require separate authorization.
