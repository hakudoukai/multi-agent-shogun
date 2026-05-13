"""cmd_016 OpenAI gpt-image-1.5 client wrapper — Phase 2 SKETCH ONLY.

CRITICAL: Phase 2 (this file's current state) is mock/placeholder only.
- NO openai client object instantiation
- NO live API call
- NO actual image generation
- NO Supabase upload
- NO cost charge

Live call logic is enabled in Phase 3 only (= after API key acquisition
+ shogun explicit approval). See docs/cmd_016_gpt_image_integration_spec.md
section 11.2 (guard #2) and section 12 (Rule 11 boundary).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


PRIMARY_MODEL = "gpt-image-1.5"
FALLBACK_MODELS = ("gpt-image-1", "gpt-image-1-mini")

SUPPORTED_SIZES = ("1024x1024", "1024x1536", "1536x1024")
SUPPORTED_QUALITY = ("low", "medium", "high")

PRICING_PER_IMAGE = {
    "gpt-image-1.5": {
        "1024x1024": {"low": 0.009, "medium": 0.034, "high": 0.133},
        "1024x1536": {"low": 0.013, "medium": 0.050, "high": 0.200},
        "1536x1024": {"low": 0.013, "medium": 0.050, "high": 0.200},
    },
    "gpt-image-1": {
        "1024x1024": {"low": 0.011, "medium": 0.042, "high": 0.167},
    },
    "gpt-image-1-mini": {
        "1024x1024": {"low": 0.005, "medium": 0.011, "high": 0.036},
    },
}

BUDGET_THRESHOLDS_USD = {"warn": 5.0, "halt_review": 10.0, "emergency_stop": 20.0}


@dataclass(frozen=True)
class ImageRequest:
    prompt: str
    n: int = 1
    size: str = "1024x1024"
    quality: str = "medium"
    model: str = PRIMARY_MODEL
    seed_id: Optional[str] = None


@dataclass(frozen=True)
class CostLogEntry:
    model: str
    size: str
    quality: str
    n: int
    estimated_cost_usd: float
    seed_id: Optional[str] = None
    extra: dict = field(default_factory=dict)


def estimate_cost(model: str, size: str, quality: str, n: int = 1) -> float:
    """Lookup per-image price from official pricing table and multiply by n.

    Phase 2: pure local calculation, no network call.
    """
    table = PRICING_PER_IMAGE.get(model, {})
    by_size = table.get(size, {})
    per_image = by_size.get(quality)
    if per_image is None:
        return 0.0
    return round(per_image * n, 6)


def _read_api_key_placeholder() -> str:
    """Phase 2: return placeholder only, never read real key.

    Phase 3 will read the OPENAI key env var. We intentionally do NOT
    read it here, to keep skeleton free of any real-key path until Phase 3.
    """
    return "<OPENAI_API_KEY_PHASE3_PLACEHOLDER>"


def generate_image(request: ImageRequest) -> dict:
    """SKETCH ONLY — Phase 2.

    Returns placeholder dict. No openai client object generated, no API call.
    Phase 3 will replace the body with the real SDK client + Supabase Storage upload.
    """
    if request.size not in SUPPORTED_SIZES:
        raise ValueError(f"unsupported size: {request.size}")
    if request.quality not in SUPPORTED_QUALITY:
        raise ValueError(f"unsupported quality: {request.quality}")
    if request.model != PRIMARY_MODEL and request.model not in FALLBACK_MODELS:
        raise ValueError(f"unsupported model: {request.model}")

    estimated_cost = estimate_cost(
        request.model, request.size, request.quality, request.n
    )
    return {
        "phase": "phase2_sketch_no_live_call",
        "model": request.model,
        "size": request.size,
        "quality": request.quality,
        "n": request.n,
        "seed_id": request.seed_id,
        "estimated_cost_usd": estimated_cost,
        "image_url_placeholder": "<PHASE3_SUPABASE_STORAGE_URL>",
        "note": "live call enabled in Phase 3 only",
    }


def record_cost_log(entry: CostLogEntry) -> dict:
    """SKETCH ONLY — Phase 2.

    Phase 3 will persist to queue/reports/openai_image_cost_log.yaml
    or Supabase table. Phase 2 returns a placeholder dict mirroring
    the future schema for skeleton tests.
    """
    return {
        "phase": "phase2_sketch_no_persist",
        "model": entry.model,
        "size": entry.size,
        "quality": entry.quality,
        "n": entry.n,
        "estimated_cost_usd": entry.estimated_cost_usd,
        "seed_id": entry.seed_id,
    }


def check_budget_threshold(accumulated_usd: float) -> str:
    """Return alert level given accumulated cost.

    Phase 2: pure local logic for skeleton tests. Phase 3 will raise +
    notify on emergency_stop.
    """
    if accumulated_usd >= BUDGET_THRESHOLDS_USD["emergency_stop"]:
        return "emergency_stop"
    if accumulated_usd >= BUDGET_THRESHOLDS_USD["halt_review"]:
        return "halt_review"
    if accumulated_usd >= BUDGET_THRESHOLDS_USD["warn"]:
        return "warn"
    return "ok"


if __name__ == "__main__":
    sample = ImageRequest(
        prompt="phase2 sketch only, no live call",
        n=1,
        size="1024x1024",
        quality="medium",
        model=PRIMARY_MODEL,
        seed_id="phase2-sketch-001",
    )
    result = generate_image(sample)
    print("[phase2_sketch] result:", result)
    print(
        "[phase2_sketch] api_key_path:",
        _read_api_key_placeholder(),
    )
