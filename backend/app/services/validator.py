from dataclasses import dataclass


@dataclass
class ValidationOutput:
    parsed: dict[str, str]
    errors: list[str]


def validate_taxonomy_string(taxonomy: str, mapping: dict) -> ValidationOutput:
    delimiter = mapping.get("delimiter", "_")
    components = mapping["components"]
    parts = taxonomy.split(delimiter) if taxonomy else []

    errors: list[str] = []
    parsed: dict[str, str] = {}

    if len(parts) != len(components):
        errors.append("invalid_component_count")

    for idx, comp in enumerate(components):
        name = comp["name"]
        required = comp.get("required", True)
        allowed = comp.get("allowed_values", [])
        aliases = comp.get("aliases", {})

        value = parts[idx].strip() if idx < len(parts) else ""
        parsed[name] = value

        if required and not value:
            errors.append(f"missing_{name}")
            continue

        normalized = aliases.get(value.lower(), value) if value else value
        parsed[name] = normalized

        if normalized and allowed and normalized not in allowed:
            errors.append(f"invalid_value_{name}")

    if not taxonomy:
        errors.append("missing_taxonomy")

    return ValidationOutput(parsed=parsed, errors=sorted(set(errors)))
