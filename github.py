from config import config
import requests
import subprocess
import tempfile
import os

HEADERS = {
    "Authorization": f'token {config["github_token"]}',
    "Accept": "application/vnd.github.v3+json",
}


def create_repository(name: str, description: str) -> int:
    response = requests.post(
        "https://api.github.com/user/repos",
        headers=HEADERS,
        json={"name": name, "description": description, "private": True},
    )

    return response.status_code


def delete_repository(name: str):
    response = requests.delete(
        f"https://api.github.com/repos/{config['github_username']}/{name}",
        headers=HEADERS,
    )

    if response.status_code == 204:
        return
    else:
        raise Exception(
            f"Failed to delete repository. Status code: {response.status_code}. Error: {response.json()}"
        )


def clone_repository(repo_name: str) -> str:
    temp_dir = tempfile.mkdtemp()

    # Construct the HTTPS URL with token auth
    https_url = f"https://{config['github_token']}@github.com/{repo_name}.git"

    result = subprocess.run(
        ["git", "clone", https_url], cwd=temp_dir, capture_output=True, text=True
    )

    if result.returncode != 0:
        raise Exception(f"Failed to clone repository: {result.stderr}")

    # Repo will be a subdir of the temp dir
    return os.path.join(temp_dir, repo_name.split("/")[-1])


def _git_config(repo_path: str):
    """Set git user.name and user.email for this specific repository."""
    subprocess.run(
        ["git", "config", "--local", "user.name", config["git_name"]],
        cwd=repo_path,
        check=True,
    )

    subprocess.run(
        ["git", "config", "--local", "user.email", config["git_email"]],
        cwd=repo_path,
        check=True,
    )


def git_add(repo_path: str, files: list[str]):
    """Add files to git staging area."""
    if not files:
        return

    result = subprocess.run(
        ["git", "add"] + files, cwd=repo_path, capture_output=True, text=True
    )

    if result.returncode != 0:
        raise Exception(f"Failed to add files: {result.stderr}")


def git_commit_and_push(repo_path: str, commit_message: str):
    """Commit changes and push to remote."""
    _git_config(repo_path)

    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise Exception(f"Failed to commit changes: {result.stderr}")

    result = subprocess.run(
        ["git", "push"], cwd=repo_path, capture_output=True, text=True
    )

    if result.returncode != 0:
        raise Exception(f"Failed to push changes: {result.stderr}")


if __name__ == "__main__":
    # create_repository("balls", "Created via GitHub API")
    # delete_repository("balls")
    repo_path = clone_repository("ivhacks/jousbot2")
    print(f"Cloned repository to: {repo_path}")
