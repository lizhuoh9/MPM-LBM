# Artifact Policy

Step reports, selected logs, and selected outputs are committed for reproducibility. Ad-hoc files should stay in scratch locations unless they become part of a documented step baseline.

## Committed Artifacts

Committed artifacts may include:

- `STEP*_REPORT.md`
- `logs/step*.log`
- `outputs/step*/` files required by contract tests
- documentation under `docs/`
- report drafts under `paper/`
- reproducibility configs under `configs/`

These files support review and regression checks.

## Scratch Artifacts

Use these paths for local scratch files:

```text
outputs/tmp/
outputs/scratch/
logs/tmp/
logs/scratch/
```

They are ignored by git and should not be cited as acceptance evidence.

## Heavy Experiments

Use these paths for ad-hoc large runs:

```text
outputs/experiments/
logs/experiments/
```

Do not commit ad-hoc large outputs unless they are documented step baselines.

## Manifest Fields

The Step 12 artifact manifest records:

```text
path
kind
extension
size_bytes
size_mb
is_large
```

The large-file threshold is:

```text
size_mb >= 5.0
```

The manifest is an audit aid. It does not delete or compress artifacts.
