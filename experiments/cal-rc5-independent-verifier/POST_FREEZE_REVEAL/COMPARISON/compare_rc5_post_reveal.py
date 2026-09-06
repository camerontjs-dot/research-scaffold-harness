#!/usr/bin/env python3
import base64, copy, hashlib, importlib.util, json, sys, traceback
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT=Path('/mnt/data/rc5_post_reveal')
PACKET_PATH=ROOT/'reveal/packet.json'
VERIFIER_PATH=ROOT/'frozen/rc5_verifier.py'
PK_PATH=ROOT/'public/PUBLIC-KEYS.json'
TP_PATH=ROOT/'public/TRUST-POLICY.json'

spec=importlib.util.spec_from_file_location('rc5_frozen', VERIFIER_PATH)
v=importlib.util.module_from_spec(spec); sys.modules[spec.name]=v; spec.loader.exec_module(v)

class Dup(Exception): pass
def no_dup(pairs):
    d={}
    for k,val in pairs:
        if k in d: raise Dup(k)
        d[k]=val
    return d

packet_raw=PACKET_PATH.read_bytes()
packet=json.loads(packet_raw.decode('utf-8'), object_pairs_hook=no_dup)
pk_raw=PK_PATH.read_bytes(); tp_raw=TP_PATH.read_bytes()
public_key_obj=json.loads(pk_raw)

def request_raw(req):
    return json.dumps(req, ensure_ascii=False, separators=(',',':'))

def expected_fields_match(observed, expected):
    if not isinstance(expected, dict) or not isinstance(observed, dict):
        return observed == expected
    return all(k in observed and observed[k] == val for k,val in expected.items())

def run_case(c):
    kind=c['kind']
    if kind=='pair':
        obs=v.verify_pair(request_raw(c['request']), c['atom_receipt'], c['proposition_receipt'], pk_raw, tp_raw)
        return obs, expected_fields_match(obs,c['expected'])
    if kind=='atom':
        obs=v.verify_atom_receipt(request_raw(c['request']), c['receipt'], pk_raw, tp_raw)
        return obs, expected_fields_match(obs,c['expected'])
    if kind=='proposition':
        obs=v.verify_proposition_receipt(request_raw(c['request']), c['receipt'], pk_raw, tp_raw)
        return obs, expected_fields_match(obs,c['expected'])
    if kind=='proposition_raw':
        obs=v.verify_proposition_receipt(request_raw(c['request']), c['receipt_raw'], pk_raw, tp_raw)
        return obs, expected_fields_match(obs,c['expected'])
    if kind=='evidence_preservation':
        outcomes=[]
        for req, receipt in zip(c['requests'],c['receipts']):
            outcomes.append(v.verify_proposition_receipt(request_raw(req), receipt, pk_raw, tp_raw))
        obs={'first':outcomes[0]['code'],'second':outcomes[1]['code'],'aggregate':'UNSUPPORTED_NO_UNIQUENESS_OR_EQUIVOCATION_RULE'}
        return obs, obs==c['expected']
    if kind=='mutation_matrix':
        rows=[]
        all_match=True
        for m in c['mutations']:
            obs=v.verify_pair(request_raw(m['request']), c['atom_receipt'], c['proposition_receipt'], pk_raw, tp_raw)
            match=expected_fields_match(obs,m['expected'])
            rows.append({'field':m['field'],'expected':m['expected'],'observed':obs,'match':match})
            all_match &= match
        return {'mutations':rows}, all_match
    raise ValueError('unknown kind '+kind)

def independent_jcs(obj):
    # Restricted packet control statements have ASCII member names and no floats.
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode('utf-8')

def dec64(s):
    return base64.urlsafe_b64decode(s+'='*((4-len(s)%4)%4))

def weak_unscoped(receipt_text):
    r=json.loads(receipt_text)
    sig=dec64(r['signature_base64url'])
    msg=independent_jcs(r['statement'])
    for e in public_key_obj['keys']:
        try:
            Ed25519PublicKey.from_public_bytes(dec64(e['public_key_base64url'])).verify(sig,msg)
            return {'decision':'ACCEPT','validating_key_id':e['key_id']}
        except InvalidSignature:
            pass
    return {'decision':'REFUSE'}

def verify_hidden_unknown_signature(c):
    r=json.loads(c['receipt']); e=c['hidden_cryptographic_validity_key']
    rawkey=dec64(e['public_key_base64url'])
    fp=hashlib.sha256(rawkey).hexdigest()
    ok_fp=(fp==e['public_key_sha256'])
    try:
        Ed25519PublicKey.from_public_bytes(rawkey).verify(dec64(r['signature_base64url']), independent_jcs(r['statement']))
        sig_ok=True
    except Exception:
        sig_ok=False
    return {'fingerprint_match':ok_fp,'signature_valid':sig_ok}

results=[]
for c in packet['cases']:
    try:
        obs,match=run_case(c)
        results.append({'id':c['id'],'kind':c['kind'],'oracle_rule':c['oracle_rule'],'expected':c.get('expected'),'observed':obs,'match':match,'exception':None})
    except Exception as exc:
        results.append({'id':c['id'],'kind':c['kind'],'oracle_rule':c['oracle_rule'],'expected':c.get('expected'),'observed':None,'match':False,'exception':repr(exc),'traceback':traceback.format_exc()})

h05=next(c for c in packet['cases'] if c['id'].startswith('H05'))
h06=next(c for c in packet['cases'] if c['id'].startswith('H06'))
h04=next(c for c in packet['cases'] if c['id'].startswith('H04'))
controls={
 'positive_control': next(r for r in results if r['id'].startswith('H16')),
 'weak_authority_control': {
   'H05': {'weak':weak_unscoped(h05['receipt']),'weak_expected':h05['weak_expected'],'candidate':next(r for r in results if r['id'].startswith('H05'))['observed']},
   'H06': {'weak':weak_unscoped(h06['receipt']),'weak_expected':h06['weak_expected'],'candidate':next(r for r in results if r['id'].startswith('H06'))['observed']},
 },
 'unknown_signer_cryptographic_validity': verify_hidden_unknown_signature(h04),
 'mutation_sensitivity': {
   'H20_all_match':next(r for r in results if r['id'].startswith('H20'))['match'],
   'H21_all_match':next(r for r in results if r['id'].startswith('H21'))['match'],
 },
 'representation_invariance': {
   'H18':next(r for r in results if r['id'].startswith('H18'))['match'],
   'H19':next(r for r in results if r['id'].startswith('H19'))['match'],
 },
 'evidence_preservation':next(r for r in results if r['id'].startswith('H17')),
}
output={'packet_sha256':hashlib.sha256(packet_raw).hexdigest(),'cases':results,'controls':controls,'mismatch_ids':[r['id'] for r in results if not r['match']],'exception_ids':[r['id'] for r in results if r.get('exception')]}
( ROOT/'comparison-observed.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'mismatch_ids':output['mismatch_ids'],'exception_ids':output['exception_ids'],'controls':controls},ensure_ascii=False,indent=2))
