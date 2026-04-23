from dataclasses import dataclass
from typing import Any

try:
    from rapidfuzz import process, fuzz
except Exception:  # pragma: no cover
    import difflib

    class _Process:
        @staticmethod
        def extractOne(query, choices, scorer=None):
            best = difflib.get_close_matches(query, choices, n=1, cutoff=0.0)
            if not best:
                return None
            score = int(difflib.SequenceMatcher(None, query, best[0]).ratio() * 100)
            return best[0], score, 0

    class _Fuzz:
        WRatio = None

    process = _Process()
    fuzz = _Fuzz()


@dataclass
class SuggestionOutput:
    suggested_components: dict[str, str]
    suggested_taxonomy: str
    source: str
    confidence: float
    reasoning: str
    needs_review: bool


def suggest_correction(parsed: dict[str, str], mapping: dict[str, Any], threshold_auto: float = 0.92) -> SuggestionOutput:
    components = mapping["components"]
    delimiter = mapping.get("delimiter", "_")

    suggested = {}
    max_conf = 1.0
    source = "exact_or_alias"
    reasoning_parts = []

    for comp in components:
        name = comp["name"]
        allowed = comp.get("allowed_values", [])
        aliases = comp.get("aliases", {})
        val = (parsed.get(name) or "").strip()

        if not val and comp.get("default"):
            suggested[name] = comp["default"]
            max_conf = min(max_conf, 0.75)
            source = "pattern_inference"
            reasoning_parts.append(f"{name}: default inferred")
            continue

        if val.lower() in aliases:
            suggested[name] = aliases[val.lower()]
            max_conf = min(max_conf, 0.96)
            reasoning_parts.append(f"{name}: alias normalized")
            continue

        if val in allowed or not allowed:
            suggested[name] = val
            reasoning_parts.append(f"{name}: exact match")
            continue

        match = process.extractOne(val, allowed, scorer=fuzz.WRatio) if allowed else None
        if match:
            matched, score, _ = match
            suggested[name] = matched
            max_conf = min(max_conf, score / 100)
            source = "fuzzy_match"
            reasoning_parts.append(f"{name}: fuzzy '{val}' -> '{matched}' ({score})")
        else:
            suggested[name] = val
            max_conf = min(max_conf, 0.5)
            source = "llm_fallback"
            reasoning_parts.append(f"{name}: unresolved, flagged for review")

    taxonomy = delimiter.join(suggested.get(c["name"], "") for c in components)
    needs_review = max_conf < threshold_auto

    return SuggestionOutput(
        suggested_components=suggested,
        suggested_taxonomy=taxonomy,
        source=source,
        confidence=round(max_conf, 4),
        reasoning="; ".join(reasoning_parts),
        needs_review=needs_review,
    )
