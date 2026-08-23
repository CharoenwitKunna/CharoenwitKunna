#!/usr/bin/env python3
"""Generate modern, polished GitHub profile stats cards as static SVGs. Stdlib only."""
import json
import os
import urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("GITHUB_USER", "CharoenwitKunna")
API = "https://api.github.com"

LANG_COLORS = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "Go": "#00ADD8", "C": "#555555", "HTML": "#e34c26", "CSS": "#563d7c",
    "PowerShell": "#2d5282", "Shell": "#89e051", "Java": "#b07219",
    "Rust": "#dea584", "PHP": "#4F5D95", "Ruby": "#701516", "Lua": "#000080",
}
FALLBACK_COLORS = ["#58a6ff", "#bc8cff", "#f0883e", "#3fb950", "#f85149"]

ICONS = {
    "star": '<path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"/>',
    "fork": '<path fill-rule="evenodd" d="M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v.878A2.25 2.25 0 005.75 8.5h4.5A2.25 2.25 0 0012.5 6.25v-.878a2.25 2.25 0 10-1.5 0v.878a.75.75 0 01-.75.75h-4.5A.75.75 0 015 6.25v-.878zm6.5-2.122a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM8 12.75a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0V9.878A2.25 2.25 0 018 7.628a2.25 2.25 0 011.5 2.25v4.994z"/>',
    "repo": '<path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1h-8a1 1 0 00-1 1v6.708A2.486 2.486 0 014.5 9h8V1.5z"/>',
    "follower": '<path fill-rule="evenodd" d="M5.5 3.5a2 2 0 100 4 2 2 0 000-4zM2 5.5a3.5 3.5 0 115.898 2.549 5.507 5.507 0 013.034 4.084.75.75 0 11-1.482.235 4.001 4.001 0 00-7.9 0 .75.75 0 01-1.482-.236A5.507 5.507 0 013.102 8.05 3.49 3.49 0 012 5.5zM11 4a.75.75 0 100 1.5 1.5 1.5 0 01.666 2.844.75.75 0 00-.416.972c.317.757.51 1.59.55 2.463a.75.75 0 001.498-.073 5.463 5.463 0 00-.653-2.91A3.001 3.001 0 0011 4z"/>'
}


def api(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "stats-card-generator",
    }
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def esc(s):
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )


def fetch_data():
    user = api(f"/users/{USER}")
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        page += 1
    own = [r for r in repos if not r.get("fork")]
    langs = {}
    for r in own:
        try:
            for name, nbytes in api(
                f"/repos/{USER}/{r['name']}/languages"
            ).items():
                langs[name] = langs.get(name, 0) + nbytes
        except Exception:
            continue
    return {
        "stars": sum(r["stargazers_count"] for r in repos),
        "forks": sum(r["forks_count"] for r in repos),
        "followers": user["followers"],
        "public_repos": len(repos),
        "langs": sorted(langs.items(), key=lambda kv: -kv[1])[:5],
    }


def fmt(n):
    return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def stats_card(d):
    w, h, pad = 380, 210, 24
    cells = [
        ("Total Stars", d["stars"], "star", "#e3b341"),
        ("Total Forks", d["forks"], "fork", "#58a6ff"),
        ("Public Repos", d["public_repos"], "repo", "#bc8cff"),
        ("Followers", d["followers"], "follower", "#3fb950"),
    ]
    col_w = (w - pad * 2) // 2
    row_h = 60
    
    parts = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{esc(USER)} GitHub stats">',
        '<defs>',
        '  <linearGradient id="grad-stats" x1="0%" y1="0%" x2="100%" y2="0%">',
        '    <stop offset="0%" stop-color="#58a6ff" />',
        '    <stop offset="100%" stop-color="#bc8cff" />',
        '  </linearGradient>',
        '</defs>',
        f'<rect width="{w}" height="{h}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1"/>',
        f'<text x="{pad}" y="38" font-family="-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif" '
        f'font-size="16" font-weight="700" fill="url(#grad-stats)">{esc(USER)}\'s GitHub Stats</text>',
        f'<line x1="{pad}" y1="50" x2="{w - pad}" y2="50" stroke="#21262d" stroke-width="1"/>',
    ]
    
    for i, (label, val, icon_key, icon_color) in enumerate(cells):
        cx = pad + (i % 2) * col_w
        cy = 82 + (i // 2) * row_h
        
        parts.append(
            f'<g transform="translate({cx}, {cy - 12})">'
            f'  <svg width="16" height="16" viewBox="0 0 16 16" fill="{icon_color}">{ICONS[icon_key]}</svg>'
            f'  <text x="22" y="13" font-family="-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif" '
            f'        font-size="12" font-weight="500" fill="#8b949e">{esc(label)}</text>'
            f'  <text x="22" y="35" font-family="-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif" '
            f'        font-size="18" font-weight="700" fill="#f0f6fc">{fmt(val)}</text>'
            f'</g>'
        )
        
    parts.append("</svg>")
    return "\n".join(parts)


def top_langs_card(d):
    entries = d["langs"]
    total = sum(v for _, v in entries) or 1
    w, h, pad = 380, 210, 24
    
    parts = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="Top languages">',
        '<defs>',
        '  <linearGradient id="grad-langs" x1="0%" y1="0%" x2="100%" y2="0%">',
        '    <stop offset="0%" stop-color="#58a6ff" />',
        '    <stop offset="100%" stop-color="#3fb950" />',
        '  </linearGradient>',
        '</defs>',
        f'<rect width="{w}" height="{h}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1"/>',
        f'<text x="{pad}" y="38" font-family="-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif" '
        f'font-size="16" font-weight="700" fill="url(#grad-langs)">Most Used Languages</text>',
        f'<line x1="{pad}" y1="50" x2="{w - pad}" y2="50" stroke="#21262d" stroke-width="1"/>',
    ]
    
    bar_w = w - pad * 2
    for i, (name, nbytes) in enumerate(entries):
        y = 74 + i * 26
        pct = round(nbytes * 100 / total, 1)
        color = LANG_COLORS.get(name, FALLBACK_COLORS[i % len(FALLBACK_COLORS)])
        bw = max(6, int(bar_w * pct / 100))
        
        parts.append(
            f'<text x="{pad}" y="{y}" font-family="-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif" '
            f'font-size="12" font-weight="500" fill="#c9d1d9">{esc(name)}</text>'
            f'<text x="{w - pad}" y="{y}" text-anchor="end" '
            f'font-family="-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif" '
            f'font-size="12" font-weight="600" fill="#8b949e">{pct}%</text>'
            f'<rect x="{pad}" y="{y + 4}" width="{bar_w}" height="5" rx="2.5" fill="#21262d"/>'
            f'<rect x="{pad}" y="{y + 4}" width="{bw}" height="5" rx="2.5" fill="{color}"/>'
        )
        
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    data = fetch_data()
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.path.dirname(here))
    with open(os.path.join(out, "stats-card.svg"), "w", encoding="utf-8") as f:
        f.write(stats_card(data))
    with open(os.path.join(out, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(top_langs_card(data))
    print("Successfully generated modern stats SVGs:", data)
