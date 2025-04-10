from config import config
import requests
import subprocess
import tempfile
import os

HEADERS = {
    "Authorization": f'token {config["github_token"]}',
    "Accept": "application/vnd.github.v3+json",
}


def create_repository(name: str, description: str):
    response = requests.post(
        "https://api.github.com/user/repos",
        headers=HEADERS,
        json={"name": name, "description": description, "private": True},
    )

    if response.status_code == 201:
        return
    else:
        raise Exception(
            f"Failed to create repository. Status code: {response.status_code}. Error: {response.json()}"
        )


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

    # Change to temp directory first
    os.chdir(temp_dir)
    result = subprocess.run(["git", "clone", https_url], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Failed to clone repository: {result.stderr}")

    # Repo will be a subdir of the temp dir
    return os.path.join(temp_dir, repo_name.split("/")[-1])


if __name__ == "__main__":
    # create_repository("balls", "Created via GitHub API")
    # delete_repository("balls")
    repo_path = clone_repository("ivhacks/jousbot2")
    print(f"Cloned repository to: {repo_path}")
