"""Tests for the new-project command prompt content.

Covers tasks 3.1, 3.3, 3.5, 3.7, 3.9, 4.1, 4.3, 4.5, 5.3, 5.5, 5.9,
5.11, 6.1, 6.3, 6.5, 6.7, 6.9.
"""
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
NEW_PROJECT_FILE = REPO_ROOT / "catalog" / "commands" / "new-project.md"


def parse_frontmatter(content: str):
    from src.catalog.yaml_frontmatter import parse
    return parse(content)


def get_body(content: str) -> str:
    _, body = parse_frontmatter(content)
    return body


# ─── Task 3.1 ────────────────────────────────────────────────────────────────

def test_new_project_uses_todo_write():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "todowrite" in body, "Prompt must instruct to open a TodoWrite"


def test_new_project_todo_includes_four_steps():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    required = [
        "template",           # clone del template
        "skills",             # skills sync
        "settings.json",      # .claude/settings.json
        "claude.md",          # generación de CLAUDE.md
    ]
    for step in required:
        assert step in body, f"TodoWrite must include step: '{step}'"


# ─── Task 3.3 ────────────────────────────────────────────────────────────────

def test_new_project_includes_skills_sync_step():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "skills" in body and ("agent-rules-and-skills" in body or "prompt 1" in body or "01-" in body)


def test_new_project_skills_sync_includes_prompt_3():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    # The prompt MUST execute Prompt 3 so the custom-skills pipeline is wired up from clone.
    # Output may be minimal for fresh projects, but the plumbing must run.
    assert "prompt 3" in body, "new-project must execute Prompt 3 (custom skills) — see /from-scratch:sync-skills for the full flow"
    assert "prompts/03-custom-skills.md" in body, "Pinned URL for Prompt 3 must be visible"


def test_new_project_warns_about_thin_custom_skills():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    # Since the project just got cloned, custom skills may be thin — the prompt must say so
    # and point users to /from-scratch:sync-skills for a richer rerun later.
    assert "básic" in body or "minim" in body or "baja calidad" in body or "poca historia" in body, \
        "Must warn that Prompt 3 output may be thin on a freshly cloned project"
    assert "from-scratch:sync-skills" in body, \
        "Must suggest re-running /from-scratch:sync-skills once there's more code"


def test_new_project_skills_sync_after_template_setup():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    template_idx = body.find("template")
    skills_idx = body.find("skills")
    assert template_idx >= 0 and skills_idx >= 0
    assert template_idx < skills_idx, "Skills sync step must come after template setup"


# ─── Task 3.5 ────────────────────────────────────────────────────────────────

def test_new_project_includes_settings_json_step():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert ".claude/settings.json" in body or "settings.json" in body


def test_new_project_settings_json_merge_logic():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "merge" in body or "fusioná" in body, "Must describe merge for settings.json"
    assert "permisos" in body or "permissions" in body


def test_new_project_settings_json_conflict_confirmation():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "conflicto" in body or "colisión" in body or "colision" in body, \
        "Must mention conflict detection for settings.json"


# ─── Task 3.7 ────────────────────────────────────────────────────────────────

def test_new_project_includes_claude_md_step():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "claude.md" in body


def test_new_project_claude_md_references_agents_md():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "agents.md" in body, "CLAUDE.md generation must reference AGENTS.md"


def test_new_project_claude_md_after_skills_sync():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    skills_idx = body.find("skills")
    claude_idx = body.rfind("claude.md")
    assert skills_idx >= 0 and claude_idx >= 0
    assert skills_idx < claude_idx, "CLAUDE.md step must come after skills sync (D2)"


def test_new_project_claude_md_uses_html_markers():
    content = NEW_PROJECT_FILE.read_text()
    assert "<!-- AUTO-GENERATED: claude-init-start -->" in content or "AUTO-GENERATED:" in content, \
        "CLAUDE.md section must use HTML markers for future merge support"


def test_new_project_claude_md_uses_at_import_for_agents_md():
    body = get_body(NEW_PROJECT_FILE.read_text())
    # Generated CLAUDE.md must reference AGENTS.md as `@AGENTS.md` (Claude Code recursive import),
    # NOT as a markdown link `[AGENTS.md](AGENTS.md)`. Markdown links do not expand the file
    # contents into the session context; only `@`-imports do.
    assert "@AGENTS.md" in body, \
        "CLAUDE.md generation step must instruct using @AGENTS.md import (not a markdown link)"
    assert "import" in body.lower(), \
        "Step must explain that @AGENTS.md is an import (so future maintainers don't 'fix' it back to a link)"


# ─── Task 3.9 ────────────────────────────────────────────────────────────────

def test_new_project_handles_skills_sync_failure():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    continue_keywords = ["continuá", "continua", "continuar", "seguí", "sigue"]
    assert any(kw in body for kw in continue_keywords), \
        "Prompt must instruct to continue if skills sync fails"


def test_new_project_skills_failure_does_not_abort():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "reportar el error" in body or "reportá el error" in body or \
        ("error" in body and "continúa" in body) or ("error" in body and "seguí" in body), \
        "Skills sync failure must be reported, not cause abort"


# ─── Task 4.1 ────────────────────────────────────────────────────────────────

def test_new_project_announces_long_operations():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    operations = ["clone", "cloná", "clonando", "analizando", "copiando", "generando"]
    assert any(op in body for op in operations), \
        "Prompt must announce long operations"


def test_new_project_feedback_for_template_clone():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "template" in body and ("cloná" in body or "clone" in body or "clonando" in body)


def test_new_project_feedback_for_skills_copy():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "skills" in body and ("instalad" in body or "copia" in body or "copiando" in body or "anunciá" in body or "reportá" in body)


# ─── Task 4.3 ────────────────────────────────────────────────────────────────

def test_new_project_actionable_error_format():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    # Errors must have 3 parts: what failed, why, what to do
    assert "qué falló" in body or "por qué" in body or "qué hacer" in body or \
        ("falló" in body and "porque" in body) or "error" in body, \
        "Prompt must describe actionable error format"


def test_new_project_covers_repo_inaccessible_error():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "inaccesible" in body or "no se pudo clonar" in body or "permisos" in body or "ssh" in body


# ─── Task 4.5 ────────────────────────────────────────────────────────────────

def test_new_project_shows_closing_summary():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "resumen" in body or "al terminar" in body or "al finalizar" in body or "cierre" in body


def test_new_project_summary_includes_project_path():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "ruta" in body or "path" in body or "directorio" in body


def test_new_project_summary_includes_skills_count():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "skills instalados" in body or "skills" in body


def test_new_project_summary_hints_sync_skills():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "from-scratch:sync-skills" in body or "sync-skills" in body


# ─── Task 5.3 ────────────────────────────────────────────────────────────────

def test_new_project_uses_html_markers_for_agents_md():
    content = NEW_PROJECT_FILE.read_text()
    assert "AUTO-GENERATED:" in content, \
        "Must use HTML markers for AGENTS.md and CLAUDE.md merge"


def test_new_project_handles_missing_markers_in_existing_files():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "sin los marcadores" in body or "no tiene los marcadores" in body or \
        "proyecto antiguo" in body or "sin marcadores" in body, \
        "Must handle files without markers (legacy projects)"


# ─── Task 5.5 ────────────────────────────────────────────────────────────────

def test_new_project_declares_atomic_writes():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "atómic" in body or "atomica" in body or "temporal" in body, \
        "Prompt must declare atomic writes"


# ─── Task 5.9 ────────────────────────────────────────────────────────────────

def test_new_project_fails_early_if_directory_exists():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "ya existe" in body or "directorio existente" in body or \
        "existe y no" in body or "no destruyas" in body or "destino ya existe" in body, \
        "Prompt must fail early if destination directory already exists"


# ─── Task 5.11 ───────────────────────────────────────────────────────────────

def test_new_project_educational_block_about_settings_in_closing():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "settings.json" in body and ("qué es" in body or "para qué sirve" in body or "permisos" in body)


def test_new_project_educational_block_includes_what_not_to_approve():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    assert "no pre-aprob" in body or "no pre-autorizar" in body or \
        "no aprobés" in body or "qué no" in body or "nunca pre-aprobés" in body or \
        "destructiv" in body, \
        "Educational block must specify what NOT to pre-approve"


def test_new_project_educational_block_in_claude_md():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    # Must say settings.json education goes into CLAUDE.md too
    assert ("claude.md" in body and "settings.json" in body) or \
        "sección" in body


# ─── Task 6.1 ────────────────────────────────────────────────────────────────

def test_new_project_global_restrictions_appear_once():
    body = get_body(NEW_PROJECT_FILE.read_text())
    count = body.lower().count("restricciones globales")
    assert count == 1, f"Global restrictions block must appear exactly once, found {count}"


# ─── Task 6.3 ────────────────────────────────────────────────────────────────

def test_new_project_no_pseudo_code():
    body = get_body(NEW_PROJECT_FILE.read_text())
    pseudo_patterns = [" if ", " else ", " for ", " while ", "if(", "for(", "while("]
    for pat in pseudo_patterns:
        assert pat not in body, f"Prompt must not contain pseudo-code: '{pat.strip()}'"


# ─── Task 6.5 ────────────────────────────────────────────────────────────────

def test_new_project_body_under_150_lines():
    content = NEW_PROJECT_FILE.read_text()
    _, body = parse_frontmatter(content)
    total_lines = len(body.splitlines())
    assert total_lines <= 150, f"Body has {total_lines} lines, must be <= 150"


# ─── Task 6.7 ────────────────────────────────────────────────────────────────

def test_new_project_uses_pinned_ref_not_main():
    body = get_body(NEW_PROJECT_FILE.read_text())
    if "agent-rules-and-skills/main" in body or "agent-rules-and-skills/master" in body:
        raise AssertionError("Ref must be pinned (tag or SHA), not 'main' or 'master'")


def test_new_project_pinned_ref_is_visible():
    body = get_body(NEW_PROJECT_FILE.read_text())
    import re
    has_tag = bool(re.search(r"v\d+\.\d+", body))
    has_sha = bool(re.search(r"\b[0-9a-f]{7,40}\b", body))
    assert has_tag or has_sha, "Pinned ref (tag or SHA) must be visible in the prompt body"


# ─── Task 6.9 ────────────────────────────────────────────────────────────────

def test_new_project_reads_prompts_at_runtime():
    body = get_body(NEW_PROJECT_FILE.read_text()).lower()
    fetch_keywords = ["leé", "lee", "fetch", "leer", "read"]
    assert any(kw in body for kw in fetch_keywords), \
        "Prompt must instruct Claude to read the remote prompts at runtime"
