#!/usr/bin/env python3
"""Import scrubbed AI daily reports into the archive.

One-time backfill helper. It does not publish on a schedule.
The inventory manifest names the chosen file for each report. File mtime
is never used. Reports are not dropped because they share a calendar day.
Markdown and PDF sources are kept and reported until a conversion is specified.
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
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
# Categories only. Matched text is never printed.
BLOCKING = {
    "local_path": re.compile(r"/Users/|/home/ubuntu|/opt/cursor"),
    "private_workflow": re.compile(r"TubeAlfred\s*积分|盒子浏览器|已登录浏览器|x_accounts\.txt|x_official_links\.json|sitemaps/snap\.sh|(?<![\w./])ff\.py\b"),
    "recipient": re.compile(r"收件人|邮件收件|投递记录|投递日志|\b(?:To|Cc|Bcc)\s*:"),
    "secret": re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
}
# The manifest must name these exact finals. Another file is never substituted.
REQUIRED = {
    "2026-11-08": {"count": 83, "label": "83-item final"},
    "2026-11-10": {"count": 61, "contains": "Anthropic", "label": "61-item Anthropic-added final"},
}


def strip_images(html: str) -> str:
    return re.sub(r"data:image/[^)\s\"']+", "", html)


def privacy_findings(html: str) -> list[dict]:
    """Report categories and counts only. Never return matched secret text."""
    text = strip_images(html)
    findings = []
    emails = EMAIL_RE.findall(text)
    if emails:
        findings.append({
            "kind": "email",
            "count": len(emails),
            "blocking": False,
            "note": "address not printed; a public author address can stay",
        })
    for kind, pattern in BLOCKING.items():
        count = len(pattern.findall(text))
        if count:
            findings.append({
                "kind": kind,
                "count": count,
                "blocking": True,
                "note": "matched text not printed",
            })
    return findings


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


def load_manifest(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("reports") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise SystemExit("manifest needs a non-empty reports list")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("id") or not entry.get("file"):
            raise SystemExit("each manifest report needs id and file")
        if entry["id"] in seen:
            raise SystemExit(f"duplicate manifest id {entry['id']}")
        seen.add(entry["id"])
    return entries


def requirement_for(entry: dict, report: dict | None) -> dict | None:
    if (entry.get("kind") or "daily") == "range":
        return None
    date = str(entry.get("date") or (report["date"] if report else ""))
    return REQUIRED.get(date)


def output_path(entry: dict, report: dict | None) -> str:
    if entry.get("path"):
        return str(entry["path"]).lstrip("/")
    if report is None:
        return f"sources/{entry['id']}"
    kind = entry.get("kind") or "daily"
    if kind == "range":
        return f"{report['year']:04d}/{report['month']:02d}/{report['day']:02d}/{entry['id']}.html"
    return report["path"]


def describe_findings(entry_id: str, findings: list[dict]) -> None:
    for finding in findings:
        print(
            f"finding {entry_id}: {finding['kind']} count={finding['count']} "
            f"blocking={finding['blocking']} ({finding['note']})",
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Import the manifest's chosen reports into the archive.")
    parser.add_argument("--manifest", required=True, help="JSON inventory whose file field is the chosen version")
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    entries = load_manifest(manifest_path)
    base = manifest_path.parent
    planned = []
    holdings = []
    blocked = False

    for entry in entries:
        source = Path(entry["file"])
        if not source.is_absolute():
            source = base / source
        if not source.is_file():
            print(f"missing chosen file for {entry['id']}: {entry['file']}", file=sys.stderr)
            blocked = True
            continue
        suffix = source.suffix.lower()
        if suffix in {".md", ".pdf"}:
            holdings.append({"id": entry["id"], "file": str(source), "suffix": suffix})
            print(
                f"hold {entry['id']}: {suffix} source kept, conversion not specified, file not dropped",
                file=sys.stderr,
            )
            continue
        if suffix not in {".html", ".htm"}:
            print(
                f"hold {entry['id']}: {suffix or 'unknown'} source kept, conversion not specified",
                file=sys.stderr,
            )
            holdings.append({"id": entry["id"], "file": str(source), "suffix": suffix or "unknown"})
            continue
        try:
            report = parse_report(source)
        except ValueError as exc:
            print(f"hold {entry['id']}: chosen HTML could not be read ({exc}); not replaced or dropped", file=sys.stderr)
            blocked = True
            continue
        findings = privacy_findings(report["raw"])
        describe_findings(entry["id"], findings)
        if any(item["blocking"] for item in findings):
            print(f"hold {entry['id']}: approved report not published and not silently skipped", file=sys.stderr)
            blocked = True
            continue
        rule = requirement_for(entry, report)
        if rule:
            text = strip_images(report["raw"])
            if report["count"] != rule["count"] or (
                rule.get("contains") and rule["contains"] not in text
            ):
                print(
                    f"reject {entry['id']}: chosen file is not the {rule['label']}; no other version was substituted",
                    file=sys.stderr,
                )
                blocked = True
                continue
        report["id"] = entry["id"]
        report["kind"] = entry.get("kind") or "daily"
        report["path"] = output_path(entry, report)
        report["legacy"] = entry.get("legacy")
        planned.append(report)

    if blocked:
        print("import stopped; no archive files were written", file=sys.stderr)
        return 2

    paths = [item["path"] for item in planned]
    if len(paths) != len(set(paths)):
        print("two chosen reports resolve to the same path; neither was dropped", file=sys.stderr)
        for item in planned:
            print(f"  {item['id']} -> {item['path']}", file=sys.stderr)
        return 2

    legacy_owner: dict[str, str] = {}
    for item in planned:
        if item["kind"] == "range":
            continue
        legacy = item["legacy"] or f"{item['date']}.html"
        previous = legacy_owner.get(legacy)
        if previous:
            print(
                f"legacy {legacy} is needed by {previous} and {item['id']}; set an explicit legacy and path",
                file=sys.stderr,
            )
            return 2
        legacy_owner[legacy] = item["id"]
        item["legacy_name"] = legacy

    # Preserve reports already on the site when this manifest does not mention them.
    for path in sorted(ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].html")):
        try:
            current = parse_report(path)
        except ValueError:
            continue
        if any(item["path"] == current["path"] for item in planned):
            continue
        current["id"] = current["date"]
        current["kind"] = "daily"
        current["legacy_name"] = f"{current['date']}.html"
        planned.append(current)

    for item in holdings:
        source = Path(item["file"])
        dest = ROOT / "sources" / item["id"] / source.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())

    for report in planned:
        if "raw" not in report:
            continue
        target = ROOT / report["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        public = f"{SITE}/{report['path']}"
        target.write_text(prepare_html(report["raw"], public), encoding="utf-8")
        if report.get("legacy_name"):
            legacy = ROOT / report["legacy_name"]
            legacy.write_text(
                redirect_html(report["date"], report["path"], report["issue"]),
                encoding="utf-8",
            )

    html_issues = [item for item in planned if item.get("issue")]
    html_issues.sort(key=lambda item: (item["date"], item["path"]), reverse=True)
    index = {
        "publication": "AI 科技日报",
        "issues": [
            {
                "id": item.get("id") or item["date"],
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
                "kind": item.get("kind") or "daily",
            }
            for item in html_issues
        ],
        "holdings": [
            {"id": item["id"], "suffix": item["suffix"], "kept": True, "converted": False}
            for item in holdings
        ],
    }
    (ROOT / "archive" / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if html_issues:
        render_homepage(html_issues)
    print(f"imported {len(html_issues)} html reports; held {len(holdings)} non-html sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
