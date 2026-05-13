"""cmd_016 Google gemini-3.1-flash-image-preview (Nano Banana 2) ImageProvider — Phase 2 SKETCH ONLY.

CRITICAL: Phase 2 (this file's current state) is mock/placeholder only.
- NO SDK live client object instantiation (the Google GenAI SDK client classes
  are not imported and not constructed in this module — see section 12 guard
  #2 of the spec doc for the explicit ban list)
- NO live API call
- NO actual image generation
- NO Supabase upload
- NO cost charge

Local mock ImageProvider class / placeholder stub function / abstraction interface
実装可 (= 必達、guard #2 整合)。Live call logic is enabled in Phase 3 only
(= after both API key acquisition + shogun explicit approval). See
docs/cmd_016_gpt_image_integration_spec.md section 12 (guard #2) and
section 13 (Rule 11 boundary).

公式 SoT 機械 verify 2026-05-13 (= WebFetch confirmed):
- model ID: gemini-3.1-flash-image-preview (= Nano Banana 2 preview)
- status: Preview
- reference images: up to 14 (= 10 objects high-fidelity + 4 character images)
- resolution: 512 / 1K / 2K / 4K
- thinking control: minimal / high + includeThoughts boolean
- endpoint: https://generativelanguage.googleapis.com/v1beta/models/
            gemini-3.1-flash-image-preview:generateContent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


PRIMARY_MODEL = "gemini-3.1-flash-image-preview"
STABLE_RETAIN_CANDIDATE = "gemini-2.5-flash-image"
FALLBACK_MODELS: tuple[str, ...] = (STABLE_RETAIN_CANDIDATE,)

SUPPORTED_RESOLUTIONS = ("512", "1K", "2K", "4K")
SUPPORTED_THINKING_LEVELS = ("minimal", "high")

REFERENCE_IMAGE_MAX = 14
REFERENCE_IMAGE_BREAKDOWN = {"object_high_fidelity": 10, "character_consistency": 4}

PRICING_PER_IMAGE: dict[str, dict[str, float]] = {}

BUDGET_THRESHOLDS_USD = {"warn": 5.0, "halt_review": 10.0, "emergency_stop": 20.0}


@dataclass(frozen=True)
class GeminiImageRequest:
    prompt: str
    resolution: str = "1K"
    thinking_level: str = "minimal"
    include_thoughts: bool = False
    reference_image_count: int = 0
    model: str = PRIMARY_MODEL
    seed_id: Optional[str] = None


@dataclass(frozen=True)
class GeminiCostLogEntry:
    model: str
    resolution: str
    thinking_level: str
    estimated_cost_usd: float
    seed_id: Optional[str] = None
    extra: dict = field(default_factory=dict)


def estimate_cost(model: str, resolution: str, thinking_level: str = "minimal") -> float:
    """Phase 2: per-image table 未確定 retain (= 公式 pricing page 機械 verify Phase 3 必達)。

    Google AI は per-token 体系 (= input/output token 別)、本 Phase 2 では placeholder 0.0、
    Phase 3 で 公式 pricing page から per-token + per-image effective cost を機械 verify。
    """
    table = PRICING_PER_IMAGE.get(model, {})
    per_image = table.get(resolution)
    if per_image is None:
        return 0.0
    return round(per_image, 6)


def _read_api_key_placeholder() -> str:
    """Phase 2: return placeholder only, never read real key.

    Phase 3 will read GOOGLE_AI_API_KEY (or GEMINI_API_KEY) env var. We
    intentionally do NOT read it here, to keep skeleton free of any
    real-key path until Phase 3.
    """
    return "<GOOGLE_AI_API_KEY_PHASE3_PLACEHOLDER>"


class GeminiImageProvider:
    """Local mock ImageProvider — Phase 2 only。

    SDK live client instantiation は本 class 内で一切行わぬ (= guard #2 整合)。
    Phase 3 で SDK 経由の実呼出を組み込む path 想定。
    """

    provider_name = "google"
    model_id = PRIMARY_MODEL

    def generate(self, prompt: str, options: Optional[dict] = None) -> dict:
        options = options or {}
        resolution = options.get("resolution", "1K")
        thinking_level = options.get("thinking_level", "minimal")
        include_thoughts = options.get("include_thoughts", False)
        reference_image_count = options.get("reference_image_count", 0)
        model = options.get("model", self.model_id)
        seed_id = options.get("seed_id")

        if resolution not in SUPPORTED_RESOLUTIONS:
            raise ValueError(f"unsupported resolution: {resolution}")
        if thinking_level not in SUPPORTED_THINKING_LEVELS:
            raise ValueError(f"unsupported thinking_level: {thinking_level}")
        if reference_image_count < 0 or reference_image_count > REFERENCE_IMAGE_MAX:
            raise ValueError(
                f"reference_image_count out of range [0,{REFERENCE_IMAGE_MAX}]: "
                f"{reference_image_count}"
            )
        if model != PRIMARY_MODEL and model not in FALLBACK_MODELS:
            raise ValueError(f"unsupported model: {model}")

        return {
            "phase": "phase2_sketch_no_live_call",
            "provider": self.provider_name,
            "model": model,
            "resolution": resolution,
            "thinking_level": thinking_level,
            "include_thoughts": include_thoughts,
            "reference_image_count": reference_image_count,
            "seed_id": seed_id,
            "estimated_cost_usd": estimate_cost(model, resolution, thinking_level),
            "image_url_placeholder": "<PHASE3_SUPABASE_STORAGE_URL>",
            "thinking_metadata_placeholder": (
                "<PHASE3_THINKING_TRACE>" if include_thoughts else None
            ),
            "note": "live call enabled in Phase 3 only",
        }


def generate_image(request: GeminiImageRequest) -> dict:
    """Compatibility wrapper — Phase 2 mock 経由 GeminiImageProvider 呼出。"""
    provider = GeminiImageProvider()
    return provider.generate(
        request.prompt,
        {
            "resolution": request.resolution,
            "thinking_level": request.thinking_level,
            "include_thoughts": request.include_thoughts,
            "reference_image_count": request.reference_image_count,
            "model": request.model,
            "seed_id": request.seed_id,
        },
    )


def record_cost_log(entry: GeminiCostLogEntry) -> dict:
    return {
        "phase": "phase2_sketch_no_persist",
        "model": entry.model,
        "resolution": entry.resolution,
        "thinking_level": entry.thinking_level,
        "estimated_cost_usd": entry.estimated_cost_usd,
        "seed_id": entry.seed_id,
    }


def check_budget_threshold(accumulated_usd: float) -> str:
    if accumulated_usd >= BUDGET_THRESHOLDS_USD["emergency_stop"]:
        return "emergency_stop"
    if accumulated_usd >= BUDGET_THRESHOLDS_USD["halt_review"]:
        return "halt_review"
    if accumulated_usd >= BUDGET_THRESHOLDS_USD["warn"]:
        return "warn"
    return "ok"


def select_provider(use_case: str) -> str:
    """Phase 2 用途別 routing logic (= spec §4.3 整合)。

    Returns the model_id string for the selected provider. Phase 3 may
    return a provider instance instead.
    """
    if use_case == "character":
        return "gpt-image-2"
    if use_case == "composition":
        return "gemini-3.1-flash-image-preview"
    if use_case == "bulk_low_cost":
        return "gemini-2.5-flash-image"
    return "gpt-image-2"


if __name__ == "__main__":
    sample = GeminiImageRequest(
        prompt="phase2 dual model sketch only, no live call",
        resolution="2K",
        thinking_level="high",
        include_thoughts=True,
        reference_image_count=3,
        model=PRIMARY_MODEL,
        seed_id="phase2-gemini-sketch-001",
    )
    result = generate_image(sample)
    print("[phase2_sketch] gemini result:", result)
    print(
        "[phase2_sketch] gemini api_key_path:",
        _read_api_key_placeholder(),
    )
