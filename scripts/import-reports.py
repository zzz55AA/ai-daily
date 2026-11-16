#!/usr/bin/env python3
"""Import scrubbed AI daily HTML into the archive.

One-time backfill helper. It does not publish on a schedule.
When several files share a date, the newest file mtime is kept.
Files that still contain private contact data, local paths, or secrets
are refused and left unpublished.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://zzz55aa.github.io/ai-daily"
CANONICAL_RE = re.compile(r"^[0-9]{4}/[0-9]{2}/[0-9]{2}\.html$")
DATE_RE = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日(?:\s*(星期[一二三四五六日]))?")
PRIVATE = [
    re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    re.compile(r"/Users/"),
    re.compile(r"/home/ubuntu"),
    re.compile(r"/opt/cursor"),
    re.compile(r"TubeAlfred\s*积分"),
    re.compile(r"盒子浏览器"),
    re.compile(r"已登录浏览器"),
    re.compile(r"x_accounts\.txt"),
    re.compile(r"x_official_links\.json"),
    re.compile(r"sitemaps/snap\.sh"),
    re.compile(r"(?<![\w./])ff\.py\b"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
]


def strip_images(html: str) -> str:
    return re.sub(r"data:image/[^)\s\"']+", "", html)


def privacy_hits(html: str) -> list[str]:
    text = strip_images(html)
    hits = []
    for pattern in PRIVATE:
        found = pattern.findall(text)
        if found:
            sample = found[0]
            hits.append(f"{pattern.pattern} ({sample[:80]})")
    return hits


def text_of(html: str, class_name: str) -> str:
    match = re.search(rf'class="{class_name}"[^>]*>(.*?)</', html, re.S)
    if not match:
        return ""
    return unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()


def parse_report(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    html = strip_images(raw)
    date_text = text_of(html, "date")
    match = DATE_RE.search(date_text) or DATE_RE.search(html)
    if not match:
        raise ValueError("no issue date")
    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
    weekday = match.group(4) or ""
    meta = text_of(html, "meta")
    issue_match = re.search(r"第\s*(\d+)\s*期", meta)
    count_match = re.search(r"共\s*(\d+)\s*条", meta)
    if not issue_match:
        raise ValueError("no issue number")
    highlights = []
    section = re.search(r'<section class="hl">(.*?)</section>', html, re.S)
    if section:
        for item in re.finditer(
            r'<a href="#([^"]+)"[^>]*>.*?<span class="n">(\d+)</span>.*?</span>(.*?)</a>',
            section.group(1),
            re.S,
        ):
            title = unescape(re.sub(r"<[^>]+>", "", item.group(3))).strip()
            if title:
                highlights.append({"n": item.group(2), "id": item.group(1), "title": title})
    count = int(count_match.group(1)) if count_match else html.count('class="item"')
    iso = f"{year:04d}-{month:02d}-{day:02d}"
    return {
        "raw": raw,
        "date": iso,
        "year": year,
        "month": month,
        "day": day,
        "weekday": weekday,
        "issue": int(issue_match.group(1)),
        "count": count,
        "window": text_of(html, "win"),
        "title": date_text or f"{year}年{month}月{day}日",
        "path": f"{year:04d}/{month:02d}/{day:02d}.html",
        "summary": text_of(html, "summary") or text_of(html, "lede"),
        "highlights": highlights,
        "mtime": path.stat().st_mtime,
        "source": str(path),
    }


def prepare_html(raw: str, public_url: str) -> str:
    html = re.sub(r'<link rel="canonical"[^>]*>', "", raw)
    html = re.sub(r'<script src="(?:\.\./)*archive\.js"></script>', "", html)
    html = re.sub(r'href="(?:\.\./)*index\.html"', 'href="../../index.html"', html, count=1)
    if "</head>" not in html or "</body>" not in html:
        raise ValueError("report is missing head or body")
    html = html.replace("</head>", f'<link rel="canonical" href="{public_url}"></head>', 1)
    html = html.replace("</body>", '<script src="../../archive.js"></script></body>', 1)
    return html


def redirect_html(date: str, target: str, issue: int) -> str:
    label = date.replace("-", "年", 1).replace("-", "月", 1) + "日"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 科技日报 · {label}</title>
<link rel="canonical" href="{SITE}/{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}"+location.hash+location.search);</script>
</head>
<body>
<p><a href="{target}">继续阅读 {label} · 第 {issue} 期</a></p>
</body>
</html>
"""


def short_week(value: str) -> str:
    return value.replace("星期", "周")


def render_homepage(issues: list[dict]) -> None:
    page = ROOT / "index.html"
    html = page.read_text(encoding="utf-8")
    newest = issues[0]
    oldest = issues[-1]
    description = (
        f"AI 科技日报档案。已发布 {len(issues)} 期，"
        f"第 {oldest['issue']} 期至第 {newest['issue']} 期。"
    )
    html = re.sub(
        r'(<meta name="description" content=")[^"]*(">)',
        rf"\1{escape(description, quote=True)}\2",
        html,
        count=1,
    )
    blocks = []
    current_month = None
    for issue in issues:
        key = (issue["year"], issue["month"])
        if key != current_month:
            current_month = key
            blocks.append(f'  <p class="month-h">{issue["year"]}年{issue["month"]}月</p>')
        href = issue["path"]
        points = ""
        if issue["highlights"]:
            items = "\n".join(
                f'          <li><a href="{href}#{escape(item["id"], quote=True)}">{escape(item["title"])}</a></li>'
                for item in issue["highlights"]
            )
            points = (
                '\n      <details class="points">\n'
                f'        <summary>今日要点 {len(issue["highlights"])} 条</summary>\n'
                f"        <ol>\n{items}\n        </ol>\n"
                "      </details>"
            )
        window = f'\n      <p class="meta">{escape(issue["window"])}</p>' if issue["window"] else ""
        summary = f'\n      <p class="summary">{escape(issue["summary"])}</p>' if issue["summary"] else ""
        blocks.append(
            "  <article class=\"issue\">\n"
            f'    <a class="dateblock" href="{href}"><span class="big">{issue["day"]}</span>'
            f'<span class="sub">{escape(short_week(issue["weekday"]))}</span></a>\n'
            "    <div>\n"
            f'      <p class="kicker">第 {issue["issue"]} 期 · {issue["count"]} 条</p>\n'
            f'      <h2><a href="{href}">{issue["year"]}年{issue["month"]}月{issue["day"]}日</a></h2>'
            f"{window}{summary}{points}\n"
            "    </div>\n"
            "  </article>"
        )
    # Title in the card is the date line without forcing a split.
    main = "<main id=\"archive-list\">\n" + "\n".join(blocks) + "\n</main>"
    html = re.sub(r"<main\b[^>]*>.*?</main>", main, html, count=1, flags=re.S)
    example = newest["date"] + ".html"
    foot = (
        '<footer class="foot" id="archive-foot">\n'
        f"  <p>已发布 {len(issues)} 期。日期地址（例如 "
        f'<a href="{example}">{example}</a>）会打开对应的日期页。</p>\n'
        "</footer>"
    )
    html = re.sub(r'<footer class="foot".*?</footer>', foot, html, count=1, flags=re.S)
    page.write_text(html, encoding="utf-8")


def collect_inputs(extra: list[str], from_tree: bool) -> list[Path]:
    found: list[Path] = []
    if from_tree:
        for path in ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].html"):
            found.append(path)
    for item in extra:
        path = Path(item)
        if path.is_dir():
            found.extend(sorted(path.rglob("*.html")))
        elif path.is_file():
            found.append(path)
        else:
            raise SystemExit(f"missing input: {item}")
    unique = []
    seen = set()
    for path in found:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def choose_latest(reports: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for report in reports:
        current = grouped.get(report["date"])
        if current is None or report["mtime"] > current["mtime"]:
            if current is not None:
                print(f"keep newer {report['date']}: {report['source']}", file=sys.stderr)
            grouped[report["date"]] = report
        else:
            print(f"skip older {report['date']}: {report['source']}", file=sys.stderr)
    return sorted(grouped.values(), key=lambda item: item["date"], reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import scrubbed daily reports into the archive.")
    parser.add_argument("inputs", nargs="*", help="HTML files or directories of scrubbed reports")
    parser.add_argument("--from-tree", action="store_true", help="include reports already stored at YYYY/MM/DD.html")
    args = parser.parse_args()
    if not args.inputs and not args.from_tree:
        parser.error("pass report files or --from-tree")

    refused = []
    parsed = []
    for path in collect_inputs(args.inputs, args.from_tree):
        try:
            report = parse_report(path)
        except ValueError as exc:
            print(f"skip {path}: {exc}", file=sys.stderr)
            continue
        hits = privacy_hits(report["raw"])
        if hits:
            refused.append((str(path), hits))
            continue
        parsed.append(report)
    if refused:
        for path, hits in refused:
            print(f"refused {path}: {'; '.join(hits)}", file=sys.stderr)
        print("refused files were not written", file=sys.stderr)
        return 2
    if not parsed and not args.from_tree:
        print("no reports imported", file=sys.stderr)
        return 1

    existing = []
    for path in sorted(ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].html")):
        if any(Path(item["source"]).resolve() == path.resolve() for item in parsed):
            continue
        try:
            report = parse_report(path)
        except ValueError:
            continue
        hits = privacy_hits(report["raw"])
        if hits:
            refused.append((str(path), hits))
            continue
        existing.append(report)
    if refused:
        for path, hits in refused:
            print(f"refused {path}: {'; '.join(hits)}", file=sys.stderr)
        return 2

    chosen = choose_latest(parsed + existing)
    if not chosen:
        print("no reports to publish", file=sys.stderr)
        return 1

    for report in chosen:
        target = ROOT / report["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        public = f"{SITE}/{report['path']}"
        target.write_text(prepare_html(report["raw"], public), encoding="utf-8")
        legacy = ROOT / f"{report['date']}.html"
        legacy.write_text(redirect_html(report["date"], report["path"], report["issue"]), encoding="utf-8")
        report["path"] = report["path"]

    index = {
        "publication": "AI 科技日报",
        "issues": [
            {
                "date": item["date"],
                "year": item["year"],
                "month": item["month"],
                "day": item["day"],
                "weekday": item["weekday"],
                "issue": item["issue"],
                "count": item["count"],
                "window": item["window"],
                "title": item["title"],
                "path": item["path"],
                "summary": item["summary"],
                "highlights": item["highlights"],
            }
            for item in chosen
        ],
    }
    (ROOT / "archive" / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    render_homepage(chosen)
    print(f"imported {len(chosen)} issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
