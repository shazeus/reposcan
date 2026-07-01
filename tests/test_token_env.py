from click.testing import CliRunner
import json
import requests

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


def test_rate_limit_json_output(monkeypatch):
    import reposcan.cli as cli_module

    monkeypatch.setattr(cli_module, "GitHubClient", DummyClient)
    result = CliRunner().invoke(cli, ["--token", "gh-token", "rate-limit", "--json-output"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload == {
        "resource": "core",
        "remaining": 5000,
        "limit": 5000,
        "reset": 0,
        "authenticated": True,
    }


def test_client_prefers_gh_token_env(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "gh-token")
    monkeypatch.setenv("GITHUB_TOKEN", "legacy-token")

    client = GitHubClient()

    assert client.token == "gh-token"


def test_client_exits_cleanly_on_request_error(monkeypatch):
    client = GitHubClient(token="gh-token")

    def fail(*args, **kwargs):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(client.session, "get", fail)
    monkeypatch.setattr("reposcan.cli.GitHubClient", lambda token=None: client)

    result = CliRunner().invoke(cli, ["--token", "gh-token", "rate-limit"])

    assert result.exit_code == 1
    assert "GitHub API request failed: boom" in result.output


def test_analyze_json_output_emits_json_error_on_rate_limit(monkeypatch):
    client = GitHubClient(token="gh-token")

    class DummyResponse:
        status_code = 403
        text = "API rate limit exceeded"

        def raise_for_status(self):
            raise AssertionError("raise_for_status should not run for rate-limit errors")

    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: DummyResponse())
    monkeypatch.setattr("reposcan.cli.GitHubClient", lambda token=None: client)

    result = CliRunner().invoke(
        cli,
        ["--token", "gh-token", "analyze", "shazeus/depstree", "--json-output"],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload == {
        "error": {
            "type": "rate_limit",
            "message": "GitHub API rate limit exceeded. Set GH_TOKEN or GITHUB_TOKEN for higher limits.",
        }
    }
