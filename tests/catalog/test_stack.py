import pytest


def parse_stack(content):
    from src.catalog.stack import parse_stack
    return parse_stack(content)


def test_valid_stack_frontmatter():
    content = "---\nname: Java Stack\ndescription: Standard Java setup\ntemplate_url: https://example.com/java\n---\n# Body\nThis is ignored."
    stack = parse_stack(content)
    assert stack["name"] == "Java Stack"
    assert stack["description"] == "Standard Java setup"
    assert stack["template_url"] == "https://example.com/java"


def test_no_frontmatter_raises():
    with pytest.raises(ValueError, match="frontmatter"):
        parse_stack("# Just markdown\nNo frontmatter here")


def test_missing_name_raises():
    content = "---\ndescription: A stack\ntemplate_url: https://example.com\n---\n"
    with pytest.raises(ValueError, match="name"):
        parse_stack(content)


def test_missing_description_raises():
    content = "---\nname: My Stack\ntemplate_url: https://example.com\n---\n"
    with pytest.raises(ValueError, match="description"):
        parse_stack(content)


def test_missing_template_url_raises():
    content = "---\nname: My Stack\ndescription: A stack\n---\n"
    with pytest.raises(ValueError, match="template_url"):
        parse_stack(content)


def test_body_markdown_is_ignored():
    content = "---\nname: My Stack\ndescription: A stack\ntemplate_url: https://example.com\n---\n# This markdown body is irrelevant"
    stack = parse_stack(content)
    # No exception; body not in result
    assert "body" not in stack
