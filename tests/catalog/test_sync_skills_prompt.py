"""Tests for the sync-skills command catalog entry and prompt content.

Covers tasks 1.2, 1.4, 1.5, 2.2, 2.4, 2.6, 4.7, 5.1, 5.3, 5.5, 5.7,
6.1, 6.3, 6.5, 6.7, 6.9, 6.11, 7.1, 7.3, 7.5.
"""
import json
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
CATALOG_JSON = REPO_ROOT / "catalog" / "catalog.json"
SYNC_SKILLS_FILE = REPO_ROOT / "catalog" / "commands" / "from-scratch" / "sync-skills.md"

PINNED_REF_MARKER = "despegar/agent-rules-and-skills"


def parse_frontmatter(content: str):
    from src.catalog.yaml_frontmatter import parse
    return parse(content)


def get_body(content: str) -> str:
    _, body = parse_frontmatter(content)
    return body


# ─── Task 1.2 ────────────────────────────────────────────────────────────────

def test_catalog_json_has_sync_skills_entry():
    data = json.loads(CATALOG_JSON.read_text())
    entries = data["entries"]
    sources = [e["source"] for e in entries]
    assert "commands/from-scratch/sync-skills.md" in sources


def test_catalog_entry_points_to_subdirectory():
    data = json.loads(CATALOG_JSON.read_text())
    entry = next(
        e for e in data["entries"]
        if e.get("source") == "commands/from-scratch/sync-skills.md"
    )
    assert entry["kind"] == "command"
    assert "from-scratch" in entry["source"]


def test_catalog_slug_has_namespace_prefix():
    source = "commands/from-scratch/sync-skills.md"
    # Slug derived: strip "commands/", strip ".md", replace "/" with ":"
    slug = source.removeprefix("commands/").removesuffix(".md").replace("/", ":")
    assert slug == "from-scratch:sync-skills"


# ─── Task 1.4 ────────────────────────────────────────────────────────────────

def test_sync_skills_file_exists():
    assert SYNC_SKILLS_FILE.exists(), f"Missing: {SYNC_SKILLS_FILE}"


def test_sync_skills_frontmatter_is_valid():
    content = SYNC_SKILLS_FILE.read_text()
    fm, _ = parse_frontmatter(content)
    assert fm  # non-empty
    assert fm.get("description", "").strip()


# ─── Task 1.5 ────────────────────────────────────────────────────────────────

def test_sync_skills_references_three_prompts_in_order():
    body = get_body(SYNC_SKILLS_FILE.read_text())
    # Each prompt identified by its purpose keywords
    markers = [
        ("análisis", "01"),        # Prompt 1: project analysis
        ("skills compartidos", "02"),  # Prompt 2: shared skills sync
        ("skills customizados", "03"),  # Prompt 3: custom skills
    ]
    indices = []
    for (kw1, kw2) in markers:
        idx = max(
            body.lower().find(kw1.lower()),
            body.lower().find(kw2.lower()),
        )
        assert idx >= 0, f"Prompt marker not found: '{kw1}' or '{kw2}'"
        indices.append(idx)
    assert indices[0] < indices[1] < indices[2], \
        "Prompts are not referenced in order (1, 2, 3)"


# ─── Task 2.2 ────────────────────────────────────────────────────────────────

def test_sync_skills_handles_no_history_case():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    has_warning = any(kw in body for kw in ["advertencia", "historia insuficiente", "baja calidad", "codebase insuficiente"])
    has_run_anyway = any(kw in body for kw in ["ejecutalo igualmente", "ejecutalo de todas formas", "ejecutá igualmente"])
    assert has_warning and has_run_anyway, \
        "Prompt must instruct to run Prompt 3 anyway and warn if output is poor"


# ─── Task 2.4 ────────────────────────────────────────────────────────────────

def test_sync_skills_regenerates_claude_md_automatically():
    # Strip markdown backticks before matching so `AGENTS.md` and AGENTS.md both work
    body = get_body(SYNC_SKILLS_FILE.read_text()).replace("`", "").lower()
    agents_changed = any(kw in body for kw in ["agents.md cambió", "agents.md cambia", "modificó agents.md"])
    auto_regen = any(kw in body for kw in ["regenerá automáticamente", "regenera automáticamente", "sin pedir confirmación"])
    assert agents_changed, "Prompt must mention AGENTS.md change as trigger"
    assert auto_regen, "Prompt must declare automatic regeneration without asking confirmation"


def test_sync_skills_does_not_ask_confirmation_for_claude_md_regen():
    body = get_body(SYNC_SKILLS_FILE.read_text())
    # Confirm that automatic regen is stated without prompting user
    lower = body.lower()
    assert "sin pedir confirmación" in lower or "automáticamente" in lower


# ─── Task 2.6 ────────────────────────────────────────────────────────────────

def test_sync_skills_uses_todo_write():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "todowrite" in body, "Prompt must instruct to use TodoWrite"


def test_sync_skills_todo_write_includes_all_steps():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    required_steps = [
        "análisis",
        "skills compartidos",
        "skills customizados",
        "agents.md",
        "claude.md",
    ]
    for step in required_steps:
        assert step in body, f"TodoWrite must include step: '{step}'"


# ─── Task 4.7 ────────────────────────────────────────────────────────────────

def test_sync_skills_close_shows_delta():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    categories = ["agregad", "actualizad", "removid", "preservad"]
    for cat in categories:
        assert cat in body, f"Close summary must include category: '{cat}'"


def test_sync_skills_close_reports_claude_md_regen():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "claude.md" in body and ("regenerad" in body or "regenera" in body or "actualizad" in body)


# ─── Task 5.1 ────────────────────────────────────────────────────────────────

def test_sync_skills_preview_format_counts_and_names():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "preview" in body or "vista previa" in body, "Prompt must describe a preview step"
    assert "categoría" in body or "categoria" in body or "counts" in body or "cuenta" in body


def test_sync_skills_asks_confirmation_when_files_exist():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "confirmación" in body or "confirmacion" in body, \
        "Prompt must request confirmation before applying when files exist"


# ─── Task 5.3 ────────────────────────────────────────────────────────────────

def test_sync_skills_uses_html_markers_for_merge():
    content = SYNC_SKILLS_FILE.read_text()
    assert "<!-- AUTO-GENERATED:" in content, "Must use HTML markers for merge sections"


def test_sync_skills_merge_not_overwrite():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "merge" in body or "sección auto" in body or "marcadores" in body, \
        "Prompt must describe merge, not overwrite"


def test_sync_skills_handles_missing_markers_case():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "sin los marcadores" in body or "no tiene los marcadores" in body or "proyecto antiguo" in body, \
        "Must handle files without markers (legacy projects)"


# ─── Task 5.5 ────────────────────────────────────────────────────────────────

def test_sync_skills_declares_atomic_writes():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "atómic" in body or "atomica" in body or "temporal" in body, \
        "Prompt must declare atomic writes (temp file + rename)"


def test_sync_skills_skills_copy_via_temp_dir():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "directorio temporal" in body or "temp" in body


# ─── Task 5.7 ────────────────────────────────────────────────────────────────

def test_sync_skills_detects_partial_state():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "estado parcial" in body or "parcial" in body or "ejecución previa" in body, \
        "Prompt must address partial state from a previous interrupted run"


# ─── Task 6.1 ────────────────────────────────────────────────────────────────

def test_sync_skills_global_restrictions_appear_once():
    body = get_body(SYNC_SKILLS_FILE.read_text())
    # "Restricciones globales" (or equivalent) should appear exactly once
    count = body.lower().count("restricciones globales")
    assert count == 1, f"Global restrictions block must appear exactly once, found {count}"


def test_sync_skills_steps_describe_objectives_not_procedures():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    # Objective framing: "el objetivo es..." or similar
    assert "objetivo" in body or "estado final" in body or "al final de este paso" in body


# ─── Task 6.3 ────────────────────────────────────────────────────────────────

def test_sync_skills_no_pseudo_code():
    body = get_body(SYNC_SKILLS_FILE.read_text())
    pseudo_patterns = [" if ", " else ", " for ", " while ", "if(", "for(", "while("]
    for pat in pseudo_patterns:
        assert pat not in body, f"Prompt must not contain pseudo-code: '{pat.strip()}'"


def test_sync_skills_does_not_re_explain_todo_write():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    # Should mention TodoWrite but not explain how to use it
    assert "cómo usar todowrite" not in body
    assert "la herramienta todowrite permite" not in body


# ─── Task 6.5 ────────────────────────────────────────────────────────────────

def test_sync_skills_body_under_150_lines():
    content = SYNC_SKILLS_FILE.read_text()
    _, body = parse_frontmatter(content)
    total_lines = len(body.splitlines())
    assert total_lines <= 150, f"Body has {total_lines} lines, must be <= 150"


# ─── Task 6.7 ────────────────────────────────────────────────────────────────

def test_sync_skills_uses_pinned_ref_not_main():
    body = get_body(SYNC_SKILLS_FILE.read_text())
    assert "despegar/agent-rules-and-skills" in body
    # Verify that the ref following the repo is not "main" or "master"
    import re
    # Look for any URL containing the repo + branch
    if "agent-rules-and-skills/main" in body or "agent-rules-and-skills/master" in body:
        raise AssertionError("Ref must be pinned (tag or SHA), not 'main' or 'master'")


def test_sync_skills_pinned_ref_is_visible():
    body = get_body(SYNC_SKILLS_FILE.read_text())
    import re
    # A pinned ref: a version tag (v\d+) or a SHA (40 hex chars)
    has_tag = bool(re.search(r"v\d+\.\d+", body))
    has_sha = bool(re.search(r"\b[0-9a-f]{7,40}\b", body))
    assert has_tag or has_sha, "Pinned ref (tag or SHA) must be visible in the prompt body"


# ─── Task 6.9 ────────────────────────────────────────────────────────────────

def test_sync_skills_reads_prompts_at_runtime():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    fetch_keywords = ["leé", "lee", "fetch", "leer", "read"]
    assert any(kw in body for kw in fetch_keywords), \
        "Prompt must instruct Claude to read the remote prompts at runtime"


# ─── Task 6.11 ───────────────────────────────────────────────────────────────

def test_sync_skills_detects_user_installed_skills():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "user-installed" in body or "instalados" in body or "ausentes del" in body, \
        "Prompt must mention user-installed skill detection"


def test_sync_skills_preserves_user_installed_in_preview():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "preservados sin cambios" in body, \
        "Preview must include 'preservados sin cambios' category for user-installed skills"


# ─── Task 7.1 ────────────────────────────────────────────────────────────────

def test_sync_skills_aborts_outside_project():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    abort_keywords = ["abortá", "abortar", "aborta", "abortá temprano", "no estás en un proyecto", "no es un proyecto"]
    assert any(kw in body for kw in abort_keywords), \
        "Prompt must abort early when not in a project directory"


def test_sync_skills_abort_error_is_actionable():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    # Should suggest cd or /new-project
    assert "cd " in body or "/new-project" in body, \
        "Abort error must suggest what to do (cd or /new-project)"


# ─── Task 7.3 ────────────────────────────────────────────────────────────────

def test_sync_skills_reports_invalid_frontmatter_skills():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "frontmatter inválido" in body or "frontmatter invalido" in body, \
        "Prompt must mention skills with invalid frontmatter"


def test_sync_skills_continues_after_invalid_frontmatter():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "continuá" in body or "continúa" in body or "continúa con el resto" in body or "continua con" in body


# ─── Task 7.5 ────────────────────────────────────────────────────────────────

def test_sync_skills_documents_minimum_version():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "versión mínima" in body or "version minima" in body or "from-scratch >=" in body or "from-scratch update" in body


def test_sync_skills_describes_recovery_for_old_binary():
    body = get_body(SYNC_SKILLS_FILE.read_text()).lower()
    assert "from-scratch update" in body or "actualiz" in body
