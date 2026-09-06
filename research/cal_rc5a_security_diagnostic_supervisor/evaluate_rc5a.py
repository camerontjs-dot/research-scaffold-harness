import argparse, importlib.util, json, pathlib, sys

ALLOWED = {
    "MALFORMED","UNSUPPORTED","UNAUTHENTICATED",
    "UNAUTHORIZED_ISSUER","BINDING_MISMATCH","INCOMPATIBLE_PAIR"
}

def load_module(path):
    spec = importlib.util.spec_from_file_location("candidate_rc5a", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

def diag_tuple(result):
    a=result.get("audit_record")
    if not isinstance(a,dict):
        raise AssertionError("missing audit_record")
    vid=a.get("verifier_id"); stage=a.get("diagnostic_stage"); code=a.get("diagnostic_code")
    if not all(isinstance(x,str) and x for x in (vid,stage,code)):
        raise AssertionError("audit_record requires nonempty verifier_id/diagnostic_stage/diagnostic_code")
    return stage,code

def protocol(result):
    p=result.get("protocol_result")
    if not isinstance(p,dict):
        raise AssertionError("missing protocol_result")
    return p

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True)
    ap.add_argument("--cases",required=True)
    ap.add_argument("--public-keys",required=True)
    ap.add_argument("--public-vectors",required=True)
    ap.add_argument("--trust-policy",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    mod=load_module(args.candidate)
    verify=mod.verify_pair
    cases=json.load(open(args.cases))
    public_keys=json.load(open(args.public_keys))
    public_vectors=json.load(open(args.public_vectors))
    trust_policy=json.load(open(args.trust_policy))

    rows=[]; failures=[]
    by_id={}
    base_request=public_vectors["semantic_request"]
    base_atom_raw=json.dumps(public_vectors["atom"]["complete_serialized_receipt"],ensure_ascii=False,separators=(",",":"))
    base_prop_raw=json.dumps(public_vectors["proposition"]["complete_serialized_receipt"],ensure_ascii=False,separators=(",",":"))
    for c in cases["cases"]:
        try:
            semantic_request=json.loads(json.dumps(base_request))
            atom_obj=json.loads(base_atom_raw)
            prop_obj=json.loads(base_prop_raw)
            atom_raw=base_atom_raw
            prop_raw=base_prop_raw
            op=c.get("op",{"type":"none"})
            typ=op["type"]
            if typ=="truncate_atom_json":
                atom_raw=base_atom_raw[:-int(op.get("chars",1))]
            elif typ=="duplicate_atom_envelope_key":
                atom_raw=base_atom_raw[:-1]+","+json.dumps(op["key"])+":"+json.dumps(op["value"])+"}"
            elif typ=="delete_atom_envelope_field":
                atom_obj.pop(op["field"],None)
                atom_raw=json.dumps(atom_obj,ensure_ascii=False,indent=2 if op.get("pretty") else None,separators=None if op.get("pretty") else (",",":"))
            elif typ=="set_atom_statement_field":
                atom_obj["statement"][op["field"]]=op["value"]
                atom_raw=json.dumps(atom_obj,ensure_ascii=False,separators=(",",":"))
            elif typ=="set_prop_statement_field":
                prop_obj["statement"][op["field"]]=op["value"]
                prop_raw=json.dumps(prop_obj,ensure_ascii=False,separators=(",",":"))
            elif typ=="set_atom_envelope_field":
                atom_obj[op["field"]]=op["value"]
                atom_raw=json.dumps(atom_obj,ensure_ascii=False,separators=(",",":"))
            elif typ=="atom_raw_override":
                atom_raw=op["raw"]
            elif typ=="prop_raw_override":
                prop_raw=op["raw"]
            elif typ=="truncate_atom_signature":
                atom_obj["signature_base64url"]=atom_obj["signature_base64url"][:-int(op.get("chars",1))]
                atom_raw=json.dumps(atom_obj,ensure_ascii=False,separators=(",",":"))
            elif typ=="flip_atom_signature_first_byte":
                import base64
                x=atom_obj["signature_base64url"]
                sig=bytearray(base64.urlsafe_b64decode(x+"="*((4-len(x)%4)%4)))
                sig[0]^=1
                atom_obj["signature_base64url"]=base64.urlsafe_b64encode(bytes(sig)).decode().rstrip("=")
                atom_raw=json.dumps(atom_obj,ensure_ascii=False,indent=2 if op.get("pretty") else None,separators=None if op.get("pretty") else (",",":"))
            elif typ=="set_request_path":
                cur=semantic_request
                for key in op["path"][:-1]: cur=cur[key]
                cur[op["path"][-1]]=op["value"]
            elif typ=="pair_claim_override":
                semantic_request["proposition"]["claim_id"]=op["proposition_claim_id"]
                prop_raw=op["prop_raw"]
            elif typ!="none":
                raise AssertionError(f"unknown hidden op {typ}")
            r=verify(semantic_request,atom_raw,prop_raw,public_keys,trust_policy)
            p=protocol(r); dt=diag_tuple(r)
            expected=c["expected_failure_class"]
            if expected is None:
                ok=(p.get("decision")=="ACCEPT" and p.get("failure_class") is None and
                    p.get("claim_id")=="claim-001" and p.get("atom_id")=="atom-001")
            else:
                ok=(p.get("decision")=="REFUSE" and p.get("failure_class")==expected and expected in ALLOWED)
            row={"case_id":c["case_id"],"expected_failure_class":expected,
                 "observed_protocol_result":p,"diagnostic_tuple":list(dt),"normative_match":ok}
            if not ok: failures.append({"case_id":c["case_id"],"kind":"NORMATIVE_MISMATCH"})
        except Exception as e:
            row={"case_id":c["case_id"],"exception":f"{type(e).__name__}: {e}","normative_match":False}
            failures.append({"case_id":c["case_id"],"kind":"EXCEPTION"})
        rows.append(row); by_id[c["case_id"]]=row

    # diagnostic stability for declared transport variants
    for c in cases["cases"]:
        if c.get("transport_variant_of"):
            a=by_id[c["case_id"]]; b=by_id[c["transport_variant_of"]]
            stable=(a.get("diagnostic_tuple")==b.get("diagnostic_tuple"))
            a["transport_diagnostic_stable"]=stable
            if not stable: failures.append({"case_id":c["case_id"],"kind":"DIAGNOSTIC_TRANSPORT_INSTABILITY"})

    # within selected same-class subcauses, require at least two distinct diagnostic tuples
    groups={
      "MALFORMED":["M-INVALID-JSON","M-DUPLICATE-KEY","M-MISSING-FIELD","M-UNKNOWN-STATEMENT-FIELD"],
      "UNSUPPORTED":["U-RECEIPT-TYPE","U-SCHEMA-MAJOR","U-SIGNATURE-PROFILE"],
      "UNAUTHENTICATED":["A-DIGEST-MISMATCH","A-UNKNOWN-SIGNER","A-SIGNATURE-FORMAT","A-SIGNATURE-INVALID"],
      "BINDING_MISMATCH":["B-ATOM-PROJECTION","B-PROP-PROJECTION","B-ATOM-ID"]
    }
    diagnostic_discrimination={}
    for cls,ids in groups.items():
        tuples=[tuple(by_id[i].get("diagnostic_tuple",[])) for i in ids]
        distinct=len(set(tuples))
        ok=distinct>=2
        diagnostic_discrimination[cls]={"distinct_tuples":distinct,"required_minimum":2,"pass":ok}
        if not ok: failures.append({"case_id":cls,"kind":"DIAGNOSTIC_COLLAPSE"})

    out={
      "profile":"CAL.RC5A/evaluator-result.v1",
      "case_count":len(rows),
      "normative_matches":sum(1 for r in rows if r.get("normative_match")),
      "exceptions":sum(1 for r in rows if "exception" in r),
      "diagnostic_discrimination":diagnostic_discrimination,
      "failures":failures,
      "rows":rows,
      "scientific_gate_pass":not failures
    }
    pathlib.Path(args.out).write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:out[k] for k in ["case_count","normative_matches","exceptions","diagnostic_discrimination","scientific_gate_pass"]},indent=2))
    raise SystemExit(0 if not failures else 1)

if __name__=="__main__":
    main()
