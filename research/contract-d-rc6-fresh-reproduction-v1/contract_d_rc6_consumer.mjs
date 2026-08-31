import crypto from 'node:crypto';

export const CONTRACT_D_VERSION = '0.3.0-rc6';
export const MAX_CONTAINER_DEPTH = 128;

const INGRESS_META = new WeakMap();

export class ContractDError extends Error {
  constructor(code, message = code) {
    super(message);
    this.name = 'ContractDError';
    this.code = code;
  }
}

function fail(code, message = code) {
  throw new ContractDError(code, message);
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function pathKey(path) {
  return JSON.stringify(path);
}

function assertUnicodeScalars(s) {
  if (typeof s !== 'string') fail('invalid_json_type');
  for (let i = 0; i < s.length; i++) {
    const u = s.charCodeAt(i);
    if (u >= 0xd800 && u <= 0xdbff) {
      if (i + 1 >= s.length) fail('invalid_unicode_scalar');
      const v = s.charCodeAt(i + 1);
      if (v < 0xdc00 || v > 0xdfff) fail('invalid_unicode_scalar');
      i++;
    } else if (u >= 0xdc00 && u <= 0xdfff) {
      fail('invalid_unicode_scalar');
    }
  }
}

function finiteJsonWalk(value, path, containerDepth, ancestors, ingressUnsafePaths) {
  if (value === null || typeof value === 'boolean') return;
  if (typeof value === 'string') {
    assertUnicodeScalars(value);
    return;
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) fail('non_finite_number');
    if (Number.isInteger(value) && !Number.isSafeInteger(value)) {
      if (!ingressUnsafePaths?.has(pathKey(path))) fail('non_interoperable_integer');
    }
    return;
  }
  if (typeof value !== 'object') fail('invalid_json_type');

  if (containerDepth > MAX_CONTAINER_DEPTH) fail('json_depth_exceeded');
  if (ancestors.has(value)) fail('cyclic_json');
  ancestors.add(value);
  try {
    if (Array.isArray(value)) {
      for (let i = 0; i < value.length; i++) {
        finiteJsonWalk(value[i], [...path, i], containerDepth + (value[i] && typeof value[i] === 'object' ? 1 : 0), ancestors, ingressUnsafePaths);
      }
    } else {
      const proto = Object.getPrototypeOf(value);
      if (proto !== Object.prototype && proto !== null) fail('invalid_json_type');
      for (const [k, v] of Object.entries(value)) {
        assertUnicodeScalars(k);
        finiteJsonWalk(v, [...path, k], containerDepth + (v && typeof v === 'object' ? 1 : 0), ancestors, ingressUnsafePaths);
      }
    }
  } finally {
    ancestors.delete(value);
  }
}

export function validateFiniteJson(value) {
  const meta = value && typeof value === 'object' ? INGRESS_META.get(value) : undefined;
  const rootDepth = value && typeof value === 'object' ? 1 : 0;
  finiteJsonWalk(value, [], rootDepth, new WeakSet(), meta?.unsafeIntegerPaths);
  return true;
}

class JsonByteParser {
  constructor(text) {
    this.text = text;
    this.i = 0;
    this.unsafeIntegerPaths = new Set();
  }

  ws() {
    while (this.i < this.text.length && /[\x20\x09\x0a\x0d]/.test(this.text[this.i])) this.i++;
  }

  parse() {
    this.ws();
    const v = this.value([], 0);
    this.ws();
    if (this.i !== this.text.length) fail('invalid_json_syntax');
    if (v && typeof v === 'object') INGRESS_META.set(v, { unsafeIntegerPaths: this.unsafeIntegerPaths });
    return v;
  }

  value(path, containerDepth) {
    this.ws();
    if (this.i >= this.text.length) fail('invalid_json_syntax');
    const c = this.text[this.i];
    if (c === '{') return this.object(path, containerDepth + 1);
    if (c === '[') return this.array(path, containerDepth + 1);
    if (c === '"') return this.string();
    if (c === 't' && this.text.startsWith('true', this.i)) { this.i += 4; return true; }
    if (c === 'f' && this.text.startsWith('false', this.i)) { this.i += 5; return false; }
    if (c === 'n' && this.text.startsWith('null', this.i)) { this.i += 4; return null; }
    if (c === '-' || (c >= '0' && c <= '9')) return this.number(path);
    fail('invalid_json_syntax');
  }

  string() {
    const start = this.i;
    this.i++;
    let escaped = false;
    while (this.i < this.text.length) {
      const c = this.text[this.i];
      if (!escaped && c === '"') {
        this.i++;
        const literal = this.text.slice(start, this.i);
        let value;
        try { value = JSON.parse(literal); } catch { fail('invalid_json_syntax'); }
        assertUnicodeScalars(value);
        return value;
      }
      if (!escaped && c.charCodeAt(0) < 0x20) fail('invalid_json_syntax');
      if (!escaped && c === '\\') escaped = true;
      else escaped = false;
      this.i++;
    }
    fail('invalid_json_syntax');
  }

  number(path) {
    const rest = this.text.slice(this.i);
    const m = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(rest);
    if (!m) fail('invalid_json_syntax');
    const token = m[0];
    this.i += token.length;
    const next = this.text[this.i];
    if (next && !/[\x20\x09\x0a\x0d,\]}]/.test(next)) fail('invalid_json_syntax');
    const n = Number(token);
    if (!Number.isFinite(n)) fail('non_finite_number');
    const integerForm = /^-?(?:0|[1-9][0-9]*)$/.test(token);
    if (integerForm) {
      const bi = BigInt(token);
      if (bi > BigInt(Number.MAX_SAFE_INTEGER) || bi < BigInt(Number.MIN_SAFE_INTEGER)) {
        let exact = false;
        if (Number.isInteger(n)) {
          try { exact = BigInt(n) === bi; } catch { exact = false; }
        }
        const canonical = JSON.stringify(n);
        if (!exact && canonical !== token) fail('non_interoperable_integer');
      }
    }
    // Byte-ingress numbers are already binary64. Once an integer-form token has
    // passed the special ambiguity rule above, any finite numeric spelling may
    // legitimately produce an integer-valued binary64 outside the host safe-int
    // range (for example 1e30). Preserve that ingress provenance by path.
    if (Number.isInteger(n) && !Number.isSafeInteger(n)) this.unsafeIntegerPaths.add(pathKey(path));
    return n;
  }

  object(path, depth) {
    if (depth > MAX_CONTAINER_DEPTH) fail('json_depth_exceeded');
    const out = {};
    const seen = new Set();
    this.i++;
    this.ws();
    if (this.text[this.i] === '}') { this.i++; return out; }
    while (true) {
      this.ws();
      if (this.text[this.i] !== '"') fail('invalid_json_syntax');
      const k = this.string();
      if (seen.has(k)) fail('duplicate_key');
      seen.add(k);
      this.ws();
      if (this.text[this.i] !== ':') fail('invalid_json_syntax');
      this.i++;
      out[k] = this.value([...path, k], depth);
      this.ws();
      if (this.text[this.i] === '}') { this.i++; return out; }
      if (this.text[this.i] !== ',') fail('invalid_json_syntax');
      this.i++;
    }
  }

  array(path, depth) {
    if (depth > MAX_CONTAINER_DEPTH) fail('json_depth_exceeded');
    const out = [];
    this.i++;
    this.ws();
    if (this.text[this.i] === ']') { this.i++; return out; }
    let idx = 0;
    while (true) {
      out.push(this.value([...path, idx], depth));
      idx++;
      this.ws();
      if (this.text[this.i] === ']') { this.i++; return out; }
      if (this.text[this.i] !== ',') fail('invalid_json_syntax');
      this.i++;
    }
  }
}

export function parseJsonBytes(bytes) {
  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch {
    fail('invalid_utf8');
  }
  return new JsonByteParser(text).parse();
}

function ensureObject(value, code = 'invalid_structure') {
  if (!isObject(value)) fail(code);
}

function exactKeys(obj, required, optional = []) {
  ensureObject(obj);
  const allowed = new Set([...required, ...optional]);
  for (const k of Object.keys(obj)) if (!allowed.has(k)) fail('unknown_field');
  for (const k of required) if (!Object.prototype.hasOwnProperty.call(obj, k)) fail('missing_field');
}

function nonEmptyString(v) {
  if (typeof v !== 'string' || v.length === 0) fail('invalid_structure');
  assertUnicodeScalars(v);
}

function validateBindingAuthority(v) {
  exactKeys(v, ['kind', 'id', 'immutable_id']);
  nonEmptyString(v.kind); nonEmptyString(v.id); nonEmptyString(v.immutable_id);
}

function validatePolicy(v) {
  exactKeys(v, ['id', 'version']);
  nonEmptyString(v.id); nonEmptyString(v.version);
}

function validateTarget(v) {
  exactKeys(v, ['kind', 'id', 'content_sha256']);
  nonEmptyString(v.kind); nonEmptyString(v.id); nonEmptyString(v.content_sha256);
  if (!/^sha256:[0-9a-f]{64}$/.test(v.content_sha256)) fail('invalid_target_hash');
}

function validateMetadata(v) {
  exactKeys(v, [], ['reason_codes', 'explanation', 'diagnostics']);
  if ('reason_codes' in v) {
    if (!Array.isArray(v.reason_codes)) fail('invalid_structure');
    for (const s of v.reason_codes) nonEmptyString(s);
  }
  if ('explanation' in v) nonEmptyString(v.explanation);
}

const REGISTRY = Object.freeze({
  'knowledge.add_verified_tag': Object.freeze({
    '1': Object.freeze({ params: Object.freeze({ scope: Object.freeze({ type: 'string', enum: Object.freeze(['claim', 'object']), required: false, default: 'claim' }) }) })
  }),
  'knowledge.cite_as_evidence': Object.freeze({ '1': Object.freeze({ params: Object.freeze({}) }) }),
  'task.dispatch': Object.freeze({ '1': Object.freeze({ params: Object.freeze({}) }) })
});

function effectSchema(effect) {
  const byType = REGISTRY[effect.type];
  if (!byType) fail('unknown_effect_type');
  const schema = byType[effect.version];
  if (!schema) fail('unknown_effect_version');
  return schema;
}

function validateStoredEffect(effect) {
  exactKeys(effect, ['type', 'version'], ['params']);
  nonEmptyString(effect.type); nonEmptyString(effect.version);
  const schema = effectSchema(effect);
  if ('params' in effect && !isObject(effect.params)) fail('invalid_effect_params');
  const params = effect.params ?? {};
  for (const k of Object.keys(params)) if (!(k in schema.params)) fail('unknown_effect_parameter');
  for (const [k, ps] of Object.entries(schema.params)) {
    if (!(k in params)) {
      if (ps.required) fail('missing_effect_parameter');
      continue;
    }
    const val = params[k];
    if (ps.type === 'string' && typeof val !== 'string') fail('invalid_effect_parameter');
    if (ps.enum && !ps.enum.includes(val)) fail('invalid_effect_parameter');
    if (typeof val === 'string') assertUnicodeScalars(val);
  }
}

export function normalizeEffect(effect) {
  validateStoredEffect(effect);
  const schema = effectSchema(effect);
  const input = effect.params ?? {};
  const params = {};
  for (const [k, ps] of Object.entries(schema.params)) {
    if (Object.prototype.hasOwnProperty.call(input, k)) params[k] = input[k];
    else if (Object.prototype.hasOwnProperty.call(ps, 'default')) params[k] = ps.default;
  }
  return { type: effect.type, version: effect.version, params };
}

export function validateDecision(decision) {
  try {
    validateFiniteJson(decision);
    exactKeys(decision, ['contract_d_version', 'input_authority', 'policy', 'target', 'evaluation'], ['effect', 'metadata']);
    if (decision.contract_d_version !== CONTRACT_D_VERSION) fail('unknown_contract_version');
    validateBindingAuthority(decision.input_authority);
    validatePolicy(decision.policy);
    validateTarget(decision.target);
    exactKeys(decision.evaluation, ['state'], ['disposition']);
    if (decision.evaluation.state === 'completed') {
      if (!Object.prototype.hasOwnProperty.call(decision.evaluation, 'disposition')) fail('missing_field');
      if (decision.evaluation.disposition !== 'clear' && decision.evaluation.disposition !== 'hold') fail('unknown_disposition');
      if (!Object.prototype.hasOwnProperty.call(decision, 'effect')) fail('missing_effect');
      validateStoredEffect(decision.effect);
    } else if (decision.evaluation.state === 'failed') {
      if (Object.prototype.hasOwnProperty.call(decision.evaluation, 'disposition')) fail('effect_on_failure');
      if (Object.prototype.hasOwnProperty.call(decision, 'effect')) fail('effect_on_failure');
    } else {
      fail('unknown_evaluation_state');
    }
    if ('metadata' in decision) validateMetadata(decision.metadata);
    return { ok: true };
  } catch (err) {
    if (err instanceof ContractDError) return { ok: false, error: err.code };
    return { ok: false, error: 'controlled_failure' };
  }
}

function jcsSerialize(value, path, ingressUnsafePaths) {
  if (value === null) return 'null';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'string') { assertUnicodeScalars(value); return JSON.stringify(value); }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) fail('non_finite_number');
    if (Number.isInteger(value) && !Number.isSafeInteger(value) && !ingressUnsafePaths?.has(pathKey(path))) fail('non_interoperable_integer');
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return '[' + value.map((v, i) => jcsSerialize(v, [...path, i], ingressUnsafePaths)).join(',') + ']';
  if (isObject(value)) {
    const keys = Object.keys(value).sort();
    return '{' + keys.map(k => `${JSON.stringify(k)}:${jcsSerialize(value[k], [...path, k], ingressUnsafePaths)}`).join(',') + '}';
  }
  fail('invalid_json_type');
}

export function canonicalJson(value) {
  validateFiniteJson(value);
  const meta = value && typeof value === 'object' ? INGRESS_META.get(value) : undefined;
  return Buffer.from(jcsSerialize(value, [], meta?.unsafeIntegerPaths) + '\n', 'utf8');
}

export function semanticProjection(decision) {
  const valid = validateDecision(decision);
  if (!valid.ok) fail(valid.error);
  const projection = {
    contract_d_version: decision.contract_d_version,
    input_authority: decision.input_authority,
    policy: decision.policy,
    target: decision.target,
    evaluation: decision.evaluation
  };
  if (decision.evaluation.state === 'completed') projection.effect = normalizeEffect(decision.effect);
  return projection;
}

export function semanticIdentity(decision) {
  const projection = semanticProjection(decision);
  const digest = crypto.createHash('sha256').update(canonicalJson(projection)).digest('hex');
  return `decision:sha256:${digest}`;
}

function validateExpectation(expectation) {
  try {
    validateFiniteJson(expectation);
    exactKeys(expectation, ['input_authority', 'policy', 'target', 'requested_operation'], ['effect_params']);
    validateBindingAuthority(expectation.input_authority);
    validatePolicy(expectation.policy);
    validateTarget(expectation.target);
    nonEmptyString(expectation.requested_operation);
    if ('effect_params' in expectation && !isObject(expectation.effect_params)) fail('invalid_expectation');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: 'invalid_expectation' };
  }
}

function deepEqualJson(a, b) {
  try { return jcsSerialize(a, [], undefined) === jcsSerialize(b, [], undefined); }
  catch { return false; }
}

function bindingMatches(decision, expectation) {
  return deepEqualJson(decision.input_authority, expectation.input_authority)
    && deepEqualJson(decision.policy, expectation.policy)
    && deepEqualJson(decision.target, expectation.target);
}

export function consume(decisionInput, expectation) {
  try {
    let decision = decisionInput;
    if (decisionInput instanceof Uint8Array || Buffer.isBuffer(decisionInput)) decision = parseJsonBytes(decisionInput);
    const dv = validateDecision(decision);
    if (!dv.ok) return { outcome: 'cannot_establish', reason: 'invalid_decision', detail: dv.error };
    const ev = validateExpectation(expectation);
    if (!ev.ok) return { outcome: 'cannot_establish', reason: 'invalid_expectation' };
    if (!bindingMatches(decision, expectation)) return { outcome: 'not_applicable' };
    if (decision.evaluation.state === 'failed') return { outcome: 'evaluation_failed' };

    const effect = normalizeEffect(decision.effect);
    if (expectation.requested_operation !== effect.type) return { outcome: 'not_applicable' };
    const constraints = expectation.effect_params ?? {};
    for (const [k, v] of Object.entries(constraints)) {
      if (!Object.prototype.hasOwnProperty.call(effect.params, k) || !deepEqualJson(v, effect.params[k])) return { outcome: 'not_applicable' };
    }
    return { outcome: decision.evaluation.disposition === 'hold' ? 'hold' : 'candidate_for_authorization' };
  } catch (err) {
    return { outcome: 'cannot_establish', reason: 'controlled_failure' };
  }
}
