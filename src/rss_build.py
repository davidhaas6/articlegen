# rss_build.py - ai generated
from datetime import datetime, timezone
from email.utils import format_datetime
import json, os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any
import json, os, html

def rfc822(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)

def parse_timestamp(ts: Optional[str]) -> datetime:
    """Your JSON gives 'YYYY-MM-DD HH:MM:SS'. Be forgiving if missing."""
    if not ts:
        return datetime.now(timezone.utc)
    try:
        # Example: "2025-10-03 13:47:11"
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)
    except Exception:
        # Last resort: ISO-ish or now
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)

def para_wrap(text: str) -> str:
    """Plaintext -> very light HTML for content:encoded."""
    if not text:
        return ""
    # Escape then wrap paragraphs
    escaped = html.escape(text)
    paragraphs = [f"<p>{p.strip()}</p>" for p in escaped.split("\n") if p.strip()]
    return "\n".join(paragraphs) or f"<p>{escaped}</p>"


def load_items_from_json_dir(
    article_dir: str,
    base_url: str,
    site_subpath_builder: Optional[Callable[[Dict[str, Any]], str]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fits YOUR schema exactly. Keys used:
      title, overview, body, generator, reading_time_minutes, category,
      parody_src, comments, img_path, timestamp, article_id, url
    """
    items: List[Dict[str, Any]] = []

    files = sorted([f for f in os.listdir(article_dir) if f.endswith(".json")], reverse=True)
    for fname in files:
        with open(os.path.join(article_dir, fname), "r", encoding="utf-8") as f:
            meta = json.load(f)

        aid   = str(meta.get("article_id") or Path(fname).stem)
        title = meta.get("title") or f"Untitled {aid}"
        overview = meta.get("overview") or ""
        body = meta.get("body") or ""
        category = meta.get("category") or None
        author = meta.get("generator") or None  # if you store real author elsewhere, swap this
        ts = parse_timestamp(meta.get("timestamp"))

        # Public URL for the article page:
        # Prefer an explicit site path builder (knowing how templater lays things out),
        # else default to /<article_id>/.
        if site_subpath_builder:
            subpath = site_subpath_builder(meta)
        else:
            subpath = f"{aid}/"
        url = f"{base_url.rstrip('/')}/{subpath.lstrip('/')}"

        image_url = f"{base_url.rstrip('/')}/static/img/{aid}.webp"

        # Description for RSS: prefer overview; fall back to a body preview.
        description = overview if overview else (body[:200] + "…") if body else "Read on at Rat News Network."

        items.append({
            "title": title,
            "url": url,
            "pub_date_rfc822": rfc822(ts),
            "description": description,
            "body_html": para_wrap(body),  # safe, minimal HTML
            "image_url": image_url,
            "category": category,
            "author": author,
            "published_dt": ts,
        })

    items.sort(key=lambda x: x["published_dt"], reverse=True)
    return items[:limit]


def render_feed(TEMPLATES_DIR, template_name: str, base_url: str, site_dir: str, items):
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(enabled_extensions=("xml", "html"))
    )

    xml = env.get_template(template_name).render(
        base_url=base_url,
        now_rfc822=rfc822(datetime.now(timezone.utc)),
        items=items,
    )
    out = os.path.join(site_dir, "feed.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write(xml)
    return out
