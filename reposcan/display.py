"""Rich terminal display for RepoScan."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.bar import Bar
from rich import box

console = Console()


def print_header(repo_name):
    console.print()
    console.print(
        Panel(
            f"[bold cyan]RepoScan[/] — analyzing [bold yellow]{repo_name}[/]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()


def print_overview(data):
    table = Table(title="Repository Overview", box=box.ROUNDED, border_style="blue")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Name", data["name"])
    table.add_row("Description", data["description"] or "—")
    table.add_row("Language", data["language"] or "—")
    table.add_row("Stars", f"★ {data['stars']}")
    table.add_row("Forks", str(data["forks"]))
    table.add_row("Watchers", str(data["watchers"]))
    table.add_row("Open Issues", str(data["open_issues"]))
    table.add_row("License", data["license"])
    table.add_row("Default Branch", data["default_branch"])
    table.add_row("Size", f"{data['size_kb']} KB")
    table.add_row("Created", data["created_at"][:10])
    table.add_row("Last Push", data["pushed_at"][:10])
    if data["topics"]:
        table.add_row("Topics", ", ".join(data["topics"]))
    if data["archived"]:
        table.add_row("Status", "[red]ARCHIVED[/]")

    console.print(table)
    console.print()


def print_commit_activity(data):
    if data["total"] == 0:
        console.print("[dim]No commit data available.[/]")
        return

    console.print(f"[bold]Commit Activity[/] — {data['total']} commits analyzed")
    console.print()

    if data.get("last_commit"):
        console.print(f"  Last commit: [green]{data['last_commit'][:10]}[/]")
    if data.get("streak"):
        console.print(f"  Current streak: [yellow]{data['streak']} day(s)[/]")
    console.print()

    day_table = Table(title="Commits by Day", box=box.SIMPLE)
    day_table.add_column("Day", style="bold")
    day_table.add_column("Commits", justify="right")
    day_table.add_column("Graph")

    max_day = max(data["by_day"].values()) if data["by_day"] else 1
    for day, count in data["by_day"].items():
        bar_len = int(count / max_day * 20) if max_day > 0 else 0
        bar = "█" * bar_len
        day_table.add_row(day[:3], str(count), f"[cyan]{bar}[/]")

    console.print(day_table)
    console.print()

    if data["by_hour"]:
        hour_table = Table(title="Peak Hours (UTC)", box=box.SIMPLE)
        hour_table.add_column("Hour", justify="right")
        hour_table.add_column("Commits", justify="right")

        sorted_hours = sorted(data["by_hour"].items(), key=lambda x: x[1], reverse=True)[:5]
        for hour, count in sorted_hours:
            hour_table.add_row(f"{hour:02d}:00", str(count))

        console.print(hour_table)
        console.print()

    if data["by_author"]:
        author_table = Table(title="Top Committers", box=box.SIMPLE)
        author_table.add_column("Author", style="bold")
        author_table.add_column("Commits", justify="right")

        for author, count in data["by_author"].items():
            author_table.add_row(author, str(count))

        console.print(author_table)
        console.print()


def print_contributors(data):
    if not data:
        return

    table = Table(title="Contributors", box=box.ROUNDED, border_style="green")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Login", style="bold")
    table.add_column("Contributions", justify="right")

    for i, c in enumerate(data, 1):
        table.add_row(str(i), c["login"], str(c["contributions"]))

    console.print(table)
    console.print()


def print_languages(data):
    if not data:
        return

    table = Table(title="Languages", box=box.ROUNDED, border_style="magenta")
    table.add_column("Language", style="bold")
    table.add_column("Bytes", justify="right")
    table.add_column("Share", justify="right")
    table.add_column("Bar")

    colors = ["cyan", "green", "yellow", "red", "blue", "magenta"]
    for i, (lang, info) in enumerate(data.items()):
        color = colors[i % len(colors)]
        bar_len = int(info["percent"] / 5)
        bar = "█" * bar_len
        table.add_row(
            lang,
            f"{info['bytes']:,}",
            f"{info['percent']}%",
            f"[{color}]{bar}[/]",
        )

    console.print(table)
    console.print()


def print_issues(data):
    table = Table(title="Issue Statistics", box=box.ROUNDED, border_style="yellow")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Issues", str(data["total"]))
    table.add_row("Open", f"[red]{data['open']}[/]")
    table.add_row("Closed", f"[green]{data['closed']}[/]")
    if data["avg_close_time_hours"] is not None:
        if data["avg_close_time_hours"] < 24:
            table.add_row("Avg Close Time", f"{data['avg_close_time_hours']}h")
        else:
            days = round(data["avg_close_time_hours"] / 24, 1)
            table.add_row("Avg Close Time", f"{days} days")

    console.print(table)

    if data["top_labels"]:
        console.print()
        label_table = Table(title="Top Labels", box=box.SIMPLE)
        label_table.add_column("Label")
        label_table.add_column("Count", justify="right")
        for label, count in data["top_labels"].items():
            label_table.add_row(label, str(count))
        console.print(label_table)

    console.print()


def print_branches(data):
    console.print(f"[bold]Branches[/] — {data['total']} total (default: [green]{data['default']}[/])")
    if data["total"] <= 10:
        for name in data["names"]:
            marker = " ★" if name == data["default"] else ""
            console.print(f"  • {name}{marker}")
    console.print()


def print_file_churn(data):
    if not data:
        console.print("[dim]No file churn data.[/]")
        return

    table = Table(title="File Hotspots (Most Changed)", box=box.ROUNDED, border_style="red")
    table.add_column("File", style="bold", max_width=50)
    table.add_column("Changes", justify="right")
    table.add_column("Added", justify="right", style="green")
    table.add_column("Deleted", justify="right", style="red")
    table.add_column("Churn", justify="right", style="yellow")

    for f in data:
        table.add_row(
            f["file"],
            str(f["changes"]),
            f"+{f['additions']}",
            f"-{f['deletions']}",
            str(f["churn"]),
        )

    console.print(table)
    console.print()


def print_health(data):
    score = data["score"]
    if score >= 80:
        color = "green"
        label = "Excellent"
    elif score >= 60:
        color = "yellow"
        label = "Good"
    elif score >= 40:
        color = "orange3"
        label = "Fair"
    else:
        color = "red"
        label = "Needs Work"

    bar_len = score // 2
    bar = "█" * bar_len + "░" * (50 - bar_len)

    console.print(
        Panel(
            f"[{color} bold]{score}/100 — {label}[/]\n[{color}]{bar}[/]",
            title="[bold]Health Score[/]",
            border_style=color,
            padding=(1, 2),
        )
    )

    details = data["details"]
    checks = Table(box=box.SIMPLE)
    checks.add_column("Check")
    checks.add_column("Status")

    for key, val in details.items():
        if isinstance(val, bool):
            status = "[green]✓[/]" if val else "[red]✗[/]"
        else:
            status = str(val)
        checks.add_row(key.replace("_", " ").title(), status)

    console.print(checks)
    console.print()


def print_full_report(report):
    print_overview(report["overview"])
    print_health(report["health"])
    print_commit_activity(report["commit_activity"])
    print_languages(report["languages"])
    print_contributors(report["contributors"])
    print_issues(report["issues"])
    print_branches(report["branches"])
    if "file_churn" in report:
        print_file_churn(report["file_churn"])
