import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  canonicalJson, consume, normalizeEffect, parseJsonBytes, semanticIdentity,
  semanticProjection, validateDecision, validateFiniteJson, ContractDError
} from '../execution/contract_d_rc6_consumer.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const VALID = JSON.parse(fs.readFileSync(path.join(ROOT,'reference/fixtures/valid.json'),'utf8')).fixtures;
const INVALID = JSON.parse(fs.readFileSync(path.join(ROOT,'reference/fixtures/invalid.json'),'utf8')).fixtures;
const clone = x => structuredClone(x);

function getFixture(name) {
  if (VALID[name]) return clone(VALID[name]);
  if (INVALID[name]) return clone(INVALID[name]);
  throw new Error(`unknown fixture ${name}`);
}
function setPath(obj, p, value) { let x=obj; for(let i=0;i<p.length-1;i++) x=x[p[i]]; x[p.at(-1)]=value; }
function delPath(obj,p) { let x=obj; for(let i=0;i<p.length-1;i++) x=x[p[i]]; delete x[p.at(-1)]; }
function mutate(obj, muts=[]) {
  for (const m of muts) {
    if (m.op==='set') setPath(obj,m.path,m.value);
    else if (m.op==='delete') delPath(obj,m.path);
    else throw new Error(`bad mutation ${m.op}`);
  }
  return obj;
}
function errObs(err) {
  return {accepted:false,error:err instanceof ContractDError ? err.code : 'uncontrolled_exception', exception: err?.name};
}
function validObs(d) {
  const r=validateDecision(d); return r.ok ? {accepted:true} : {accepted:false,error:r.error};
}
function expectationFor(d, spec={}) {
  const e={
    input_authority:clone(d.input_authority), policy:clone(d.policy), target:clone(d.target),
    requested_operation: spec.requested_operation ?? d.effect?.type ?? 'knowledge.add_verified_tag'
  };
  if (spec.effect_params_mode==='explicit') e.effect_params=clone(spec.effect_params ?? {});
  for(const m of spec.mutations ?? []) {
    if(m.op==='set') setPath(e,m.path,m.value); else if(m.op==='delete') delPath(e,m.path);
  }
  if(spec.special==='cycle') e.loop=e;
  if(spec.special==='nonfinite_params') e.effect_params={scope:NaN};
  if(spec.special==='host_only_params') e.effect_params={scope:new Set(['claim'])};
  if(spec.special==='surrogate_operation') e.requested_operation='knowledge.add_verified_tag\ud800';
  if(spec.special==='cycle_params') { const x={}; x.self=x; e.effect_params=x; }
  return e;
}
function nestedLists(count) { let x='leaf'; for(let i=0;i<count;i++) x=[x]; return x; }
function numberFromBits(hex) {
  const b=Buffer.from(hex,'hex');
  return b.readDoubleBE(0);
}
function baseWithDiagnostic(value) { const d=getFixture('source-audit-clear.json'); d.metadata ??={}; d.metadata.diagnostics={number:value}; return d; }

async function run(c) {
  try {
    switch(c.action) {
      case 'validate': return validObs(mutate(getFixture(c.fixture),c.mutations));
      case 'normalize_effect': {
        try { return {accepted:true,effect:normalizeEffect(clone(c.effect))}; } catch(e) { return errObs(e); }
      }
      case 'semantic': {
        const d=mutate(getFixture(c.fixture),c.mutations);
        try { const p=semanticProjection(d); return {accepted:true,projection:p,identity:semanticIdentity(d),canonical_projection_hex:canonicalJson(p).toString('hex')}; } catch(e) { return errObs(e); }
      }
      case 'consume': {
        const d=mutate(getFixture(c.fixture),c.mutations);
        return consume(d,expectationFor(d,c.expectation));
      }
      case 'parse_raw': {
        const bytes=c.hex ? Buffer.from(c.hex,'hex') : Buffer.from(c.raw,'utf8');
        try {
          const d=parseJsonBytes(bytes); const v=validateDecision(d);
          if(!v.ok) return {accepted:false,error:v.error};
          return {accepted:true,canonical_hex:canonicalJson(d).toString('hex'),identity:semanticIdentity(d)};
        } catch(e) { return errObs(e); }
      }
      case 'raw_numeric_token': {
        const d=getFixture('source-audit-clear.json');
        d.metadata.diagnostics={number:'__TOKEN__'};
        let raw=JSON.stringify(d);
        raw=raw.replace('"__TOKEN__"',c.token);
        try {
          const parsed=parseJsonBytes(Buffer.from(raw)); const v=validateDecision(parsed);
          if(!v.ok) return {accepted:false,error:v.error};
          return {accepted:true,canonical_hex:canonicalJson(parsed).toString('hex'),parsed_number:parsed.metadata.diagnostics.number};
        } catch(e) { return errObs(e); }
      }
      case 'host_number': {
        const n = c.bits ? numberFromBits(c.bits) : Number(c.number);
        const d=baseWithDiagnostic(n);
        const v=validateDecision(d);
        if(!v.ok) return {accepted:false,error:v.error};
        try { return {accepted:true,canonical_hex:canonicalJson({n}).toString('hex'),number:n}; } catch(e) { return errObs(e); }
      }
      case 'finite_special': {
        let value;
        if(c.kind==='self_cycle') { value={}; value.self=value; }
        else if(c.kind==='mutual_cycle') { const a={},b={}; a.b=b;b.a=a; value=a; }
        else if(c.kind==='shared') { const s={values:[1,2,3]}; value={a:s,b:s}; }
        else if(c.kind==='depth') value=nestedLists(c.count);
        else if(c.kind==='surrogate') value={x:'\ud800'};
        else if(c.kind==='nonfinite') value={x:Infinity};
        else if(c.kind==='unsafe_integer') value={x:Number(c.number)};
        else throw new Error('bad special');
        try { validateFiniteJson(value); return {accepted:true,canonical_hex:canonicalJson(value).toString('hex')}; } catch(e) { return errObs(e); }
      }
      case 'consume_special': {
        const d=getFixture('source-audit-clear.json');
        if(c.kind==='cycle') { d.metadata.diagnostics={}; d.metadata.diagnostics.loop=d; }
        else if(c.kind==='surrogate') d.metadata.diagnostics={bad:'\ud800'};
        else if(c.kind==='nonfinite') d.metadata.diagnostics={n:Infinity};
        else if(c.kind==='depth') d.metadata.diagnostics={deep:nestedLists(c.nested_count)};
        else throw new Error('bad consume special');
        return consume(d,expectationFor(getFixture('source-audit-clear.json'),{}));
      }
      case 'decision_depth': {
        const d=getFixture('source-audit-clear.json'); d.metadata.diagnostics={deep:nestedLists(c.nested_count)};
        const v=validateDecision(d); return v.ok ? {accepted:true} : {accepted:false,error:v.error};
      }
      case 'metadata_identity': {
        const a=getFixture(c.fixture); const b=clone(a);
        if(c.mode==='remove') delete b.metadata;
        else b.metadata={diagnostics:clone(c.diagnostics ?? {})};
        return {accepted:true,identity_a:semanticIdentity(a),identity_b:semanticIdentity(b),same:semanticIdentity(a)===semanticIdentity(b)};
      }
      default: throw new Error(`unknown action ${c.action}`);
    }
  } catch(e) { return {accepted:false,error:'driver_exception',detail:String(e?.stack??e)}; }
}
const cases=JSON.parse(fs.readFileSync(0,'utf8'));
const out=[];
for(const c of cases) out.push({id:c.id,observation:await run(c)});
process.stdout.write(JSON.stringify(out));
