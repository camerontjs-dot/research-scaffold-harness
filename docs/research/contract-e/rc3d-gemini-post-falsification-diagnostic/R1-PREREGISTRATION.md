# RC3D Gemini post-falsification diagnostic R1 — apparatus-only correction

## Status

The first hosted diagnostic run (`33438328587`) is **INCONCLUSIVE** as a scientific diagnostic because the diagnostic script crashed before treatment evaluation.

Frozen Gemini integrity checks and the unchanged 42-test suite passed before the crash.

## Exact apparatus defect

`diagnose.py` assumed every non-omission semantic metamorphic variant stored its payload under a `result` key.

The already-revealed frozen RC3C corpus supports both:

- labeled variants with a `result` member; and
- direct payload objects.

The first run raised `KeyError: 'result'` while constructing the diagnostic corpus.

## Authorized R1 correction

R1 may only correct semantic-variant materialization to mirror the already-frozen comparison harness:

1. if `omit` is true, remove `result`;
2. else if a labeled variant contains `result`, use that payload;
3. otherwise treat the variant object itself as the opaque result payload.

No hypothesis, treatment transformation, frozen consumer/test file, eligibility rule, expected outcome, safety stop, or interpretation may change.

## Falsifier

If R1 control correspondence does not reproduce the terminal comparison for overlapping cases, stop and treat the diagnostic as invalid.

Any treatment authority-relevant false permit remains a diagnostic failure.
