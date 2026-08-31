'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const {
  ContractDError,
  canonicalDecisionBytes,
  canonicalJsonBytes,
  consume,
  parseDecisionBytes,
  parseJsonBytes,
  semanticIdentity,
  validateDecision,
} = require('./contract_d_rc5');

const H = 'sha256:' + '1'.repeat(64);

function clone(value) {
  return structuredClone(value);
}

const sourceAuditClear = {
  contract_d_version: '0.3.0-rc5',
  effect: { params: { scope: 'claim' }, type: 'knowledge.add_verified_tag', version: '1' },
  evaluation: { disposition: 'clear', state: 'completed' },
  input_authority: { id: 'c1', immutable_id: 'result-set:' + 'a'.repeat(64), kind: 'contract-c' },
  metadata: { diagnostics: { trace: 'fixture' }, explanation: 'Research fixture', reason_codes: ['policy_clear'] },
  policy: { id: 'mainframe.source-audit', version: '1' },
  target: { content_sha256: H, id: 'k1', kind: 'knowledge' },
};

const citationClear = {
  contract_d_version: '0.3.0-rc5',
  effect: { type: 'knowledge.cite_as_evidence', version: '1' },
  evaluation: { disposition: 'clear', state: 'completed' },
  input_authority: { id: 'c2', immutable_id: 'result-set:' + 'b'.repeat(64), kind: 'contract-c' },
  policy: { id: 'mainframe.citation-use', version: '1' },
  target: { content_sha256: H, id: 'k2', kind: 'knowledge' },
};

const taskDispatchClear = {
  contract_d_version: '0.3.0-rc5',
  effect: { type: 'task.dispatch', version: '1' },
  evaluation: { disposition: 'clear', state: 'completed' },
  input_authority: { id: 'r1', immutable_id: 'task-review:' + 'c'.repeat(64), kind: 'task-review' },
  policy: { id: 'mainframe.task-dispatch', version: '1' },
  target: { content_sha256: H, id: 't1', kind: 'task' },
};

const completedHold = {
  contract_d_version: '0.3.0-rc5',
  effect: { type: 'knowledge.add_verified_tag', version: '1' },
  evaluation: { disposition: 'hold', state: 'completed' },
  input_authority: { id: 'c3', immutable_id: 'result-set:' + 'd'.repeat(64), kind: 'contract-c' },
  policy: { id: 'mainframe.source-audit', version: '1' },
  target: { content_sha256: H, id: 'k3', kind: 'knowledge' },
};

const evaluationFailed = {
  contract_d_version: '0.3.0-rc5',
  evaluation: { state: 'failed' },
  input_authority: { id: 'c4', immutable_id: 'result-set:' + 'e'.repeat(64), kind: 'contract-c' },
  metadata: { reason_codes: ['policy_evaluation_failure'] },
  policy: { id: 'mainframe.source-audit', version: '1' },
  target: { content_sha256: H, id: 'k4', kind: 'knowledge' },
};

function expectationFor(decision, requestedOperation, effectParamsMarker = Symbol.for('absent')) {
  const out = {
    input_authority: clone(decision.input_authority),
    policy: clone(decision.policy),
    requested_operation: requestedOperation,
    target: clone(decision.target),
  };
  if (effectParamsMarker !== Symbol.for('absent')) out.effect_params = effectParamsMarker;
  return out;
}

function outcome(decision, expectation) {
  return consume(decision, expectation).outcome;
}

function assertContractError(fn, code) {
  assert.throws(fn, (err) => err instanceof ContractDError && err.code === code);
}

function nestedContainers(count) {
  let value = { leaf: null };
  for (let i = 1; i < count; i += 1) value = { child: value };
  return value;
}

test('exact version accepted; future, case-varied, aliased, and numeric versions rejected', () => {
  assert.doesNotThrow(() => validateDecision(sourceAuditClear));
  for (const bad of ['0.3.0-rc6', '0.3.0-RC5', 'rc5', 0.3]) {
    const d = clone(sourceAuditClear);
    d.contract_d_version = bad;
    assertContractError(() => validateDecision(d), 'unsupported_version');
  }
});

test('source-audit CLEAR is candidate_for_authorization', () => {
  assert.equal(outcome(sourceAuditClear, expectationFor(sourceAuditClear, 'knowledge.add_verified_tag', { scope: 'claim' })), 'candidate_for_authorization');
});

test('citation-use CLEAR is candidate_for_authorization', () => {
  assert.equal(outcome(citationClear, expectationFor(citationClear, 'knowledge.cite_as_evidence')), 'candidate_for_authorization');
});

test('task-dispatch CLEAR is candidate_for_authorization', () => {
  assert.equal(outcome(taskDispatchClear, expectationFor(taskDispatchClear, 'task.dispatch')), 'candidate_for_authorization');
});

test('completed HOLD remains distinct from evaluation failure', () => {
  assert.equal(outcome(completedHold, expectationFor(completedHold, 'knowledge.add_verified_tag')), 'hold');
  assert.equal(outcome(evaluationFailed, expectationFor(evaluationFailed, 'knowledge.add_verified_tag')), 'evaluation_failed');
});

test('wrong requested operation makes both CLEAR and HOLD not applicable', () => {
  assert.equal(outcome(sourceAuditClear, expectationFor(sourceAuditClear, 'task.dispatch')), 'not_applicable');
  assert.equal(outcome(completedHold, expectationFor(completedHold, 'task.dispatch')), 'not_applicable');
});

test('upstream, policy, and target substitutions are non-applicable', () => {
  const base = expectationFor(sourceAuditClear, 'knowledge.add_verified_tag');
  const variations = [
    ['upstream immutable replay', (e) => { e.input_authority.immutable_id = 'result-set:' + 'f'.repeat(64); }],
    ['upstream kind substitution', (e) => { e.input_authority.kind = 'other'; }],
    ['policy substitution', (e) => { e.policy.id = 'other.policy'; }],
    ['policy version substitution', (e) => { e.policy.version = '2'; }],
    ['target id substitution', (e) => { e.target.id = 'k2'; }],
    ['target content replay', (e) => { e.target.content_sha256 = 'sha256:' + '2'.repeat(64); }],
  ];
  for (const [name, mutate] of variations) {
    const e = clone(base);
    mutate(e);
    assert.equal(outcome(sourceAuditClear, e), 'not_applicable', name);
  }
});

test('absent, empty, and explicit requested params follow constraint semantics and safe default normalization', () => {
  const d = clone(sourceAuditClear);
  delete d.effect.params;
  const noParams = expectationFor(d, 'knowledge.add_verified_tag');
  const empty = expectationFor(d, 'knowledge.add_verified_tag', {});
  const explicitDefault = expectationFor(d, 'knowledge.add_verified_tag', { scope: 'claim' });
  const conflict = expectationFor(d, 'knowledge.add_verified_tag', { scope: 'object' });
  assert.equal(outcome(d, noParams), 'candidate_for_authorization');
  assert.equal(outcome(d, empty), 'candidate_for_authorization');
  assert.equal(outcome(d, explicitDefault), 'candidate_for_authorization');
  assert.equal(outcome(d, conflict), 'not_applicable');

  const explicit = clone(d);
  explicit.effect.params = { scope: 'claim' };
  assert.equal(semanticIdentity(d), semanticIdentity(explicit));
});

test('metadata is excluded from semantic identity', () => {
  const a = clone(sourceAuditClear);
  const b = clone(sourceAuditClear);
  b.metadata = { diagnostics: { trace: 'different', nested: [1, true, null] }, explanation: 'Changed', reason_codes: ['other'] };
  assert.equal(semanticIdentity(a), semanticIdentity(b));
});

test('Authorization-like diagnostics cannot become Decision authority', () => {
  const d = clone(sourceAuditClear);
  const originalIdentity = semanticIdentity(d);
  d.metadata.diagnostics = {
    actor: 'root',
    authorization: { approved: true, requested_operation: 'task.dispatch' },
    execution_permission: true,
  };
  assert.equal(semanticIdentity(d), originalIdentity);
  assert.equal(outcome(d, expectationFor(d, 'knowledge.add_verified_tag')), 'candidate_for_authorization');
  assert.equal(outcome(d, expectationFor(d, 'task.dispatch')), 'not_applicable');

  const injected = clone(sourceAuditClear);
  injected.actor = 'root';
  assertContractError(() => validateDecision(injected), 'unknown_field');
});

test('container depths below and at 128 are accepted; 129 is rejected deterministically', () => {
  const below = clone(sourceAuditClear);
  below.metadata.diagnostics = nestedContainers(10);
  assert.doesNotThrow(() => validateDecision(below));

  const boundary = clone(sourceAuditClear);
  boundary.metadata.diagnostics = nestedContainers(126); // Decision root=1, metadata=2, diagnostics chain reaches 128.
  assert.doesNotThrow(() => validateDecision(boundary));

  const over = clone(sourceAuditClear);
  over.metadata.diagnostics = nestedContainers(127);
  assertContractError(() => validateDecision(over), 'json_depth_exceeded');
});

test('self-cycle and mutual-cycle are rejected; shared-but-acyclic structures are accepted', () => {
  const self = clone(sourceAuditClear);
  const s = {};
  s.self = s;
  self.metadata.diagnostics = s;
  assertContractError(() => validateDecision(self), 'cyclic_container');

  const mutual = clone(sourceAuditClear);
  const a = {};
  const b = {};
  a.b = b;
  b.a = a;
  mutual.metadata.diagnostics = a;
  assertContractError(() => validateDecision(mutual), 'cyclic_container');

  const shared = clone(sourceAuditClear);
  const child = { x: 1 };
  shared.metadata.diagnostics = { a: child, b: child };
  assert.doesNotThrow(() => validateDecision(shared));
});

test('invalid UTF-8 and duplicate keys are rejected at byte ingress', () => {
  assertContractError(() => parseJsonBytes(Buffer.from([0x7b, 0x22, 0x61, 0x22, 0x3a, 0x22, 0xc3, 0x28, 0x22, 0x7d])), 'invalid_utf8');
  assertContractError(() => parseJsonBytes(Buffer.from('{"a":1,"a":2}', 'utf8')), 'duplicate_key');
  assertContractError(() => parseJsonBytes(Buffer.from('{"a":1,"\\u0061":2}', 'utf8')), 'duplicate_key');
});

test('non-finite host values are rejected', () => {
  for (const n of [NaN, Infinity, -Infinity]) {
    const d = clone(sourceAuditClear);
    d.metadata.diagnostics = { n };
    assertContractError(() => validateDecision(d), 'non_finite_number');
  }
});

test('unpaired Unicode surrogates in values and keys are rejected', () => {
  const value = clone(sourceAuditClear);
  value.metadata.diagnostics = '\ud800';
  assertContractError(() => validateDecision(value), 'invalid_unicode_scalar');

  const keyed = clone(sourceAuditClear);
  keyed.metadata.diagnostics = { ['\udc00']: 1 };
  assertContractError(() => validateDecision(keyed), 'invalid_unicode_scalar');

  assertContractError(() => parseJsonBytes(Buffer.from('{"x":"\\ud800"}', 'utf8')), 'invalid_unicode_scalar');
});

test('JCS sorting uses raw UTF-16 code units including non-BMP keys', () => {
  const value = {
    '\u20ac': 'Euro Sign',
    '\r': 'Carriage Return',
    '\ufb33': 'Hebrew Letter Dalet With Dagesh',
    '1': 'One',
    '😀': 'Emoji: Grinning Face',
    '\u0080': 'Control',
    'ö': 'Latin Small Letter O With Diaeresis',
  };
  const canonical = canonicalJsonBytes(value).toString('utf8');
  assert.equal(canonical, '{"\\r":"Carriage Return","1":"One","":"Control","ö":"Latin Small Letter O With Diaeresis","€":"Euro Sign","😀":"Emoji: Grinning Face","דּ":"Hebrew Letter Dalet With Dagesh"}\n');
});

test('negative zero canonicalizes as zero', () => {
  assert.equal(canonicalJsonBytes({ n: -0 }).toString('utf8'), '{"n":0}\n');
});

test('RFC 8785 exponent and precision examples canonicalize with ECMAScript spelling', () => {
  const parsed = parseJsonBytes(Buffer.from('{"numbers":[333333333.33333329,1E30,4.50,2e-3,0.000000000000000000000000001]}', 'utf8'));
  assert.equal(canonicalJsonBytes(parsed).toString('utf8'), '{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27]}\n');
});

test('unsafe precision-losing integer-form token is rejected', () => {
  assertContractError(() => parseJsonBytes(Buffer.from('{"n":9007199254740993}', 'utf8')), 'non_interoperable_integer');
  const host = { n: 9007199254740992 };
  assertContractError(() => canonicalJsonBytes(host), 'non_interoperable_integer');
});

test('canonical out-of-safe-integer RFC 8785 sample round-trips at byte ingress', () => {
  const bytes = Buffer.from('{"n":295147905179352830000}', 'utf8');
  const parsed = parseJsonBytes(bytes);
  assert.equal(canonicalJsonBytes(parsed).toString('utf8'), '{"n":295147905179352830000}\n');
});

test('malformed expectation shapes fail closed as invalid_expectation', () => {
  const base = expectationFor(sourceAuditClear, 'knowledge.add_verified_tag');
  const cases = [];

  const missing = clone(base);
  delete missing.policy;
  cases.push(missing);

  const extra = clone(base);
  extra.actor = 'root';
  cases.push(extra);

  const wrongType = clone(base);
  wrongType.requested_operation = 5;
  cases.push(wrongType);

  const badHash = clone(base);
  badHash.target.content_sha256 = 'ABC';
  cases.push(badHash);

  const hostOnly = clone(base);
  hostOnly.effect_params = { scope: () => 'claim' };
  cases.push(hostOnly);

  const nonFinite = clone(base);
  nonFinite.effect_params = { n: Infinity };
  cases.push(nonFinite);

  for (const malformed of cases) {
    const result = consume(sourceAuditClear, malformed);
    assert.deepEqual({ outcome: result.outcome, reason: result.reason }, { outcome: 'cannot_establish', reason: 'invalid_expectation' });
  }
});

test('failed evaluation is returned only after upstream/policy/target applicability succeeds', () => {
  const exact = expectationFor(evaluationFailed, 'anything');
  assert.equal(outcome(evaluationFailed, exact), 'evaluation_failed');
  const wrongTarget = clone(exact);
  wrongTarget.target.id = 'other';
  assert.equal(outcome(evaluationFailed, wrongTarget), 'not_applicable');
});

test('public operations translate malformed domain failures rather than leaking runtime exceptions', () => {
  const tooDeep = clone(sourceAuditClear);
  tooDeep.metadata.diagnostics = nestedContainers(127);
  const result = consume(tooDeep, expectationFor(sourceAuditClear, 'knowledge.add_verified_tag'));
  assert.equal(result.outcome, 'cannot_establish');
  assert.equal(result.reason, 'invalid_decision');
  assert.equal(result.error, 'json_depth_exceeded');

  assertContractError(() => canonicalJsonBytes({ s: '\ud800' }), 'invalid_unicode_scalar');
  assertContractError(() => parseDecisionBytes(Buffer.from('{not json}', 'utf8')), 'invalid_json_syntax');
});

test('canonical Decision bytes are JCS plus exactly one trailing LF', () => {
  const bytes = canonicalDecisionBytes(citationClear);
  assert.equal(bytes.at(-1), 0x0a);
  assert.notEqual(bytes.at(-2), 0x0a);
  assert.equal(bytes.toString('utf8'), '{"contract_d_version":"0.3.0-rc5","effect":{"type":"knowledge.cite_as_evidence","version":"1"},"evaluation":{"disposition":"clear","state":"completed"},"input_authority":{"id":"c2","immutable_id":"result-set:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","kind":"contract-c"},"policy":{"id":"mainframe.citation-use","version":"1"},"target":{"content_sha256":"sha256:1111111111111111111111111111111111111111111111111111111111111111","id":"k2","kind":"knowledge"}}\n');
});
