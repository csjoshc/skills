import re
from src.infra.db import save_order


def make_slug(text):
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def archive_report(report_id: str, title: str) -> None:
    save_order(report_id, make_slug(title))
