from config import config
import requests

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


# create_repository("balls", "Created via GitHub API")
delete_repository("balls")
