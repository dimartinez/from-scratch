def parse(content: str) -> tuple:
    """Parse YAML frontmatter from content.

    Returns (frontmatter_dict, body_string).
    Only supports flat key: value pairs. Raises ValueError for nested/lists.
    """
    if not content.startswith("---"):
        return {}, content

    lines = content.split("\n")
    # Find closing ---
    close_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close_idx = i
            break

    if close_idx is None:
        raise ValueError("Malformed frontmatter: missing closing ---")

    fm_lines = lines[1:close_idx]
    body = "\n".join(lines[close_idx + 1:])

    result = {}
    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Detect list items (lines starting with -)
        if stripped.startswith("- "):
            raise ValueError("list values are not supported in frontmatter")

        # Detect indented lines (nested keys)
        if line.startswith(" ") or line.startswith("\t"):
            # Could be nested key or list item
            if stripped.startswith("- "):
                raise ValueError("list values are not supported in frontmatter")
            raise ValueError("nested keys are not supported in frontmatter")

        colon_idx = stripped.find(":")
        if colon_idx == -1:
            raise ValueError(f"Invalid frontmatter line: {line!r}")

        key = stripped[:colon_idx].strip()
        raw_val = stripped[colon_idx + 1:].strip()

        # A bare key with no value followed by indented children (nested or list)
        if raw_val == "":
            # Peek at remaining lines to distinguish list vs nested key
            remaining = "\n".join(fm_lines[fm_lines.index(line) + 1:])
            if "- " in remaining:
                raise ValueError("list values are not supported in frontmatter")
            raise ValueError(f"nested keys are not supported in frontmatter (key: {key!r})")

        # Strip surrounding quotes
        if (raw_val.startswith('"') and raw_val.endswith('"')) or \
           (raw_val.startswith("'") and raw_val.endswith("'")):
            raw_val = raw_val[1:-1]

        result[key] = raw_val

    return result, body
