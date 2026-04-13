import httpx
from fastapi import HTTPException
from config import SLACK_WEBHOOK_URL, MAX_PER_LABEL
from utils import redact_url, label_emoji
from github import format_issue 
from logger import logs_for_grafana

logger = logs_for_grafana(__name__)

def build_slack_message(repo: str, issues_by_label: dict) -> dict:
    total = sum(len(v) for v in issues_by_label.values())
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Open Issues: {repo}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{total} open issue(s)* across {len(issues_by_label)} watched label(s)"
            }
        },
        {"type": "divider"},
    ]

    for label, issues in issues_by_label.items():
        emoji = label_emoji(label)

        if not issues:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{label.capitalize()}*\n_No open issues_"
                }
            })
            blocks.append({"type": "divider"})
            continue

        lines = []
        for raw in issues[:MAX_PER_LABEL]:
            issue = format_issue(raw)
            number = issue["number"]
            title = issue["title"] or "Untitled"
            url = issue["url"]
            age = issue["days_open"]
            comments = issue["comments"]

            age_str      = f"{age}d old"
            comment_str  = f"{comments} 💬" if comments else ""
            meta         = "  ·  ".join(filter(None, [age_str, comment_str]))

            lines.append(f"• <{url}|#{number} {title}>\n  _{meta}_")

        overflow = len(issues) - MAX_PER_LABEL
        if overflow > 0:
            lines.append(f"_...and {overflow} more — <https://github.com/{repo}/issues?q=is:open+label:{label}|view all>_")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{label.capitalize()}*  ({len(issues)} open)\n" + "\n".join(lines)
            }
        })
        blocks.append({"type": "divider"})

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"<https://github.com/{repo}/issues|View all open issues on GitHub>"
        }
    })

    return {
        "blocks": blocks,
        "text": f"Open issues digest for {repo} — {total} issue(s) across {len(issues_by_label)} label(s)"
    }

async def post_to_slack(message: dict) -> None:
    if not SLACK_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="SLACK_WEBHOOK_URL not configured")

    logger.info(f"Posting to Slack at {redact_url(SLACK_WEBHOOK_URL)}...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(SLACK_WEBHOOK_URL, json=message)
        except httpx.TimeoutException:
            logger.error("Slack request timed out")
            raise HTTPException(status_code=504, detail="Slack request timed out")
        except httpx.RequestError as e:
            logger.error(f"Could not reach Slack: {e}")
            raise HTTPException(status_code=502, detail=f"Could not reach Slack: {str(e)}")

    if resp.status_code != 200:
        logger.error(f"Slack rejected message — HTTP {resp.status_code}: {resp.text}")
        raise HTTPException(status_code=502, detail=f"Slack rejected the message: {resp.text}")

    logger.info(f"Slack message delivered — HTTP {resp.status_code}")