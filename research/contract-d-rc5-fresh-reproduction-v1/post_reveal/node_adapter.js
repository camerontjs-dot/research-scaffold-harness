'use strict';

const fs = require('node:fs');
const path = require('node:path');

const modulePath = process.argv[2];
if (!modulePath) throw new Error('module path required');
const d = require(path.resolve(modulePath));

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function resultOf(fn) {
  try {
    return { status: 'accept', value: fn() };
  } catch (err) {
    return {
      status: 'reject_controlled',
      error: err && err.code ? err.code : (err && err.name ? err.name : 'error'),
    };
  }
}

function f64FromHex(bits) {
  const b = Buffer.from(bits, 'hex');
  return b.readDoubleBE(0);
}

function nestedLists(count) {
  let x = 'leaf';
  for (let i = 0; i < count; i += 1) x = [x];
  return x;
}

function run(req) {
  switch (req.action) {
    case 'validate':
      return resultOf(() => { d.validateDecision(req.decision); return 'accepted'; });
    case 'consume':
      return { status: 'accept', value: d.consume(req.decision, req.expectation).outcome };
    case 'identity':
      return resultOf(() => d.semanticIdentity(req.decision));
    case 'canonical_value':
      return resultOf(() => d.canonicalJsonBytes(req.value).toString('utf8'));
    case 'canonical_decision':
      return resultOf(() => d.canonicalDecisionBytes(req.decision).toString('utf8'));
    case 'parse_bytes':
      return resultOf(() => {
        const raw = Buffer.from(req.hex, 'hex');
        const parsed = d.parseDecisionBytes(raw);
        return d.canonicalDecisionBytes(parsed).toString('utf8');
      });
    case 'number_bits':
      return resultOf(() => d.canonicalJsonBytes({ n: f64FromHex(req.bits) }).toString('utf8'));
    case 'self_cycle':
      return resultOf(() => {
        const x = clone(req.base);
        const cycle = {};
        cycle.self = cycle;
        x.metadata.diagnostics = cycle;
        d.validateDecision(x);
        return 'accepted';
      });
    case 'mutual_cycle':
      return resultOf(() => {
        const x = clone(req.base);
        const left = [];
        const right = { left };
        left.push(right);
        x.metadata.diagnostics = { cycle: left };
        d.validateDecision(x);
        return 'accepted';
      });
    case 'shared_acyclic':
      return resultOf(() => {
        const x = clone(req.base);
        const shared = { values: [1, 2, 3] };
        x.metadata.diagnostics = { a: shared, b: shared };
        d.validateDecision(x);
        return 'accepted';
      });
    case 'depth':
      return resultOf(() => {
        const x = clone(req.base);
        x.metadata.diagnostics = { deep: nestedLists(req.count) };
        d.validateDecision(x);
        return 'accepted';
      });
    case 'consume_nonfinite_param': {
      const e = clone(req.expectation);
      e.effect_params = { scope: NaN };
      return { status: 'accept', value: d.consume(req.decision, e).outcome };
    }
    case 'consume_host_only_param': {
      const e = clone(req.expectation);
      e.effect_params = { scope: new Set(['claim']) };
      return { status: 'accept', value: d.consume(req.decision, e).outcome };
    }
    case 'consume_surrogate_operation': {
      const e = clone(req.expectation);
      e.requested_operation = 'knowledge.add_verified_tag\ud800';
      return { status: 'accept', value: d.consume(req.decision, e).outcome };
    }
    case 'host_integer_valued_binary64':
      return resultOf(() => d.canonicalJsonBytes({ n: Number(req.decimal) }).toString('utf8'));
    default:
      throw new Error(`unknown action ${req.action}`);
  }
}

const req = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(run(req)));
