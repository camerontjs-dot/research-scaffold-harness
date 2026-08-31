import copy, json, math, unittest
import contract_d_independent as c
import weak_consumers as w

S1='sha256:'+'1'*64; S2='sha256:'+'2'*64

def dec(effect='knowledge.add_verified_tag', disposition='clear', scope='claim', state='completed'):
    d={'contract_d_version':'0.3.0-rc4','input_authority':{'kind':'contract-c','id':'c1','immutable_id':'result-set:'+'a'*64},'policy':{'id':'mainframe.source-audit','version':'1'},'target':{'kind':'knowledge','id':'k1','content_sha256':S1},'evaluation':{'state':state}}
    if state=='completed':
        d['evaluation']['disposition']=disposition; d['effect']={'type':effect,'version':'1'}
        if effect=='knowledge.add_verified_tag' and scope is not None: d['effect']['params']={'scope':scope}
    return d

def call(d, op=None, params='ABSENT', **kw):
    args={'expected_input_authority':copy.deepcopy(d['input_authority']),'expected_policy':copy.deepcopy(d['policy']),'expected_target':copy.deepcopy(d['target']),'requested_operation':op if op is not None else d.get('effect',{}).get('type','unused')}
    args.update(kw)
    if params!='ABSENT': args['requested_effect_params']=params
    return c.consume(d,**args)

class RC4(unittest.TestCase):
    def test_public_conformance_and_states(self):
        clear=dec(); obj=dec(scope='object'); hold=dec(disposition='hold'); failed=dec(state='failed')
        cases=[(clear,None,{'scope':'claim'},'candidate_for_authorization'),(obj,None,'ABSENT','candidate_for_authorization'),(obj,None,{'scope':'claim'},'not_applicable'),(hold,'task.dispatch','ABSENT','not_applicable'),(hold,None,'ABSENT','hold')]
        for d,op,p,want in cases:
            with self.subTest(want=want): self.assertEqual(call(d,op,p),want)
        t=copy.deepcopy(clear['target']); t['content_sha256']=S2
        self.assertEqual(call(clear,params={'scope':'claim'},expected_target=t),'not_applicable')
        self.assertEqual(call(failed),'evaluation_failed'); self.assertNotEqual(call(hold),call(failed))
        for e in ('knowledge.cite_as_evidence','task.dispatch'):
            self.assertEqual(call(dec(effect=e,scope=None)), 'candidate_for_authorization')

    def test_requested_parameter_discriminators(self):
        hold=dec(disposition='hold'); obj=dec(scope='object')
        self.assertEqual(call(hold,'task.dispatch'),'not_applicable')
        self.assertEqual(call(hold,params={'scope':'object'}),'not_applicable')
        self.assertEqual(call(hold,params={'scope':'claim'}),'hold')
        for p,want in [('ABSENT','candidate_for_authorization'),({},'candidate_for_authorization'),({'scope':'claim'},'not_applicable'),({'scope':'object'},'candidate_for_authorization')]:
            with self.subTest(p=p): self.assertEqual(call(obj,params=p),want)

    def test_unknown_future_and_structural_fail_closed(self):
        base=dec()
        muts=[]
        x=copy.deepcopy(base); x['contract_d_version']='0.3.0-rc5'; muts.append(x)
        x=copy.deepcopy(base); x['contract_d_version']=0.4; muts.append(x)
        x=copy.deepcopy(base); x['evaluation']['state']='future'; muts.append(x)
        x=copy.deepcopy(base); x['evaluation']['disposition']='maybe'; muts.append(x)
        x=copy.deepcopy(base); x['effect']['type']='future.effect'; muts.append(x)
        x=copy.deepcopy(base); x['effect']['version']='2'; muts.append(x)
        x=copy.deepcopy(base); x['effect']['params']['actor']='root'; muts.append(x)
        x=copy.deepcopy(base); x['policy']['approval']=True; muts.append(x)
        x=copy.deepcopy(base); x['actor']='root'; muts.append(x)
        for x in muts:
            with self.subTest(x=x): self.assertEqual(call(x),'cannot_establish')
        x=dec(state='failed'); x['effect']=dec()['effect']; self.assertEqual(call(x),'cannot_establish')
        x=dec(); x.pop('effect'); self.assertEqual(call(x),'cannot_establish')

    def test_replay_substitution_and_authority_sensitivity(self):
        d=dec(); base_id=c.semantic_identity(d)
        for part,key in [('input_authority','kind'),('input_authority','id'),('input_authority','immutable_id'),('policy','id'),('policy','version'),('target','kind'),('target','id')]:
            exp=copy.deepcopy(d[part]); exp[key]+='x'
            kwargs={'expected_'+part:exp}
            with self.subTest(part=part,key=key): self.assertEqual(call(d,params={'scope':'claim'},**kwargs),'not_applicable')
        exp=copy.deepcopy(d['target']); exp['content_sha256']=S2; self.assertEqual(call(d,params={'scope':'claim'},expected_target=exp),'not_applicable')
        self.assertEqual(call(d,'knowledge.cite_as_evidence',{'scope':'claim'}),'not_applicable')
        for mut in [('input_authority','id','x'),('policy','version','2'),('target','content_sha256',S2),('evaluation','disposition','hold')]:
            x=copy.deepcopy(d); x[mut[0]][mut[1]]=mut[2]; self.assertNotEqual(c.semantic_identity(x),base_id)
        x=copy.deepcopy(d); x['effect']['params']['scope']='object'; self.assertNotEqual(c.semantic_identity(x),base_id)

    def test_defaults_metadata_and_authorization_invariance(self):
        ids=[]
        for eff in [{'type':'knowledge.add_verified_tag','version':'1'},{'type':'knowledge.add_verified_tag','version':'1','params':{}},{'type':'knowledge.add_verified_tag','version':'1','params':{'scope':'claim'}}]:
            x=dec(); x['effect']=eff; ids.append(c.semantic_identity(x))
        self.assertEqual(len(set(ids)),1)
        d=dec(); base=c.semantic_identity(d)
        for md in [None,{'reason_codes':['x']},{'explanation':'x','diagnostics':{'n':1}}]:
            x=copy.deepcopy(d)
            if md is None: x.pop('metadata',None)
            else: x['metadata']=md
            self.assertEqual(c.semantic_identity(x),base); self.assertEqual(call(x,params={'scope':'claim'}),'candidate_for_authorization')
        auth={'actor':'a','approval':True}; auth['actor']='b'; self.assertEqual(c.semantic_identity(d),base)
        for f in ('actor','approval','delegation','autonomy','profile','trust','execution_permission','execution_state','execution_receipt'):
            x=copy.deepcopy(d); x[f]=True; self.assertEqual(call(x),'cannot_establish')

    def test_finite_json_ingress_and_decoded_values(self):
        bad=[b'{"x":"\xff"}',b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":-Infinity}']
        for raw in bad:
            with self.subTest(raw=raw):
                with self.assertRaises(c.ContractDError): c.parse_json_bytes(raw)
        d=dec(); d['metadata']={'diagnostics':{'x':object()}}; self.assertEqual(call(d),'cannot_establish')
        d=dec(); d['metadata']={'diagnostics':{1:'x'}}; self.assertEqual(call(d),'cannot_establish')
        cyc=[]; cyc.append(cyc); d=dec(); d['metadata']={'diagnostics':cyc}; self.assertEqual(call(d),'cannot_establish')
        a=[]; b={'a':a}; a.append(b); d=dec(); d['metadata']={'diagnostics':a}; self.assertEqual(call(d),'cannot_establish')
        shared={'leaf':[1,2]}; d=dec(); d['metadata']={'diagnostics':[shared,shared]}; self.assertEqual(call(d,params={'scope':'claim'}),'candidate_for_authorization')
        d=dec(); d['metadata']={'diagnostics':{'x':math.inf}}; self.assertEqual(call(d),'cannot_establish')

    def test_canonicalization(self):
        a={'b':1,'a':'é'}; b={'a':'é','b':1}; self.assertEqual(c.canonical_json_bytes(a),c.canonical_json_bytes(b))
        parsed=c.parse_json_bytes(b'{  "b":1, "a":"\xc3\xa9" }'); self.assertEqual(c.canonical_json_bytes(parsed),c.canonical_json_bytes(a))
        raw=c.canonical_json_bytes({'x':'é'}); self.assertTrue(raw.endswith(b'\n')); self.assertIn('é'.encode(),raw); self.assertNotIn(b'\\u00e9',raw)
        self.assertNotEqual(c.canonical_json_bytes([1,2]),c.canonical_json_bytes([2,1]))

    def test_weak_consumer_discrimination(self):
        d=dec(); bad=copy.deepcopy(d); bad['contract_d_version']='future'; self.assertEqual(call(bad),'cannot_establish'); self.assertEqual(w.clear_disposition_only(bad),'candidate_for_authorization')
        t=copy.deepcopy(d['target']); t['content_sha256']=S2; self.assertEqual(call(d,params={'scope':'claim'},expected_target=t),'not_applicable'); self.assertEqual(w.target_id_only(d,expected_target=t),'candidate_for_authorization'); self.assertEqual(w.target_ignore_kind_content(d,expected_target=t),'candidate_for_authorization')
        failed=dec(state='failed'); self.assertEqual(call(failed),'evaluation_failed'); self.assertEqual(w.hold_failure_collapse(failed),'hold')
        failed['metadata']={'explanation':'verified clear'}; self.assertEqual(w.reason_text_effect_inference(failed),'candidate_for_authorization')
        x=copy.deepcopy(d); x['effect']['type']='future.effect'; self.assertEqual(call(x),'cannot_establish'); self.assertEqual(w.unknown_effect_acceptance(x),'candidate_for_authorization')
        p=copy.deepcopy(d['policy']); p['version']='2'; self.assertEqual(call(d,params={'scope':'claim'},expected_policy=p),'not_applicable'); self.assertEqual(w.policy_blind(d,expected_input_authority=d['input_authority'],expected_target=d['target']),'candidate_for_authorization')
        u=copy.deepcopy(d['input_authority']); u['immutable_id']+='x'; self.assertEqual(call(d,params={'scope':'claim'},expected_input_authority=u),'not_applicable'); self.assertEqual(w.upstream_blind(d,expected_policy=d['policy'],expected_target=d['target']),'candidate_for_authorization')
        obj=dec(scope='object'); self.assertEqual(call(obj),'candidate_for_authorization'); self.assertEqual(w.omitted_params_as_defaults(obj,requested_effect_params=None),'not_applicable')
        hold=dec(disposition='hold'); self.assertEqual(call(hold,'task.dispatch'),'not_applicable'); self.assertEqual(w.hold_before_applicability(hold),'hold')
        x=dec(); x['metadata']={'diagnostics':{'x':object()}}; self.assertEqual(call(x),'cannot_establish'); self.assertEqual(w.host_only_diagnostics_acceptance(x),'candidate_for_authorization')
        cyc=[]; cyc.append(cyc); x=dec(); x['metadata']={'diagnostics':cyc}; self.assertEqual(call(x),'cannot_establish'); self.assertEqual(w.cyclic_acceptance(x),'candidate_for_authorization')
        self.assertNotEqual(w.identity_with_authorization_context(d,{'actor':'a'}),w.identity_with_authorization_context(d,{'actor':'b'})); self.assertEqual(c.semantic_identity(d),c.semantic_identity(d))

if __name__=='__main__': unittest.main(verbosity=2)
