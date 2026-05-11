#!/usr/bin/env python3
"""extract_dentalbi_form_inventory.py — cmd_004 cycle3 mechanical inventory.

Parses DentalBI source-of-truth files to enumerate the 25-form catalog and
classify each form's route reachability via the standard PdfOverlayPage
navigation (/patients/:patientId/pdf-form/:formType).

For each formType, the script inspects four backend endpoint contracts that
usePdfOverlay invokes in parallel:

  1. /api/documents/template-image  — requires TEMPLATE_SPECS[formType]
                                       (or special-cased lab_order_*)
  2. /api/documents/auto-data       — requires renderer_map[formType]
                                       (lab_order_* needs order_id; nigo_sheet
                                       is rejected by _get_renderer)
  3. /api/documents/field-map       — requires FIELD_MAPS[formType]
  4. /api/documents/generate        — requires renderer_map OR lab_order_map
                                       (with order_id) OR nigo_sheet special

It also checks DocumentLinkBar.tsx (handover-sheet navigation hub) for
operator-facing exposure.

Output: YAML inventory written to <out_path>. Paths in the inventory are
relative to <dentalbi_root> so the report does not leak absolute paths
through the privacy gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Source-file relative paths inside DentalBI
# ---------------------------------------------------------------------------

DOCUMENTS_API_REL = "backend/api/documents.py"
TEMPLATE_OVERLAY_REL = "backend/pdf/template_overlay.py"
FIELD_COORDINATES_REL = "backend/pdf/field_coordinates.py"
DOCUMENT_LINK_BAR_REL = "frontend/src/features/handover-sheet/DocumentLinkBar.tsx"
PDF_OVERLAY_PAGE_REL = "frontend/src/features/documents/PdfOverlayPage.tsx"


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _extract_dict_block(text: str, dict_name: str) -> str:
    """Return the literal body between the first '{' and the matching '}' for
    an assignment ``<dict_name> ... = {``. Empty string if not found.
    """
    pattern = re.compile(rf"\b{re.escape(dict_name)}\b[^=]*=\s*\{{")
    m = pattern.search(text)
    if not m:
        return ""
    start = m.end() - 1  # position of '{'
    depth = 1
    i = start + 1
    while i < len(text) and depth > 0:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i]
        i += 1
    return ""


def _extract_keys(block: str) -> list[str]:
    """Return all "string" keys appearing at depth 0 inside a dict-literal block."""
    keys: list[str] = []
    depth = 0
    i = 0
    while i < len(block):
        c = block[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == '"' and depth == 0:
            # find closing quote
            end = block.find('"', i + 1)
            if end == -1:
                break
            key = block[i + 1 : end]
            # only consider followed by ":" (dict-key form)
            after = block[end + 1 :].lstrip()
            if after.startswith(":"):
                keys.append(key)
            i = end + 1
            continue
        i += 1
    return keys


def parse_renderer_maps(documents_py: str) -> tuple[set[str], set[str], bool]:
    """Return (renderer_map_keys, lab_order_map_keys, has_nigo_special)."""
    renderer_block = _extract_dict_block(documents_py, "renderer_map")
    lab_order_block = _extract_dict_block(documents_py, "lab_order_map")
    has_nigo = bool(re.search(r'form_type\s*==\s*"nigo_sheet"', documents_py))
    return set(_extract_keys(renderer_block)), set(_extract_keys(lab_order_block)), has_nigo


def parse_template_specs(template_py: str) -> set[str]:
    block = _extract_dict_block(template_py, "TEMPLATE_SPECS")
    return set(_extract_keys(block))


def parse_field_maps(field_py: str) -> set[str]:
    block = _extract_dict_block(field_py, "FIELD_MAPS")
    keys = set(_extract_keys(block))
    # also pick up dynamic assignments: FIELD_MAPS["foo"] = ...
    for m in re.finditer(r'FIELD_MAPS\["([^"]+)"\]\s*=', field_py):
        keys.add(m.group(1))
    return keys


def parse_template_labels(template_py: str) -> dict[str, str]:
    block = _extract_dict_block(template_py, "TEMPLATE_LABELS")
    labels: dict[str, str] = {}
    if not block:
        return labels
    for m in re.finditer(r'"([^"]+)"\s*:\s*"([^"]+)"', block):
        labels[m.group(1)] = m.group(2)
    return labels


def parse_document_link_bar(tsx: str) -> set[str]:
    """Collect every formType: 'xxx' (or formType: "xxx") declared in DocumentLinkBar."""
    exposed: set[str] = set()
    for m in re.finditer(r"formType\s*:\s*['\"]([A-Za-z0-9_]+)['\"]", tsx):
        exposed.add(m.group(1))
    return exposed


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

@dataclass
class FormStatus:
    form_type: str
    label: str
    backend_template_image: str   # "available" | "missing" | "special_lab_order"
    backend_field_map: str        # "available" | "missing"
    backend_auto_data: str        # "available" | "lab_order_requires_order_id" | "nigo_sheet_unsupported_in_resolver" | "missing"
    backend_generate: str         # "available" | "lab_order_requires_order_id" | "nigo_sheet_special_case" | "missing"
    navigation_hub_exposure: str  # "exposed" | "not_exposed"
    route_status: str             # "passes" | "broken"
    failure_endpoints: list[str] = field(default_factory=list)
    root_cause_class: str = "none"
    notes: list[str] = field(default_factory=list)


LAB_ORDER_FORM_TYPES = {"lab_order_crown_bridge", "lab_order_denture"}
NIGO_SHEET = "nigo_sheet"


def classify(
    form_type: str,
    template_specs: set[str],
    field_maps: set[str],
    renderer_map: set[str],
    lab_order_map: set[str],
    nigo_special: bool,
    exposed_in_link_bar: set[str],
    labels: dict[str, str],
) -> FormStatus:
    # template-image
    if form_type in template_specs:
        backend_ti = "available"
    elif form_type in LAB_ORDER_FORM_TYPES:
        # documents.py special-cases lab_order_* with hard-coded jpeg/pdf paths
        backend_ti = "special_lab_order"
    else:
        backend_ti = "missing"

    # field-map
    backend_fm = "available" if form_type in field_maps else "missing"

    # auto-data and generate (both invoke _get_renderer)
    if form_type in renderer_map:
        backend_ad = "available"
        backend_gen = "available"
    elif form_type in lab_order_map:
        # _get_renderer raises 400 without order_id; PdfOverlayPage route does
        # not propagate order_id, so auto-data fails.
        backend_ad = "lab_order_requires_order_id"
        backend_gen = "lab_order_requires_order_id"
    elif form_type == NIGO_SHEET and nigo_special:
        # generate is special-cased earlier; auto-data is not.
        backend_ad = "nigo_sheet_unsupported_in_resolver"
        backend_gen = "nigo_sheet_special_case"
    else:
        backend_ad = "missing"
        backend_gen = "missing"

    exposure = "exposed" if form_type in exposed_in_link_bar else "not_exposed"

    failure_endpoints: list[str] = []
    if backend_ti == "missing":
        failure_endpoints.append("/api/documents/template-image")
    if backend_fm == "missing":
        failure_endpoints.append("/api/documents/field-map")
    if backend_ad in {"missing", "lab_order_requires_order_id", "nigo_sheet_unsupported_in_resolver"}:
        failure_endpoints.append("/api/documents/auto-data")
    if backend_gen == "missing":
        failure_endpoints.append("/api/documents/generate")

    # Root-cause classification
    root_cause = "none"
    notes: list[str] = []
    if not failure_endpoints:
        if exposure == "not_exposed":
            root_cause = "navigation_only_gap"
            notes.append("Route works end-to-end but DocumentLinkBar does not surface a button.")
        route_status = "passes"
    else:
        route_status = "broken"
        # Prioritized cause assignment
        if backend_ad == "lab_order_requires_order_id":
            root_cause = "route_contract_mismatch_order_id_required"
            notes.append(
                "_get_renderer raises HTTPException(400, '技工指示書にはorder_idが必要です'); "
                "PdfOverlayPage URL has no order_id slot."
            )
        elif backend_ad == "nigo_sheet_unsupported_in_resolver":
            root_cause = "renderer_resolver_excludes_nigo_sheet"
            notes.append(
                "generate endpoint short-circuits to render_nigo_sheet but auto-data goes "
                "through _get_renderer which lacks a nigo_sheet branch (HTTPException 400)."
            )
        elif backend_ti == "missing" and backend_fm == "missing":
            root_cause = "backend_template_and_field_map_missing"
            notes.append(
                "Renderer exists, but neither TEMPLATE_SPECS nor FIELD_MAPS has an entry."
            )
        elif backend_ti == "missing":
            root_cause = "template_spec_missing"
        elif backend_fm == "missing":
            root_cause = "field_map_missing"
        else:
            root_cause = "other"

    return FormStatus(
        form_type=form_type,
        label=labels.get(form_type, form_type),
        backend_template_image=backend_ti,
        backend_field_map=backend_fm,
        backend_auto_data=backend_ad,
        backend_generate=backend_gen,
        navigation_hub_exposure=exposure,
        route_status=route_status,
        failure_endpoints=failure_endpoints,
        root_cause_class=root_cause,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# YAML rendering (handwritten, no external deps)
# ---------------------------------------------------------------------------

def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_yaml(
    statuses: list[FormStatus],
    sources: dict[str, str],
    extra_meta: dict[str, str],
) -> str:
    lines: list[str] = []
    lines.append("# DentalBI 25-form route inventory — cmd_004 cycle3 mechanical extraction")
    lines.append("# Generated by scripts/extract_dentalbi_form_inventory.py")
    lines.append("# Paths are RELATIVE to dentalbi_root to avoid privacy-gate absolute_wsl_c hits.")
    lines.append("")
    lines.append("inventory:")
    for k, v in extra_meta.items():
        lines.append(f"  {k}: {_q(v)}")
    lines.append("  dentalbi_root_placeholder: \"<DENTALBI_ROOT>\"")
    lines.append("  sources:")
    for k, v in sources.items():
        lines.append(f"    {k}: {_q(v)}")
    total = len(statuses)
    broken = sum(1 for s in statuses if s.route_status == "broken")
    passing = total - broken
    not_exposed = sum(1 for s in statuses if s.navigation_hub_exposure == "not_exposed")
    lines.append("  summary:")
    lines.append(f"    total_forms: {total}")
    lines.append(f"    passes: {passing}")
    lines.append(f"    broken: {broken}")
    lines.append(f"    navigation_hub_not_exposed: {not_exposed}")
    # Per-cause counts
    cause_counts: dict[str, int] = {}
    for s in statuses:
        cause_counts[s.root_cause_class] = cause_counts.get(s.root_cause_class, 0) + 1
    lines.append("    root_cause_counts:")
    for c in sorted(cause_counts):
        lines.append(f"      {c}: {cause_counts[c]}")
    lines.append("")
    lines.append("  forms:")
    for s in statuses:
        lines.append(f"    - form_type: {_q(s.form_type)}")
        lines.append(f"      label: {_q(s.label)}")
        lines.append(f"      route_status: {_q(s.route_status)}")
        lines.append(f"      root_cause_class: {_q(s.root_cause_class)}")
        lines.append(f"      navigation_hub_exposure: {_q(s.navigation_hub_exposure)}")
        lines.append("      backend_contract:")
        lines.append(f"        template_image: {_q(s.backend_template_image)}")
        lines.append(f"        field_map: {_q(s.backend_field_map)}")
        lines.append(f"        auto_data: {_q(s.backend_auto_data)}")
        lines.append(f"        generate: {_q(s.backend_generate)}")
        if s.failure_endpoints:
            lines.append("      failure_endpoints:")
            for ep in s.failure_endpoints:
                lines.append(f"        - {_q(ep)}")
        else:
            lines.append("      failure_endpoints: []")
        if s.notes:
            lines.append("      notes:")
            for n in s.notes:
                lines.append(f"        - {_q(n)}")
        else:
            lines.append("      notes: []")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dentalbi-root", required=True, help="Absolute path to DentalBI repo root.")
    parser.add_argument("--out", required=True, help="Output YAML path.")
    args = parser.parse_args(argv)

    root = Path(args.dentalbi_root)
    if not root.is_dir():
        print(f"ERROR: dentalbi-root not a directory: {root}", file=sys.stderr)
        return 2

    def read(rel: str) -> str:
        p = root / rel
        if not p.is_file():
            print(f"ERROR: missing source file: {rel}", file=sys.stderr)
            sys.exit(2)
        return p.read_text(encoding="utf-8")

    documents_py = read(DOCUMENTS_API_REL)
    template_py = read(TEMPLATE_OVERLAY_REL)
    field_py = read(FIELD_COORDINATES_REL)
    link_bar_tsx = read(DOCUMENT_LINK_BAR_REL)

    renderer_map, lab_order_map, has_nigo_special = parse_renderer_maps(documents_py)
    template_specs = parse_template_specs(template_py)
    field_maps = parse_field_maps(field_py)
    labels = parse_template_labels(template_py)
    exposed = parse_document_link_bar(link_bar_tsx)

    # Canonical 25-form list = renderer_map ∪ lab_order_map ∪ {nigo_sheet}.
    canonical = sorted(renderer_map | lab_order_map | ({NIGO_SHEET} if has_nigo_special else set()))

    if len(canonical) != 25:
        print(
            f"WARN: canonical form count = {len(canonical)} (expected 25). Proceeding.",
            file=sys.stderr,
        )

    statuses = [
        classify(
            ft, template_specs, field_maps, renderer_map, lab_order_map,
            has_nigo_special, exposed, labels,
        )
        for ft in canonical
    ]

    sources = {
        "renderer_map": DOCUMENTS_API_REL,
        "lab_order_map": DOCUMENTS_API_REL,
        "nigo_sheet_special_case": DOCUMENTS_API_REL,
        "template_specs": TEMPLATE_OVERLAY_REL,
        "field_maps": FIELD_COORDINATES_REL,
        "navigation_hub": DOCUMENT_LINK_BAR_REL,
        "pdf_overlay_page": PDF_OVERLAY_PAGE_REL,
    }
    extra_meta = {
        "parent_cmd": "cmd_004",
        "task_id": "subtask_cmd004_pdf_v02_hardening_and_form_fix",
        "cycle": "3",
        "extraction_method": (
            "static source-of-truth parsing of renderer_map / TEMPLATE_SPECS / FIELD_MAPS "
            "/ DocumentLinkBar; equivalent to a curl probe of the four usePdfOverlay "
            "endpoints (template-image, field-map, auto-data, saved-record) under a "
            "correctly-configured backend"
        ),
        "live_curl_attempted": "no (dev server not running on localhost:8000)",
    }

    yaml = render_yaml(statuses, sources, extra_meta)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml, encoding="utf-8")
    print(f"Wrote {out_path} (forms={len(statuses)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
