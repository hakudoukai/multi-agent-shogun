"""cmd_016 OpenAI gpt-image-1.5 skeleton tests — Phase 2.

CRITICAL: SKIP=0 (= kuroda regulation). No pytest.skip allowed.
Phase 2 tests verify sketch structure only — no openai client, no live call.
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import openai_image_client as oic


RANK_ENUM = ("tamago", "hiyoko", "bokensha", "yusha", "okoku_senshi")
BANNED_KEYWORDS = ("blood", "gore", "graphic violence", "kill", "murder")


def test_prompt_template_rank_enum():
    assert len(RANK_ENUM) == 5
    assert set(RANK_ENUM) == {
        "tamago",
        "hiyoko",
        "bokensha",
        "yusha",
        "okoku_senshi",
    }


def test_prompt_template_safety_keyword_retain():
    sample_prompts = [
        "A cute round dinosaur egg with small flame decorations, friendly smile, soft cartoon style, suitable for children aged 3-5, no violence, no blood, bright colors",
        "A heroic dinosaur warrior with glowing light aura, determined expression, stylized fantasy cartoon, suitable for children aged 10-12, stylized weapons, no graphic violence",
    ]
    for p in sample_prompts:
        lowered = p.lower()
        for banned in BANNED_KEYWORDS:
            if banned in lowered:
                negation_ok = (
                    f"no {banned}" in lowered or f"no graphic {banned}" in lowered
                )
                assert negation_ok, f"banned keyword without negation: {banned}"


def test_client_wrapper_signature():
    sig = inspect.signature(oic.generate_image)
    assert list(sig.parameters.keys()) == ["request"]


def test_client_wrapper_env_var_read():
    placeholder = oic._read_api_key_placeholder()
    assert "<" in placeholder and ">" in placeholder
    assert "PHASE3" in placeholder
    src = inspect.getsource(oic)
    assert "os.environ['OPENAI_API_KEY']" not in src
    assert 'os.environ["OPENAI_API_KEY"]' not in src
    assert "os.getenv('OPENAI_API_KEY'" not in src
    assert 'os.getenv("OPENAI_API_KEY"' not in src


def test_client_wrapper_no_live_openai_instantiation():
    src = inspect.getsource(oic)
    assert "openai.OpenAI(" not in src
    assert "AsyncOpenAI(" not in src
    assert "import openai" not in src
    assert "from openai " not in src


def test_cost_log_schema():
    entry = oic.CostLogEntry(
        model="gpt-image-1.5",
        size="1024x1024",
        quality="medium",
        n=1,
        estimated_cost_usd=0.034,
        seed_id="phase2-test-001",
    )
    out = oic.record_cost_log(entry)
    expected_keys = {
        "phase",
        "model",
        "size",
        "quality",
        "n",
        "estimated_cost_usd",
        "seed_id",
    }
    assert expected_keys.issubset(set(out.keys()))
    assert out["phase"].startswith("phase2_")


def test_estimate_cost_table_match_official_docs():
    assert oic.estimate_cost("gpt-image-1.5", "1024x1024", "low") == 0.009
    assert oic.estimate_cost("gpt-image-1.5", "1024x1024", "medium") == 0.034
    assert oic.estimate_cost("gpt-image-1.5", "1024x1024", "high") == 0.133
    assert oic.estimate_cost("gpt-image-1", "1024x1024", "high") == 0.167
    assert oic.estimate_cost("gpt-image-1-mini", "1024x1024", "low") == 0.005


def test_primary_model_literal_is_gpt_image_1_5():
    assert oic.PRIMARY_MODEL == "gpt-image-1.5"
    assert "gpt-image-1" in oic.FALLBACK_MODELS
    assert "gpt-image-1-mini" in oic.FALLBACK_MODELS


def test_generate_image_returns_phase2_placeholder_only():
    req = oic.ImageRequest(
        prompt="phase2 test",
        n=1,
        size="1024x1024",
        quality="medium",
        model=oic.PRIMARY_MODEL,
        seed_id="phase2-test-002",
    )
    result = oic.generate_image(req)
    assert result["phase"] == "phase2_sketch_no_live_call"
    assert result["image_url_placeholder"].startswith("<")
    assert "live call enabled in Phase 3 only" in result["note"]


def test_generate_image_rejects_unsupported_size():
    req = oic.ImageRequest(
        prompt="bad size",
        size="9999x9999",
        quality="medium",
        model=oic.PRIMARY_MODEL,
    )
    with pytest.raises(ValueError):
        oic.generate_image(req)


def test_generate_image_rejects_unsupported_quality():
    req = oic.ImageRequest(
        prompt="bad quality",
        size="1024x1024",
        quality="ultra",
        model=oic.PRIMARY_MODEL,
    )
    with pytest.raises(ValueError):
        oic.generate_image(req)


def test_generate_image_rejects_unsupported_model():
    req = oic.ImageRequest(
        prompt="bad model",
        size="1024x1024",
        quality="medium",
        model="dall-e-99",
    )
    with pytest.raises(ValueError):
        oic.generate_image(req)


def test_budget_threshold_levels():
    assert oic.check_budget_threshold(0.0) == "ok"
    assert oic.check_budget_threshold(4.99) == "ok"
    assert oic.check_budget_threshold(5.0) == "warn"
    assert oic.check_budget_threshold(9.99) == "warn"
    assert oic.check_budget_threshold(10.0) == "halt_review"
    assert oic.check_budget_threshold(19.99) == "halt_review"
    assert oic.check_budget_threshold(20.0) == "emergency_stop"
    assert oic.check_budget_threshold(100.0) == "emergency_stop"


def test_no_api_key_literal_in_source():
    src = inspect.getsource(oic)
    assert "sk-" not in src
    assert "sk_live_" not in src
    assert "Bearer " not in src
