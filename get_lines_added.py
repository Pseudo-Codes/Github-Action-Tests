import os
import git
from git import Repo
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

def is_python_src_file(file_path: Path) -> bool:
    return (
        file_path.name.endswith(".py") and not
        (file_path.name.startswith("test_")
        or file_path.name.endswith("_test.py"))
    )

def get_src_lines_changed(repo_path: str):
    """
    Calculate lines changed (additions + deletions) only in `src/` while excluding `tests/`.
    Returns: Total lines changed in src/ (int)
    """
    repo = Repo(repo_path)
    # Get the base branch (e.g., main) and PR head commit
    base_branch = "main"  # Change this to your base branch
    pr_head = repo.head.commit
    
    # Find the common ancestor commit
    base_commit = repo.merge_base(f"origin/{base_branch}", pr_head)[0]
    
    # Get diff between base and PR head, only for src/ and exclude tests/
    diff = repo.git.diff(
        base_commit, pr_head,
        "--numstat",
    )
    
    # Count added/deleted lines (excluding diff metadata)
    lines_changed = 0
    for line in diff.split('\n'):
        lines_added, lines_deleted, file_path = line.split("\t")
        file_path = Path(file_path)

        if is_python_src_file(file_path):
            total_lines = int(lines_added) + int(lines_deleted)
            lines_changed += total_lines

    return lines_changed

def write_lines_changed_to_file(lines_changed: int, output_file: str) -> None:
    with open(output_file, "a") as f:
        f.write(f'lines_changed={str(lines_changed).lower()}\n')


if __name__ == "__main__":
    repo_path = "."
    lines_changed = get_src_lines_changed(repo_path)
    write_lines_changed_to_file(lines_changed, os.environ.get("GITHUB_OUTPUT"))
