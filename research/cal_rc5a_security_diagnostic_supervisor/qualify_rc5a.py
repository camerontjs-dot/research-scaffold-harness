import json, os, pathlib, subprocess, sys, tempfile

HERE=pathlib.Path(__file__).resolve().parent
AP=HERE.parent/"cal_rc5a_security_diagnostic_aperture"
EVAL=HERE/"evaluate_rc5a.py"
CASES=HERE/"HIDDEN-CASE-PROGRAM.json"
PUB=AP/"PUBLIC-KEYS.json"
VEC=AP/"PUBLIC-POSITIVE-VECTORS.json"
POL=AP/"TRUST-POLICY.json"

controls={
 "accept_wrong_role":{"expect":["NORMATIVE_MISMATCH"]},
 "all_refusals_malformed":{"expect":["NORMATIVE_MISMATCH"]},
 "old_rc5_profile_as_schema":{"expect":["NORMATIVE_MISMATCH"]},
 "signature_format_as_malformed":{"expect":["NORMATIVE_MISMATCH"]},
 "generic_diagnostic":{"expect":["DIAGNOSTIC_COLLAPSE"]},
 "transport_sensitive_diagnostic":{"expect":["DIAGNOSTIC_TRANSPORT_INSTABILITY"]}
}

def run(candidate, out, env=None):
    cp=subprocess.run([
      sys.executable,str(EVAL),"--candidate",str(candidate),"--cases",str(CASES),
      "--public-keys",str(PUB),"--public-vectors",str(VEC),"--trust-policy",str(POL),"--out",str(out)
    ],capture_output=True,text=True,env=env)
    data=json.load(open(out))
    return cp.returncode,data,cp.stdout,cp.stderr

result={"profile":"CAL.RC5A/evaluator-qualification.v1","controls":{}}
with tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td)
    code,data,stdout,stderr=run(HERE/"reference_rc5a.py",td/"reference.json")
    result["reference"]={
      "exit_code":code,"scientific_gate_pass":data["scientific_gate_pass"],
      "normative_matches":data["normative_matches"],"case_count":data["case_count"],
      "exceptions":data["exceptions"]
    }
    ok=(code==0 and data["scientific_gate_pass"] and data["normative_matches"]==data["case_count"] and data["exceptions"]==0)
    result["reference"]["pass"]=ok

    all_controls=True
    for mode,spec in controls.items():
        env=dict(os.environ); env["RC5A_WEAK_MODE"]=mode
        code,data,stdout,stderr=run(HERE/"weak_control_rc5a.py",td/(mode+".json"),env)
        kinds=sorted(set(x["kind"] for x in data["failures"]))
        caught=(code!=0 and all(k in kinds for k in spec["expect"]))
        result["controls"][mode]={
          "exit_code":code,"failure_kinds":kinds,"expected_failure_kinds":spec["expect"],"caught":caught
        }
        all_controls=all_controls and caught

    result["all_controls_caught"]=all_controls
    result["local_qualification_pass"]=ok and all_controls
    result["seal_status"]="NOT_SEALED_PENDING_INDEPENDENT_ORACLE_REVIEW"
    pathlib.Path(HERE/"QUALIFICATION-RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["local_qualification_pass"] else 1)
