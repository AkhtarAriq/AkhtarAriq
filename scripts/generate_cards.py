#!/usr/bin/env python3
"""Build self-contained GitHub profile SVGs from public repository data."""

from __future__ import annotations

import argparse
import html
import json
import os
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


INK = "#090A12"
WHITE = "#F5F6FA"
MUTED = "#B8BBD1"
FAINT = "#858AA4"
BLUE = "#5B8DEF"
VIOLET = "#8B5CF6"
PINK = "#E879B9"
COLORS = (BLUE, VIOLET, PINK, "#8AC7FA", "#B8A3FF")


def _public(repo: dict) -> bool:
    return (
        not repo.get("private", False)
        and not repo.get("fork", False)
        and not repo.get("archived", False)
        and repo.get("name", "").lower() != "akhtarariq"
    )


def _escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _short(value: object, length: int) -> str:
    text = str(value or "").strip()
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"


def summarize_languages(repos: list[dict], languages_by_repo: dict) -> list[dict]:
    """Percent of public, owned, non-fork source bytes per language."""
    counts: Counter[str] = Counter()
    for repo in repos:
        if not _public(repo):
            continue
        for language, count in languages_by_repo.get(repo["full_name"], {}).items():
            if isinstance(count, (int, float)) and count > 0:
                counts[language] += int(count)
    total = sum(counts.values())
    if total == 0:
        return []
    return [
        {"name": name, "bytes": amount, "percentage": amount * 100 / total}
        for name, amount in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def select_projects(repos: list[dict], pinned_names: list[str], limit: int = 4) -> list[dict]:
    """Use public pinned repositories first, then latest public repositories."""
    public = {repo["full_name"].lower(): repo for repo in repos if _public(repo)}
    result: list[dict] = []
    seen: set[str] = set()
    for name in pinned_names:
        key = name.lower()
        if key in public and key not in seen:
            result.append(public[key])
            seen.add(key)
    for repo in sorted(public.values(), key=lambda item: item.get("pushed_at") or "", reverse=True):
        key = repo["full_name"].lower()
        if key not in seen:
            result.append(repo)
            seen.add(key)
    return result[:limit]


def _background(width: int, height: int) -> str:
    return f"""
  <defs>
    <linearGradient id="spectrum" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{BLUE}"/>
      <stop offset="55%" stop-color="{VIOLET}"/>
      <stop offset="100%" stop-color="{PINK}"/>
    </linearGradient>
    <radialGradient id="nebula"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".23"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
    <linearGradient id="subtle" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="#111522"/><stop offset="100%" stop-color="#0C0F18"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="22" fill="{INK}" stroke="#383651" stroke-width="2"/>
  <ellipse cx="{width-80}" cy="28" rx="280" ry="190" fill="url(#nebula)"/>
  <path d="M 24 2 H {width-24}" stroke="url(#spectrum)" stroke-width="3" opacity=".9"/>
"""


def _svg(width: int, height: int, label: str, content: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="asset-title asset-desc">\n'
        f'  <title id="asset-title">{_escape(label)}</title>\n'
        f'  <desc id="asset-desc">Live GitHub profile data from public repositories, refreshed daily.</desc>\n'
        + content
        + "\n</svg>\n"
    )


def render_language_svg(languages: list[dict], repo_count: int, updated: str, mobile: bool = False) -> str:
    width, height = (520, 674) if mobile else (1080, 516)
    left = 32 if mobile else 58
    parts = [_background(width, height)]
    title_size = 31 if mobile else 43
    parts.append(f'<text x="{left}" y="{76 if mobile else 82}" fill="{WHITE}" font-size="{title_size}" font-weight="750" font-family="Arial, sans-serif">Technical toolkit</text>')
    parts.append(f'<text x="{left}" y="{111 if mobile else 118}" fill="{MUTED}" font-size="{17 if mobile else 19}" font-family="Arial, sans-serif">Language mix · public source code</text>')
    parts.append(f'<path d="M {left} {137 if mobile else 143} H {width-left}" stroke="#333A52"/>')
    if not languages:
        parts.append(f'<text x="{left}" y="{202 if mobile else 218}" fill="{WHITE}" font-size="{25 if mobile else 28}" font-weight="700" font-family="Arial, sans-serif">Awaiting first live sync</text>')
        parts.append(f'<text x="{left}" y="{242 if mobile else 255}" fill="{MUTED}" font-size="{16 if mobile else 19}" font-family="Arial, sans-serif">Run the profile workflow to load your language mix.</text>')
        for i, shade in enumerate((BLUE, VIOLET, PINK)):
            bar_y = (295 if mobile else 309) + i * 58
            parts.append(f'<rect x="{left}" y="{bar_y}" width="{width-2*left}" height="13" rx="6.5" fill="#272B3B"/>')
            parts.append(f'<rect x="{left}" y="{bar_y}" width="{85+i*30}" height="13" rx="6.5" fill="{shade}" opacity=".24"/>')
    for index, lang in enumerate(languages[:5]):
        label = _escape(_short(lang["name"], 25 if mobile else 28))
        percent = max(0.0, min(100.0, float(lang["percentage"])))
        color = COLORS[index % len(COLORS)]
        if mobile:
            y = 193 + index * 86
            bar_x, bar_w, bar_y = left, width - left * 2, y + 22
            parts.extend([
                f'<circle cx="{left+7}" cy="{y-6}" r="6" fill="{color}"/>',
                f'<text x="{left+23}" y="{y}" fill="{WHITE}" font-size="20" font-weight="650" font-family="Arial, sans-serif">{label}</text>',
                f'<text x="{width-left}" y="{y}" fill="{color}" text-anchor="end" font-size="20" font-weight="700" font-family="Arial, sans-serif">{percent:.1f}%</text>',
            ])
        else:
            y = 201 + index * 52
            bar_x, bar_w, bar_y = 448, 550, y - 16
            parts.extend([
                f'<circle cx="{left+7}" cy="{y-7}" r="6" fill="{color}"/>',
                f'<text x="{left+23}" y="{y}" fill="{WHITE}" font-size="20" font-weight="650" font-family="Arial, sans-serif">{label}</text>',
                f'<text x="423" y="{y}" fill="{color}" text-anchor="end" font-size="20" font-weight="700" font-family="Arial, sans-serif">{percent:.1f}%</text>',
            ])
        fill_w = bar_w * percent / 100
        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="11" rx="5.5" fill="#282D3B"/>')
        if fill_w > 0:
            parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{fill_w:.2f}" height="11" rx="5.5" fill="{color}"/>')
    footer_y = height - 37
    parts.append(f'<path d="M {left} {footer_y-28} H {width-left}" stroke="#333A52"/>')
    repo_label = "scanned" if languages else "found"
    parts.append(f'<text x="{left}" y="{footer_y}" fill="{FAINT}" font-size="{14 if mobile else 16}" font-family="Arial, sans-serif">{repo_count} public repositories {repo_label}</text>')
    parts.append(f'<text x="{width-left}" y="{footer_y}" fill="{FAINT}" text-anchor="end" font-size="{13 if mobile else 16}" font-family="Arial, sans-serif">{_escape(updated)}</text>')
    return _svg(width, height, "Live language mix", "\n".join(parts))


def _date(value: str | None) -> str:
    try:
        return datetime.fromisoformat((value or "").replace("Z", "+00:00")).strftime("%d %b %Y")
    except ValueError:
        return "Date unavailable"


def _project_card(repo: dict, x: int, y: int, width: int, height: int, mobile: bool) -> str:
    title = _escape(_short(repo.get("name") or "Untitled repository", 26 if mobile else 30))
    description = str(repo.get("description") or "No description provided.").strip()
    lines = textwrap.wrap(description, width=43 if mobile else 40, break_long_words=True, break_on_hyphens=False)[:2]
    if len(description) > sum(len(line) for line in lines) + 2 and lines:
        lines[-1] = _short(lines[-1], len(lines[-1]) - 1)
    color = BLUE if (repo.get("language") or "").lower() == "typescript" else VIOLET
    tag = _escape(_short(repo.get("language") or "Mixed stack", 22))
    parts = [
        f'<g class="project-card">',
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="15" fill="url(#subtle)" stroke="#45415F" stroke-width="1.5"/>',
        f'<path d="M {x+1} {y+48} H {x+width-1}" stroke="#343A54"/>',
        f'<circle cx="{x+25}" cy="{y+26}" r="5" fill="{color}"/>',
        f'<text x="{x+41}" y="{y+32}" fill="{MUTED}" font-size="{15 if mobile else 15}" font-family="monospace">REPOSITORY / PUBLIC</text>',
        f'<text x="{x+25}" y="{y+87}" fill="{WHITE}" font-size="{23 if mobile else 24}" font-weight="750" font-family="Arial, sans-serif">{title}</text>',
    ]
    for i, line in enumerate(lines):
        parts.append(f'<text x="{x+25}" y="{y+122+i*23}" fill="{MUTED}" font-size="{18 if mobile else 17}" font-family="Arial, sans-serif">{_escape(line)}</text>')
    parts += [
        f'<rect x="{x+25}" y="{y+height-51}" width="{min(208,max(125,len(tag)*12+30))}" height="28" rx="14" fill="#22243B" stroke="#4B4974"/>',
        f'<text x="{x+42}" y="{y+height-31}" fill="#C8BCFF" font-size="16" font-family="Arial, sans-serif">{tag}</text>',
        f'<text x="{x+width-24}" y="{y+height-31}" text-anchor="end" fill="{FAINT}" font-size="14" font-family="Arial, sans-serif">{_escape(_date(repo.get("pushed_at")))}</text>',
        '</g>',
    ]
    return "\n".join(parts)


def render_projects_svg(projects: list[dict], updated: str, mobile: bool = False) -> str:
    width, height = (520, 1240) if mobile else (1080, 686)
    left = 28 if mobile else 58
    parts = [_background(width, height)]
    parts.append(f'<text x="{left}" y="{74 if mobile else 82}" fill="{WHITE}" font-size="{34 if mobile else 43}" font-weight="750" font-family="Arial, sans-serif">Selected projects</text>')
    parts.append(f'<text x="{left}" y="{106 if mobile else 118}" fill="{MUTED}" font-size="{17 if mobile else 19}" font-family="Arial, sans-serif">Pinned first · refreshed from GitHub</text>')
    parts.append(f'<path d="M {left} {133 if mobile else 142} H {width-left}" stroke="#333A52"/>')
    if not projects:
        parts.append(f'<text x="{left}" y="240" fill="{MUTED}" font-size="22" font-family="Arial, sans-serif">No public projects available</text>')
    for index, repo in enumerate(projects[:4]):
        if mobile:
            x, y, w, h = left, 153 + index * 258, width - left * 2, 234
        else:
            x, y, w, h = left + (index % 2) * 498, 166 + (index // 2) * 240, 466, 215
        parts.append(_project_card(repo, x, y, w, h, mobile))
    footer_y = height - 29
    parts.append(f'<text x="{left}" y="{footer_y}" fill="{FAINT}" font-size="{14 if mobile else 16}" font-family="Arial, sans-serif">{len(projects[:4])} public projects</text>')
    parts.append(f'<text x="{width-left}" y="{footer_y}" text-anchor="end" fill="{FAINT}" font-size="{13 if mobile else 16}" font-family="Arial, sans-serif">{_escape(updated)}</text>')
    return _svg(width, height, "Live selected repositories", "\n".join(parts))


def create_assets(payload: dict, out: Path, updated: str) -> None:
    repos = payload.get("repos", [])
    languages = summarize_languages(repos, payload.get("languages_by_repo", {}))
    projects = select_projects(repos, payload.get("pinned_names", []))
    eligible = sum(_public(repo) for repo in repos)
    out.mkdir(parents=True, exist_ok=True)
    items = {
        "language-stack.svg": render_language_svg(languages, eligible, updated),
        "language-stack-mobile.svg": render_language_svg(languages, eligible, updated, mobile=True),
        "projects.svg": render_projects_svg(projects, updated),
        "projects-mobile.svg": render_projects_svg(projects, updated, mobile=True),
    }
    # Render before writing so an invalid API payload cannot leave half a fresh snapshot.
    for name, content in items.items():
        tmp = out / f".{name}.tmp"
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(out / name)


def _github_json(url: str, token: str, payload: dict | None = None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "akhtarariq-profile-cards"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def fetch_github_data(username: str, token: str) -> dict:
    repos: list[dict] = []
    page = 1
    while True:
        endpoint = f"https://api.github.com/users/{urllib.parse.quote(username)}/repos?type=owner&per_page=100&page={page}"
        batch = _github_json(endpoint, token)
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    languages_by_repo = {}
    for repo in repos:
        if _public(repo):
            full_name = repo["full_name"]
            endpoint = "https://api.github.com/repos/" + urllib.parse.quote(full_name, safe="/") + "/languages"
            languages_by_repo[full_name] = _github_json(endpoint, token)
    pinned: list[str] = []
    if token:
        query = "query($login:String!){user(login:$login){pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{nameWithOwner}}}}}"
        try:
            result = _github_json("https://api.github.com/graphql", token, {"query": query, "variables": {"login": username}})
            pinned = [node["nameWithOwner"] for node in result.get("data", {}).get("user", {}).get("pinnedItems", {}).get("nodes", []) if node and node.get("nameWithOwner")]
        except (urllib.error.URLError, KeyError, TypeError, ValueError):
            # Optional customization; public recency ordering still yields useful cards.
            pinned = []
    return {"repos": repos, "languages_by_repo": languages_by_repo, "pinned_names": pinned}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="AkhtarAriq")
    parser.add_argument("--fixture", type=Path, help="Offline JSON payload for previews/tests")
    parser.add_argument("--out", type=Path, default=Path("assets"))
    args = parser.parse_args()
    payload = json.loads(args.fixture.read_text(encoding="utf-8")) if args.fixture else fetch_github_data(args.user, os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", ""))
    updated = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%d %b %Y · %H:%M WIB")
    create_assets(payload, args.out, updated)
    print(f"Generated 4 SVG cards in {args.out}")


if __name__ == "__main__":
    main()
