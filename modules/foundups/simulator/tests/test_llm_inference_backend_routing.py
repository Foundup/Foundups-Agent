"""Tests for simulator LLM backend routing toggles."""

from __future__ import annotations

from modules.foundups.simulator.ai.llm_inference import InferenceResult, SimulatorLLM


def test_qwen_backend_defaults_to_local(monkeypatch):
    monkeypatch.delenv("SIM_QWEN_BACKEND", raising=False)
    llm = SimulatorLLM("qwen")
    assert llm._backend == "local"


def test_qwen_backend_routes_to_ironclaw(monkeypatch):
    monkeypatch.setenv("SIM_QWEN_BACKEND", "ironclaw")
    llm = SimulatorLLM("qwen")

    monkeypatch.setattr(
        llm,
        "_generate_via_ironclaw",
        lambda prompt, max_tokens, temperature: InferenceResult(
            text=f"ironclaw:{prompt}",
            model="qwen_ironclaw",
            latency_ms=5,
            confidence=0.8,
        ),
    )

    def _init_should_not_run():
        raise AssertionError("local initializer should not run when ironclaw route succeeds")

    monkeypatch.setattr(llm, "_initialize", _init_should_not_run)
    result = llm.generate("hello", max_tokens=64, temperature=0.1)
    assert result.model == "qwen_ironclaw"
    assert result.text.startswith("ironclaw:")


def test_qwen_wre_ironclaw_falls_back_to_local_when_route_unavailable(monkeypatch):
    monkeypatch.setenv("SIM_QWEN_BACKEND", "wre_ironclaw")
    llm = SimulatorLLM("qwen")
    monkeypatch.setattr(llm, "_generate_via_wre_ironclaw", lambda **kwargs: None)

    def _init_local():
        llm._llm = lambda *_args, **_kwargs: {
            "choices": [{"text": "local-response"}],
            "usage": {"completion_tokens": 3},
        }
        llm._initialized = True
        return True

    monkeypatch.setattr(llm, "_initialize", _init_local)
    result = llm.generate("fallback")
    assert result.model == "qwen"
    assert result.text == "local-response"
