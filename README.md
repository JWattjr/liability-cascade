# Liability Cascade

GenLayer validators judge each pipeline step against its received input and frozen duty. Deterministic code attributes the incident to the earliest proven violation, slashes only that operator's entire synthetic bond, and refunds all other operators. An earlier unclear or unavailable step blocks later attribution; deadline settlement then refunds every bond. Configured operators cannot report a failure or become the claimant through their configured address.

This release covers Phase 2 only: a local contract, direct-mode tests and lint. It has no deployment or remote repository. Bonds are synthetic ledger units, not GEN or real custody. Committed logs prove byte consistency, not truthful execution or authenticated handoff continuity. An unconfigured affiliated account can still claim; the operator-address restriction does not establish independence.

Read [the approved design](docs/DESIGN.md) and [the Phase 2 handoff](docs/PHASE2_HANDOFF.md) for the state machine, requirement coverage, exact verification results and limitations.

## Local verification

From the repository root, use the existing pinned environment without upgrades:

```powershell
& 'C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv\Scripts\genvm-lint.exe' check contracts/liability_cascade.py --json
& 'C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv\Scripts\python.exe' -m pytest --junitxml=verification/pytest.xml
```

The inherited Windows/legacy-SDK direct-runner shim in `tests/conftest.py` makes the installed `genlayer-test` work with SDK `v0.6.0-rc5`. Direct-mode execution and explicit invocations of captured validator callbacks are local tests with mocked web/model responses; they are not distributed network consensus. The contract itself starts with the frozen runner hash in the design, independently of the local direct-test SDK label.

## Constructor and lifecycle

`LiabilityCascade(pipeline_id: str, charter: str, steps_json: str, recording_deadline: int, adjudication_deadline: int)` freezes an ordered list of 2-5 distinct operators. Each JSON step has exactly `step_id`, `operator`, `duty`, and `bond_units`. Deadlines are UTC Unix seconds. Each operator deposits its own synthetic bond; only the final fully funding deposit activates recording. Each operator records its step once. After recording closes, a nonoperator reports; anyone may adjudicate. Timeout refunds are permissionless and need no external evidence.

The public methods are `deposit`, `record_step`, `report_failure`, `adjudicate`, `settle_deadline`, `get_state`, and `get_accounting`. Exact signatures and the requirement-to-test map are in the handoff. All writes reject terminal states. Views remain usable and expose the effective deadline window.
