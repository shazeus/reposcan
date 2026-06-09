"""GitHub API client for RepoScan."""

import os
import sys
from datetime import datetime, timezone

import requests


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token=None):
        self.token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoScan",
        })
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"

    def _get(self, endpoint, params=None):
        url = f"{self.BASE_URL}{endpoint}"
        resp = self.session.get(url, params=params)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            print("GitHub API rate limit exceeded. Set GH_TOKEN or GITHUB_TOKEN for higher limits.")
            sys.exit(1)
        if resp.status_code == 404:
            print(f"Repository not found: {endpoint}")
            sys.exit(1)
        resp.raise_for_status()
        return resp.json()

    def _get_paginated(self, endpoint, params=None, max_pages=10):
        params = params or {}
        params.setdefault("per_page", 100)
        results = []
        for page in range(1, max_pages + 1):
            params["page"] = page
            data = self._get(endpoint, params)
            if not data:
                break
            results.extend(data)
        return results

    def get_repo(self, owner, repo):
        return self._get(f"/repos/{owner}/{repo}")

    def get_commits(self, owner, repo, since=None, max_pages=5):
        params = {}
        if since:
            params["since"] = since.isoformat()
        return self._get_paginated(f"/repos/{owner}/{repo}/commits", params, max_pages)

    def get_contributors(self, owner, repo):
        return self._get_paginated(f"/repos/{owner}/{repo}/contributors", max_pages=3)

    def get_languages(self, owner, repo):
        return self._get(f"/repos/{owner}/{repo}/languages")

    def get_branches(self, owner, repo):
        return self._get_paginated(f"/repos/{owner}/{repo}/branches", max_pages=3)

    def get_issues(self, owner, repo, state="all", max_pages=3):
        return self._get_paginated(
            f"/repos/{owner}/{repo}/issues",
            params={"state": state},
            max_pages=max_pages,
        )

    def get_pulls(self, owner, repo, state="all", max_pages=3):
        return self._get_paginated(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state},
            max_pages=max_pages,
        )

    def get_releases(self, owner, repo):
        return self._get_paginated(f"/repos/{owner}/{repo}/releases", max_pages=2)

    def get_commit_detail(self, owner, repo, sha):
        return self._get(f"/repos/{owner}/{repo}/commits/{sha}")

    def get_rate_limit(self):
        return self._get("/rate_limit")
