<p align="center">
  <h1 align="center">RepoScan</h1>
  <p align="center">GitHub repository analytics from your terminal.</p>
  <p align="center">
    <a href="https://pypi.org/project/reposcan/"><img src="https://img.shields.io/pypi/v/reposcan?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/reposcan/"><img src="https://img.shields.io/pypi/pyversions/reposcan" alt="Python"></a>
    <a href="https://github.com/shazeus/reposcan/blob/main/LICENSE"><img src="https://img.shields.io/github/license/shazeus/reposcan" alt="License"></a>
    <a href="https://github.com/shazeus/reposcan/stargazers"><img src="https://img.shields.io/github/stars/shazeus/reposcan?style=social" alt="Stars"></a>
  </p>
</p>

---

Analyze any public GitHub repository in seconds — commit patterns, contributor stats, language breakdown, file hotspots, and a health score, all in a clean terminal UI.

- **Repository Overview** — stars, forks, watchers, license, topics, and size
- **Commit Activity** — by day, hour, and author with bar charts
- **Health Score** — weighted 0–100 rating based on activity, docs, and community
- **File Churn** — most frequently changed files across recent commits
- **Language Breakdown** — byte count and percentage per language
- **Issue Statistics** — open vs closed, average close time, top labels
- **Repo Comparison** — side-by-side table for multiple repositories

## Installation

```bash
pip install reposcan
```

Requires Python 3.8+. Works on Linux, macOS, and Windows.

## Usage

```bash
# Full analysis of any public repo
reposcan analyze torvalds/linux

# Just the overview
reposcan overview facebook/react

# Health score only
reposcan health golang/go

# Compare multiple repos side by side
reposcan compare "pallets/flask,django/django"

# File hotspot analysis
reposcan churn rust-lang/rust

# Language breakdown
reposcan languages shazeus/reposcan
```

## Commands

| Command | Description |
|---------|-------------|
| `reposcan analyze <repo>` | Full repository report |
| `reposcan overview <repo>` | Basic repo info (stars, forks, license, etc.) |
| `reposcan commits <repo>` | Commit activity breakdown (by day, hour, author) |
| `reposcan health <repo>` | Repository health score (0–100) |
| `reposcan churn <repo>` | File hotspots — most frequently changed files |
| `reposcan languages <repo>` | Language breakdown with percentages |
| `reposcan compare <repos>` | Side-by-side comparison of multiple repos |
| `reposcan rate-limit` | Check your GitHub API rate limit |

`<repo>` accepts both `owner/repo` format and full GitHub URLs.

## Configuration

### GitHub Token

Without a token you get **60 requests/hour**. With a token you get **5,000 requests/hour**.

```bash
# Set as environment variable (recommended)
export GITHUB_TOKEN=ghp_your_token_here

# Or pass directly
reposcan --token ghp_xxxx analyze owner/repo
```

Generate a token at [github.com/settings/tokens](https://github.com/settings/tokens) — no special scopes needed for public repos.

### Options

```bash
# Include file churn in full analysis (makes extra API calls)
reposcan analyze owner/repo --churn

# Get JSON output for piping to other tools
reposcan analyze owner/repo --json-output | jq '.health.score'
```

## Health Score

A weighted score (0–100) based on:

| Check | Points |
|-------|--------|
| Has description | +15 |
| Has license | +15 |
| Has topics | +10 |
| Active within 30 days | +20 |
| Active within 90 days | +10 |
| 5+ contributors | +15 |
| 2+ contributors | +10 |
| 100+ stars | +15 |
| Low open issue ratio | +10 |

## License

[MIT](LICENSE)
