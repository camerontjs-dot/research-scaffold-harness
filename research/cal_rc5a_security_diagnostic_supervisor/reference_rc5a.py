import base64, hashlib, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

CTX="cal.rc5a.asymmetric-two-receipt.strict-comparison.v1"
CLAIM_NS="cal.rc5a.experimental.claims.v1"
AUTH="CAL.RC8J/claim-bound@8e75c6782bb95c3763d06230b9c5df2b6af44054:blob:f55156e43e0c1b4a7868bc8339585b8892edda38"
FIELDS=["execution_state","evidence_admitted","authority_subject_id","raw_source_id","authority_subject_source_id","raw_bundle_id","authority_subject_bundle_id","raw_passage_id","authority_subject_passage_id","admitted_passage_span","raw_claim_id","authority_subject_claim_id","target_atom_id","authority_subject_atom_id","proposal","assertion","operator","field_warrants","required_fields","composition","aperture"]

def _utf16(s): return s.encode("utf-16-be")
def _jcs(o):
    if o is None:return b"null"
    if o is True:return b"true"
    if o is False:return b"false"
    if isinstance(o,int) and not isinstance(o,bool):
        if not(-9007199254740991<=o<=9007199254740991):raise ValueError
        return str(o).encode()
    if isinstance(o,float):raise ValueError
    if isinstance(o,str):o.encode();return json.dumps(o,ensure_ascii=False,separators=(",",":")).encode()
    if isinstance(o,list):return b"["+b",".join(_jcs(x) for x in o)+b"]"
    if isinstance(o,dict):
        return b"{"+b",".join(json.dumps(k,ensure_ascii=False).encode()+b":"+_jcs(o[k]) for k in sorted(o,key=_utf16))+b"}"
    raise ValueError

def _loads(raw):
    def hook(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise RuntimeError("DUP")
            d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=hook)

def _out(dec,cls,code,stage,claim=None,atom=None):
    p={"decision":dec,"failure_class":cls}
    if dec=="ACCEPT":p.update(claim_id=claim,atom_id=atom)
    return {"protocol_result":p,"audit_record":{"verifier_id":"reference-rc5a-v1","diagnostic_stage":stage,"diagnostic_code":code}}

def _struct(r,kind):
    if not isinstance(r,dict) or set(r)!={"statement","statement_digest_sha256","signature_base64url"}: return False
    s=r["statement"]
    if not isinstance(s,dict) or not isinstance(r["statement_digest_sha256"],str) or not isinstance(r["signature_base64url"],str):return False
    if kind=="atom":
        req={"receipt_type","schema_major","context_id","signature_profile","authority_profile_id","issuer_key_id","authority_status","authority_reason","claim_id","atom_id","atom_projection"}
    else:
        req={"receipt_type","schema_major","context_id","signature_profile","claim_namespace","issuer_key_id","claim_id","proposition_projection"}
    return set(s)==req

def verify_pair(req, atom_raw, prop_raw, public_keys, trust_policy):
    # parse/struct
    try:a=_loads(atom_raw)
    except RuntimeError:return _out("REFUSE","MALFORMED","DUPLICATE_JSON_KEY","transport")
    except Exception:return _out("REFUSE","MALFORMED","INVALID_JSON","transport")
    try:p=_loads(prop_raw)
    except RuntimeError:return _out("REFUSE","MALFORMED","DUPLICATE_JSON_KEY","transport")
    except Exception:return _out("REFUSE","MALFORMED","INVALID_JSON","transport")
    if not isinstance(req,dict) or set(req)!={"context_id","authority_case","proposition"}:return _out("REFUSE","MALFORMED","INVALID_INPUT","structure")
    if not _struct(a,"atom") or not _struct(p,"prop"):return _out("REFUSE","MALFORMED","STRUCTURE_INVALID","structure")
    s=a["statement"]; t=p["statement"]
    # nested shapes
    if not isinstance(s.get("atom_projection"),dict) or set(s["atom_projection"])!=set(FIELDS):return _out("REFUSE","MALFORMED","ATOM_STRUCTURE","structure")
    if not isinstance(t.get("proposition_projection"),dict) or set(t["proposition_projection"])!={"family","lhs_entity","rhs_entity","comparison_direction"}:return _out("REFUSE","MALFORMED","PROP_STRUCTURE","structure")
    # profile
    expected_atom={"receipt_type":"CAL.AtomWarrant/v1","schema_major":1,"context_id":CTX,"signature_profile":"Ed25519","authority_profile_id":AUTH,"authority_status":"WARRANTED","authority_reason":"ALL_REQUIRED_WARRANT_ESTABLISHED"}
    for k,v in expected_atom.items():
        if s.get(k)!=v:return _out("REFUSE","UNSUPPORTED",f"ATOM_PROFILE_{k}","profile")
    expected_prop={"receipt_type":"CAL.PropositionBinding/v1","schema_major":1,"context_id":CTX,"signature_profile":"Ed25519","claim_namespace":CLAIM_NS}
    for k,v in expected_prop.items():
        if t.get(k)!=v:return _out("REFUSE","UNSUPPORTED",f"PROP_PROFILE_{k}","profile")
    # auth helper
    keys={x["key_id"]:x for x in public_keys["keys"]}
    def auth(r, label):
        st=r["statement"]
        try:cb=_jcs(st)
        except Exception:return ("UNAUTHENTICATED",f"{label}_JCS","canonicalization")
        dig=r["statement_digest_sha256"]
        if not re_full_hex64(dig):return ("UNAUTHENTICATED",f"{label}_DIGEST_FORMAT","integrity")
        if hashlib.sha256(cb).hexdigest()!=dig:return ("UNAUTHENTICATED",f"{label}_DIGEST_MISMATCH","integrity")
        kid=st["issuer_key_id"]
        if kid not in keys:return ("UNAUTHENTICATED",f"{label}_UNKNOWN_SIGNER","key_lookup")
        sigs=r["signature_base64url"]
        try:
            if "=" in sigs:return ("UNAUTHENTICATED",f"{label}_SIGNATURE_FORMAT","signature_input")
            sig=base64.urlsafe_b64decode(sigs+"="*((4-len(sigs)%4)%4))
            if len(sig)!=64:return ("UNAUTHENTICATED",f"{label}_SIGNATURE_FORMAT","signature_input")
        except Exception:return ("UNAUTHENTICATED",f"{label}_SIGNATURE_FORMAT","signature_input")
        try:
            pk=base64.urlsafe_b64decode(keys[kid]["public_key_base64url"]+"==")
            Ed25519PublicKey.from_public_bytes(pk).verify(sig,cb)
        except Exception:return ("UNAUTHENTICATED",f"{label}_SIGNATURE_INVALID","signature")
        return None
    import re
    def re_full_hex64_local(x): return bool(re.fullmatch(r"[0-9a-f]{64}",x or ""))
    global re_full_hex64
    re_full_hex64=re_full_hex64_local
    for rr,label in [(a,"ATOM"),(p,"PROP")]:
        z=auth(rr,label)
        if z:return _out("REFUSE",z[0],z[1],z[2])
    # authz
    def allowed(st):
        for e in trust_policy["authorizations"]:
            if e["key_id"]!=st["issuer_key_id"] or e["receipt_type"]!=st["receipt_type"] or e["schema_major"]!=st["schema_major"] or e["context_id"]!=st["context_id"]: continue
            if st["receipt_type"]=="CAL.AtomWarrant/v1" and e.get("authority_profile_id")==st.get("authority_profile_id"):return True
            if st["receipt_type"]=="CAL.PropositionBinding/v1" and e.get("claim_namespace")==st.get("claim_namespace"):return True
        return False
    if not allowed(s):return _out("REFUSE","UNAUTHORIZED_ISSUER","ATOM_UNAUTHORIZED_ISSUER","issuer_policy")
    if not allowed(t):return _out("REFUSE","UNAUTHORIZED_ISSUER","PROP_UNAUTHORIZED_ISSUER","issuer_policy")
    # binding
    ac=req["authority_case"]; pr=req["proposition"]
    try: ap={k:ac[k] for k in FIELDS}
    except Exception:return _out("REFUSE","MALFORMED","INVALID_INPUT","structure")
    if s["atom_projection"]!=ap:return _out("REFUSE","BINDING_MISMATCH","ATOM_PROJECTION_MISMATCH","semantic_binding")
    if s["claim_id"]!=ac.get("raw_claim_id"):return _out("REFUSE","BINDING_MISMATCH","ATOM_CLAIM_MISMATCH","semantic_binding")
    if s["atom_id"]!=ac.get("target_atom_id"):return _out("REFUSE","BINDING_MISMATCH","ATOM_ID_MISMATCH","semantic_binding")
    pp={k:pr.get(k) for k in ["family","lhs_entity","rhs_entity","comparison_direction"]}
    if t["proposition_projection"]!=pp:return _out("REFUSE","BINDING_MISMATCH","PROP_PROJECTION_MISMATCH","semantic_binding")
    if t["claim_id"]!=pr.get("claim_id"):return _out("REFUSE","BINDING_MISMATCH","PROP_CLAIM_MISMATCH","semantic_binding")
    # pair
    if req["context_id"]!=CTX or s["context_id"]!=req["context_id"] or t["context_id"]!=req["context_id"]:
        return _out("REFUSE","INCOMPATIBLE_PAIR","PAIR_CONTEXT","pair")
    if not(s["claim_id"]==t["claim_id"]==pr.get("claim_id")==ac.get("raw_claim_id")):
        return _out("REFUSE","INCOMPATIBLE_PAIR","PAIR_CLAIM","pair")
    return _out("ACCEPT",None,"ACCEPT","complete",s["claim_id"],s["atom_id"])
