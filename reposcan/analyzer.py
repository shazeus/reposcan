"""Repository analysis logic for RepoScan."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone


class RepoAnalyzer:
    def __init__(self, client, owner, repo):
        self.client = client
        self.owner = owner
        self.repo = repo
        self._repo_data = None
        self._commits = None

    @property
    def repo_data(self):
        if self._repo_data is None:
            self._repo_data = self.client.get_repo(self.owner, self.repo)
        return self._repo_data

    @property
    def commits(self):
        if self._commits is None:
            self._commits = self.client.get_commits(self.owner, self.repo)
        return self._commits

    def overview(self):
        r = self.repo_data
        return {
            "name": r["full_name"],
            "description": r.get("description", "N/A"),
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "watchers": r["subscribers_count"],
            "open_issues": r["open_issues_count"],
            "language": r.get("language", "N/A"),
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "pushed_at": r["pushed_at"],
            "default_branch": r["default_branch"],
            "license": r.get("license", {}).get("spdx_id", "None") if r.get("license") else "None",
            "archived": r["archived"],
            "size_kb": r["size"],
            "topics": r.get("topics", []),
        }

    def commit_activity(self):
        commits = self.commits
        if not commits:
            return {"total": 0, "by_day": {}, "by_hour": {}, "by_author": {}}

        by_day = Counter()
        by_hour = Counter()
        by_author = Counter()
        dates = []

        for c in commits:
            commit_info = c.get("commit", {})
            author_info = commit_info.get("author", {})
            date_str = author_info.get("date", "")
            if date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                by_day[dt.strftime("%A")] += 1
                by_hour[dt.hour] += 1
                dates.append(dt)

            author_name = author_info.get("name", "Unknown")
            by_author[author_name] += 1

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sorted_days = {d: by_day.get(d, 0) for d in day_order}

        streak = self._calculate_streak(dates)

        return {
            "total": len(commits),
            "by_day": sorted_days,
            "by_hour": dict(sorted(by_hour.items())),
            "by_author": dict(by_author.most_common(10)),
            "streak": streak,
            "first_commit": min(dates).isoformat() if dates else None,
            "last_commit": max(dates).isoformat() if dates else None,
        }

    def _calculate_streak(self, dates):
        if not dates:
            return 0
        unique_days = sorted(set(d.date() for d in dates), reverse=True)
        if not unique_days:
            return 0
        streak = 1
        for i in range(1, len(unique_days)):
            if (unique_days[i - 1] - unique_days[i]).days == 1:
                streak += 1
            else:
                break
        return streak

    def file_churn(self, max_commits=50):
        commits = self.commits[:max_commits]
        file_changes = Counter()
        file_additions = Counter()
        file_deletions = Counter()

        for c in commits:
            sha = c["sha"]
            detail = self.client.get_commit_detail(self.owner, self.repo, sha)
            for f in detail.get("files", []):
                filename = f["filename"]
                file_changes[filename] += 1
                file_additions[filename] += f.get("additions", 0)
                file_deletions[filename] += f.get("deletions", 0)

        hotspots = []
        for filename, changes in file_changes.most_common(15):
            hotspots.append({
                "file": filename,
                "changes": changes,
                "additions": file_additions[filename],
                "deletions": file_deletions[filename],
                "churn": file_additions[filename] + file_deletions[filename],
            })
        return hotspots

    def contributor_stats(self):
        contributors = self.client.get_contributors(self.owner, self.repo)
        return [
            {
                "login": c["login"],
                "contributions": c["contributions"],
                "avatar": c["avatar_url"],
                "profile": c["html_url"],
            }
            for c in contributors[:20]
        ]

    def language_breakdown(self):
        languages = self.client.get_languages(self.owner, self.repo)
        total = sum(languages.values()) or 1
        return {lang: {"bytes": b, "percent": round(b / total * 100, 1)} for lang, b in languages.items()}

    def issue_stats(self):
        issues = self.client.get_issues(self.owner, self.repo)
        prs = {i["number"] for i in issues if "pull_request" in i}
        issues_only = [i for i in issues if i["number"] not in prs]

        open_count = sum(1 for i in issues_only if i["state"] == "open")
        closed_count = sum(1 for i in issues_only if i["state"] == "closed")

        close_times = []
        for i in issues_only:
            if i["state"] == "closed" and i.get("closed_at"):
                created = datetime.fromisoformat(i["created_at"].replace("Z", "+00:00"))
                closed = datetime.fromisoformat(i["closed_at"].replace("Z", "+00:00"))
                close_times.append((closed - created).total_seconds() / 3600)

        avg_close_hours = round(sum(close_times) / len(close_times), 1) if close_times else None

        label_counts = Counter()
        for i in issues_only:
            for label in i.get("labels", []):
                label_counts[label["name"]] += 1

        return {
            "total": len(issues_only),
            "open": open_count,
            "closed": closed_count,
            "avg_close_time_hours": avg_close_hours,
            "top_labels": dict(label_counts.most_common(10)),
        }

    def branch_info(self):
        branches = self.client.get_branches(self.owner, self.repo)
        return {
            "total": len(branches),
            "names": [b["name"] for b in branches[:20]],
            "default": self.repo_data["default_branch"],
        }

    def health_score(self):
        r = self.repo_data
        score = 0
        details = {}

        if r.get("description"):
            score += 15
            details["description"] = True
        else:
            details["description"] = False

        if r.get("license"):
            score += 15
            details["license"] = True
        else:
            details["license"] = False

        if r.get("topics"):
            score += 10
            details["topics"] = True
        else:
            details["topics"] = False

        commits = self.commits
        if commits:
            last_commit_date = commits[0].get("commit", {}).get("author", {}).get("date", "")
            if last_commit_date:
                dt = datetime.fromisoformat(last_commit_date.replace("Z", "+00:00"))
                days_since = (datetime.now(timezone.utc) - dt).days
                if days_since < 30:
                    score += 20
                    details["recent_activity"] = f"{days_since}d ago"
                elif days_since < 90:
                    score += 10
                    details["recent_activity"] = f"{days_since}d ago"
                else:
                    details["recent_activity"] = f"{days_since}d ago (stale)"

        contributors = self.client.get_contributors(self.owner, self.repo)
        if len(contributors) >= 5:
            score += 15
            details["contributors"] = f"{len(contributors)} (strong)"
        elif len(contributors) >= 2:
            score += 10
            details["contributors"] = f"{len(contributors)} (growing)"
        else:
            score += 5
            details["contributors"] = f"{len(contributors)} (solo)"

        if r["stargazers_count"] >= 100:
            score += 15
        elif r["stargazers_count"] >= 10:
            score += 10
        elif r["stargazers_count"] >= 1:
            score += 5
        details["stars"] = r["stargazers_count"]

        open_ratio = r["open_issues_count"] / max(r["stargazers_count"], 1)
        if open_ratio < 0.1:
            score += 10
            details["issue_ratio"] = "healthy"
        elif open_ratio < 0.5:
            score += 5
            details["issue_ratio"] = "moderate"
        else:
            details["issue_ratio"] = "high"

        return {"score": min(score, 100), "details": details}

    def full_report(self, include_churn=False):
        report = {
            "overview": self.overview(),
            "commit_activity": self.commit_activity(),
            "contributors": self.contributor_stats(),
            "languages": self.language_breakdown(),
            "issues": self.issue_stats(),
            "branches": self.branch_info(),
            "health": self.health_score(),
        }
        if include_churn:
            report["file_churn"] = self.file_churn()
        return report
