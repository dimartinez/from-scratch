import hashlib
from pathlib import Path


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def diff(catalog, installed, dest_base):
    from src.sync.diff import compute_diff
    return compute_diff(catalog, installed, dest_base)


def test_user_created_file_not_in_catalog_not_in_diff(tmp_path):
    # User created their own stack file not in catalog
    (tmp_path / "from-scratch" / "stacks").mkdir(parents=True)
    (tmp_path / "from-scratch" / "stacks" / "local-experiment.md").write_text("my local stack")

    catalog = [{"path": "commands/foo.md", "content": "catalog"}]
    installed = []

    result = diff(catalog, installed, tmp_path)
    all_paths = (
        [e["path"] for e in result["added"]]
        + [e["path"] for e in result["modified"]]
        + [e["path"] for e in result["unchanged"]]
        + [e["path"] for e in result["removed"]]
        + [e["path"] for e in result["user_modified"]]
        + [e["path"] for e in result["unowned_conflict"]]
    )
    assert "from-scratch/stacks/local-experiment.md" not in all_paths


def test_user_commands_not_in_catalog_not_in_diff(tmp_path):
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "my-custom.md").write_text("my custom command")

    catalog = []  # User file not in catalog
    installed = []  # And not tracked

    result = diff(catalog, installed, tmp_path)
    all_paths = (
        [e["path"] for e in result["added"]]
        + [e["path"] for e in result["removed"]]
    )
    assert "commands/my-custom.md" not in all_paths


def test_diff_only_iterates_over_catalog_and_state_paths(tmp_path):
    # Fill dest with lots of files not in catalog or state
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "my-agent.md").write_text("agent")
    (tmp_path / "settings.json").write_text("{}")

    catalog = [{"path": "commands/foo.md", "content": "x"}]
    installed = []

    result = diff(catalog, installed, tmp_path)
    all_paths = (
        [e["path"] for e in result["added"]]
        + [e["path"] for e in result["modified"]]
        + [e["path"] for e in result["unchanged"]]
        + [e["path"] for e in result["removed"]]
    )
    assert "agents/my-agent.md" not in all_paths
    assert "settings.json" not in all_paths
    assert len(result["added"]) == 1
