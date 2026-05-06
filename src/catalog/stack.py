from src.catalog.yaml_frontmatter import parse

REQUIRED_FIELDS = ("name", "description", "template_url")


def parse_stack(content: str) -> dict:
    fm, _body = parse(content)

    if not fm:
        raise ValueError("Stack file tiene frontmatter ausente o vacío")

    for field in REQUIRED_FIELDS:
        if field not in fm:
            raise ValueError(f"Stack file falta campo requerido: '{field}'")

    return {field: fm[field] for field in REQUIRED_FIELDS}
