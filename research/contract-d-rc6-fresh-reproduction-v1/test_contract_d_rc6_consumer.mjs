import assert from 'node:assert/strict';
import {
  CONTRACT_D_VERSION,
  MAX_CONTAINER_DEPTH,
  canonicalJson,
  consume,
  normalizeEffect,
  parseJsonBytes,
  semanticIdentity,
  semanticProjection,
  validateDecision,
  validateFiniteJson,
  ContractDError
} from './contract_d_rc6_consumer.mjs';

const H = 'sha256:' + '1'.repeat(64);
const H2 = 'sha256:' + '2'.repeat(64);

function clone(x) { return structuredClone(x); }

function addDecision({ disposition='clear', scope='claim', omitParams=false, authority='c1', immutable='result-set:'+'a'.repeat(64), targetId='k1', targetHash=H, metadata } = {}) {
  const effect = { type: 'knowledge.add_verified_tag', version: '1' };
  if (!omitParams) effect.params = { scope };
  const d = {
    contract_d_version: CONTRACT_D_VERSION,
    input_authority: { kind: 'contract-c', id: authority, immutable_id: immutable },
    policy: { id: 'mainframe.source-audit', version: '1' },
    target: { kind: 'knowledge', id: targetId, content_sha256: targetHash },
    evaluation: { state: 'completed', disposition },
    effect
  };
  if (metadata !== undefined) d.metadata = metadata;
  return d;
}

function citationDecision({ explicitParams=false } = {}) {
  const effect = { type: 'knowledge.cite_as_evidence', version: '1' };
  if (explicitParams) effect.params = {};
  return {
    contract_d_version: CONTRACT_D_VERSION,
    input_authority: { kind: 'contract-c', id: 'c2', immutable_id: 'result-set:'+'b'.repeat(64) },
    policy: { id: 'mainframe.citation-use', version: '1' },
    target: { kind: 'knowledge', id: 'k2', content_sha256: H },
    evaluation: { state: 'completed', disposition: 'clear' },
    effect
  };
}

function dispatchDecision({ explicitParams=false } = {}) {
  const effect = { type: 'task.dispatch', version: '1' };
  if (explicitParams) effect.params = {};
  return {
    contract_d_version: CONTRACT_D_VERSION,
    input_authority: { kind: 'task-review', id: 'r1', immutable_id: 'task-review:'+'c'.repeat(64) },
    policy: { id: 'mainframe.task-dispatch', version: '1' },
    target: { kind: 'task', id: 't1', content_sha256: H },
    evaluation: { state: 'completed', disposition: 'clear' },
    effect
  };
}

function failedDecision() {
  return {
    contract_d_version: CONTRACT_D_VERSION,
    input_authority: { kind: 'contract-c', id: 'c4', immutable_id: 'result-set:'+'e'.repeat(64) },
    policy: { id: 'mainframe.source-audit', version: '1' },
    target: { kind: 'knowledge', id: 'k4', content_sha256: H },
    evaluation: { state: 'failed' },
    metadata: { reason_codes: ['policy_evaluation_failure'] }
  };
}

function expectationFor(d, op=d.effect?.type ?? 'knowledge.add_verified_tag', effectParams=undefined) {
  const e = {
    input_authority: clone(d.input_authority),
    policy: clone(d.policy),
    target: clone(d.target),
    requested_operation: op
  };
  if (effectParams !== undefined) e.effect_params = effectParams;
  return e;
}

const tests = [];
function test(name, fn) { tests.push([name, fn]); }
function throwsCode(fn, code) {
  assert.throws(fn, err => err instanceof ContractDError && err.code === code);
}

// Decision semantics.
test('exact version accepted', () => assert.equal(validateDecision(addDecision()).ok, true));
test('future version rejected', () => { const d=addDecision(); d.contract_d_version='0.3.0-rc7'; assert.equal(validateDecision(d).error,'unknown_contract_version'); });
test('numeric version rejected', () => { const d=addDecision(); d.contract_d_version=0.3; assert.equal(validateDecision(d).error,'unknown_contract_version'); });
test('source-audit CLEAR', () => { const d=addDecision(); assert.equal(consume(d,expectationFor(d)).outcome,'candidate_for_authorization'); });
test('citation-use CLEAR', () => { const d=citationDecision(); assert.equal(consume(d,expectationFor(d)).outcome,'candidate_for_authorization'); });
test('task-dispatch CLEAR', () => { const d=dispatchDecision(); assert.equal(consume(d,expectationFor(d)).outcome,'candidate_for_authorization'); });
test('completed HOLD distinct from failure', () => { const d=addDecision({disposition:'hold'}); assert.equal(consume(d,expectationFor(d)).outcome,'hold'); });
test('evaluation failure distinct from HOLD', () => { const d=failedDecision(); assert.equal(consume(d,expectationFor(d,'knowledge.add_verified_tag')).outcome,'evaluation_failed'); });
test('wrong requested operation for CLEAR', () => { const d=addDecision(); assert.equal(consume(d,expectationFor(d,'task.dispatch')).outcome,'not_applicable'); });
test('wrong requested operation for HOLD', () => { const d=addDecision({disposition:'hold'}); assert.equal(consume(d,expectationFor(d,'task.dispatch')).outcome,'not_applicable'); });
test('upstream id substitution non-applicable', () => { const d=addDecision(); const e=expectationFor(d); e.input_authority.id='other'; assert.equal(consume(d,e).outcome,'not_applicable'); });
test('upstream immutable substitution non-applicable', () => { const d=addDecision(); const e=expectationFor(d); e.input_authority.immutable_id='result-set:'+'f'.repeat(64); assert.equal(consume(d,e).outcome,'not_applicable'); });
test('policy substitution non-applicable', () => { const d=addDecision(); const e=expectationFor(d); e.policy.id='other.policy'; assert.equal(consume(d,e).outcome,'not_applicable'); });
test('policy version substitution non-applicable', () => { const d=addDecision(); const e=expectationFor(d); e.policy.version='2'; assert.equal(consume(d,e).outcome,'not_applicable'); });
test('target substitution non-applicable', () => { const d=addDecision(); const e=expectationFor(d); e.target.content_sha256=H2; assert.equal(consume(d,e).outcome,'not_applicable'); });
test('absent requested effect params unconstrained', () => { const d=addDecision({scope:'object'}); assert.equal(consume(d,expectationFor(d)).outcome,'candidate_for_authorization'); });
test('empty requested effect params unconstrained', () => { const d=addDecision({scope:'object'}); assert.equal(consume(d,expectationFor(d,d.effect.type,{})).outcome,'candidate_for_authorization'); });
test('explicit requested effect params match', () => { const d=addDecision({scope:'object'}); assert.equal(consume(d,expectationFor(d,d.effect.type,{scope:'object'})).outcome,'candidate_for_authorization'); });
test('explicit requested effect params conflict', () => { const d=addDecision({scope:'object'}); assert.equal(consume(d,expectationFor(d,d.effect.type,{scope:'claim'})).outcome,'not_applicable'); });
test('metadata changes do not change semantic identity', () => { const a=addDecision({metadata:{diagnostics:{trace:'a'},explanation:'A'}}); const b=addDecision({metadata:{diagnostics:{trace:'b',authorization:{approved:true}},explanation:'B'}}); assert.equal(semanticIdentity(a),semanticIdentity(b)); });
test('Authorization-like top-level data cannot become Decision authority', () => { const d=addDecision(); d.actor='root'; assert.equal(validateDecision(d).ok,false); assert.equal(consume(d,expectationFor(addDecision())).outcome,'cannot_establish'); });
test('Authorization-like metadata remains non-authoritative', () => { const a=addDecision(); const b=addDecision({metadata:{diagnostics:{actor:'root',approval:true,execution_permission:true}}}); assert.equal(validateDecision(b).ok,true); assert.equal(semanticIdentity(a),semanticIdentity(b)); });

// Malformed expectation behavior.
test('malformed expectation missing binding key cannot establish', () => { const d=addDecision(); const e=expectationFor(d); delete e.policy.version; assert.deepEqual(consume(d,e),{outcome:'cannot_establish',reason:'invalid_expectation'}); });
test('malformed expectation extra binding key cannot establish', () => { const d=addDecision(); const e=expectationFor(d); e.policy.approval=true; assert.equal(consume(d,e).outcome,'cannot_establish'); });
test('malformed expectation target hash cannot establish', () => { const d=addDecision(); const e=expectationFor(d); e.target.content_sha256='sha256:BAD'; assert.equal(consume(d,e).outcome,'cannot_establish'); });
test('malformed expectation effect_params container cannot establish', () => { const d=addDecision(); const e=expectationFor(d); e.effect_params=[]; assert.equal(consume(d,e).outcome,'cannot_establish'); });

// RC6 clarification controls for empty-schema effects.
for (const [label, make] of [['knowledge.cite_as_evidence@1', citationDecision], ['task.dispatch@1', dispatchDecision]]) {
  test(`${label} omitted params normalizes to total effect`, () => {
    const n=normalizeEffect(make({explicitParams:false}).effect);
    assert.deepEqual(n,{type:make().effect.type,version:'1',params:{}});
    assert.deepEqual(Object.keys(n).sort(),['params','type','version']);
  });
  test(`${label} explicit empty params normalizes identically`, () => {
    const a=normalizeEffect(make({explicitParams:false}).effect);
    const b=normalizeEffect(make({explicitParams:true}).effect);
    assert.deepEqual(a,b); assert.deepEqual(b.params,{});
  });
  test(`${label} semantic projection contains exact normalized effect`, () => {
    const d=make({explicitParams:false});
    assert.deepEqual(semanticProjection(d).effect,{type:d.effect.type,version:'1',params:{}});
  });
  test(`${label} omission versus explicit empty params has identical semantic identity`, () => {
    assert.equal(semanticIdentity(make({explicitParams:false})),semanticIdentity(make({explicitParams:true})));
  });
}

test('add_verified_tag omitted params defaults to claim', () => assert.deepEqual(normalizeEffect(addDecision({omitParams:true}).effect),{type:'knowledge.add_verified_tag',version:'1',params:{scope:'claim'}}));
test('add_verified_tag explicit empty params defaults to claim', () => { const d=addDecision({omitParams:true}); d.effect.params={}; assert.deepEqual(normalizeEffect(d.effect).params,{scope:'claim'}); });
test('add_verified_tag explicit claim equals default identity', () => assert.equal(semanticIdentity(addDecision({omitParams:true})),semanticIdentity(addDecision({scope:'claim'}))));
test('add_verified_tag explicit object remains distinct', () => assert.notEqual(semanticIdentity(addDecision({scope:'claim'})),semanticIdentity(addDecision({scope:'object'}))));
test('RC6 stored-effect clarification does not inject defaults into external empty request', () => { const d=addDecision({scope:'object'}); const e=expectationFor(d,d.effect.type,{}); assert.equal(consume(d,e).outcome,'candidate_for_authorization'); });

// Interoperable JSON and depth hardening.
function nestedArrays(depth) { let v=[]; for(let i=1;i<depth;i++) v=[v]; return v; }
test('depth below maximum accepted', () => assert.equal(validateFiniteJson(nestedArrays(64)),true));
test('exact depth-128 boundary accepted', () => assert.equal(validateFiniteJson(nestedArrays(MAX_CONTAINER_DEPTH)),true));
test('depth beyond 128 rejected', () => throwsCode(()=>validateFiniteJson(nestedArrays(MAX_CONTAINER_DEPTH+1)),'json_depth_exceeded'));
test('byte parser exact depth-128 accepted', () => { const s='['.repeat(128)+']'.repeat(128); assert.equal(Array.isArray(parseJsonBytes(Buffer.from(s))),true); });
test('byte parser depth-129 controlled rejection', () => { const s='['.repeat(129)+']'.repeat(129); throwsCode(()=>parseJsonBytes(Buffer.from(s)),'json_depth_exceeded'); });
test('self-cycle rejected', () => { const a={}; a.self=a; throwsCode(()=>validateFiniteJson(a),'cyclic_json'); });
test('mutual-cycle rejected', () => { const a={}, b={}; a.b=b; b.a=a; throwsCode(()=>validateFiniteJson(a),'cyclic_json'); });
test('shared-but-acyclic structure accepted', () => { const shared={x:1}; assert.equal(validateFiniteJson({a:shared,b:shared}),true); });
test('invalid UTF-8 rejected at byte ingress', () => throwsCode(()=>parseJsonBytes(Uint8Array.from([0x7b,0x22,0x78,0x22,0x3a,0xff,0x7d])),'invalid_utf8'));
test('duplicate key rejected at byte ingress', () => throwsCode(()=>parseJsonBytes(Buffer.from('{"a":1,"a":2}')),'duplicate_key'));
test('non-finite host value rejected', () => throwsCode(()=>validateFiniteJson({x:Infinity}),'non_finite_number'));
test('NaN host value rejected', () => throwsCode(()=>validateFiniteJson({x:NaN}),'non_finite_number'));
test('unpaired Unicode surrogate rejected in host value', () => throwsCode(()=>validateFiniteJson({x:'\ud800'}),'invalid_unicode_scalar'));
test('unpaired Unicode surrogate rejected at byte ingress', () => throwsCode(()=>parseJsonBytes(Buffer.from('{"x":"\\ud800"}')),'invalid_unicode_scalar'));

test('non-BMP key ordering uses UTF-16 code units', () => {
  const v={'\ue000':1,'😀':2};
  assert.equal(canonicalJson(v).toString('utf8'),'{"😀":2,"":1}\n');
});
test('negative zero canonicalizes as zero', () => assert.equal(canonicalJson({n:-0}).toString('utf8'),'{"n":0}\n'));
test('JCS exponent serialization positive exponent', () => { const v=parseJsonBytes(Buffer.from('{"n":1e30}')); assert.equal(canonicalJson(v).toString('utf8'),'{"n":1e+30}\n'); });
test('JCS exponent serialization small magnitude', () => assert.equal(canonicalJson({n:1e-7}).toString('utf8'),'{"n":1e-7}\n'));
test('JCS fixed serialization threshold', () => assert.equal(canonicalJson({n:1e-6}).toString('utf8'),'{"n":0.000001}\n'));
test('JCS precision-edge number rounds to ECMAScript binary64 spelling', () => assert.equal(canonicalJson({n:333333333.33333329}).toString('utf8'),'{"n":333333333.3333333}\n'));
test('unsafe precision-losing integer token rejected', () => throwsCode(()=>parseJsonBytes(Buffer.from('{"n":9007199254740993}')),'non_interoperable_integer'));
test('exactly representable unsafe integer token accepted at byte ingress', () => { const v=parseJsonBytes(Buffer.from('{"n":9007199254740992}')); assert.equal(canonicalJson(v).toString('utf8'),'{"n":9007199254740992}\n'); });
test('canonical RFC8785 large integer-form sample accepted and stable', () => { const src='{"n":295147905179352830000}'; const v=parseJsonBytes(Buffer.from(src)); assert.equal(canonicalJson(v).toString('utf8'),src+'\n'); });
test('programmatic unsafe integer-form number rejected', () => throwsCode(()=>validateFiniteJson({n:9007199254740992}),'non_interoperable_integer'));
test('canonical framing has exactly one trailing LF', () => { const b=canonicalJson({b:1,a:2}); assert.equal(b.toString(),'{"a":2,"b":1}\n'); assert.equal(b.at(-1),0x0a); assert.notEqual(b.at(-2),0x0a); });

// Controlled fail-closed behavior.
test('consumer controls invalid Unicode rather than leaking encoder exception', () => { const d=addDecision({metadata:{diagnostics:{bad:'\ud800'}}}); const r=consume(d,expectationFor(addDecision())); assert.equal(r.outcome,'cannot_establish'); assert.equal(r.reason,'invalid_decision'); });
test('consumer controls cyclic decision rather than raw recursion error', () => { const d=addDecision(); d.metadata={diagnostics:{}}; d.metadata.diagnostics.loop=d; const r=consume(d,expectationFor(addDecision())); assert.equal(r.outcome,'cannot_establish'); });
test('consumer controls malformed expectation cycle', () => { const d=addDecision(); const e=expectationFor(d); e.loop=e; assert.equal(consume(d,e).outcome,'cannot_establish'); });

let passed=0;
const failures=[];
for (const [name, fn] of tests) {
  try {
    await fn();
    passed++;
    console.log(`ok ${passed} - ${name}`);
  } catch (err) {
    failures.push({name, err});
    console.log(`not ok ${passed+failures.length} - ${name}`);
    console.log(`  ${err?.stack ?? err}`);
  }
}
console.log(`# prereveal: ${passed} passed, ${failures.length} failed, ${tests.length} total`);
if (failures.length) process.exitCode=1;
