import importlib.util, os, pathlib, sys

HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("reference_rc5a_for_weak", HERE/"reference_rc5a.py")
ref=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=ref
spec.loader.exec_module(ref)

def verify_pair(req, atom_raw, prop_raw, public_keys, trust_policy):
    r=ref.verify_pair(req,atom_raw,prop_raw,public_keys,trust_policy)
    mode=os.environ.get("RC5A_WEAK_MODE","")
    p=r["protocol_result"]; a=r["audit_record"]
    if mode=="accept_wrong_role" and p.get("failure_class")=="UNAUTHORIZED_ISSUER":
        r["protocol_result"]={"decision":"ACCEPT","failure_class":None,"claim_id":"claim-001","atom_id":"atom-001"}
    elif mode=="all_refusals_malformed" and p.get("decision")=="REFUSE":
        p["failure_class"]="MALFORMED"
    elif mode=="old_rc5_profile_as_schema" and p.get("failure_class")=="UNSUPPORTED":
        p["failure_class"]="MALFORMED"
    elif mode=="signature_format_as_malformed" and "SIGNATURE_FORMAT" in a.get("diagnostic_code",""):
        p["failure_class"]="MALFORMED"
    elif mode=="generic_diagnostic" and p.get("decision")=="REFUSE":
        a["diagnostic_stage"]="verify"; a["diagnostic_code"]="REFUSED"
    elif mode=="transport_sensitive_diagnostic" and p.get("decision")=="REFUSE":
        # Deliberately make diagnostics depend on raw transport length.
        a["diagnostic_code"]=a["diagnostic_code"]+f"_LEN_{len(atom_raw)}_{len(prop_raw)}"
    return r
