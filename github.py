import asyncio
import httpx
from fastapi import HTTPException
from config import GITHUB_TOKEN, GITHUB_REPO, WATCH_LABELS
from logger import logs_for_grafana
from utils import days_open

logger = logs_for_grafana(__name__)

def get_github_headers() -> dict:
    """Return headers for GitHub API requests."""
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

# print(get_github_headers())

def format_issue(issue):
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "url": issue.get("html_url"),
        "days_open": days_open(issue.get("created_at", "")),
        "comments": issue.get("comments", 0),
        "labels": [l.get("name") for l in issue.get("labels", [])],
    }

async def fetch_issues_for_label(client: httpx.AsyncClient, label: str) -> list:
    issues = []
    page   = 1

    while True:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        params = {
            "state": "open",
            "labels": label,
            "sort": "updated",
            "direction": "desc",
            "per_page": 100,
            "page": page,
        }

        try:
            resp = await client.get(url, params=params)
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail=f"Gateway Timeout '{label}' issues")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Bad Gateway: {str(e)}")

        if resp.status_code == 401:
            raise HTTPException(status_code=500, detail="Unauthorized - Check Github token")
        if resp.status_code == 403:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"GitHub Repo '{GITHUB_REPO}' not found")
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Success {resp.status_code}")

        batch = resp.json()

        issues += [i for i in batch if "pull_request" not in i]

        if len(batch) < 100:
            break

        page += 1

    return issues


async def fetch_all_issues() -> dict:
    if not GITHUB_REPO:
        raise HTTPException(
            status_code=500, 
            detail="GITHUB_REPO not configured"
        )

    logger.info(f"Fetching issues for {GITHUB_REPO} — labels: {', '.join(WATCH_LABELS)}")

    async with httpx.AsyncClient(timeout=15.0, headers=get_github_headers()) as client:
        results = await asyncio.gather(
            *[fetch_issues_for_label(client, label) for label in WATCH_LABELS]
        )

    issues_by_label = dict(zip(WATCH_LABELS, results))

    for label, issues in issues_by_label.items():
        logger.info(f"  {label}: {len(issues)} open issue(s)")

    return issues_by_label