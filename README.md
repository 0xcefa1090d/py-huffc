# py-huffc

Python wrapper and version manager for the Huff compiler

## Dependencies

To build binaries from source when a pre-built binary isn't available, the build tool `cargo` must be installed. Refer to the `cargo`
[documentation](https://doc.rust-lang.org/cargo/) for instruction on installing it.

To prevent rate limits when querying the GitHub API, it is recommended to include a GitHub personal access token as an environment variable.
Refer to the GitHub API [documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) for information on generating a personal access token.

```bash
export GITHUB_TOKEN="github_pat_XXXX"
```

## Installation

```bash
$ pip install py-huffc
```

## Usage

```python
>>> import huffc
>>> with huffc.VersionManager() as hvm:
...     hvm.fetch_remote_versions()  # list versions available to install
...
[Version('0.3.1')]
>>> with huffc.VersionManager() as hvm:
...     hvm.install("0.3.1", silent=True)  # install a version
...
>>> huffc.VersionManager.fetch_local_versions()  # list locally installed versions
[Version('0.3.1')]
>>> huffc.VersionManager.get_executable("0.3.1")  # get the path for an installed binary
PosixPath('/home/user/.huffc/huffc-0.3.1')
>>> huffc.compile(["../huff-rs/huff-examples/erc20/contracts/ERC20.huff"], version="0.3.1")  # compile a list of contracts
{"../huff-rs/huff-examples/erc20/contracts/ERC20.huff": {...}}
>>> huffc.VersionManager.uninstall("0.3.1")  # uninstall a version
```
