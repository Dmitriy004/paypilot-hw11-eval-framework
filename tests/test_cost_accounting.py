"""Reporting integrity: unknown cost must not become zero."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_eval


def call(model, input_tokens, output_tokens, cached=0):
    return {"gen_ai.request.model": model, "gen_ai.usage.input_tokens": input_tokens,
            "gen_ai.usage.output_tokens": output_tokens,
            "gen_ai.usage.cache_read_input_tokens": cached}


def test_tariff_uses_cached_bucket_and_output_including_reasoning():
    # 600 uncached + 400 cached input, 200 output; reasoning already inside output.
    assert run_eval.estimate_cost([call("gpt-4.1-mini-2025-04-14",1000,200,400)]) == pytest.approx(0.0006)


def test_unknown_model_or_missing_calls_has_unknown_cost():
    assert run_eval.estimate_cost([call("unpriced",1000,200)]) is None
    assert run_eval.estimate_cost([]) is None


def test_gpt5_preflight_tariff_is_separate_from_main_model():
    assert run_eval.estimate_cost([call("gpt-5-mini-2025-08-07",1000,100,0)]) == pytest.approx(0.00045)


def test_meter_does_not_turn_unknown_into_zero(monkeypatch):
    class Stand:
        def chat(self): return {"request_id":"R-unknown","usage":{"cost_usd":None}}
        def trace(self, request_id): return {}
        def llm_calls(self, tree): return [call("unpriced",100,20)]
    monkeypatch.setattr(run_eval,"SPENT",{"agent_calls":0,"cost_usd":0.0,"requests":[]})
    stand=Stand()
    run_eval._meter(stand)
    stand.chat()
    assert run_eval.SPENT["cost_usd"] is None
    assert run_eval.SPENT["requests"][0]["cost_basis"] == "unknown"


@pytest.mark.parametrize("reported", [None, 0.012])
def test_successful_chat_stays_recorded_when_trace_transport_fails(monkeypatch, reported):
    class Stand:
        class StandError(RuntimeError): pass
        def chat(self): return {"request_id":"R-paid", "usage":{"cost_usd":reported},"answer":"done"}
        def trace(self, request_id): raise self.StandError("trace service unavailable")
        def llm_calls(self, tree): raise AssertionError("no tree should be parsed")
    monkeypatch.setattr(run_eval,"SPENT",{"agent_calls":0,"cost_usd":0.0,"requests":[]})
    stand=Stand(); run_eval._meter(stand)
    assert stand.chat()["answer"]=="done"
    assert run_eval.SPENT["cost_usd"]==reported
    assert run_eval.SPENT["requests"][0]["request_id"]=="R-paid"
    assert run_eval.SPENT["requests"][0]["trace_error"]


@pytest.mark.parametrize("inp,out,cached", [
    (0,0,0), (None,10,0), (-1,10,0), (100,-1,0),
    (100,10,None), (100,10,-1), (100,10,101), (True,10,0),
])
def test_missing_or_invalid_token_usage_remains_unknown(inp,out,cached):
    assert run_eval.estimate_cost([call("gpt-4.1-mini-2025-04-14",inp,out,cached)]) is None
