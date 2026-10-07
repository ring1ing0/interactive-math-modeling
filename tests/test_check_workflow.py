import hashlib, json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_workflow as cw

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); (self.root/'.interactive-mm').mkdir()
        self.state={'schema_version':'0.2','modeling_complete':False,'handoff_ready':False,'integration_review':'PENDING','final_figures_audited':False,'manuscript_audit':'NOT_PROVIDED','award_assessment':'PENDING','project_snapshot_id':'project-v1','questions':{}}
    def tearDown(self): self.tmp.cleanup()
    def put(self, rel, obj):
        p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj),encoding='utf-8');return rel
    def hashed(self, rel, content='evidence'):
        p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8');return {'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    def digest_ref(self, rel):
        p=self.root/rel;return {'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    def refresh_claim_manifest(self,q):
        m=json.loads((self.root/q['snapshot_manifest']).read_text())
        for item in m['files']:
            if item['path']==q['claim_contract_ref']: item.update(self.digest_ref(q['claim_contract_ref']))
        (self.root/q['snapshot_manifest']).write_text(json.dumps(m))
    def refresh_manifest_ref(self,q,rel):
        m=json.loads((self.root/q['snapshot_manifest']).read_text())
        for item in m['files']:
            if item['path']==rel: item.update(self.digest_ref(rel))
        (self.root/q['snapshot_manifest']).write_text(json.dumps(m))
    def review_obj(self, stage, qid, sid):
        checks=[{'id':i,'required':True,'verdict':'PASS','evidence_refs':[self.hashed(f'evidence/{stage}-{i}.txt')]} for i in sorted(cw.MANDATORY[stage])]
        return {'stage':stage,'question':qid,'snapshot_id':sid,'reviewer_id':'reviewer-2','independence':'independent','verdict':'PASS','checks':checks,'findings':[]}
    def review(self, stage, qid, sid): return self.put(f'reports/{qid}-{stage}.json',self.review_obj(stage,qid,sid))
    def complete_question(self,qid='q1',deps=None):
        snap='snap-'+qid; data=self.hashed(f'data/{qid}.csv')
        claim_ev=self.hashed(f'evidence/{qid}-claim.txt')
        claims=self.put(f'claims/{qid}.json',{'question':qid,'snapshot_id':snap,'claims':[{'id':'c1','requirement_ids':['r1'],'statement':'Supported result','support_status':'SUPPORTED','scope':'x','limitations':[],'obligations':['evidence_sufficiency'],'evidence_refs':[claim_ev],'forbidden_claims':[]}]})
        q={'dependencies':deps or [],'requirement_ids':['r1'],'snapshot_id':snap,'snapshot_manifest':f'manifests/{qid}.json','claim_contract_ref':claims,'units':{'u1':{'caliber_decided':True,'decided':True,'preprocessing_plan_confirmed':True}},'visual_confirmed':True,'chart_plan_confirmed':True,'param_spec_confirmed':True,'code_contract_confirmed':True,'coded':True,'frozen':True,'review_refs':{}}
        for g in cw.GATES: q[g]='PASS'; q['review_refs'][g]=self.review(g,qid,snap)
        files=[data,claim_ev,self.digest_ref(claims)]
        for gate in cw.GATES:
            report=json.loads((self.root/q['review_refs'][gate]).read_text())
            files.append(self.digest_ref(q['review_refs'][gate]))
            for check in report['checks']: files.extend(check['evidence_refs'])
        self.put(q['snapshot_manifest'],{'snapshot_id':snap,'files':files})
        self.state['questions'][qid]=q; return q
    def finalize_model(self):
        files=[]
        for q in self.state['questions'].values():
            files.extend([self.digest_ref(q['snapshot_manifest']),self.digest_ref(q['claim_contract_ref'])])
        files.append(self.hashed('deliverables/final-chart.png','chart'));files.append(self.hashed('deliverables/handoff.json','handoff'))
        self.state['final_evidence_refs']=[self.digest_ref('deliverables/final-chart.png'),self.digest_ref('deliverables/handoff.json')]
        self.state['project_snapshot_manifest']=self.put('manifests/project.json',{'snapshot_id':'project-v1','files':files})
        self.state['integration_review_ref']=self.review('integration_review','global','project-v1')
        self.state.update(modeling_complete=True,handoff_ready=True,final_figures_audited=True,integration_review='PASS')
    def save(self): cw.write_json_atomic(self.root/'.interactive-mm/state.json',self.state)
    def test_valid_completed_project_without_manuscript(self):
        self.complete_question(); self.finalize_model();self.save();cw.validate_project(self.root)
        self.assertEqual('NOT_PROVIDED',self.state['manuscript_audit'])
    def test_open_major_and_missing_or_self_check_report_fail(self):
        q=self.complete_question(); self.save(); p=self.root/q['review_refs']['plan_review'];r=json.loads(p.read_text());r['findings']=[{'severity':'major','status':'open'}];p.write_text(json.dumps(r));self.refresh_manifest_ref(q,q['review_refs']['plan_review'])
        with self.assertRaisesRegex(ValueError,'open critical/major'): cw.validate_project(self.root)
        r['findings']=[];r['independence']='self_check';p.write_text(json.dumps(r));self.refresh_manifest_ref(q,q['review_refs']['plan_review'])
        with self.assertRaisesRegex(ValueError,'not independent'): cw.validate_project(self.root)
        r['independence']='independent';p.write_text(json.dumps(r));self.refresh_manifest_ref(q,q['review_refs']['plan_review']);q['review_refs'].pop('code_review');self.save()
        with self.assertRaisesRegex(ValueError,'missing review_refs'): cw.validate_project(self.root)
    def test_hash_drift_and_escape_rejected(self):
        q=self.complete_question(); self.save(); (self.root/'data/q1.csv').write_text('drift')
        with self.assertRaisesRegex(ValueError,'hash drift'): cw.validate_project(self.root)
        (self.root/'data/q1.csv').write_text('evidence'); q['snapshot_manifest']='../outside.json'; self.save()
        with self.assertRaisesRegex(ValueError,'escapes root'): cw.validate_project(self.root)
    def test_empty_snapshot_and_missing_claim_evidence_fail(self):
        q=self.complete_question();m=json.loads((self.root/q['snapshot_manifest']).read_text());m['files']=[];(self.root/q['snapshot_manifest']).write_text(json.dumps(m));self.save()
        with self.assertRaisesRegex(ValueError,'empty'):cw.validate_project(self.root)
        q=self.complete_question();m=json.loads((self.root/q['snapshot_manifest']).read_text());c=json.loads((self.root/q['claim_contract_ref']).read_text());c['claims'][0]['evidence_refs']=[];(self.root/q['claim_contract_ref']).write_text(json.dumps(c));self.refresh_claim_manifest(q);self.save()
        with self.assertRaisesRegex(ValueError,'lacks evidence'):cw.validate_project(self.root)
    def test_claim_obligations_and_conditional_fields_are_checked(self):
        q=self.complete_question();claims=json.loads((self.root/q['claim_contract_ref']).read_text());claims['claims'][0]['obligations']=['not-a-required-check'];(self.root/q['claim_contract_ref']).write_text(json.dumps(claims));self.refresh_claim_manifest(q);self.save()
        with self.assertRaisesRegex(ValueError,'obligation'):cw.validate_project(self.root)
        claims['claims'][0].update(obligations=['evidence_sufficiency'],support_status='CONDITIONAL',conditions=['condition'],limitations=[]);(self.root/q['claim_contract_ref']).write_text(json.dumps(claims));self.refresh_claim_manifest(q);self.save()
        with self.assertRaisesRegex(ValueError,'conditions and limitations'):cw.validate_project(self.root)
    def test_claim_ids_and_requirement_ids_must_be_nonempty_and_unique(self):
        q=self.complete_question();claims=json.loads((self.root/q['claim_contract_ref']).read_text());claims['claims'].append(dict(claims['claims'][0]));(self.root/q['claim_contract_ref']).write_text(json.dumps(claims));self.refresh_claim_manifest(q);self.save()
        with self.assertRaisesRegex(ValueError,'duplicate claim id'):cw.validate_project(self.root)
        q['requirement_ids']=[];claims['claims']=[];(self.root/q['claim_contract_ref']).write_text(json.dumps(claims));self.refresh_claim_manifest(q);self.save()
        with self.assertRaisesRegex(ValueError,'requirement_ids must be nonempty'):cw.validate_project(self.root)
    def test_review_rejects_extra_required_fail_duplicate_and_blank_reviewer(self):
        q=self.complete_question();p=self.root/q['review_refs']['code_review'];r=json.loads(p.read_text());r['checks'].append({'id':'extra','required':True,'verdict':'FAIL'});p.write_text(json.dumps(r));self.refresh_manifest_ref(q,q['review_refs']['code_review']);self.save()
        with self.assertRaisesRegex(ValueError,'required check extra'):cw.validate_project(self.root)
        r['checks'].pop();r['checks'].append(dict(r['checks'][0]));p.write_text(json.dumps(r));self.refresh_manifest_ref(q,q['review_refs']['code_review'])
        with self.assertRaisesRegex(ValueError,'duplicate check'):cw.validate_project(self.root)
        r['checks'].pop();r['reviewer_id']=' ';p.write_text(json.dumps(r));self.refresh_manifest_ref(q,q['review_refs']['code_review'])
        with self.assertRaisesRegex(ValueError,'reviewer_id missing'):cw.validate_project(self.root)
    def test_stage_snapshot_can_precede_final_snapshot_but_evidence_must_be_frozen(self):
        q=self.complete_question();q['review_snapshot_ids']={'plan_review':'plan-stage-v0'}
        report_path=q['review_refs']['plan_review'];rp=self.root/report_path;report=json.loads(rp.read_text());report['snapshot_id']='plan-stage-v0';rp.write_text(json.dumps(report));self.refresh_manifest_ref(q,report_path);self.save();cw.validate_project(self.root)
        ev=report['checks'][0]['evidence_refs'][0]['path'];(self.root/ev).write_text('changed evidence')
        with self.assertRaisesRegex(ValueError,'hash drift'):cw.validate_project(self.root)
    def test_claim_candidate_matches_result_and_caliber_not_final_snapshot(self):
        q=self.complete_question();q['snapshot_id']='q-final1';q['review_snapshot_ids']={'plan_review':'p1','code_review':'c1','result_review':'r1','caliber_review':'r1'}
        manifest_path=self.root/q['snapshot_manifest']
        claims_path=self.root/q['claim_contract_ref'];claims=json.loads(claims_path.read_text());claims['snapshot_id']='r1';claims_path.write_text(json.dumps(claims));self.refresh_manifest_ref(q,q['claim_contract_ref'])
        for gate,sid in q['review_snapshot_ids'].items():
            path=q['review_refs'][gate];rp=self.root/path;report=json.loads(rp.read_text());report['snapshot_id']=sid;rp.write_text(json.dumps(report));self.refresh_manifest_ref(q,path)
        manifest=json.loads(manifest_path.read_text());manifest['snapshot_id']='q-final1';manifest_path.write_text(json.dumps(manifest));self.save();cw.validate_project(self.root)
        q['review_snapshot_ids']['caliber_review']='r2';caliber=q['review_refs']['caliber_review'];rp=self.root/caliber;report=json.loads(rp.read_text());report['snapshot_id']='r2';rp.write_text(json.dumps(report));self.refresh_manifest_ref(q,caliber);self.save()
        with self.assertRaisesRegex(ValueError,'must share a candidate snapshot'):cw.validate_project(self.root)
    def test_project_snapshot_drift_and_global_review_scope_fail(self):
        self.complete_question();self.finalize_model();self.save();cw.validate_project(self.root)
        path=self.root/'manifests/q1.json';original=path.read_text();path.write_text(original+' ')
        with self.assertRaisesRegex(ValueError,'project snapshot hash drift'):cw.validate_project(self.root)
        path.write_text(original);self.save()
        rp=self.root/self.state['integration_review_ref'];r=json.loads(rp.read_text());r['question']='q1';rp.write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,'question mismatch'):cw.validate_project(self.root)
    def test_transitive_invalidation_and_preview(self):
        a=self.complete_question('q1'); b=self.complete_question('q2',['q1']); c=self.complete_question('q3',['q2'])
        a.update(chart_plan_confirmed=True,param_spec_confirmed=True,code_contract_confirmed=True,coded=True)
        self.state.update(modeling_complete=True,handoff_ready=True,final_figures_audited=True,integration_review='PASS',award_assessment='COMPLETE');self.save();cw.invalidate(self.root,self.state,'q1','algorithm')
        for q in (a,b,c):
            self.assertFalse(q['units']['u1']['decided']);self.assertFalse(q['chart_plan_confirmed']);self.assertFalse(q['param_spec_confirmed']);self.assertFalse(q['code_contract_confirmed']);self.assertFalse(q['coded'])
        self.assertFalse(self.state['modeling_complete']);self.assertEqual('PENDING',self.state['award_assessment'])
        self.assertTrue(json.loads((self.root/'.interactive-mm/state.json').read_text())['modeling_complete'])
    def test_manuscript_change_does_not_invalidate_model(self):
        q=self.complete_question();self.state.update(modeling_complete=True,handoff_ready=True,final_figures_audited=True,award_assessment='COMPLETE',award_assessment_ref=self.put('award.json',{'evidence_basis':'modeling_artifacts','manuscript_reviewed':False,'project_snapshot_id':'project-v1'}));self.save()
        cw.invalidate(self.root,self.state,'q1','manuscript')
        self.assertTrue(self.state['modeling_complete']);self.assertTrue(q['frozen']);self.assertEqual('PENDING',self.state['manuscript_audit']);self.assertEqual('COMPLETE',self.state['award_assessment'])
    def test_award_cannot_bypass_model_gates_or_false_complete(self):
        self.complete_question();self.state.update(modeling_complete=False,handoff_ready=True,final_figures_audited=True,integration_review='PENDING',award_assessment='COMPLETE',award_assessment_ref=self.put('award.json',{'evidence_basis':'modeling_artifacts','manuscript_reviewed':False,'project_snapshot_id':'project-v1'}));self.save()
        with self.assertRaisesRegex(ValueError,'integration, audited figures'):cw.validate_project(self.root)
        self.state.update(integration_review='PASS',modeling_complete=True);self.save()
        with self.assertRaisesRegex(ValueError,'project_snapshot_manifest'):cw.validate_project(self.root)
    def test_award_basis_requires_correct_manuscript_state_and_global_gate(self):
        self.complete_question();self.finalize_model()
        self.state['award_assessment']='COMPLETE';self.state['award_assessment_ref']=self.put('award.json',{'evidence_basis':'manuscript_and_artifacts','manuscript_reviewed':True,'project_snapshot_id':'project-v1'});self.save()
        with self.assertRaisesRegex(ValueError,'manuscript award basis'):cw.validate_project(self.root)
        self.state['manuscript_audit']='PASS';self.save();cw.validate_project(self.root)
        self.state['award_assessment_ref']=self.put('award.json',{'evidence_basis':'modeling_artifacts','manuscript_reviewed':True,'project_snapshot_id':'project-v1'});self.save()
        with self.assertRaisesRegex(ValueError,'model-only award basis'):cw.validate_project(self.root)
    def test_dependencies_reject_cycle(self):
        self.complete_question('q1',['q2']);self.complete_question('q2',['q1']);self.save()
        with self.assertRaisesRegex(ValueError,'cycle'):cw.validate_project(self.root)
    def test_check_skill_checks_links_and_scans_path_leaks(self):
        skill=self.root/'skill';(skill/'references').mkdir(parents=True);(skill/'SKILL.md').write_text('---\nname: x\ndescription: y\n---\n[ref](references/ref.md#part)',encoding='utf-8');(skill/'references/ref.md').write_text('# ref',encoding='utf-8')
        self.assertIn('OK:',cw.check_skill(skill))
        (skill/'references'/'bad-link.md').write_text('[missing](absent.md#anchor)',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'missing Markdown references'):cw.check_skill(skill)
        (skill/'references'/'bad-link.md').unlink()
        (skill/'references'/'bad-link.md').write_text('example C:/Users/'+'Someone/private.txt',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'path leak'):cw.check_skill(skill)
        (skill/'references'/'bad-link.md').unlink()

if __name__=='__main__':unittest.main()

