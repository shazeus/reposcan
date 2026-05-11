# RepoScan

GitHub repository analytics from your terminal. Analyze any public repo in seconds — commit patterns, contributor stats, language breakdown, file hotspots, and a health score, all in a clean terminal UI.

## Install

```bash
pip install reposcan
```

## Quick Start

```bash
# Full analysis of any public repo
reposcan analyze torvalds/linux

# Just the overview
reposcan overview facebook/react

# Health score only
reposcan health golang/go

# Compare multiple repos side by side
reposcan compare "pallets/flask,django/django,fastapi/tiangolo"
```

## Commands

| Command | Description |
|---------|-------------|
| `reposcan analyze <repo>` | Full repository report |
| `reposcan overview <repo>` | Basic repo info (stars, forks, license, etc.) |
| `reposcan commits <repo>` | Commit activity breakdown (by day, hour, author) |
| `reposcan health <repo>` | Repository health score (0-100) |
| `reposcan churn <repo>` | File hotspots — most frequently changed files |
| `reposcan languages <repo>` | Language breakdown with percentages |
| `reposcan compare <repos>` | Side-by-side comparison of multiple repos |
| `reposcan rate-limit` | Check your GitHub API rate limit |

`<repo>` accepts both `owner/repo` format and full GitHub URLs.

## Options

```bash
# Include file churn in full analysis (makes extra API calls)
reposcan analyze owner/repo --churn

# Get JSON output instead of tables
reposcan analyze owner/repo --json-output

# Use a GitHub token for higher rate limits
reposcan --token ghp_xxxx analyze owner/repo

# Or set it as an environment variable
export GITHUB_TOKEN=ghp_xxxx
```

## What It Analyzes

### Repository Overview
Stars, forks, watchers, open issues, license, topics, creation date, last push, and size.

### Commit Activity
- Total commits analyzed
- Commits by day of week (with bar chart)
- Peak commit hours (UTC)
- Top committers
- Current commit streak

### Health Score (0-100)
A weighted score based on:
- Has description (+15)
- Has license (+15)
- Has topics (+10)
- Recent activity within 30 days (+20) or 90 days (+10)
- Contributor count (+5 to +15)
- Star count (+5 to +15)
- Open issue ratio (+5 to +10)

### File Churn / Hotspots
The most frequently modified files across recent commits — helps identify areas of high change that may need refactoring or extra test coverage.

### Language Breakdown
Byte count and percentage for each language detected by GitHub.

### Issue Statistics
Open vs closed counts, average close time, and most used labels.

### Repo Comparison
Compare stars, forks, issues, language, health score, and last push date across multiple repos in one table.

## GitHub API Rate Limits

Without a token, you get **60 requests/hour**. With a token, you get **5,000 requests/hour**.

Generate a personal access token at [github.com/settings/tokens](https://github.com/settings/tokens) — no special scopes needed for public repos.

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

## Examples

```bash
# Analyze your own repo
reposcan analyze shazeus/reposcan

# Deep dive into commit patterns
reposcan commits rust-lang/rust

# Check if a dependency is well maintained
reposcan health some-org/some-library

# Compare web frameworks
reposcan compare "pallets/flask,django/django"

# Pipe JSON to other tools
reposcan analyze owner/repo --json-output | jq '.health.score'
```

## Requirements

- Python 3.8+
- Works on Linux, macOS, and Windows

## License

MIT
