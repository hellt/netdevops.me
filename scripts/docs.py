"""Prepare the blog features not yet implemented by Zensical.

Authoring stays in blog/ and mkdocs.yml. Only disposable staging files change.
"""

import argparse
from datetime import date, datetime, timezone
from email.utils import format_datetime
import html
import math
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
import threading
from urllib.parse import quote, unquote, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import markdown
from pymdownx.slugs import slugify
from watchfiles import watch
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "blog"
STAGE = ROOT / ".build/docs"
CONFIG = ROOT / ".mkdocs-generated.yml"


def frontmatter(text):
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    return (yaml.safe_load(match[1]) or {}, text[match.end():]) if match else ({}, text)


def as_datetime(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if not isinstance(value, (date, datetime)):
        raise ValueError(f"Invalid post date: {value!r}")
    if not isinstance(value, datetime):
        value = datetime.combine(value, datetime.min.time())
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def git_dates(path):
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%aI", "--", str(path)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    return (as_datetime(result[-1]), as_datetime(result[0])) if result else (None, None)


def read_posts(preview=False):
    posts = []
    defaults = yaml.safe_load((SOURCE / ".meta.yml").read_text()) or {}
    for source in sorted((SOURCE / "posts").rglob("*.md")):
        meta, body = frontmatter(source.read_text())
        meta = defaults | meta
        dates = meta["date"]
        created = as_datetime(dates.get("created") if isinstance(dates, dict) else dates)
        heading = re.search(r"^#\s+(.+)$", body, re.M)
        title = meta.get("title") or (heading[1] if heading else source.stem)
        title = BeautifulSoup(markdown.markdown(title), "html.parser").get_text()
        slug = meta.get("slug") or slugify(case="lower")(title, "-")
        if not slug or "/" in slug or slug in {".", ".."}:
            raise ValueError(f"Invalid slug in {source}: {slug!r}")
        url = f"{created.year}/{slug}/"
        _, modified = git_dates(source)
        updated = as_datetime(dates["updated"]) if isinstance(dates, dict) and dates.get("updated") else modified or created
        posts.append(dict(source=source.relative_to(SOURCE).as_posix(), meta=meta,
                          body=body, title=title, url=url, created=created,
                          updated=max(created, updated), draft=bool(meta.get("draft"))))
    urls = [p["url"] for p in posts]
    if len(urls) != len(set(urls)):
        raise ValueError("Duplicate blog post URLs")
    return sorted((p for p in posts if preview or not p["draft"]),
                  key=lambda p: (bool(p["meta"].get("pin")), p["created"]), reverse=True)


def rewrite_links(body, source, destinations):
    """Rewrite existing local destinations, leaving fenced code untouched."""
    def resolve(value):
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or not parts.path:
            return value
        path = unquote(parts.path)
        key = posixpath.normpath(path.lstrip("/") if path.startswith("/") else
                                 posixpath.join(posixpath.dirname(source), path))
        if key not in destinations:
            return value
        return urlunsplit(("", "", "/" + quote(destinations[key], safe="/"), parts.query, parts.fragment))

    # Inline links/images, reference definitions, and HTML href/src attributes.
    pattern = re.compile(r'(\]\(<?)([^\s)>]+)|(^\s*\[[^\]]+\]:\s*<?)([^\s>]+)|((?:href|src)=["\'])([^"\']+)', re.M)
    def replace(match):
        groups = match.groups()
        for i in (0, 2, 4):
            if groups[i] is not None:
                return groups[i] + resolve(groups[i + 1])

    fence = None
    lines = []
    for line in body.splitlines(keepends=True):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            lines.append(line)
        else:
            lines.append(line if fence else pattern.sub(replace, line))
    return "".join(lines)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text() != content:
        path.write_text(content)


def page(meta, body):
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n" + body


def excerpt(post, number):
    body = post["body"].split("<!-- more -->", 1)[0]
    body = re.sub(r"^#\s+.+\n", "", body, count=1, flags=re.M)
    # Definitions often live after the excerpt separator. Isolate labels so that
    # two posts using e.g. [github] don't share destinations on an index page.
    definitions = re.findall(r"^ {0,3}\[([^\]^]+)\]:\s*(.+)$", post["body"], re.M)
    body = re.sub(r"^ {0,3}\[[^\]^]+\]:[^\n]*\n?", "", body, flags=re.M)
    for label, destination in definitions:
        renamed = f"post-{number}-{label}"
        escaped = re.escape(label)
        body = re.sub(r"(\[[^\]\n]+\])\[" + escaped + r"\]", lambda m: m[1] + f"[{renamed}]", body, flags=re.I)
        body = re.sub(r"\[" + escaped + r"\](?![\[(])", lambda m: m[0] + f"[{renamed}]", body, flags=re.I)
        body += f"\n[{renamed}]: {destination}\n"
    return body


def feeds(posts, config):
    """Stable feed URLs and GUIDs, with plain text abstracts (up to 5000 chars)."""
    base = config["site_url"]
    for kind, field in (("created", "created"), ("updated", "updated")):
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        for key, value in (("title", config["site_name"]), ("link", base),
                           ("description", config["site_description"])):
            ET.SubElement(channel, key).text = value
        for post in sorted(posts, key=lambda p: p[field], reverse=True)[:20]:
            item = ET.SubElement(channel, "item")
            url = base.rstrip("/") + "/" + quote(post["url"], safe="/")
            abstract = BeautifulSoup(markdown.markdown(post["body"]), "html.parser").get_text(" ", strip=True)[:5000]
            for key, value in (("title", post["title"]), ("link", url), ("guid", url),
                               ("pubDate", format_datetime(post[field])),
                               ("description", abstract), ("comments", url + "#__comments")):
                ET.SubElement(item, key).text = value
            for tag in post["meta"].get("tags", []):
                ET.SubElement(item, "category").text = str(tag)
        yield f"feed_rss_{kind}.xml", ET.tostring(rss, encoding="unicode", xml_declaration=True)


def prepare(preview=False):
    # Keep YAML tags intact in the inherited configuration; read only plain values here.
    text = (ROOT / "mkdocs.yml").read_text()
    class Loader(yaml.SafeLoader):
        pass
    Loader.add_multi_constructor("tag:yaml.org,2002:python/name:", lambda loader, suffix, node: suffix)
    config = yaml.load(text, Loader=Loader)
    posts = read_posts(preview)
    destinations = {p["source"]: p["url"] for p in posts}
    assets = []
    for path in SOURCE.rglob("*"):
        if not path.is_file() or "overrides" in path.parts or path.name.startswith(".") or path.name.startswith("htmltest"):
            continue
        key = path.relative_to(SOURCE).as_posix()
        if key.startswith("posts/") and path.suffix == ".md":
            continue
        dest = key.removeprefix("posts/")
        destinations[key] = (dest[:-3] + "/").replace("index/", "") if path.suffix == ".md" else dest
        assets.append((path, dest))
    expected = set()
    for path, dest in assets:
        target = STAGE / dest
        expected.add(target)
        if path.suffix == ".md":
            meta, body = frontmatter(path.read_text())
            created, updated = git_dates(path)
            if os.getenv("CI", "").lower() == "true" and created:
                meta.update(git_creation_date_localized=created.strftime("%B %d, %Y"),
                            git_revision_date_localized=updated.strftime("%B %d, %Y"))
            write(target, page(meta, rewrite_links(body, path.relative_to(SOURCE).as_posix(), destinations)))
        elif not target.exists() or path.read_bytes() != target.read_bytes():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    # Native meta plugin still supplies inherited comments/authors for all pages.
    for path in SOURCE.rglob(".meta.yml"):
        target = STAGE / path.relative_to(SOURCE)
        expected.add(target)
        write(target, path.read_text())
    authors = yaml.safe_load((SOURCE / ".authors.yml").read_text())["authors"]
    templates = Environment(
        loader=FileSystemLoader(SOURCE / "overrides"), autoescape=True,
        trim_blocks=True, lstrip_blocks=True,
    )
    metadata_template = templates.get_template("partials/post-meta.html")
    pagination_template = templates.get_template("partials/pagination.html")
    for post in posts:
        meta = post["meta"].copy()
        meta.update(title=post["title"], template="post.html",
                    source_path=post["source"], published=post["created"].strftime("%B %d, %Y"),
                    post_authors=[authors[a] for a in meta.get("authors", [])],
                    readtime=max(1, math.ceil(len(post["body"].split()) / 265)))
        post["display_meta"] = meta
        if os.getenv("CI", "").lower() == "true":
            created, updated = git_dates(SOURCE / post["source"])
            if created:
                meta.update(git_creation_date_localized=created.strftime("%B %d, %Y"),
                            git_revision_date_localized=updated.strftime("%B %d, %Y"))
        target = STAGE / (post["url"].rstrip("/") + ".md")
        expected.add(target)
        post["body"] = rewrite_links(post["body"], post["source"], destinations)
        write(target, page(meta, post["body"]))
    count = max(1, math.ceil(len(posts) / 10))
    for number in range(1, count + 1):
        body = ""
        for index, post in enumerate(posts[(number - 1) * 10:number * 10]):
            title = html.escape(post["title"])
            body += f'## <a href="/{quote(post["url"], safe="/")}">{title}</a>\n\n'
            body += metadata_template.render(post_meta=post["display_meta"]) + "\n\n"
            body += excerpt(post, index) + f'\n\n[Continue reading](/{quote(post["url"], safe="/")})\n\n---\n\n'
        body += pagination_template.render(current=number, total=count)
        target = STAGE / ("index.md" if number == 1 else f"page/{number}.md")
        expected.add(target)
        write(target, page(dict(title="Blog", template="blog.html", hide=["navigation", "toc"], comments=False), body))
    for name, content in feeds(posts, config):
        target = STAGE / name
        expected.add(target)
        write(target, content)
    for path in STAGE.rglob("*"):
        if path.is_file() and path not in expected:
            path.unlink()
    urls = sorted({destinations[p["source"]] for p in posts} |
                  {destinations[path.relative_to(SOURCE).as_posix()] for path, _ in assets if path.suffix == ".md"} |
                  {f"page/{n}/" for n in range(2, count + 1)})
    generated = dict(INHERIT="mkdocs.yml", docs_dir=".build/docs", site_dir="site",
                     extra=dict(sitemap_urls=[config["site_url"].rstrip("/") + "/" + quote(url, safe="/") for url in urls]))
    write(CONFIG, "# Generated by scripts/docs.py; edit mkdocs.yml instead.\n" + yaml.safe_dump(generated))
    print(f'Prepared {len(posts)} posts ({"preview, including drafts" if preview else "production"}).', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "serve"])
    parser.add_argument("--address", default="127.0.0.1:8002")
    args = parser.parse_args()
    os.chdir(ROOT)
    prepare(preview=args.command == "serve")
    command = [sys.executable, "-m", "zensical", args.command, "-f", str(CONFIG)]
    if args.command == "build":
        # Zensical --clean clears its cache; remove output too to avoid stale drafts.
        shutil.rmtree(ROOT / "site", ignore_errors=True)
        subprocess.run(command + ["--clean", "--strict"], check=True)
        (ROOT / "site/.nojekyll").touch()
        return
    stop = threading.Event()
    def refresh():
        for _ in watch(SOURCE, ROOT / "macros", ROOT / "mkdocs.yml", stop_event=stop):
            try:
                prepare(preview=True)
            except Exception as error:
                print(f"Preview preparation failed: {error}", file=sys.stderr, flush=True)
    worker = threading.Thread(target=refresh, daemon=True)
    worker.start()
    try:
        subprocess.run(command + ["--dev-addr", args.address], check=True)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        worker.join(timeout=5)


if __name__ == "__main__":
    main()
