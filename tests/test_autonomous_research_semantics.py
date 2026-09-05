"""Public synthetic cases only; no private pilot data or implementation."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PUBLIC = Path(__file__).resolve().parents[1]
ASSETS = PUBLIC / '.agents/skills/holoforge-auto-research/assets'
SCRIPT = PUBLIC / '.agents/skills/holoforge-auto-research/scripts/validate_autonomous_campaign.py'
spec = importlib.util.spec_from_file_location('validator', SCRIPT)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class SemanticRegressions(unittest.TestCase):
    def setUp(self):
        self.m = json.loads((ASSETS/'autonomous-mission.example.json').read_text())
        self.s = json.loads((ASSETS/'autonomous-campaign-state.example.json').read_text())
        self.p = json.loads((ASSETS/'autonomous-terminal-package.example.json').read_text())

    def check(self):
        self.s['mission_sha256'] = v.canonical_sha256(self.m)
        self.p['mission_sha256'] = v.canonical_sha256(self.m)
        self.p['state_sha256'] = v.canonical_sha256(self.s)
        v.validate_mission(self.m)
        v.validate_state(self.m, self.s)
        v.validate_package(self.m, self.s, self.p)

    def complete_candidate(self):
        self.s['candidate_ledger'] = [{'candidate_id':'candidate-001', 'status':'packaged', 'disposition':'Synthetic complete test', 'gate_contract_sha256':'a'*64, 'repairs_used':0}]
        self.s['budgets_used']['candidates'] = 1
        phases = ['initialized','searching','screening','selected','discovery','confirmation','verification','critique','packaging','awaiting-owner','terminal']
        template = self.s['transitions'][0]
        self.s['transitions'] = []
        for i, (before, after) in enumerate(zip(phases, phases[1:]),1):
            transition = copy.deepcopy(template)
            transition.update(sequence=i, **{'from':before,'to':after})
            transition['delegated_decision'] = 'candidate_generation' if i == 1 else 'candidate_selection' if after == 'selected' else 'gate_transition'
            transition['candidate_id'] = None if i < 3 else 'candidate-001'
            self.s['transitions'].append(transition)
        self.s['terminal_outcome'] = self.p['outcome'] = 'submission-ready-candidate'
        self.p['manuscript'] = {'status':'ready','path':'campaign/paper.md'}
        self.p['code'] = {'status':'ready','path':'campaign/code'}
        self.p['claims'] = [{'statement':'Synthetic claim used to test successful control flow only.', 'support_level':'hypothesis', 'generated_by_ai':True, 'review_status':'unreviewed', 'evidence_refs':['campaign/evidence.json']}]
        for check in self.p['checks'].values():
            check['status'] = 'pass'
            check['evidence_refs'] = ['campaign/evidence.json']

    def populate(self, root):
        for name in ('campaign/paper.md','campaign/code/main.py','campaign/evidence.json'):
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic fixture\n')
            self.p['artifacts'].append({'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':'synthetic-test'})

    def test_original_stop_remains_valid(self): self.check()

    def test_draft_can_validate_before_launch(self):
        self.m['status']='draft'
        self.m['authorization']['authorized_on']=None
        self.m['authorization']['expires_on']=None
        v.validate_mission(self.m)

    def test_draft_cannot_execute(self):
        self.m['status']='draft'
        self.m['authorization']['authorized_on']=None
        self.m['authorization']['expires_on']=None
        with self.assertRaisesRegex(v.ValidationError,'owner-authorized'): self.check()

    def test_future_authorization_rejected(self):
        self.m['authorization']['authorized_on']='2098-01-01'
        with self.assertRaisesRegex(v.ValidationError,'not started'): self.check()

    def test_decision_label_cannot_expand_authority(self):
        self.m['authorization']['delegated_decisions']=['local_execution']
        for transition in self.s['transitions']: transition['delegated_decision']='local_execution'
        with self.assertRaisesRegex(v.ValidationError,'requires candidate_generation'): self.check()

    def test_selection_requires_selection_authority(self):
        self.complete_candidate()
        self.m['authorization']['delegated_decisions'].remove('candidate_selection')
        self.s['transitions'][2]['delegated_decision']='gate_transition'
        with self.assertRaisesRegex(v.ValidationError,'requires candidate_selection'): self.check()

    def test_discovery_requires_execution_authority(self):
        self.complete_candidate()
        self.m['authorization']['delegated_decisions'].remove('local_execution')
        with self.assertRaisesRegex(v.ValidationError,'local_execution'): self.check()

    def test_success_cannot_skip_independent_phases(self):
        self.s['terminal_outcome']=self.p['outcome']='submission-ready-candidate'
        with self.assertRaisesRegex(v.ValidationError,'completed confirmation'): self.check()

    def test_candidate_contract_cannot_be_missing(self):
        self.complete_candidate()
        self.s['candidate_ledger'][0]['gate_contract_sha256']=None
        with self.assertRaisesRegex(v.ValidationError,'frozen gate contract hash'): self.check()

    def test_candidate_cannot_disappear(self):
        self.complete_candidate()
        self.s['transitions'][5]['candidate_id']='candidate-999'
        with self.assertRaisesRegex(v.ValidationError,'exist in the ledger'): self.check()

    def pivot(self):
        self.s['transitions'].insert(1, copy.deepcopy(self.s['transitions'][0]))
        self.s['transitions'][1].update(sequence=2, **{'from':'searching','to':'screening','delegated_decision':'gate_transition'})
        self.s['transitions'].insert(2, copy.deepcopy(self.s['transitions'][0]))
        self.s['transitions'][2].update(sequence=3, **{'from':'screening','to':'searching','delegated_decision':'candidate_pivot','candidate_id':'candidate-001'})
        self.s['transitions'][3]['sequence']=4
        self.s['candidate_ledger']=[{'candidate_id':'candidate-001','status':'stopped','disposition':'Synthetic screening rejection', 'gate_contract_sha256':None,'repairs_used':0}]
        self.s['budgets_used'].update(candidates=1,pivots=1)

    def test_preserved_screening_pivot_valid(self): self.pivot(); self.check()

    def test_pivot_requires_selection_authority(self):
        self.pivot()
        self.m['authorization']['delegated_decisions'].remove('candidate_selection')
        with self.assertRaisesRegex(v.ValidationError,'pivot requires candidate_selection'): self.check()

    def test_pivot_requires_stopped_candidate(self):
        self.pivot()
        self.s['candidate_ledger'][0]['status']='screening'
        with self.assertRaisesRegex(v.ValidationError,'preserved stopped candidate'): self.check()

    def test_missing_checks_cannot_vacuously_pass(self):
        self.complete_candidate()
        self.p['checks']={}
        with self.assertRaisesRegex(v.ValidationError,'all six'): self.check()

    def test_check_evidence_cannot_escape(self):
        self.p['checks']['hostile_review']['evidence_refs']=['../outside.json']
        with self.assertRaisesRegex(v.ValidationError,'must not escape'): self.check()

    def test_complete_success_with_hashes_passes(self):
        self.complete_candidate()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.populate(root)
            self.check()
            v.validate_project_artifacts(self.p,root)

    def test_nonexistent_unlisted_evidence_fails(self):
        self.complete_candidate()
        self.check()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(v.ValidationError,'absent from hashed artifacts'): v.validate_project_artifacts(self.p,Path(directory))

    def test_missing_product_fails_even_with_check_evidence(self):
        self.complete_candidate()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.populate(root)
            self.p['manuscript']['path']='campaign/nonexistent.md'
            with self.assertRaisesRegex(v.ValidationError,'manuscript is missing'): v.validate_project_artifacts(self.p,root)

    def test_unhashed_code_file_fails(self):
        self.complete_candidate()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.populate(root)
            (root/'campaign/code/extra.py').write_text('unhashed\n')
            with self.assertRaisesRegex(v.ValidationError,'code file is absent'): v.validate_project_artifacts(self.p,root)

    def test_changed_artifact_fails(self):
        self.complete_candidate()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.populate(root)
            (root/'campaign/evidence.json').write_text('changed\n')
            with self.assertRaisesRegex(v.ValidationError,'hash mismatch'): v.validate_project_artifacts(self.p,root)

if __name__ == '__main__': unittest.main(verbosity=2)
