"""End-to-end acceptance tests for from-scratch init.

Covers tasks 8.1 (sync-skills installed), 8.2 (sync-skills content),
8.3 (new-project content after init).
"""
import io
import json
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
REAL_CATALOG_DIR = REPO_ROOT / "catalog"


def run_init(catalog_dir, dest_dir, state_file, stdin_text="s\n"):
    from src.commands.init import run_init as _run_init
    out = io.StringIO()
    stdin = io.StringIO(stdin_text)
    return _run_init(
        catalog_dir=catalog_dir,
        dest_dir=dest_dir,
        state_path=state_file,
        force=False,
        out=out,
        stdin=stdin,
    )


def parse_frontmatter(content: str):
    from src.catalog.yaml_frontmatter import parse
    return parse(content)


# ─── Task 8.1 ────────────────────────────────────────────────────────────────

def test_init_installs_sync_skills_command(tmp_path):
    dest_dir = tmp_path / ".claude"
    state_file = tmp_path / ".state.json"

    exit_code = run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    assert exit_code == 0
    installed = dest_dir / "commands" / "from-scratch" / "sync-skills.md"
    assert installed.exists(), f"sync-skills.md was not installed at {installed}"


def test_init_sync_skills_has_valid_frontmatter(tmp_path):
    dest_dir = tmp_path / ".claude"
    state_file = tmp_path / ".state.json"

    run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    installed = dest_dir / "commands" / "from-scratch" / "sync-skills.md"
    content = installed.read_text()
    fm, _ = parse_frontmatter(content)
    assert fm.get("description", "").strip(), "Installed sync-skills.md must have a non-empty description"


# ─── Task 8.2 ────────────────────────────────────────────────────────────────

def test_init_sync_skills_content_has_role_declaration(tmp_path):
    dest_dir = tmp_path / ".claude"
    state_file = tmp_path / ".state.json"

    run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    installed = dest_dir / "commands" / "from-scratch" / "sync-skills.md"
    _, body = parse_frontmatter(installed.read_text())
    first_lines = "\n".join(body.splitlines()[:5]).lower()
    assert "sos" in first_lines or "tu objetivo" in first_lines or "desarrollador" in first_lines, \
        "Role declaration must appear at the top of sync-skills.md"


def test_init_sync_skills_content_has_global_restrictions(tmp_path):
    dest_dir = tmp_path / ".claude"
    state_file = tmp_path / ".state.json"

    run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    installed = dest_dir / "commands" / "from-scratch" / "sync-skills.md"
    _, body = parse_frontmatter(installed.read_text())
    assert "restricciones globales" in body.lower(), \
        "sync-skills.md must contain a global restrictions block"


def test_init_sync_skills_content_has_pinned_ref(tmp_path):
    import re
    dest_dir = tmp_path / ".claude"
    state_file = tmp_path / ".state.json"

    run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    installed = dest_dir / "commands" / "from-scratch" / "sync-skills.md"
    _, body = parse_frontmatter(installed.read_text())
    has_tag = bool(re.search(r"v\d+\.\d+", body))
    has_sha = bool(re.search(r"\b[0-9a-f]{7,40}\b", body))
    assert has_tag or has_sha, "Pinned ref must be visible in installed sync-skills.md"


def test_init_sync_skills_content_has_closing_summary(tmp_path):
    dest_dir = tmp_path / ".claire"
    state_file = tmp_path / ".state.json"

    run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    installed = dest_dir / "commands" / "from-scratch" / "sync-skills.md"
    _, body = parse_frontmatter(installed.read_text())
    assert "cierre" in body.lower() or "resumen" in body.lower() or "delta" in body.lower(), \
        "sync-skills.md must contain a closing summary block"


# ─── Task 8.3 ────────────────────────────────────────────────────────────────

def test_init_new_project_has_extended_flow(tmp_path):
    dest_dir = tmp_path / ".claude"
    state_file = tmp_path / ".state.json"

    run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    installed = dest_dir / "commands" / "new-project.md"
    assert installed.exists()
    _, body = parse_frontmatter(installed.read_text())
    body_lower = body.lower()

    # 4 extended steps in order: template, skills sync, settings.json, CLAUDE.md
    template_idx = body_lower.find("template")
    skills_idx = body_lower.find("skills")
    settings_idx = body_lower.find("settings.json")
    claude_idx = body_lower.rfind("claude.md")

    assert template_idx >= 0 and skills_idx >= 0 and settings_idx >= 0 and claude_idx >= 0
    assert template_idx < skills_idx < settings_idx < claude_idx, \
        "Extended new-project flow must declare 4 steps in order: template → skills sync → settings.json → CLAUDE.md"


def test_init_new_project_has_pinned_ref(tmp_path):
    import re
    dest_dir = tmp_path / ".claude"
    state_file = tmp_path / ".state.json"

    run_init(REAL_CATALOG_DIR, dest_dir, state_file)

    installed = dest_dir / "commands" / "new-project.md"
    _, body = parse_frontmatter(installed.read_text())
    has_tag = bool(re.search(r"v\d+\.\d+", body))
    has_sha = bool(re.search(r"\b[0-9a-f]{7,40}\b", body))
    assert has_tag or has_sha, "Pinned ref must be visible in installed new-project.md"
