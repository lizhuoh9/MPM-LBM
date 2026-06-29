# Step150 Fluent Official Monitor Intake and Real Error Localization

- Status: `missing_official_monitor`
- Official reference loaded: `False`
- Solver monitor loaded: `True`
- Official monitor rows: `0`
- Official time range: `None` to `None`
- Official monitor hash: `None`
- Official monitor committed: `False`
- Schema valid: `False`
- Solver monitor rows: `26`
- Solver time range: `0.0` to `0.125`
- Step149 comparison ran: `False`
- Aligned sample count: `0`
- Error metrics present: `False`
- Solver bug hypotheses present: `False`
- Top bug category: `None`
- Recommended next step: `None`
- Validation claim allowed: `False`
- Selected96 execution allowed: `False`

Step150 validates the private official monitor intake and only runs Step149 comparison when the official and solver monitors are usable.
Private official CSV contents are not copied into committed artifacts; only metadata and hash are recorded.

Schema errors:
- official monitor is missing
