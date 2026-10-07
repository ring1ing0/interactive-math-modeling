from __future__ import annotations
import argparse, hashlib, json, os, re, sys, tempfile
from pathlib import Path

GATES = ('plan_review','code_review','result_review','caliber_review')
ALL_GATES = GATES + ('integration_review',)
MANDATORY = {'plan_review': {'task_coverage','model_validity','validation_design'}, 'code_review': {'execution','reproduction','constraints'}, 'result_review': {'task_coverage','evidence_sufficiency','counterexamples'}, 'caliber_review': {'numeric_units','claim_strength','handoff_consistency'}, 'integration_review': {'cross_question','coverage','reproduction'}}
CHANGES = {'caliber','algorithm','data','parameters','charts','manuscript'}

def fail(msg): raise ValueError(msg)
def read_json(path):
    try:
        with path.open(encoding='utf-8') as f: return json.load(f)
    except (OSError, json.JSONDecodeError) as e: fail(f'cannot read JSON {path}: {e}')
def write_json_atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name+'.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f:
            json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def safe_path(root, ref, must_exist=True):
    if not isinstance(ref,str) or not ref.strip(): fail('reference path must be a nonempty string')
    p=Path(ref)
    if p.is_absolute() or re.match(r'^[A-Za-z]:',ref) or ref.startswith(('\\\\','//')): fail(f'absolute path forbidden: {ref}')
    base=root.resolve(); target=(base/p).resolve(strict=False)
    try: target.relative_to(base)
    except ValueError: fail(f'path escapes root: {ref}')
    if must_exist and not target.exists(): fail(f'missing referenced file: {ref}')
    return target

def digest_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def verify_evidence(root, refs):
    if not isinstance(refs,list): fail('evidence_refs must be a list')
    for item in refs:
        if not isinstance(item,dict) or not isinstance(item.get('sha256'),str): fail('evidence ref requires path and sha256')
        p=safe_path(root,item.get('path'))
        if digest_file(p).lower()!=item['sha256'].lower(): fail(f'hash drift: {item["path"]}')

def report_ref(root, state, key):
    if key == 'integration_review' and state.get('integration_review_ref'):
        return safe_path(root,state['integration_review_ref'])
    refs=state.get('review_refs',{})
    if key not in refs: fail(f'missing review_refs.{key}')
    return safe_path(root,refs[key])

def validate_review(root, state, key, expected_question=None, expected_snapshot=None):
    p=report_ref(root,state,key); r=read_json(p)
    if not isinstance(r,dict) or r.get('stage')!=key: fail(f'{key}: wrong stage')
    if expected_question is not None and r.get('question')!=expected_question: fail(f'{key}: question mismatch')
    snap=expected_snapshot if expected_snapshot is not None else state.get('project_snapshot_id')
    if not isinstance(snap,str) or not snap: fail(f'{key}: expected snapshot id missing')
    if r.get('snapshot_id')!=snap: fail(f'{key}: snapshot mismatch')
    if not isinstance(r.get('reviewer_id'),str) or not r['reviewer_id'].strip(): fail(f'{key}: reviewer_id missing')
    if r.get('independence')!='independent': fail(f'{key}: reviewer is not independent')
    if r.get('verdict')!='PASS': fail(f'{key}: verdict is not PASS')
    checks=r.get('checks')
    if not isinstance(checks,list): fail(f'{key}: checks missing')
    by_id={}
    for c in checks:
        if not isinstance(c,dict) or not isinstance(c.get('id'),str) or not c['id'].strip(): fail(f'{key}: malformed check id')
        if c['id'] in by_id: fail(f'{key}: duplicate check id {c["id"]}')
        by_id[c['id']]=c
        if c.get('required') is True and c.get('verdict')!='PASS': fail(f'{key}: required check {c["id"]} not passed')
        if c.get('required') is True:
            verify_evidence(root,c.get('evidence_refs',[]))
            if not c.get('evidence_refs'): fail(f'{key}: required check {c["id"]} lacks evidence')
    for cid in MANDATORY[key]:
        c=by_id.get(cid)
        if not c or c.get('required') is not True or c.get('verdict')!='PASS': fail(f'{key}: mandatory check {cid} not passed')
    findings=r.get('findings',[])
    if not isinstance(findings,list): fail(f'{key}: findings must be a list')
    if any(isinstance(f,dict) and f.get('severity') in ('critical','major') and f.get('status')=='open' for f in findings): fail(f'{key}: open critical/major finding')
    return r

def validate_snapshot(root, q):
    sid=q.get('snapshot_id'); ref=q.get('snapshot_manifest')
    if not isinstance(sid,str) or not sid: fail('question snapshot_id missing')
    manifest=read_json(safe_path(root,ref))
    if not isinstance(manifest,dict) or manifest.get('snapshot_id')!=sid or not isinstance(manifest.get('files'),list) or not manifest['files']: fail('snapshot manifest mismatch/malformed or empty')
    manifest_paths={}
    for item in manifest['files']:
        if not isinstance(item,dict) or not isinstance(item.get('sha256'),str): fail('malformed snapshot file entry')
        p=safe_path(root,item.get('path'))
        manifest_paths[str(Path(item['path']).as_posix())]=item['sha256'].lower()
        if digest_file(p).lower()!=item['sha256'].lower(): fail(f'snapshot hash drift: {item["path"]}')
    claim_ref=q.get('claim_contract_ref')
    if not isinstance(claim_ref,str) or not claim_ref.strip(): fail('claim_contract_ref missing')
    if Path(claim_ref).as_posix() not in manifest_paths: fail('snapshot manifest must include claim contract')
    return sid, manifest_paths

def validate_claims(root,q,qid,result_report=None,manifest_paths=None,claim_snapshot_id=None):
    p=safe_path(root,q.get('claim_contract_ref')); obj=read_json(p)
    expected_sid=claim_snapshot_id if claim_snapshot_id is not None else q.get('snapshot_id')
    if not isinstance(obj,dict) or obj.get('question')!=qid or obj.get('snapshot_id')!=expected_sid: fail(f'{qid}: claims question/snapshot mismatch')
    req=q.get('requirement_ids')
    if not isinstance(req,list) or not req or any(not isinstance(x,str) or not x.strip() for x in req): fail(f'{qid}: requirement_ids must be nonempty')
    required=set(req); covered=set(); seen=set()
    claims=obj.get('claims')
    if not isinstance(claims,list): fail(f'{qid}: claims missing')
    for c in claims:
        if not isinstance(c,dict): fail('malformed claim')
        cid=c.get('id')
        if not isinstance(cid,str) or not cid.strip() or cid in seen: fail(f'{qid}: missing or duplicate claim id')
        seen.add(cid)
        status=c.get('support_status')
        if status not in ('SUPPORTED','CONDITIONAL','UNSUPPORTED'): fail('invalid claim support_status')
        ids=c.get('requirement_ids',[])
        if not isinstance(ids,list) or not ids or any(not isinstance(x,str) or not x.strip() for x in ids): fail('claim requirement_ids must be nonempty')
        covered.update(ids)
        if status=='UNSUPPORTED' and set(ids)&required: fail(f'{qid}: unsupported core claim {c.get("id")}')
        if status in ('SUPPORTED','CONDITIONAL') and any(not isinstance(c.get(k),str) or not c[k].strip() for k in ('statement','scope')): fail(f'{qid}: core claim requires statement and scope')
        if status=='CONDITIONAL' and (not c.get('conditions') or not c.get('limitations')): fail(f'{qid}: conditional claim needs conditions and limitations')
        verify_evidence(root,c.get('evidence_refs',[]))
        if status in ('SUPPORTED','CONDITIONAL') and not c.get('evidence_refs'): fail(f'{qid}: supported claim lacks evidence')
        obligations=c.get('obligations',[])
        if not isinstance(obligations,list) or any(not isinstance(x,str) or not x.strip() for x in obligations): fail(f'{qid}: obligations must be nonempty check IDs')
        if status in ('SUPPORTED','CONDITIONAL') and not obligations: fail(f'{qid}: supported claim requires validation obligations')
        if obligations:
            if not isinstance(result_report,dict): fail(f'{qid}: claim obligations require result review')
            required_checks={x['id']:x for x in result_report.get('checks',[]) if isinstance(x,dict) and x.get('required') is True and x.get('verdict')=='PASS'}
            for obligation in obligations:
                check=required_checks.get(obligation)
                if not check or not check.get('evidence_refs'): fail(f'{qid}: obligation {obligation} lacks required PASS evidence')
        if status in ('SUPPORTED','CONDITIONAL'):
            for ref in c['evidence_refs']:
                path=Path(ref['path']).as_posix()
                if manifest_paths is None or path not in manifest_paths: fail(f'{qid}: claim evidence missing from snapshot: {path}')
                if manifest_paths[path]!=ref['sha256'].lower(): fail(f'{qid}: claim evidence hash differs from snapshot: {path}')
    missing=required-covered
    if missing: fail(f'{qid}: requirements not covered by claims: {sorted(missing)}')

def validate_question(root,qid,q):
    sid,manifest_paths=validate_snapshot(root,q)
    units=q.get('units')
    if not isinstance(units,dict) or not units: fail(f'{qid}: units missing')
    for unit, flags in units.items():
        if not isinstance(flags,dict) or any(flags.get(k) is not True for k in ('caliber_decided','decided','preprocessing_plan_confirmed')): fail(f'{qid}.{unit}: units not confirmed')
    for field in ('visual_confirmed','chart_plan_confirmed','param_spec_confirmed','code_contract_confirmed','coded'):
        if q.get(field) is not True: fail(f'{qid}: {field} is not true')
    reports={}
    stage_ids=q.get('review_snapshot_ids',{})
    if not isinstance(stage_ids,dict): fail(f'{qid}: review_snapshot_ids must be an object')
    for gate in GATES:
        if q.get(gate)!='PASS': fail(f'{qid}: {gate} is not PASS')
        stage_sid=stage_ids.get(gate,sid)
        if not isinstance(stage_sid,str) or not stage_sid.strip(): fail(f'{qid}: invalid {gate} snapshot id')
        reports[gate]=validate_review(root,q,gate,qid,stage_sid)
        report_path=Path(q['review_refs'][gate]).as_posix()
        if report_path not in manifest_paths: fail(f'{qid}: review report missing from final snapshot: {report_path}')
        report_file=safe_path(root,q['review_refs'][gate])
        if manifest_paths[report_path]!=digest_file(report_file): fail(f'{qid}: review report hash differs from final snapshot: {report_path}')
        for check in reports[gate]['checks']:
            if check.get('required') is True:
                for evidence in check.get('evidence_refs',[]):
                    evidence_path=Path(evidence['path']).as_posix()
                    if evidence_path not in manifest_paths: fail(f'{qid}: review evidence missing from final snapshot: {evidence_path}')
                    if manifest_paths[evidence_path]!=evidence['sha256'].lower(): fail(f'{qid}: review evidence hash differs from final snapshot: {evidence_path}')
    if stage_ids.get('result_review',sid)!=stage_ids.get('caliber_review',sid): fail(f'{qid}: result_review and caliber_review must share a candidate snapshot')
    validate_claims(root,q,qid,reports['result_review'],manifest_paths,stage_ids.get('result_review',sid))
    if q.get('frozen') is not True: fail(f'{qid}: not frozen')

def validate_project(root):
    state_path=root/'.interactive-mm'/'state.json'; s=read_json(state_path)
    if s.get('schema_version')!='0.2': fail('schema_version must be 0.2')
    if not isinstance(s.get('questions'),dict): fail('questions must be an object')
    qs=s['questions']
    for qid,q in qs.items():
        if not isinstance(q,dict): fail(f'{qid}: question must be an object')
        deps=q.get('dependencies',[])
        if not isinstance(deps,list) or qid in deps or any(d not in qs for d in deps): fail(f'{qid}: invalid dependencies')
    visiting=set(); visited=set()
    def visit(qid):
        if qid in visiting: fail('question dependency cycle')
        if qid in visited: return
        visiting.add(qid)
        for dep in qs[qid].get('dependencies',[]): visit(dep)
        visiting.remove(qid); visited.add(qid)
    for qid in qs: visit(qid)
    if s.get('award_assessment')=='COMPLETE':
        ref=s.get('award_assessment_ref')
        if not ref: fail('COMPLETE award requires award_assessment_ref')
        award=read_json(safe_path(root,ref))
        if award.get('evidence_basis') not in ('modeling_artifacts','manuscript_and_artifacts'): fail('invalid award evidence_basis')
        if award.get('project_snapshot_id')!=s.get('project_snapshot_id'): fail('award project snapshot mismatch')
        if award.get('evidence_basis')=='manuscript_and_artifacts' and (award.get('manuscript_reviewed') is not True or s.get('manuscript_audit')!='PASS'): fail('manuscript award basis requires reviewed PASS manuscript')
        if award.get('evidence_basis')=='modeling_artifacts' and award.get('manuscript_reviewed') is not False: fail('model-only award basis requires manuscript_reviewed false')
        if s.get('integration_review')!='PASS' or s.get('final_figures_audited') is not True or s.get('handoff_ready') is not True: fail('COMPLETE award requires integration, audited figures, and handoff')
        if not s['questions']: fail('COMPLETE award requires validated modeling questions')
        for qid,q in s['questions'].items():
            if q.get('frozen') is not True: fail('COMPLETE award requires every question frozen')
            validate_question(root,qid,q)
    all_frozen=True
    for qid,q in s['questions'].items():
        if q.get('frozen'):
            validate_question(root,qid,q)
        else: all_frozen=False
    if s.get('modeling_complete'):
        if not all_frozen or not s['questions']: fail('modeling_complete requires every question frozen')
        if s.get('integration_review')!='PASS': fail('modeling_complete requires integration_review PASS')
        if s.get('final_figures_audited') is not True or s.get('handoff_ready') is not True: fail('modeling_complete requires audited figures and ready handoff')
        global_sid=s.get('project_snapshot_id')
        if not isinstance(global_sid,str) or not global_sid: fail('project_snapshot_id missing')
        if not s.get('project_snapshot_manifest'): fail('project_snapshot_manifest missing')
        manifest=read_json(safe_path(root,s['project_snapshot_manifest']))
        if not isinstance(manifest,dict) or manifest.get('snapshot_id')!=global_sid or not isinstance(manifest.get('files'),list) or not manifest['files']: fail('project snapshot manifest mismatch/malformed or empty')
        paths=set()
        for item in manifest['files']:
            if not isinstance(item,dict) or not isinstance(item.get('sha256'),str): fail('malformed project snapshot entry')
            fp=safe_path(root,item.get('path')); paths.add(Path(item['path']).as_posix())
            if digest_file(fp).lower()!=item['sha256'].lower(): fail(f'project snapshot hash drift: {item["path"]}')
        for qid,q in qs.items():
            if Path(q.get('snapshot_manifest','')).as_posix() not in paths or Path(q.get('claim_contract_ref','')).as_posix() not in paths: fail(f'project snapshot must include {qid} manifest and claims')
        final_refs=s.get('final_evidence_refs',[])
        if not isinstance(final_refs,list) or not final_refs: fail('final_evidence_refs missing')
        for ref in final_refs:
            verify_evidence(root,[ref])
            if Path(ref['path']).as_posix() not in paths: fail('project snapshot must include final chart/handoff evidence')
        validate_review(root,s,'integration_review','global',global_sid)
    if s.get('award_assessment')=='COMPLETE' and not s.get('modeling_complete'):
        fail('COMPLETE award requires modeling_complete')
    return s

def check_skill(root):
    text=(root/'SKILL.md').read_text(encoding='utf-8')
    if not text.startswith('---'): fail('SKILL.md missing YAML frontmatter')
    end=text.find('\n---',3)
    if end<0: fail('unterminated YAML frontmatter')
    fm=text[3:end]
    for field in ('name','description'):
        if not re.search(rf'(?m)^{field}:\s*\S',fm): fail(f'frontmatter {field} missing')
    docs=[p for p in root.rglob('*.md') if '.git' not in p.parts]
    links=set()
    for doc in docs:
        body=doc.read_text(encoding='utf-8')
        links.update((doc,x) for x in re.findall(r'\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)',body))
        links.update((doc,x) for x in re.findall(r'(?m)^\s*\[[^]]+\]:\s*<?([^\s>]+)>?',body))
    refs=set()
    for doc,link in links:
        if re.match(r'(?i)^(https?://|mailto:|data:|tel:)',link) or link.startswith('#'): continue
        target=link.split('#',1)[0].split('?',1)[0]
        if target: refs.add((doc,target))
    missing=[]
    for doc,link in sorted(refs,key=lambda x:(str(x[0]),x[1])):
        try:
            target=(doc.parent/link).resolve(strict=False)
            target.relative_to(root.resolve())
            if not target.is_file(): missing.append(f'{doc.relative_to(root)} -> {link}')
        except ValueError: missing.append(f'{doc.relative_to(root)} -> {link}')
    if missing: fail('missing Markdown references: '+', '.join(missing))
    # Scan this skill tree only; .git is deliberately excluded.
    sep=r'[/\\]'
    patterns=(re.compile(r'(?i)[A-Z]:'+sep+r'Users'+sep+r'[^\s"\']+'), re.compile(r'\\\\[A-Za-z0-9._-]+'+sep+r'[A-Za-z0-9._ $-]+'))
    leaks=[]
    for p in root.rglob('*'):
        if '.git' in p.parts or not p.is_file() or p.suffix.lower() not in ('.md','.yaml','.yml','.json','.py'): continue
        try: body=p.read_text(encoding='utf-8')
        except (UnicodeError,OSError): continue
        if any(rx.search(body) for rx in patterns): leaks.append(str(p.relative_to(root)))
    if leaks: fail('local absolute Windows path leak: '+', '.join(leaks))
    return f'OK: {len(refs)} Markdown references; no local path leaks'

def reset_gate(q, *gates):
    for g in gates: q[g]='PENDING'
    q['frozen']=False

def reset_runtime(q):
    q['chart_plan_confirmed']=False; q['param_spec_confirmed']=False
    q['code_contract_confirmed']=False; q['coded']=False
    reset_gate(q,'plan_review','code_review','result_review','caliber_review')

def invalidate(root, state, qid, change):
    if change not in CHANGES: fail(f'unknown change: {change}')
    if change=='manuscript':
        state['manuscript_audit']='PENDING'
        ref=state.get('award_assessment_ref')
        if ref:
            try: award=read_json(safe_path(root,ref))
            except (ValueError,OSError): award={}
            if award.get('evidence_basis')=='manuscript_and_artifacts': state['award_assessment']='PENDING'
        return
    if qid not in state.get('questions',{}): fail(f'unknown question: {qid}')
    qs=state['questions']; affected={qid}; queue=[qid]
    while queue:
        current=queue.pop(0)
        for other,q in qs.items():
            if other not in affected and current in q.get('dependencies',[]): affected.add(other); queue.append(other)
    source=qs[qid]
    if change in ('caliber','data'):
        for u in source.get('units',{}).values():
            u['caliber_decided']=False; u['decided']=False; u['preprocessing_plan_confirmed']=False
        reset_runtime(source)
    elif change=='algorithm':
        for u in source.get('units',{}).values(): u['decided']=False
        reset_runtime(source)
    elif change=='parameters':
        source['param_spec_confirmed']=False; source['code_contract_confirmed']=False; source['coded']=False
        reset_gate(source,'code_review','result_review','caliber_review')
    elif change=='charts':
        source['chart_plan_confirmed']=False; source['code_contract_confirmed']=False; source['coded']=False
        reset_gate(source,'code_review','result_review','caliber_review')
    for dependent in affected-{qid}:
        q=qs[dependent]
        for u in q.get('units',{}).values():
            u['decided']=False
            if change in ('caliber','data'):
                u['caliber_decided']=False; u['preprocessing_plan_confirmed']=False
        reset_runtime(q)
    for q in qs.values(): q['frozen']=False if q is source or q in [qs[x] for x in affected] else q.get('frozen',False)
    state.update(modeling_complete=False,handoff_ready=False,final_figures_audited=False,integration_review='PENDING',award_assessment='PENDING')
    state['integration_review_ref']=None

def main(argv=None):
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('check-project'); p.add_argument('project_root')
    p=sp.add_parser('check-skill'); p.add_argument('skill_root')
    p=sp.add_parser('invalidate'); p.add_argument('project_root'); p.add_argument('--question',required=True); p.add_argument('--change',required=True,choices=sorted(CHANGES)); p.add_argument('--apply',action='store_true')
    a=ap.parse_args(argv)
    try:
        if a.cmd=='check-skill': print(check_skill(Path(a.skill_root).resolve())); return 0
        root=Path(a.project_root).resolve(); path=root/'.interactive-mm'/'state.json'; state=read_json(path)
        if a.cmd=='check-project':
            validate_project(root); print('OK: project state and all required evidence validated'); return 0
        invalidate(root,state,a.question,a.change)
        if a.apply:
            write_json_atomic(path,state); print(f'APPLIED: {a.change} invalidation for {a.question}')
        else: print(f'PREVIEW: {a.change} invalidation for {a.question}; use --apply to write')
        return 0
    except (ValueError,OSError,KeyError,TypeError,AttributeError,UnicodeError) as e:
        print(f'ERROR: {e}',file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())

