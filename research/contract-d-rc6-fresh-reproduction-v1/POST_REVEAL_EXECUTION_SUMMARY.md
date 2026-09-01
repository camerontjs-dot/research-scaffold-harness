# Contract D RC6 Post-Reveal Execution Summary

- frozen independent prereveal result: **67 passed, 0 failed, 67 total**
- frozen independent post-reveal byte-identical rerun: **67 passed, 0 failed, 67 total**
- frozen reference suite: **71 passed, 0 failed**
- differential comparisons: **166**
- authority-relevant agreements: **159**
- authority-relevant disagreements: **0**
- public-authority ambiguities: **0**
- non-authority differences: **7**

Differential summary log SHA-256: `6353475de10bf201c01f0966b82c9b6b15643c5b2edf8d81e4bca023b0c6d078`.

The machine-readable per-case record is described by `DIFFERENTIAL_RESULTS/manifest.json` (content SHA-256 `e25776f270557beefe9b87a9e1e512ce7a8abaf561474210ffe09be35488225d`). Its nine SHA-256-bound JSON chunks are preserved together in deterministic `DIFFERENTIAL_RESULTS.tar.gz` (SHA-256 `032adea622510a506dde2d55229299c1ee4df568721f5ca104b21d9f32ce8368`). The exact orchestrator bytes are preserved as `POST_REVEAL_DIFFERENTIAL_HARNESS/run_differential.py.gz` (uncompressed SHA-256 `ead48542941734a21f083ca8af24101b22e76de885dd8342302729cee301aae8`); the independent drivers remain plain text in that harness directory.
