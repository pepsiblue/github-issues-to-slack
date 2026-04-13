# Deliver GH Issues as Slack Notification
---
## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/status` | Confirm all environment variables are configured correctly |
| `GET` | `/issues` | View all GH Issues but do not post to slack |
| `POST` | `/trigger` | Deliver GH Issues to Slack |
---
## Prerequisites
- Determine any Github Repo you wish to use with open issues and available labels (I picked netdata) https://github.com/netdata/netdata
    - Labels chosen: bug, feature request (e.g. feature)
- python3 installed with homebrew (easiest on macOS)
- Slack Channel and Slack incoming webook URL avaialble

---
## Setup & Config
### 1. Clone GH repo

```bash
git clone git@github.com:pepsiblue/github-issues-to-slack.git
cd github-issues-to-slack
```

### 2. Configure environment variables

```bash
cp env.example .env
```

### 3. Create local log file
Inside the repo directory create a new empty log file. This file is used to persist all logging ouputs:
```bash
# be sure you're in the correct repo directory
cd github-issues-to-slack

# create empty log file
touch github-issues-to-slack-full-log.log

# let's grab the absolute path and store it in the .env file
pwd

# result
/User/<name>/path/to/local/repo # copy the whole path and paste inside the .env file
```
Paste the dir path in `.env` after `LOG_FILE=` retaining the filename: `/github-issues-to-slack-full-log.log`

### 4. Create a new GitHub Access Token

- Generate a new Gihub Access Token (legacy)
- No scopes are needed when using public repos
- Copy/Paste access token in the `.env` file after `"GITHUB_TOKEN="`

### 5. Create a new Slack Incoming Webhook

- Go to https://api.slack.com/apps → Create New App → From Scratch
- Enable Incoming Webhooks then add it to your desired channel
- Copy/Paste the Webhook URL in the `.env` file after `"SLACK_WEBHOOK_URL="`


### 6. Install and run

```bash
python3 -m venv venv #using python3 on macOS with homebrew install
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Try it out!

**Status Check - Confirm all variables are set correctly:**
```bash

curl -s http://localhost:8000/status | python3 -m json.tool
```

**View GH Issues but do not post to slack :**
```bash
curl http://localhost:8000/issues
```

**Deliver GH Issues to Slack:**
```bash
curl -X POST http://localhost:8000/trigger
```

# Resources
- [netdata - example GH public repo](https://github.com/netdata/netdata/)
- [Bruno - Git API client](https://www.usebruno.com)
- [Slack - Block Kit docs](https://docs.slack.dev/block-kit/formatting-with-rich-text#header-block)
- [HTTP Status Codes](https://codeshack.io/http-status-codes/)
