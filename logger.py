import logging
import os

def logs_for_grafana(name: str) -> logging.Logger:
    LOG_FILE = os.getenv("LOG_FILE", "/var/log/github-issues-to-slack-full-log.log")

    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ]
)
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logging.getLogger(name)