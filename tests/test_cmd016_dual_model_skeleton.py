"""cmd_016 dual model (OpenAI gpt-image-2 + Google gemini-3.1-flash-image-preview)
skeleton tests — Phase 2.

CRITICAL: SKIP=0 (= kuroda regulation). No pytest.skip allowed.
Phase 2 tests verify sketch structure only — no SDK true client, no live call.

Renamed from tests/test_cmd016_gpt_image_skeleton.py via `git mv`
(履歴 link path retain、AC 整合).
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import openai_image_client as oic  # noqa: E402
import gemini_image_client as gic  # noqa: E402


RANK_ENUM = ("tamago", "hiyoko", "bokensha", "yusha", "okoku_senshi")
BANNED_KEYWORDS = ("blood", "gore", "graphic violence", "kill", "murder")


# ──────────────────────────────────────────────────────────
# OpenAI provider (= gpt-image-2)
# ──────────────────────────────────────────────────────────


def test_openai_provider_model_id_is_gpt_image_2():
    assert oic.PRIMARY_MODEL == "gpt-image-2"
    provider = oic.OpenAIImageProvider()
    assert provider.model_id == "gpt-image-2"
    assert provider.provider_name == "openai"


def test_openai_provider_no_sdk_instantiation():
    src = inspect.getsource(oic)
    assert "openai.OpenAI(" not in src
    assert "AsyncOpenAI(" not in src
    assert "import openai" not in src
    assert "from openai " not in src


def test_openai_provider_generate_returns_phase2_placeholder():
    provider = oic.OpenAIImageProvider()
    result = provider.generate("phase2 test", {"size": "1024x1024", "quality": "medium"})
    assert result["phase"] == "phase2_sketch_no_live_call"
    assert result["provider"] == "openai"
    assert result["model"] == "gpt-image-2"
    assert result["image_url_placeholder"].startswith("<")
    assert "live call enabled in Phase 3 only" in result["note"]


def test_openai_provider_rejects_unsupported_size():
    provider = oic.OpenAIImageProvider()
    with pytest.raises(ValueError):
        provider.generate("bad size", {"size": "9999x9999"})


def test_openai_provider_rejects_unsupported_quality():
    provider = oic.OpenAIImageProvider()
    with pytest.raises(ValueError):
        provider.generate("bad quality", {"quality": "ultra"})


def test_openai_provider_rejects_unsupported_model():
    provider = oic.OpenAIImageProvider()
    with pytest.raises(ValueError):
        provider.generate("bad model", {"model": "dall-e-99"})


def test_openai_env_var_placeholder_only():
    placeholder = oic._read_api_key_placeholder()
    assert "<" in placeholder and ">" in placeholder
    assert "PHASE3" in placeholder
    src = inspect.getsource(oic)
    assert "os.environ['OPENAI_API_KEY']" not in src
    assert 'os.environ["OPENAI_API_KEY"]' not in src
    assert "os.getenv('OPENAI_API_KEY'" not in src
    assert 'os.getenv("OPENAI_API_KEY"' not in src


def test_openai_rate_limit_official_verified():
    assert oic.RATE_LIMIT_IPM_BY_TIER[1] == 5
    assert oic.RATE_LIMIT_IPM_BY_TIER[5] == 250


def test_openai_pricing_per_image_table_phase3_verify_pending():
    assert oic.PRICING_PER_IMAGE == {}
    assert oic.estimate_cost("gpt-image-2", "1024x1024", "medium") == 0.0


def test_openai_legacy_generate_image_wrapper_returns_phase2_placeholder():
    req = oic.ImageRequest(
        prompt="phase2 legacy wrapper",
        n=1,
        size="1024x1024",
        quality="medium",
        model=oic.PRIMARY_MODEL,
        seed_id="phase2-test-legacy",
    )
    result = oic.generate_image(req)
    assert result["phase"] == "phase2_sketch_no_live_call"
    assert result["provider"] == "openai"


def test_openai_cost_log_schema():
    entry = oic.CostLogEntry(
        model="gpt-image-2",
        size="1024x1024",
        quality="medium",
        n=1,
        estimated_cost_usd=0.0,
        seed_id="phase2-test-001",
    )
    out = oic.record_cost_log(entry)
    expected_keys = {"phase", "model", "size", "quality", "n", "estimated_cost_usd", "seed_id"}
    assert expected_keys.issubset(set(out.keys()))
    assert out["phase"].startswith("phase2_")


def test_openai_budget_threshold_levels():
    assert oic.check_budget_threshold(0.0) == "ok"
    assert oic.check_budget_threshold(4.99) == "ok"
    assert oic.check_budget_threshold(5.0) == "warn"
    assert oic.check_budget_threshold(9.99) == "warn"
    assert oic.check_budget_threshold(10.0) == "halt_review"
    assert oic.check_budget_threshold(19.99) == "halt_review"
    assert oic.check_budget_threshold(20.0) == "emergency_stop"
    assert oic.check_budget_threshold(100.0) == "emergency_stop"


def test_openai_no_api_key_literal_in_source():
    src = inspect.getsource(oic)
    assert "sk-" not in src
    assert "sk_live_" not in src
    assert "Bearer " not in src


# ──────────────────────────────────────────────────────────
# Gemini provider (= gemini-3.1-flash-image-preview = Nano Banana 2)
# ──────────────────────────────────────────────────────────


def test_gemini_provider_model_id_is_3_1_flash_image_preview():
    assert gic.PRIMARY_MODEL == "gemini-3.1-flash-image-preview"
    assert gic.STABLE_RETAIN_CANDIDATE == "gemini-2.5-flash-image"
    provider = gic.GeminiImageProvider()
    assert provider.model_id == "gemini-3.1-flash-image-preview"
    assert provider.provider_name == "google"


def test_gemini_provider_no_sdk_instantiation():
    src = inspect.getsource(gic)
    assert "google.generativeai.GenerativeModel(" not in src
    assert "genai.Client(" not in src
    assert "genai.GenerativeModel(" not in src
    assert "import google.generativeai" not in src
    assert "from google.generativeai" not in src
    assert "from google import genai" not in src


def test_gemini_provider_generate_returns_phase2_placeholder():
    provider = gic.GeminiImageProvider()
    result = provider.generate("phase2 test", {"resolution": "2K", "thinking_level": "high"})
    assert result["phase"] == "phase2_sketch_no_live_call"
    assert result["provider"] == "google"
    assert result["model"] == "gemini-3.1-flash-image-preview"
    assert result["image_url_placeholder"].startswith("<")
    assert "live call enabled in Phase 3 only" in result["note"]


def test_gemini_provider_reference_image_max_14():
    """Official Google docs verify ✅ 2026-05-13: up to 14 reference images
    (= 10 objects high-fidelity + 4 character images for consistency)."""
    assert gic.REFERENCE_IMAGE_MAX == 14
    assert gic.REFERENCE_IMAGE_BREAKDOWN["object_high_fidelity"] == 10
    assert gic.REFERENCE_IMAGE_BREAKDOWN["character_consistency"] == 4

    provider = gic.GeminiImageProvider()
    result = provider.generate("composition", {"reference_image_count": 14})
    assert result["reference_image_count"] == 14

    with pytest.raises(ValueError):
        provider.generate("over limit", {"reference_image_count": 15})
    with pytest.raises(ValueError):
        provider.generate("negative", {"reference_image_count": -1})


def test_gemini_provider_thinking_levels_minimal_high():
    assert set(gic.SUPPORTED_THINKING_LEVELS) == {"minimal", "high"}
    provider = gic.GeminiImageProvider()
    for level in ("minimal", "high"):
        result = provider.generate("p", {"thinking_level": level})
        assert result["thinking_level"] == level
    with pytest.raises(ValueError):
        provider.generate("bad", {"thinking_level": "deep"})


def test_gemini_provider_include_thoughts_metadata_placeholder():
    provider = gic.GeminiImageProvider()
    on = provider.generate("p", {"include_thoughts": True})
    off = provider.generate("p", {"include_thoughts": False})
    assert on["thinking_metadata_placeholder"] is not None
    assert on["thinking_metadata_placeholder"].startswith("<")
    assert off["thinking_metadata_placeholder"] is None


def test_gemini_provider_supported_resolutions():
    assert set(gic.SUPPORTED_RESOLUTIONS) == {"512", "1K", "2K", "4K"}
    provider = gic.GeminiImageProvider()
    with pytest.raises(ValueError):
        provider.generate("p", {"resolution": "8K"})


def test_gemini_provider_rejects_unsupported_model():
    provider = gic.GeminiImageProvider()
    with pytest.raises(ValueError):
        provider.generate("bad", {"model": "imagen-99"})


def test_gemini_env_var_placeholder_only():
    placeholder = gic._read_api_key_placeholder()
    assert "<" in placeholder and ">" in placeholder
    assert "PHASE3" in placeholder
    src = inspect.getsource(gic)
    assert "os.environ['GOOGLE_AI_API_KEY']" not in src
    assert 'os.environ["GOOGLE_AI_API_KEY"]' not in src
    assert "os.getenv('GOOGLE_AI_API_KEY'" not in src
    assert 'os.getenv("GOOGLE_AI_API_KEY"' not in src


def test_gemini_no_api_key_literal_in_source():
    src = inspect.getsource(gic)
    assert "AIza" not in src
    assert "Bearer " not in src


def test_gemini_cost_log_schema():
    entry = gic.GeminiCostLogEntry(
        model="gemini-3.1-flash-image-preview",
        resolution="2K",
        thinking_level="high",
        estimated_cost_usd=0.0,
        seed_id="phase2-gemini-001",
    )
    out = gic.record_cost_log(entry)
    expected = {"phase", "model", "resolution", "thinking_level", "estimated_cost_usd", "seed_id"}
    assert expected.issubset(set(out.keys()))
    assert out["phase"].startswith("phase2_")


def test_gemini_budget_threshold_levels():
    assert gic.check_budget_threshold(4.99) == "ok"
    assert gic.check_budget_threshold(5.0) == "warn"
    assert gic.check_budget_threshold(10.0) == "halt_review"
    assert gic.check_budget_threshold(20.0) == "emergency_stop"


# ──────────────────────────────────────────────────────────
# ImageProvider abstraction + routing
# ──────────────────────────────────────────────────────────


def test_image_provider_protocol_attrs():
    """OpenAIImageProvider and GeminiImageProvider both satisfy the
    Phase 2 ImageProvider protocol shape (= model_id + provider_name + generate)."""
    o = oic.OpenAIImageProvider()
    g = gic.GeminiImageProvider()
    for p in (o, g):
        assert hasattr(p, "model_id")
        assert hasattr(p, "provider_name")
        assert callable(getattr(p, "generate"))


def test_image_provider_protocol_runtime_check_openai():
    o = oic.OpenAIImageProvider()
    assert isinstance(o, oic.ImageProvider)


def test_router_character_returns_openai():
    assert gic.select_provider("character") == "gpt-image-2"


def test_router_composition_returns_gemini_3_1():
    assert gic.select_provider("composition") == "gemini-3.1-flash-image-preview"


def test_router_bulk_low_cost_returns_gemini_2_5():
    assert gic.select_provider("bulk_low_cost") == "gemini-2.5-flash-image"


def test_router_default_returns_openai():
    assert gic.select_provider("unknown_use_case") == "gpt-image-2"


# ──────────────────────────────────────────────────────────
# Cross-cutting (= v1-v3 retain + 旧 model ID grep guard)
# ──────────────────────────────────────────────────────────


def test_prompt_template_rank_enum():
    assert len(RANK_ENUM) == 5
    assert set(RANK_ENUM) == {"tamago", "hiyoko", "bokensha", "yusha", "okoku_senshi"}


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


def test_no_old_model_id_gpt_image_1_5_in_code():
    """旧モデル ID 'gpt-image-1.5' literal は code body 内全件禁。
    Reflection note 内のみ retain (= 連帯失策 retain reflection、本能寺戒め integrity)。"""
    oic_src = inspect.getsource(oic)
    gic_src = inspect.getsource(gic)
    assert "gpt-image-1.5" not in oic_src
    assert "gpt-image-1.5" not in gic_src
