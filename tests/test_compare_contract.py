"""Comparison must not label incomplete/different-condition records comparable."""
import json
import pytest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_eval


def record(**changes):
    return {"prompt_version":"base.v1","set_hash":"abc","profile":"clean",
            "judge_model":"not-used","rubric_version":"rubric.v1","elapsed":1,
            "passed":1,"failed":0,"cases":[{"id":"X","passed":True}],**changes}


def compare(tmp_path,a,b):
    paths=[tmp_path/'a.json',tmp_path/'b.json']
    for p,d in zip(paths,[a,b]): p.write_text(json.dumps(d),encoding="utf-8")
    return run_eval.compare(*map(str,paths))


def test_missing_version_field_is_not_comparable(tmp_path):
    b=record(); del b['judge_model']
    assert compare(tmp_path,record(),b)==1


def test_inconsistent_case_membership_is_not_comparable(tmp_path):
    assert compare(tmp_path,record(),record(cases=[{"id":"Y","passed":True}]))==1


def test_model_and_prompt_changes_are_two_conditions(tmp_path):
    def machine(model):
        return {"requests":[{"llm_calls":[{"gen_ai.request.model":model}]}]}
    assert compare(tmp_path,record(machine=machine('model-A')),
                   record(prompt_version='base.v4',machine=machine('model-B')))==1


@pytest.mark.parametrize("bad", [
    [{"passed":True}],
    [{"id":"X"}],
    [{"id":"X","passed":"false"}],
    [None],
])
def test_invalid_case_rows_are_diagnostic_not_comparable(tmp_path,bad):
    assert compare(tmp_path,record(),record(cases=bad))==1


def test_null_required_condition_is_not_comparable(tmp_path):
    assert compare(tmp_path,record(set_hash=None),record(set_hash=None))==1
