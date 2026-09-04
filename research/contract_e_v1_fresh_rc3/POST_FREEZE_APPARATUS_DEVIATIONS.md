# Contract E RC3 Fresh Independent Reproduction — Post-Freeze Apparatus Deviations

## Deviation 1 — missing sealed-evaluator runtime dependency

Classification: **APPARATUS_FAILURE_BEFORE_SCIENTIFIC_COMPARISON**

First post-freeze hosted comparison:

- run: `33890524011`
- job: `101080780257`
- reproduction head: `1ee3f040c48266ac087f48d909314efe14df696a`
- artifact: `9943626417`
- artifact ZIP SHA-256: `1f39bfcabbb7cb4b6f701f05d402c913b36e68fbc874e5b60af6a04bb687f055`

Observed sequence before failure:

1. frozen implementation/test Git blob checks passed;
2. frozen implementation/test SHA-256 checks passed;
3. all 33 frozen prereveal tests re-ran successfully;
4. exact Apparatus final-seal commit and sealed evaluator/reference/case blobs verified successfully;
5. the sealed evaluator then failed while importing its exact frozen predecessor reference with `ModuleNotFoundError: No module named 'rfc8785'`;
6. no hidden case was compared and no `RESULTS.json` was produced.

The failure therefore does not support or falsify fresh independent semantic recoverability.

### Permitted apparatus repair

Install exact public dependency `rfc8785==0.1.4` in the hosted post-freeze comparison environment before invoking the unchanged sealed evaluator. This dependency is required by the sealed Apparatus reference implementation and was an explicit public normative dependency of the pre-freeze specification.

The repair MUST NOT change:

- frozen fresh implementation blob `9019abd8ade820988de1f899b2ccef9e57e9a908`;
- frozen prereveal-test blob `818c44ad377d95344d158a7698d625548c0f5397`;
- Apparatus final seal `a678c73a661853a3a704666fc6bbf29fa378948f`;
- successor reference blob `00d4d8f078073388d751546c24678825b89a6402`;
- evaluator blob `5bba49c6a412c689232ea1315df0153455dd316f`;
- target-cardinality case blob `94b6d2c91b0124e7d9469ae24731945a60721ac8`;
- hidden cases, expected outputs, normative projection, or comparison rules.

Preserve the failed run and artifact as historical apparatus evidence. Do not overwrite or reinterpret them as a scientific result.
