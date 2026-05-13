"""cmd_016 OpenAI gpt-image-2 ImageProvider — Phase 2 SKETCH ONLY.

CRITICAL: Phase 2 (this file's current state) is mock/placeholder only.
- NO SDK live client object instantiation (the OpenAI SDK client classes are
  not imported and not constructed in this module — see section 12 guard #2
  of the spec doc for the explicit ban list)
- NO live API call
- NO actual image generation
- NO Supabase upload
- NO cost charge

Local mock ImageProvider class / placeholder stub function / abstraction
interface 実装可 (= 必達、guard #2 整合)。Live call logic is enabled in
Phase 3 only (= after both API key acquisition + shogun explicit approval).
See docs/cmd_016_gpt_image_integration_spec.md section 12 (guard #2) and
section 13 (Rule 11 boundary).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable


PRIMARY_MODEL = "gpt-image-2"
FALLBACK_MODELS: tuple[str, ...] = ()

SUPPORTED_SIZES = ("1024x1024", "1024x1536", "1536x1024")
SUPPORTED_QUALITY = ("low", "medium", "high")

RATE_LIMIT_IPM_BY_TIER = {1: 5, 2: 20, 3: 50, 4: 150, 5: 250}

PRICING_PER_IMAGE: dict[str, dict[str, dict[str, float]]] = {}

BUDGET_THRESHOLDS_USD = {"warn": 5.0, "halt_review": 10.0, "emergency_stop": 20.0}


@runtime_checkable
class ImageProvider(Protocol):
    """Phase 2 abstraction interface — local mock allowed, SDK live client 禁."""

    model_id: str
    provider_name: str

    def generate(self, prompt: str, options: Optional[dict] = None) -> dict:
        ...


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
    """Phase 2: per-image table 未確定 retain (= 公式 calculator 機械 verify Phase 3 必達)。

    旧 v1 spec の previous-id per-image table は SoT 不一致 retain 撤退、Phase 2 では
    placeholder 0.0 を返す。Phase 3 で 公式 calculator から per-image cost を機械 verify
    後に PRICING_PER_IMAGE table を埋める。
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


class OpenAIImageProvider:
    """Local mock ImageProvider — Phase 2 only。

    SDK live client instantiation は本 class 内で一切行わぬ (= guard #2 整合)。
    Phase 3 で _live_call() 等の internal helper を追加し、SDK 経由の実呼出を
    組み込む path 想定。
    """

    provider_name = "openai"
    model_id = PRIMARY_MODEL

    def generate(self, prompt: str, options: Optional[dict] = None) -> dict:
        options = options or {}
        size = options.get("size", "1024x1024")
        quality = options.get("quality", "medium")
        n = options.get("n", 1)
        model = options.get("model", self.model_id)
        seed_id = options.get("seed_id")

        if size not in SUPPORTED_SIZES:
            raise ValueError(f"unsupported size: {size}")
        if quality not in SUPPORTED_QUALITY:
            raise ValueError(f"unsupported quality: {quality}")
        if model != PRIMARY_MODEL and model not in FALLBACK_MODELS:
            raise ValueError(f"unsupported model: {model}")

        return {
            "phase": "phase2_sketch_no_live_call",
            "provider": self.provider_name,
            "model": model,
            "size": size,
            "quality": quality,
            "n": n,
            "seed_id": seed_id,
            "estimated_cost_usd": estimate_cost(model, size, quality, n),
            "image_url_placeholder": "<PHASE3_SUPABASE_STORAGE_URL>",
            "note": "live call enabled in Phase 3 only",
        }


def generate_image(request: ImageRequest) -> dict:
    """Compatibility wrapper retained for v1-v3 test 整合。

    内部で OpenAIImageProvider().generate(...) を呼出すのみ、SDK 真実 client は
    一切 instantiate せぬ。
    """
    provider = OpenAIImageProvider()
    return provider.generate(
        request.prompt,
        {
            "size": request.size,
            "quality": request.quality,
            "n": request.n,
            "model": request.model,
            "seed_id": request.seed_id,
        },
    )


def record_cost_log(entry: CostLogEntry) -> dict:
    """SKETCH ONLY — Phase 2。

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
        prompt="phase2 dual model sketch only, no live call",
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
