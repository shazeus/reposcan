from click.testing import CliRunner

from reposcan.cli import cli
from reposcan.github_api import GitHubClient


class DummyClient:
    last_token = None

    def __init__(self, token=None):
        DummyClient.last_token = token
        self.token = token

    def get_rate_limit(self):
        return {"resources": {"core": {"remaining": 5000, "limit": 5000, "reset": 0}}}


def test_rate_limit_accepts_gh_token_env(monkeypatch):
    import reposcan.cli as cli_module

    monkeypatch.setattr(cli_module, "GitHubClient", DummyClient)
    result = CliRunner().invoke(cli, ["rate-limit"], env={"GH_TOKEN": "gh-token"})

    assert result.exit_code == 0
    assert DummyClient.last_token == "gh-token"


def test_client_prefers_gh_token_env(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "gh-token")
    monkeypatch.setenv("GITHUB_TOKEN", "legacy-token")

    client = GitHubClient()

    assert client.token == "gh-token"
