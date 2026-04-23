from app.services.correction import suggest_correction
from app.services.validator import validate_taxonomy_string


MAPPING = {
    "delimiter": "_",
    "components": [
        {
            "name": "channel",
            "required": True,
            "allowed_values": ["meta", "google"],
            "aliases": {"facebook": "meta", "fb": "meta"},
        },
        {
            "name": "market",
            "required": True,
            "allowed_values": ["us", "uk", "de"],
            "aliases": {"usa": "us", "unitedstates": "us"},
        },
        {
            "name": "objective",
            "required": True,
            "allowed_values": ["awareness", "conversion"],
            "aliases": {"conv": "conversion"},
        },
    ],
}


def test_validation_valid():
    out = validate_taxonomy_string("meta_us_conversion", MAPPING)
    assert out.errors == []
    assert out.parsed["channel"] == "meta"


def test_validation_detects_invalid_and_missing():
    out = validate_taxonomy_string("meta_us", MAPPING)
    assert "invalid_component_count" in out.errors
    assert "missing_objective" in out.errors


def test_correction_alias_and_fuzzy():
    parsed = {"channel": "facebook", "market": "usa", "objective": "conversoin"}
    suggestion = suggest_correction(parsed, MAPPING)
    assert suggestion.suggested_components["channel"] == "meta"
    assert suggestion.suggested_components["market"] == "us"
    assert suggestion.suggested_components["objective"] == "conversion"
    assert suggestion.confidence > 0.7
