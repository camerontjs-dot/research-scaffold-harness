'use strict';

const { createHash } = require('node:crypto');

const VERSION = '0.3.0-rc5';
const SAFE_INTEGER_MAX = 9007199254740991;
const MAX_CONTAINER_DEPTH = 128;
const SHA256_RE = /^sha256:[0-9a-f]{64}$/;
const BYTE_INGRESS_ROOTS = new WeakSet();

class ContractDError extends Error {
  constructor(code, message) {
    super(message || code);
    this.name = 'ContractDError';
    this.code = code;
  }
}

function fail(code, message) {
  throw new ContractDError(code, message);
}

function isUnicodeScalarString(value) {
  if (typeof value !== 'string') return false;
  for (let i = 0; i < value.length; i += 1) {
    const unit = value.charCodeAt(i);
    if (unit >= 0xd800 && unit <= 0xdbff) {
      if (i + 1 >= value.length) return false;
      const next = value.charCodeAt(i + 1);
      if (next < 0xdc00 || next > 0xdfff) return false;
      i += 1;
    } else if (unit >= 0xdc00 && unit <= 0xdfff) {
      return false;
    }
  }
  return true;
}

function requireScalarString(value, code = 'invalid_unicode_scalar') {
  if (!isUnicodeScalarString(value)) fail(code);
}

function isPlainJsonObject(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const proto = Object.getPrototypeOf(value);
  return proto === Object.prototype || proto === null;
}

function validateJsonDomain(value, options = {}) {
  const allowUnsafeIntegers = options.allowUnsafeIntegers === true;
  const ancestors = new Set();

  function walk(node, containerDepth) {
    if (node === null || typeof node === 'boolean') return;

    if (typeof node === 'string') {
      requireScalarString(node);
      return;
    }

    if (typeof node === 'number') {
      if (!Number.isFinite(node)) fail('non_finite_number');
      if (!allowUnsafeIntegers && Number.isInteger(node) && !Number.isSafeInteger(node)) {
        fail('non_interoperable_integer');
      }
      return;
    }

    if (typeof node !== 'object') fail('invalid_json_type');
    if (containerDepth > MAX_CONTAINER_DEPTH) fail('json_depth_exceeded');
    if (ancestors.has(node)) fail('cyclic_container');
    ancestors.add(node);

    try {
      if (Array.isArray(node)) {
        const keys = Object.keys(node);
        if (keys.length !== node.length) fail('invalid_json_type', 'array holes or extra properties are not JSON');
        for (let i = 0; i < node.length; i += 1) {
          if (!Object.prototype.hasOwnProperty.call(node, String(i))) {
            fail('invalid_json_type', 'array hole is not JSON');
          }
          walk(node[i], containerDepth + 1);
        }
        if (Object.getOwnPropertySymbols(node).length !== 0) fail('invalid_json_type');
        return;
      }

      if (!isPlainJsonObject(node)) fail('invalid_json_type');
      if (Object.getOwnPropertySymbols(node).length !== 0) fail('invalid_json_type');

      const ownNames = Object.getOwnPropertyNames(node);
      const enumerableNames = Object.keys(node);
      if (ownNames.length !== enumerableNames.length) fail('invalid_json_type');

      for (const key of enumerableNames) {
        requireScalarString(key);
        const descriptor = Object.getOwnPropertyDescriptor(node, key);
        if (!descriptor || !descriptor.enumerable || !Object.prototype.hasOwnProperty.call(descriptor, 'value')) {
          fail('invalid_json_type');
        }
        walk(descriptor.value, containerDepth + 1);
      }
    } finally {
      ancestors.delete(node);
    }
  }

  walk(value, 1);
  return true;
}

function parseJsonBytes(bytes) {
  if (!(bytes instanceof Uint8Array)) fail('invalid_json_type', 'byte ingress requires Uint8Array/Buffer');

  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch (_) {
    fail('invalid_utf8');
  }

  let i = 0;

  function syntax(message) {
    fail('invalid_json_syntax', message);
  }

  function skipWhitespace() {
    while (i < text.length) {
      const c = text.charCodeAt(i);
      if (c === 0x20 || c === 0x09 || c === 0x0a || c === 0x0d) i += 1;
      else break;
    }
  }

  function parseStringToken() {
    if (text[i] !== '"') syntax('expected string');
    const start = i;
    i += 1;
    while (i < text.length) {
      const code = text.charCodeAt(i);
      if (code === 0x22) {
        i += 1;
        const token = text.slice(start, i);
        let result;
        try {
          result = JSON.parse(token);
        } catch (_) {
          syntax('invalid string');
        }
        requireScalarString(result);
        return result;
      }
      if (code < 0x20) syntax('unescaped control character');
      if (code === 0x5c) {
        i += 1;
        if (i >= text.length) syntax('unterminated escape');
        const esc = text[i];
        if ('"\\/bfnrt'.includes(esc)) {
          i += 1;
          continue;
        }
        if (esc === 'u') {
          if (!/^[0-9a-fA-F]{4}$/.test(text.slice(i + 1, i + 5))) syntax('invalid unicode escape');
          i += 5;
          continue;
        }
        syntax('invalid escape');
      }
      i += 1;
    }
    syntax('unterminated string');
  }

  function parseNumberToken() {
    const rest = text.slice(i);
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(rest);
    if (!match) syntax('invalid number');
    const token = match[0];
    i += token.length;

    const next = text[i];
    if (next !== undefined && !/[\s,\]}]/.test(next)) syntax('invalid number terminator');

    const value = Number(token);
    if (!Number.isFinite(value)) fail('non_finite_number');

    if (!/[.eE]/.test(token)) {
      let exactInteger;
      try {
        exactInteger = BigInt(token);
      } catch (_) {
        syntax('invalid integer');
      }
      const max = BigInt(SAFE_INTEGER_MAX);
      if (exactInteger > max || exactInteger < -max) {
        let exactlyRepresentable = false;
        if (Number.isInteger(value)) {
          try {
            exactlyRepresentable = BigInt(value) === exactInteger;
          } catch (_) {
            exactlyRepresentable = false;
          }
        }
        const canonical = JSON.stringify(value);
        if (!exactlyRepresentable && canonical !== token) {
          fail('non_interoperable_integer');
        }
      }
    }

    return value;
  }

  function parseValue(containerDepth) {
    skipWhitespace();
    if (i >= text.length) syntax('unexpected end');
    const ch = text[i];

    if (ch === '{') return parseObject(containerDepth);
    if (ch === '[') return parseArray(containerDepth);
    if (ch === '"') return parseStringToken();
    if (ch === '-' || (ch >= '0' && ch <= '9')) return parseNumberToken();
    if (text.startsWith('true', i)) {
      i += 4;
      return true;
    }
    if (text.startsWith('false', i)) {
      i += 5;
      return false;
    }
    if (text.startsWith('null', i)) {
      i += 4;
      return null;
    }
    syntax('invalid token');
  }

  function parseObject(containerDepth) {
    if (containerDepth > MAX_CONTAINER_DEPTH) fail('json_depth_exceeded');
    const obj = Object.create(null);
    const keys = new Set();
    i += 1;
    skipWhitespace();
    if (text[i] === '}') {
      i += 1;
      return obj;
    }

    while (true) {
      skipWhitespace();
      const key = parseStringToken();
      if (keys.has(key)) fail('duplicate_key');
      keys.add(key);
      skipWhitespace();
      if (text[i] !== ':') syntax('expected colon');
      i += 1;
      obj[key] = parseValue(containerDepth + 1);
      skipWhitespace();
      if (text[i] === '}') {
        i += 1;
        return obj;
      }
      if (text[i] !== ',') syntax('expected comma');
      i += 1;
    }
  }

  function parseArray(containerDepth) {
    if (containerDepth > MAX_CONTAINER_DEPTH) fail('json_depth_exceeded');
    const arr = [];
    i += 1;
    skipWhitespace();
    if (text[i] === ']') {
      i += 1;
      return arr;
    }

    while (true) {
      arr.push(parseValue(containerDepth + 1));
      skipWhitespace();
      if (text[i] === ']') {
        i += 1;
        return arr;
      }
      if (text[i] !== ',') syntax('expected comma');
      i += 1;
    }
  }

  const value = parseValue(1);
  skipWhitespace();
  if (i !== text.length) syntax('trailing data');
  if (value !== null && typeof value === 'object') BYTE_INGRESS_ROOTS.add(value);
  return value;
}

function utf16Sort(a, b) {
  if (a === b) return 0;
  return a < b ? -1 : 1;
}

function canonicalJsonBytes(value) {
  try {
    validateJsonDomain(value, { allowUnsafeIntegers: value && typeof value === 'object' && BYTE_INGRESS_ROOTS.has(value) });

    let output = '';
    function serialize(node) {
      if (node === null || typeof node === 'boolean' || typeof node === 'number' || typeof node === 'string') {
        const s = JSON.stringify(node);
        if (s === undefined) fail('canonicalization_error');
        output += s;
        return;
      }
      if (Array.isArray(node)) {
        output += '[';
        for (let idx = 0; idx < node.length; idx += 1) {
          if (idx) output += ',';
          serialize(node[idx]);
        }
        output += ']';
        return;
      }
      output += '{';
      const keys = Object.keys(node).sort(utf16Sort);
      keys.forEach((key, idx) => {
        if (idx) output += ',';
        output += JSON.stringify(key);
        output += ':';
        serialize(node[key]);
      });
      output += '}';
    }

    serialize(value);
    return Buffer.from(output + '\n', 'utf8');
  } catch (err) {
    if (err instanceof ContractDError) throw err;
    fail('canonicalization_error');
  }
}

function assertExactKeys(obj, required, optional = []) {
  if (!isPlainJsonObject(obj)) fail('invalid_structure');
  const allowed = new Set([...required, ...optional]);
  const keys = Object.keys(obj);
  for (const key of keys) if (!allowed.has(key)) fail('unknown_field');
  for (const key of required) if (!Object.prototype.hasOwnProperty.call(obj, key)) fail('missing_field');
}

function requireNonEmptyString(value) {
  if (typeof value !== 'string' || value.length === 0) fail('invalid_structure');
  requireScalarString(value);
}

function validateInputAuthority(value) {
  assertExactKeys(value, ['kind', 'id', 'immutable_id']);
  requireNonEmptyString(value.kind);
  requireNonEmptyString(value.id);
  requireNonEmptyString(value.immutable_id);
}

function validatePolicy(value) {
  assertExactKeys(value, ['id', 'version']);
  requireNonEmptyString(value.id);
  requireNonEmptyString(value.version);
}

function validateTarget(value) {
  assertExactKeys(value, ['kind', 'id', 'content_sha256']);
  requireNonEmptyString(value.kind);
  requireNonEmptyString(value.id);
  if (typeof value.content_sha256 !== 'string' || !SHA256_RE.test(value.content_sha256)) fail('invalid_target_hash');
}

function validateMetadata(value) {
  assertExactKeys(value, [], ['reason_codes', 'explanation', 'diagnostics']);
  if (Object.prototype.hasOwnProperty.call(value, 'reason_codes')) {
    if (!Array.isArray(value.reason_codes)) fail('invalid_structure');
    for (const reason of value.reason_codes) requireNonEmptyString(reason);
  }
  if (Object.prototype.hasOwnProperty.call(value, 'explanation')) requireNonEmptyString(value.explanation);
}

function validateAndNormalizeEffect(effect) {
  assertExactKeys(effect, ['type', 'version'], ['params']);
  requireNonEmptyString(effect.type);
  requireNonEmptyString(effect.version);
  if (Object.prototype.hasOwnProperty.call(effect, 'params') && !isPlainJsonObject(effect.params)) fail('invalid_effect_params');

  const params = Object.prototype.hasOwnProperty.call(effect, 'params') ? effect.params : Object.create(null);

  if (effect.type === 'knowledge.add_verified_tag' && effect.version === '1') {
    assertExactKeys(params, [], ['scope']);
    const scope = Object.prototype.hasOwnProperty.call(params, 'scope') ? params.scope : 'claim';
    if (scope !== 'claim' && scope !== 'object') fail('invalid_effect_params');
    return { type: effect.type, version: effect.version, params: { scope } };
  }

  if ((effect.type === 'knowledge.cite_as_evidence' || effect.type === 'task.dispatch') && effect.version === '1') {
    assertExactKeys(params, []);
    return { type: effect.type, version: effect.version };
  }

  fail('unknown_effect');
}

function validateDecision(decision) {
  const allowUnsafeIntegers = decision && typeof decision === 'object' && BYTE_INGRESS_ROOTS.has(decision);
  validateJsonDomain(decision, { allowUnsafeIntegers });
  assertExactKeys(
    decision,
    ['contract_d_version', 'input_authority', 'policy', 'target', 'evaluation'],
    ['effect', 'metadata'],
  );

  if (decision.contract_d_version !== VERSION) fail('unsupported_version');
  validateInputAuthority(decision.input_authority);
  validatePolicy(decision.policy);
  validateTarget(decision.target);
  assertExactKeys(decision.evaluation, ['state'], ['disposition']);

  let normalizedEffect;
  if (decision.evaluation.state === 'completed') {
    if (decision.evaluation.disposition !== 'clear' && decision.evaluation.disposition !== 'hold') {
      fail('invalid_evaluation');
    }
    if (!Object.prototype.hasOwnProperty.call(decision, 'effect')) fail('missing_effect');
    normalizedEffect = validateAndNormalizeEffect(decision.effect);
  } else if (decision.evaluation.state === 'failed') {
    if (Object.prototype.hasOwnProperty.call(decision.evaluation, 'disposition')) fail('invalid_evaluation');
    if (Object.prototype.hasOwnProperty.call(decision, 'effect')) fail('effect_on_failed_evaluation');
  } else {
    fail('invalid_evaluation');
  }

  if (Object.prototype.hasOwnProperty.call(decision, 'metadata')) validateMetadata(decision.metadata);
  return { normalizedEffect };
}

function authorityProjection(decision) {
  const { normalizedEffect } = validateDecision(decision);
  const projection = {
    contract_d_version: decision.contract_d_version,
    input_authority: decision.input_authority,
    policy: decision.policy,
    target: decision.target,
    evaluation: decision.evaluation,
  };
  if (decision.evaluation.state === 'completed') projection.effect = normalizedEffect;
  return projection;
}

function semanticIdentity(decision) {
  const projection = authorityProjection(decision);
  const digest = createHash('sha256').update(canonicalJsonBytes(projection)).digest('hex');
  return `decision:sha256:${digest}`;
}

function parseDecisionBytes(bytes) {
  const value = parseJsonBytes(bytes);
  validateDecision(value);
  return value;
}

function canonicalDecisionBytes(decisionOrBytes) {
  const decision = decisionOrBytes instanceof Uint8Array ? parseDecisionBytes(decisionOrBytes) : decisionOrBytes;
  validateDecision(decision);
  return canonicalJsonBytes(decision);
}

function parseMaybeBytes(value) {
  return value instanceof Uint8Array ? parseJsonBytes(value) : value;
}

function validateExpectation(expectationInput) {
  const expectation = parseMaybeBytes(expectationInput);
  const allowUnsafeIntegers = expectation && typeof expectation === 'object' && BYTE_INGRESS_ROOTS.has(expectation);
  validateJsonDomain(expectation, { allowUnsafeIntegers });
  assertExactKeys(expectation, ['input_authority', 'policy', 'target', 'requested_operation'], ['effect_params']);
  validateInputAuthority(expectation.input_authority);
  validatePolicy(expectation.policy);
  validateTarget(expectation.target);
  requireNonEmptyString(expectation.requested_operation);
  if (Object.prototype.hasOwnProperty.call(expectation, 'effect_params') && !isPlainJsonObject(expectation.effect_params)) {
    fail('invalid_expectation');
  }
  return expectation;
}

function sameBinding(a, b, fields) {
  return fields.every((field) => a[field] === b[field]);
}

function jsonValueEqual(a, b) {
  try {
    return canonicalJsonBytes(a).equals(canonicalJsonBytes(b));
  } catch (_) {
    return false;
  }
}

function consume(decisionInput, expectationInput) {
  let decision;
  let validated;
  try {
    decision = decisionInput instanceof Uint8Array ? parseDecisionBytes(decisionInput) : decisionInput;
    validated = validateDecision(decision);
  } catch (err) {
    const code = err instanceof ContractDError ? err.code : 'internal_error';
    return { outcome: 'cannot_establish', reason: 'invalid_decision', error: code };
  }

  let expectation;
  try {
    expectation = validateExpectation(expectationInput);
  } catch (err) {
    const code = err instanceof ContractDError ? err.code : 'internal_error';
    return { outcome: 'cannot_establish', reason: 'invalid_expectation', error: code };
  }

  if (!sameBinding(decision.input_authority, expectation.input_authority, ['kind', 'id', 'immutable_id'])) {
    return { outcome: 'not_applicable', reason: 'input_authority_mismatch' };
  }
  if (!sameBinding(decision.policy, expectation.policy, ['id', 'version'])) {
    return { outcome: 'not_applicable', reason: 'policy_mismatch' };
  }
  if (!sameBinding(decision.target, expectation.target, ['kind', 'id', 'content_sha256'])) {
    return { outcome: 'not_applicable', reason: 'target_mismatch' };
  }

  if (decision.evaluation.state === 'failed') {
    return { outcome: 'evaluation_failed' };
  }

  if (expectation.requested_operation !== validated.normalizedEffect.type) {
    return { outcome: 'not_applicable', reason: 'requested_operation_mismatch' };
  }

  if (Object.prototype.hasOwnProperty.call(expectation, 'effect_params')) {
    const requested = expectation.effect_params;
    const actual = validated.normalizedEffect.params || Object.create(null);
    for (const key of Object.keys(requested)) {
      if (!Object.prototype.hasOwnProperty.call(actual, key) || !jsonValueEqual(requested[key], actual[key])) {
        return { outcome: 'not_applicable', reason: 'requested_effect_params_mismatch' };
      }
    }
  }

  return decision.evaluation.disposition === 'hold'
    ? { outcome: 'hold' }
    : { outcome: 'candidate_for_authorization' };
}

module.exports = {
  ContractDError,
  MAX_CONTAINER_DEPTH,
  VERSION,
  canonicalDecisionBytes,
  canonicalJsonBytes,
  consume,
  parseDecisionBytes,
  parseJsonBytes,
  semanticIdentity,
  validateDecision,
  validateExpectation,
  validateJsonDomain,
};
