#!/usr/bin/env bash
set -u

ROOT="$(pwd)"
WORK="${RUNNER_TEMP:-/tmp}/contract-d-rc5-post-reveal"
REF="$WORK/reference"
IND="$WORK/independent"
rm -rf "$WORK"
mkdir -p "$REF/tests" "$REF/fixtures" "$IND"

REF_BASE="https://raw.githubusercontent.com/camerontjs-dot/apparatus-contracts/f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8/research/contract-d-independent-authority-rc5/candidate"
IND_BASE="https://raw.githubusercontent.com/camerontjs-dot/research-scaffold-harness/54c78823e289a3d0d490189d1ffafc25d127d585/research/contract-d-rc5-fresh-reproduction-v1"

blob_fetch() {
  local url="$1" dest="$2" expected="$3"
  mkdir -p "$(dirname "$dest")"
  curl --fail --location --silent --show-error "$url" -o "$dest" || return 20
  local actual
  actual="$(git hash-object "$dest")"
  echo "BLOB $(basename "$dest") $actual"
  if [[ "$actual" != "$expected" ]]; then
    echo "REFERENCE_BLOB_MISMATCH expected=$expected actual=$actual path=$dest"
    return 21
  fi
}

# Newly authorized reference files, exact frozen identities.
blob_fetch "$REF_BASE/contract_d_core.py" "$REF/contract_d_core.py" "6c3fbe3e6ac6effe0a4ed66f17145ffd32705edf" || exit $?
blob_fetch "$REF_BASE/contract_d_validate.py" "$REF/contract_d_validate.py" "8cc6d81515d7c5b0a86df163a38d1c12931f897f" || exit $?
blob_fetch "$REF_BASE/contract_d_consume.py" "$REF/contract_d_consume.py" "42536aaac5acd953f150a87891a70e9c194b7aaf" || exit $?
blob_fetch "$REF_BASE/requirements.txt" "$REF/requirements.txt" "9bc3e4b733b2963a79a756a696eeafc92b532634" || exit $?
blob_fetch "$REF_BASE/tests/test_rc5.py" "$REF/tests/test_rc5.py" "1f8470b4f6efea5bec3260cd575a626e8242c045" || exit $?
blob_fetch "$REF_BASE/tests/test_rc5_expectation_hardening.py" "$REF/tests/test_rc5_expectation_hardening.py" "9d02b269fe83ba79ded16d154f59fed0267e87c5" || exit $?
blob_fetch "$REF_BASE/tests/test_rc5_jcs_vectors.py" "$REF/tests/test_rc5_jcs_vectors.py" "35a01f918fc4b993e5367d7878e5b11a90bcd428" || exit $?

# Already-public authority required by the frozen reference suite.
blob_fetch "$REF_BASE/effect-registry.json" "$REF/effect-registry.json" "53df222ca439248a44029e02a662825235db892f" || exit $?
blob_fetch "$REF_BASE/fixtures/valid.json" "$REF/fixtures/valid.json" "f03b16f41f119a8a485e0f7ac3dac30f509c40b9" || exit $?
blob_fetch "$REF_BASE/fixtures/invalid.json" "$REF/fixtures/invalid.json" "8c3fd3370d7f96a7cb162d8acfeacb7b189b4d86" || exit $?
blob_fetch "$REF_BASE/conformance-cases.json" "$REF/conformance-cases.json" "29825bfa89b2b91bfa9e457c001e2c869a3649a4" || exit $?

# Immutable independent objects under evaluation.
blob_fetch "$IND_BASE/contract_d_rc5.js" "$IND/contract_d_rc5.js" "e60d3a15da98e32a732f1860808b8dda7ba7f3ee" || exit $?
blob_fetch "$IND_BASE/test_contract_d_rc5.js" "$IND/test_contract_d_rc5.js" "102327e348364c62454369d2614ca98ce80d94c5" || exit $?

echo "RUNTIME_PYTHON=$(python --version 2>&1)"
echo "RUNTIME_NODE=$(node --version 2>&1)"
echo "PIP_VERSION=$(python -m pip --version 2>&1)"

python -m pip install --disable-pip-version-check --quiet -r "$REF/requirements.txt" pytest
PIP_STATUS=$?
if [[ $PIP_STATUS -ne 0 ]]; then
  echo "DEPENDENCY_INSTALL_FAILED status=$PIP_STATUS"
  exit $PIP_STATUS
fi

echo "DEPENDENCY_RFC8785=$(python - <<'PY'
import importlib.metadata
print(importlib.metadata.version('rfc8785'))
PY
)"
echo "TEST_RUNNER=$(python -m pytest --version 2>&1)"

echo "REFERENCE_SUITE_COMMAND=python -m pytest -q tests/test_rc5.py tests/test_rc5_expectation_hardening.py tests/test_rc5_jcs_vectors.py"
pushd "$REF" >/dev/null
set +e
REFERENCE_OUTPUT="$(python -m pytest -q tests/test_rc5.py tests/test_rc5_expectation_hardening.py tests/test_rc5_jcs_vectors.py 2>&1)"
REFERENCE_STATUS=$?
set -e
popd >/dev/null
printf '%s\n' "$REFERENCE_OUTPUT"
echo "REFERENCE_SUITE_EXIT=$REFERENCE_STATUS"

export REF_DIR="$REF"
export NODE_MODULE="$IND/contract_d_rc5.js"
export NODE_ADAPTER="$ROOT/research/contract-d-rc5-fresh-reproduction-v1/post_reveal/node_adapter.js"
set +e
DIFF_OUTPUT="$(python "$ROOT/research/contract-d-rc5-fresh-reproduction-v1/post_reveal/differential.py" 2>&1)"
DIFF_STATUS=$?
set -e
printf '%s\n' "$DIFF_OUTPUT"
echo "DIFFERENTIAL_EXIT=$DIFF_STATUS"

# A reference-suite failure is preserved, but comparison still runs as required.
if [[ $REFERENCE_STATUS -ne 0 ]]; then
  exit $REFERENCE_STATUS
fi
exit $DIFF_STATUS
