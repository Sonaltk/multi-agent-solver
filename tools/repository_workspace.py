import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager


@contextmanager
def pr_workspace(repository: str, pr_number: int):
    """
    Create a temporary workspace containing the PR code.

    The workspace is automatically deleted when the
    context manager exits.
    """

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")

    workspace = tempfile.mkdtemp(prefix="pr-review-")

    repo_url = (
        f"https://x-access-token:{token}"
        f"@github.com/{repository}.git"
    )

    try:
        print("1. Starting clone...")
        subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                repo_url,
                workspace,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("2. Clone finished!")

        print("3. Starting PR fetch...")    
        subprocess.run(
            [
                "git",
                "-C",
                workspace,
                "fetch",
                "--quiet",
                "origin",
                f"refs/pull/{pr_number}/head:"
                f"refs/remotes/origin/pr-{pr_number}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("4. Fetch finished!")

        print("5. Starting checkout...")

        subprocess.run(
            [
                "git",
                "-C",
                workspace,
                "checkout",
                "--quiet",
                f"refs/remotes/origin/pr-{pr_number}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("6. Checkout finished!")
        yield workspace

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to create PR workspace: {e.stderr}"
        )

    finally:
        shutil.rmtree(workspace, ignore_errors=True)