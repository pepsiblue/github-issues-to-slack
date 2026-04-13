import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
MAX_PER_LABEL = int(os.getenv("MAX_PER_LABEL", "5"))

# Comma-separated list — override by using .env
WATCH_LABELS = [
    l.strip()
    for l in os.getenv("WATCH_LABELS", "bug").split(",")
    if l.strip()
]