import contextlib
import itertools
import os
import pathlib
import platform
import tarfile
import tempfile

import requests
import semantic_version as semver


class VersionManager:
    HUFFC_DIR = pathlib.Path.home() / ".huffc"

    def __init__(self):
        self.session = None
        self.HUFFC_DIR.mkdir(exist_ok=True)

    def fetch_remote_versions(self):
        versions = []
        for page in itertools.count(1):
            r = self.session.get(
                "https://api.github.com/repos/huff-language/huff-rs/releases",
                params={"per_page": 100, "page": page},
            )

            for release in (releases := r.json()):
                with contextlib.suppress(ValueError):
                    versions.append(semver.Version(release["name"].removeprefix("v")))

            if len(releases) < 100:
                break

        return versions

    def fetch_local_versions(self):
        versions = []
        for binary in self.HUFFC_DIR.iterdir():
            versions.append(semver.Version(binary.removeprefix("huffc-")))

        return versions

    def install(self, version, overwrite=False):
        assert semver.Version(version) in self.fetch_remote_versions()

        if not overwrite:
            assert semver.Version(version) not in self.fetch_local_versions()

        r = self.session.get(
            f"https://api.github.com/repos/huff-language/huff-rs/releases/tags/{version}"
        )

        system = platform.system().lower()
        match platform.machine().lower():
            case "amd64" | "x86_64" | "i386" | "i586" | "i686":
                machine = "amd64"
            case "aarch64_be" | "aarch64" | "armv8b" | "armv8l":
                machine = "arm64"
            case _:
                raise Exception("Platform is not supported.")

        for asset in r.json()["assets"]:
            if not all((val in asset["name"].lower() for val in (system, machine))):
                continue

            with tempfile.NamedTemporaryFile() as tmp:
                with self.session.get(asset["browser_download_url"], stream=True) as resp:
                    resp.raise_for_status()
                    for chunk in resp.iter_content(None):
                        tmp.write(chunk)

                with tarfile.open(tmp.name, "r:gz") as tar:
                    tar.extract("huffc", self.HUFFC_DIR)

            (self.HUFFC_DIR / "huffc").rename(self.HUFFC_DIR / f"huffc-{version}")
            return

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
