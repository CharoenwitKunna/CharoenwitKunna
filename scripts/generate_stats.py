#!/usr/bin/env python3
"""Generate GitHub profile stats cards as static SVGs. Stdlib only."""
import json
import os
import urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("GITHUB_USER", "CharoenwitKunna")
API = "https://api.github.com"

LANG_COLORS = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "Go": "#00ADD8", "C": "#555555", "HTML": "#e34c26", "CSS": "#563d7c",
    "PowerShell": "#012456", "Shell": "#89e051", "Java": "#b07219",
    "Rust": "#dea584", "PHP": "#4F5D95", "Ruby": "#701516", "Lua": "#000080",
}
FALLBACK_COLORS = ["#8b5cf6", "#06b6d4", "#f59e0b", "#10b981", "#ef4444"]


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
    w, h, pad = 420, 190, 28
    cells = [
        ("Total Stars", d["stars"]), ("Total Forks", d["forks"]),
        ("Followers", d["followers"]), ("Public Repos", d["public_repos"]),
    ]
    col_w = (w - pad * 2) // 2
    row_h = 52
    parts = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{esc(USER)} GitHub stats">',
        f'<rect width="{w}" height="{h}" rx="12" fill="#161b22" '
        'stroke="#30363d"/>',
        f'<text x="{pad}" y="42" font-family="Segoe UI,Ubuntu,sans-serif" '
        f'font-size="17" font-weight="700" fill="#e6edf3">{esc(USER)}\'s '
        'GitHub Stats</text>',
        '<line x1="%d" y1="56" x2="%d" y2="56" stroke="#21262d"/>' % (
            pad, w - pad),
    ]
    for i, (label, val) in enumerate(cells):
        cx = pad + (i % 2) * col_w
        cy = 88 + (i // 2) * row_h
        parts.append(
            f'<circle cx="{cx + 5}" cy="{cy - 5}" r="4" fill="#2f81f7"/>'
            f'<text x="{cx + 16}" y="{cy}" font-family="Segoe UI,Ubuntu,'
            f'sans-serif" font-size="13" fill="#9198a1">{esc(label)}:</text>'
            f'<text x="{cx + 16}" y="{cy + 20}" font-family="Segoe UI,'
            f'Ubuntu,sans-serif" font-size="15" font-weight="600" '
            f'fill="#e6edf3">{fmt(val)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def top_langs_card(d):
    entries = d["langs"]
    total = sum(v for _, v in entries) or 1
    w, pad = 360, 24
    h = 66 + len(entries) * 32 + pad
    parts = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="Top languages">',
        f'<rect width="{w}" height="{h}" rx="12" fill="#161b22" '
        'stroke="#30363d"/>',
        f'<text x="{pad}" y="42" font-family="Segoe UI,Ubuntu,sans-serif" '
        'font-size="17" font-weight="700" fill="#e6edf3">Top Languages'
        "</text>",
        '<line x1="%d" y1="56" x2="%d" y2="56" stroke="#21262d"/>' % (
            pad, w - pad),
    ]
    bar_w = w - pad * 2
    for i, (name, nbytes) in enumerate(entries):
        y = 78 + i * 32
        pct = round(nbytes * 100 / total, 1)
        color = LANG_COLORS.get(name, FALLBACK_COLORS[i % len(FALLBACK_COLORS)])
        if color.lower() == "#012456":
            color = "#1e3a5f"  # PowerShell navy too dark against card bg
        bw = max(4, int(bar_w * pct / 100))
        parts.append(
            f'<text x="{pad}" y="{y}" font-family="Segoe UI,Ubuntu,'
            f'sans-serif" font-size="13" fill="#e6edf3">'
            f'<tspan fill="{color}" font-size="15">&#9632;</tspan> '
            f'{esc(name)}</text>'
            f'<text x="{w - pad}" y="{y}" text-anchor="end" '
            f'font-family="Segoe UI,Ubuntu,sans-serif" font-size="13" '
            f'fill="#9198a1">{pct}%</text>'
            f'<rect x="{pad}" y="{y + 7}" width="{bar_w}" height="7" '
            'rx="3.5" fill="#21262d"/>'
            f'<rect x="{pad}" y="{y + 7}" width="{bw}" height="7" '
            f'rx="3.5" fill="{color}"/>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    data = fetch_data()
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.path.dirname(here))
    with open(os.path.join(out, "stats-card.svg"), "w") as f:
        f.write(stats_card(data))
    with open(os.path.join(out, "top-langs.svg"), "w") as f:
        f.write(top_langs_card(data))
    print("written:", data)
