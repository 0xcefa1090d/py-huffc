import contextlib
import os

import requests
import semantic_version as semver


class VersionManager:
    def __init__(self):
        self.session = None

    def fetch_remote_versions(self):
        r = self.session.get("https://api.github.com/repos/huff-language/huff-rs/releases")

        versions = []
        for release in r.json():
            with contextlib.suppress(ValueError):
                versions.append(semver.Version(release["name"].removeprefix("v")))

        return versions

    def __enter__(self):
        session = requests.Session()
        session.headers.update({"Accept": "application/json", "X-GitHub-Api-Version": "2022-11-28"})

        if token := os.getenv("GITHUB_TOKEN"):
            session.headers.update({"Authorization": f"token {token}"})

        self.session = session
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
        self.session = None
