from datetime import datetime, timezone
from urllib.parse import urlparse

def redact_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/***"
    except Exception:
        return "***"

def days_open(created_at: str) -> int:
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - created).days


def label_emoji(label: str) -> str:
    mapping = {
        "bug": "🐛",
        "enhancement": "✨",
        "help wanted": "🙋",
        "question": "❓",
        "documentation": "📄",
        "duplicate": "🔁",
        "wontfix": "🚫",
    }
    return mapping.get(label.lower(), "🏷️")