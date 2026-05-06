import pytest


def parse(content):
    from src.catalog.yaml_frontmatter import parse
    return parse(content)


def test_flat_key_value():
    fm, body = parse("---\nname: hello\n---\nrest")
    assert fm == {"name": "hello"}
    assert body == "rest"


def test_double_quoted_value():
    fm, body = parse('---\nname: "hello world"\n---\n')
    assert fm == {"name": "hello world"}


def test_single_quoted_value():
    fm, body = parse("---\nname: 'hello world'\n---\n")
    assert fm == {"name": "hello world"}


def test_colon_inside_double_quotes():
    fm, body = parse('---\nurl: "http://example.com"\n---\n')
    assert fm == {"url": "http://example.com"}


def test_colon_inside_single_quotes():
    fm, body = parse("---\nurl: 'http://example.com'\n---\n")
    assert fm == {"url": "http://example.com"}


def test_blank_lines_ignored():
    fm, body = parse("---\nname: foo\n\ndesc: bar\n---\n")
    assert fm == {"name": "foo", "desc": "bar"}


def test_comment_lines_ignored():
    fm, body = parse("---\n# this is a comment\nname: foo\n---\n")
    assert fm == {"name": "foo"}


def test_no_frontmatter():
    fm, body = parse("just some content\nno frontmatter")
    assert fm == {}
    assert body == "just some content\nno frontmatter"


def test_unclosed_frontmatter_raises():
    with pytest.raises(ValueError, match="frontmatter"):
        parse("---\nname: foo\n")


def test_nested_keys_raise():
    with pytest.raises(ValueError, match="nested"):
        parse("---\nparent:\n  child: val\n---\n")


def test_list_raises():
    with pytest.raises(ValueError, match="list"):
        parse("---\nitems:\n  - one\n  - two\n---\n")


def test_multiple_keys():
    fm, body = parse("---\nname: My Stack\ndescription: Does stuff\ntemplate_url: https://example.com\n---\nbody here")
    assert fm["name"] == "My Stack"
    assert fm["description"] == "Does stuff"
    assert fm["template_url"] == "https://example.com"
    assert body == "body here"


def test_body_preserved():
    content = "---\nkey: val\n---\n# Heading\nSome text."
    _, body = parse(content)
    assert body == "# Heading\nSome text."
