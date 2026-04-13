import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from config import GITHUB_TOKEN, GITHUB_REPO, SLACK_WEBHOOK_URL, MAX_PER_LABEL, WATCH_LABELS
from logger import logs_for_grafana
from github import fetch_all_issues, format_issue
from slack import build_slack_message, post_to_slack
from utils import days_open

app = FastAPI(title="GitHub Issues to Slack")

# Logs for Grafana Alloy
logger = logs_for_grafana(__name__)


# status check: validate if values are empty, if so, let me know.
@app.get("/status")
async def status():
    is_github_token_set = bool(GITHUB_TOKEN and GITHUB_TOKEN.strip())
    is_slack_configured = bool(SLACK_WEBHOOK_URL and SLACK_WEBHOOK_URL.strip())
    is_repo_configured  = bool(GITHUB_REPO and GITHUB_REPO.strip())

    is_ready = is_github_token_set and is_slack_configured and is_repo_configured

    return {
        "status": "ready" if is_ready else "error, check env",
        "repo": GITHUB_REPO or "ENV NOT SET",
        "watch_labels": WATCH_LABELS or "ENV NOT SET",
        "max_per_label": MAX_PER_LABEL or "ENV NOT SET",
        "github_token_set": is_github_token_set or "ENV NOT SET",
        "slack_configured": is_slack_configured or "ENV NOT SET",
        "repo_configured": is_repo_configured or "ENV NOT SET",
    }

# Test & Confirm.
@app.get("/issues")
async def get_issues():
    issues_by_label = await fetch_all_issues()

    return {
        "repo":   GITHUB_REPO,
        "labels": WATCH_LABELS,
        "total":  sum(len(v) for v in issues_by_label.items()),
        "breakdown": {
            label: [format_issue(i) for i in issues]
            for label, issues in issues_by_label.items()
        }
    }


# Run it.
@app.post("/trigger")
async def trigger():
    logger.info("Trigger started | fetching GitHub issues...")

    issues_by_label = await fetch_all_issues()
    total = sum(len(v) for v in issues_by_label.values())

    message = build_slack_message(GITHUB_REPO, issues_by_label)
    await post_to_slack(message)

    logger.info(f"Trigger complete | {total} total issue(s) reported")

    return {
        "status": "sent",
        "repo":   GITHUB_REPO,
        "total_issues": total,
        "breakdown": {label: len(issues) for label, issues in issues_by_label.items()},
    }

