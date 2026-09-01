from __future__ import annotations
import copy, json, math, os, struct, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
REF=ROOT/'reference'
sys.path.insert(0,str(REF/'vendor'))
sys.path.insert(0,str(REF))
from contract_d_core import ContractDError, canonical_json_bytes, semantic_identity, semantic_projection, validate_decision, validate_effect, validate_json_value
from contract_d_consume import ApplicabilityExpectation, consume
from contract_d_validate import parse_json_bytes
VALID=json.loads((REF/'fixtures/valid.json').read_text())['fixtures']
INVALID=json.loads((REF/'fixtures/invalid.json').read_text())['fixtures']

def fixture(name): return copy.deepcopy(VALID.get(name,INVALID.get(name)))
def set_path(obj,p,val):
    x=obj
    for k in p[:-1]: x=x[k]
    x[p[-1]]=val
def del_path(obj,p):
    x=obj
    for k in p[:-1]: x=x[k]
    del x[p[-1]]
def mutate(obj,muts=None):
    for m in muts or []:
        (set_path(obj,m['path'],m.get('value')) if m['op']=='set' else del_path(obj,m['path']))
    return obj
def err(e): return {'accepted':False,'error':e.code if isinstance(e,ContractDError) else 'uncontrolled_exception','exception':type(e).__name__}
def expectation_for(d,spec=None):
    spec=spec or {}
    e=ApplicabilityExpectation(copy.deepcopy(d['input_authority']),copy.deepcopy(d['policy']),copy.deepcopy(d['target']),spec.get('requested_operation',d.get('effect',{}).get('type','knowledge.add_verified_tag')), None)
    if spec.get('effect_params_mode')=='explicit': object.__setattr__(e,'effect_params',copy.deepcopy(spec.get('effect_params',{})))
    for m in spec.get('mutations',[]):
        target=e.input_authority if m['path'][0]=='input_authority' else e.policy if m['path'][0]=='policy' else e.target if m['path'][0]=='target' else None
        if target is not None:
            sub=m['path'][1:]
            if m['op']=='set': set_path(target,sub,m.get('value'))
            else: del_path(target,sub)
    sp=spec.get('special')
    if sp=='nonfinite_params': object.__setattr__(e,'effect_params',{'scope':float('nan')})
    elif sp=='host_only_params': object.__setattr__(e,'effect_params',{'scope':{'claim'}})
    elif sp=='surrogate_operation': object.__setattr__(e,'requested_operation','knowledge.add_verified_tag\ud800')
    elif sp=='cycle_params':
        x={}; x['self']=x; object.__setattr__(e,'effect_params',x)
    return e
def nested_lists(count):
    x='leaf'
    for _ in range(count): x=[x]
    return x
def fbits(h): return struct.unpack('>d',bytes.fromhex(h))[0]

def run(c):
    try:
        a=c['action']
        if a=='validate':
            d=mutate(fixture(c['fixture']),c.get('mutations'))
            try: validate_decision(d); return {'accepted':True}
            except Exception as e: return err(e)
        if a=='normalize_effect':
            try: return {'accepted':True,'effect':validate_effect(copy.deepcopy(c['effect']))}
            except Exception as e: return err(e)
        if a=='semantic':
            d=mutate(fixture(c['fixture']),c.get('mutations'))
            try:
                p=semantic_projection(d); return {'accepted':True,'projection':p,'identity':semantic_identity(d),'canonical_projection_hex':canonical_json_bytes(p).hex()}
            except Exception as e: return err(e)
        if a=='consume':
            d=mutate(fixture(c['fixture']),c.get('mutations'))
            e=expectation_for(d,c.get('expectation'))
            return consume(d,e)
        if a=='parse_raw':
            b=bytes.fromhex(c['hex']) if c.get('hex') else c['raw'].encode()
            try:
                d=parse_json_bytes(b); return {'accepted':True,'canonical_hex':canonical_json_bytes(d).hex(),'identity':semantic_identity(d)}
            except Exception as e: return err(e)
        if a=='raw_numeric_token':
            d=fixture('source-audit-clear.json'); d['metadata']['diagnostics']={'number':'__TOKEN__'}
            raw=json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('"__TOKEN__"',c['token']).encode()
            try:
                p=parse_json_bytes(raw); return {'accepted':True,'canonical_hex':canonical_json_bytes(p).hex(),'parsed_number':p['metadata']['diagnostics']['number']}
            except Exception as e: return err(e)
        if a=='host_number':
            n=fbits(c['bits']) if c.get('bits') else (int(c['number']) if c.get('reference_kind','float')=='int' else float(c['number']))
            d=fixture('source-audit-clear.json'); d['metadata']['diagnostics']={'number':n}
            try:
                validate_decision(d); return {'accepted':True,'canonical_hex':canonical_json_bytes({'n':n}).hex(),'number':n}
            except Exception as e: return err(e)
        if a=='finite_special':
            k=c['kind']
            if k=='self_cycle': value={}; value['self']=value
            elif k=='mutual_cycle':
                a1=[]; b={'left':a1}; a1.append(b); value=a1
            elif k=='shared':
                s={'values':[1,2,3]}; value={'a':s,'b':s}
            elif k=='depth': value=nested_lists(c['count'])
            elif k=='surrogate': value={'x':'\ud800'}
            elif k=='nonfinite': value={'x':float('inf')}
            elif k=='unsafe_integer': value={'x':int(c['number'])}
            else: raise ValueError('bad special')
            try: validate_json_value(value); return {'accepted':True,'canonical_hex':canonical_json_bytes(value).hex()}
            except Exception as e: return err(e)
        if a=='consume_special':
            d=fixture('source-audit-clear.json')
            if c['kind']=='cycle': d['metadata']['diagnostics']={}; d['metadata']['diagnostics']['loop']=d
            elif c['kind']=='surrogate': d['metadata']['diagnostics']={'bad':'\ud800'}
            elif c['kind']=='nonfinite': d['metadata']['diagnostics']={'n':float('inf')}
            elif c['kind']=='depth': d['metadata']['diagnostics']={'deep':nested_lists(c['nested_count'])}
            else: raise ValueError('bad consume special')
            return consume(d,expectation_for(fixture('source-audit-clear.json'),{}))
        if a=='decision_depth':
            d=fixture('source-audit-clear.json'); d['metadata']['diagnostics']={'deep':nested_lists(c['nested_count'])}
            try: validate_decision(d); return {'accepted':True}
            except Exception as e: return err(e)
        if a=='metadata_identity':
            a1=fixture(c['fixture']); b=copy.deepcopy(a1)
            if c['mode']=='remove': b.pop('metadata',None)
            else: b['metadata']={'diagnostics':copy.deepcopy(c.get('diagnostics',{}))}
            ia,ib=semantic_identity(a1),semantic_identity(b); return {'accepted':True,'identity_a':ia,'identity_b':ib,'same':ia==ib}
        raise ValueError(f"unknown action {a}")
    except Exception as e: return {'accepted':False,'error':'driver_exception','detail':repr(e)}

cases=json.load(sys.stdin)
json.dump([{'id':c['id'],'observation':run(c)} for c in cases],sys.stdout,separators=(',',':'),ensure_ascii=False)
