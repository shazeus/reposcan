"""CLI interface for RepoScan."""

import json
import sys

import click
from rich.console import Console

from reposcan import __version__
from reposcan.github_api import GitHubClient
from reposcan.analyzer import RepoAnalyzer
from reposcan import display

console = Console()


def parse_repo(repo_str):
    repo_str = repo_str.strip().rstrip("/")
    if "github.com/" in repo_str:
        parts = repo_str.split("github.com/")[-1].split("/")
    else:
        parts = repo_str.split("/")
    if len(parts) < 2:
        console.print("[red]Invalid format. Use: owner/repo or a GitHub URL[/]")
        sys.exit(1)
    return parts[0], parts[1]


@click.group()
@click.version_option(version=__version__, prog_name="reposcan")
@click.option(
    "--token",
    envvar=["GH_TOKEN", "GITHUB_TOKEN"],
    help="GitHub personal access token",
)
@click.pass_context
def cli(ctx, token):
    """RepoScan - GitHub repository analytics from your terminal."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = GitHubClient(token)


@cli.command()
@click.argument("repo")
@click.option("--churn", is_flag=True, help="Include file churn analysis (slower)")
@click.option("--json-output", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def analyze(ctx, repo, churn, as_json):
    """Run a full analysis on a repository.

    REPO can be 'owner/repo' or a full GitHub URL.
    """
    owner, repo_name = parse_repo(repo)
    client = ctx.obj["client"]
    analyzer = RepoAnalyzer(client, owner, repo_name)

    if as_json:
        report = analyzer.full_report(include_churn=churn)
        click.echo(json.dumps(report, indent=2, default=str))
        return

    display.print_header(f"{owner}/{repo_name}")
    with console.status("[cyan]Analyzing repository...[/]"):
        report = analyzer.full_report(include_churn=churn)
    display.print_full_report(report)


@cli.command()
@click.argument("repo")
@click.pass_context
def overview(ctx, repo):
    """Show basic repository info."""
    owner, repo_name = parse_repo(repo)
    analyzer = RepoAnalyzer(ctx.obj["client"], owner, repo_name)
    display.print_header(f"{owner}/{repo_name}")
    display.print_overview(analyzer.overview())


@cli.command()
@click.argument("repo")
@click.pass_context
def commits(ctx, repo):
    """Show commit activity analysis."""
    owner, repo_name = parse_repo(repo)
    analyzer = RepoAnalyzer(ctx.obj["client"], owner, repo_name)
    display.print_header(f"{owner}/{repo_name}")
    with console.status("[cyan]Fetching commits...[/]"):
        data = analyzer.commit_activity()
    display.print_commit_activity(data)


@cli.command()
@click.argument("repo")
@click.pass_context
def health(ctx, repo):
    """Calculate repository health score."""
    owner, repo_name = parse_repo(repo)
    analyzer = RepoAnalyzer(ctx.obj["client"], owner, repo_name)
    display.print_header(f"{owner}/{repo_name}")
    with console.status("[cyan]Calculating health score...[/]"):
        data = analyzer.health_score()
    display.print_health(data)


@cli.command()
@click.argument("repo")
@click.pass_context
def churn(ctx, repo):
    """Show file churn / hotspot analysis."""
    owner, repo_name = parse_repo(repo)
    analyzer = RepoAnalyzer(ctx.obj["client"], owner, repo_name)
    display.print_header(f"{owner}/{repo_name}")
    with console.status("[cyan]Analyzing file changes (this may take a moment)...[/]"):
        data = analyzer.file_churn()
    display.print_file_churn(data)


@cli.command()
@click.argument("repo")
@click.pass_context
def languages(ctx, repo):
    """Show language breakdown."""
    owner, repo_name = parse_repo(repo)
    analyzer = RepoAnalyzer(ctx.obj["client"], owner, repo_name)
    display.print_header(f"{owner}/{repo_name}")
    data = analyzer.language_breakdown()
    display.print_languages(data)


@cli.command()
@click.argument("repo")
@click.option("--limit", default=10, help="Max repos to compare")
@click.pass_context
def compare(ctx, repo, limit):
    """Compare multiple repos (comma-separated).

    Example: reporadar compare owner/repo1,owner/repo2
    """
    repos = [r.strip() for r in repo.split(",")]
    client = ctx.obj["client"]

    from rich.table import Table
    from rich import box

    table = Table(title="Repository Comparison", box=box.ROUNDED, border_style="cyan")
    table.add_column("Repo", style="bold")
    table.add_column("Stars", justify="right")
    table.add_column("Forks", justify="right")
    table.add_column("Issues", justify="right")
    table.add_column("Language")
    table.add_column("Health", justify="right")
    table.add_column("Last Push")

    for r in repos[:limit]:
        owner, repo_name = parse_repo(r)
        analyzer = RepoAnalyzer(client, owner, repo_name)
        with console.status(f"[cyan]Fetching {owner}/{repo_name}...[/]"):
            ov = analyzer.overview()
            h = analyzer.health_score()

        score = h["score"]
        if score >= 80:
            score_str = f"[green]{score}[/]"
        elif score >= 60:
            score_str = f"[yellow]{score}[/]"
        else:
            score_str = f"[red]{score}[/]"

        table.add_row(
            ov["name"],
            f"★ {ov['stars']}",
            str(ov["forks"]),
            str(ov["open_issues"]),
            ov["language"] or "—",
            score_str,
            ov["pushed_at"][:10],
        )

    console.print()
    console.print(table)
    console.print()


@cli.command(name="rate-limit")
@click.pass_context
def rate_limit(ctx):
    """Check GitHub API rate limit status."""
    client = ctx.obj["client"]
    data = client.get_rate_limit()
    core = data["resources"]["core"]

    console.print(f"\n[bold]GitHub API Rate Limit[/]")
    console.print(f"  Remaining: [{'green' if core['remaining'] > 100 else 'red'}]{core['remaining']}[/] / {core['limit']}")
    from datetime import datetime, timezone
    reset_time = datetime.fromtimestamp(core["reset"], tz=timezone.utc)
    console.print(f"  Resets at: {reset_time.strftime('%H:%M:%S UTC')}")
    if not ctx.obj["client"].token:
        console.print("  [yellow]Tip: Set GH_TOKEN or GITHUB_TOKEN for 5000 req/hr instead of 60[/]")
    console.print()
