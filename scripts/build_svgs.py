#!/usr/bin/env python3
"""Generates the profile SVGs in ../assets, matching assets/header.svg (navy -> #2563eb, Inter, rx 18).

Edit the data below, then run:  python3 scripts/build_svgs.py
Every output is parsed as XML before it is written, so a broken file fails loudly.
"""
import base64
from pathlib import Path
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FONT = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
BLUE, SKY, ICE, TEXT, MUTED = "#2563eb", "#60a5fa", "#93c5fd", "#e2e8f0", "#bfdbfe"
WIDTH, LEFT, RIGHT = 1200, 48, 1152

# ---------------------------------------------------------------- content

STATS = [("8", "apps shipped"), ("99%+", "crash-free sessions"), ("6+", "years in mobile")]

CLIENTS = [
    ("medical", "Wundservice", ["Wound-care app for clinicians and patients:", "offline bedside records, sync, encrypted data."],
     ["React Native", "Swift Vision", "Kotlin ML Kit", "TurboModule", "Keychain / Keystore"]),
    ("snow", "GAC Winterdienst", ["Field-operations app for winter-service crews:", "route planning, geo-tagged tasks, offline sync."],
     ["React Native", "Maps & location", "Offline-first sync"]),
    ("receipt", "Flotix", ["B2B fleet-expense platform with on-device", "receipt scanning instead of manual entry."],
     ["React Native", "Supabase", "ML Kit", "Apollo GraphQL"]),
    ("box", "Moverly.io", ["CRM for moving companies: Next.js dashboard", "and React Native app on one typed API client."],
     ["Next.js", "React Native", "Turborepo", "pnpm", "Vercel"]),
    ("scissors", "Barber X", ["Booking platform with mobile and desktop in", "real-time sync, reconnection and reconciliation."],
     ["React Native", "Electron", "WebSockets"]),
]
CLIENT_TILES = [("#2563eb", "#60a5fa"), ("#0284c7", "#38bdf8"), ("#4f46e5", "#818cf8"),
                ("#0891b2", "#22d3ee"), ("#1d4ed8", "#93c5fd"), ("#334155", "#64748b")]

AI_STEPS = [
    ("plan", "scope, constraints & acceptance criteria, written first"),
    ("build", "small, reviewable diffs · tests run on every step"),
    ("review", "I read every diff · check it on a real device · then a PR"),
    ("context", "rules, skills & hooks live in git, reviewed like code"),
    ("tools", "MCP → Figma · Sentry · GitHub · Linear · browser automation"),
    ("guard", "allowlists + pre-tool hooks: no destructive commands, secrets or user data"),
    ("product", "in-app assistant on OpenAI + Anthropic, read-only: a person completes the action"),
]

STACK = [
    ("Mobile", ["React Native", "Expo", "TypeScript", "Swift", "Kotlin", "Hermes + New Arch", "Reanimated"]),
    ("Web", ["React", "Next.js", "Tailwind CSS", "TanStack Query", "Zustand", "Turborepo"]),
    ("Backend & data", ["Node.js", "NestJS", "MongoDB", "Supabase (Postgres)", "GraphQL", "WebSockets"]),
    ("Cloud, CI & releases", ["AWS (Amplify, ECS, EC2)", "Vercel", "GitHub Actions", "Fastlane", "EAS", "Sentry"]),
    ("Testing", ["Jest", "Testing Library", "Detox", "Maestro", "Swift Testing"]),
    ("AI tooling", ["Claude Code", "MCP", "Cursor", "GitHub Copilot", "OpenAI + Anthropic APIs"]),
]
STACK_DOTS = [SKY, "#38bdf8", "#818cf8", "#22d3ee", "#a5b4fc", "#f59e0b"]

BUTTONS = [
    ("btn-portfolio", "harpreet-kumar.vercel.app", "triangle", "#0f172a"),
    ("btn-linkedin", "LinkedIn", "linkedin", "#0A66C2"),
    ("btn-email", "harpreetkbadhan@gmail.com", "mail", "#EA4335"),
    ("btn-budgetsum", "budgetsum.app", "globe", BLUE),
]

# Stroke icons on a 32x32 grid.
ICONS = {
    "medical": '<rect x="4" y="4" width="24" height="24" rx="6"/><path d="M16 10v12M10 16h12"/>',
    "snow": '<path d="M16 3v26M4.7 9.5l22.6 13M4.7 22.5l22.6-13"/><path d="M12 5l4 3 4-3M12 27l4-3 4 3"/>',
    "receipt": '<path d="M7 3h18v26l-3-2-3 2-3-2-3 2-3-2-3 2z"/><path d="M11 10h10M11 15h10M11 20h6"/>',
    "box": '<path d="M4 10l12-6 12 6v12l-12 6-12-6z"/><path d="M4 10l12 6 12-6M16 16v12"/>',
    "scissors": '<circle cx="8" cy="24" r="4"/><circle cx="24" cy="24" r="4"/><path d="M11 21L26 4M21 21L6 4"/>',
    "lock": '<rect x="6" y="14" width="20" height="14" rx="3"/><path d="M10 14v-4a6 6 0 0 1 12 0v4"/>',
    "triangle": '<path d="M16 6l11 19H5z"/>',
    "linkedin": '<rect x="5" y="5" width="22" height="22" rx="4"/><path d="M11 14v8M11 10v.5M16 22v-8M16 17a3 3 0 0 1 6 0v5"/>',
    "mail": '<rect x="4" y="7" width="24" height="18" rx="3"/><path d="M5 9l11 8 11-8"/>',
    "globe": '<circle cx="16" cy="16" r="12"/><ellipse cx="16" cy="16" rx="5" ry="12"/><path d="M4 16h24"/>',
}

# ---------------------------------------------------------------- design system (mirrors header.svg)

DEFS = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1220"/><stop offset=".55" stop-color="#0f2a5a"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SKY}" stop-opacity="0"/><stop offset=".5" stop-color="{ICE}" stop-opacity=".9"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#020617" flood-opacity=".45"/></filter>
"""
CSS = f"""
text {{ font-family: {FONT}; }}
.mono {{ font-family: {MONO}; }}
.rise {{ animation: rise .7s ease-out both; }}
.blink {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .rise, .blink {{ animation: none !important; }} }}
"""


def svg(height, label, body, defs="", width=WIDTH):
    aria = escape(label, {'"': "&quot;"})
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="{aria}"><defs>{DEFS}{defs}<style>{CSS}</style></defs>{body}</svg>')


def panel(height, width=WIDTH):
    """Header-style backdrop: navy-to-blue gradient, soft orbs, 150px grid."""
    grid_h = "".join(f"M0 {y}H{width}" for y in range(75, height, 75))
    grid_v = "".join(f"M{x} 0V{height}" for x in range(150, width, 150))
    return (f'<clipPath id="clip"><rect width="{width}" height="{height}" rx="18"/></clipPath><g clip-path="url(#clip)">'
            f'<rect width="{width}" height="{height}" fill="url(#bg)"/>'
            f'<circle cx="{width - 190}" cy="70" r="150" fill="#3b82f6" fill-opacity=".22"/>'
            f'<circle cx="140" cy="{height - 10}" r="130" fill="#1d4ed8" fill-opacity=".25"/>'
            f'<path d="{grid_h}{grid_v}" stroke="#fff" stroke-opacity=".05"/></g>')


def text(x, y, s, size=18, fill="#fff", weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def text_width(s, size):
    """Rough Inter semibold width; SVG can't measure text, so chips are sized from this."""
    def units(c):
        if c in "il.,:;'|!Ijtf() /":
            return .3
        if c in "mwMW@":
            return .86
        return .66 if c.isupper() or c.isdigit() else .56
    return sum(units(c) for c in s) * size


def icon(name, x, y, scale=1.0, color="#fff", stroke=2.2):
    return (f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{color}" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def gradient(gid, start, end):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{start}"/>'
            f'<stop offset="1" stop-color="{end}"/></linearGradient>')


def chip_width(label, size, dot):
    return text_width(label, size) + (30 if dot else 14) + 14


def chip(x, y, label, size=15, height=32, dot=None):
    pad_left = 30 if dot else 14
    dot_mark = f'<circle cx="{x + 15}" cy="{y + height / 2}" r="4" fill="{dot}"/>' if dot else ""
    return (f'<rect x="{x}" y="{y}" width="{chip_width(label, size, dot):.0f}" height="{height}" rx="{height / 2}" fill="#fff" fill-opacity=".1"/>'
            + dot_mark + text(x + pad_left, y + height / 2 + 5, label, size, "#dbeafe", 600))


def chip_row(x, y, labels, max_x, size=15, gap=8, row_gap=10, dot=None):
    """Lays chips left to right, wrapping at max_x. Returns (markup, bottom_y)."""
    parts, cx = [], x
    for label in labels:
        w = chip_width(label, size, dot)
        if cx + w > max_x and cx > x:
            cx, y = x, y + 32 + row_gap
        parts.append(chip(cx, y, label, size, dot=dot))
        cx += w + gap
    return "".join(parts), y + 32

# ---------------------------------------------------------------- sections


def build_stats():
    height, col_w = 150, (RIGHT - LEFT) / len(STATS)
    tiles = "".join(
        text(LEFT + col_w * (i + .5), 78, num, 48, "#fff", 700, "middle", 'letter-spacing="-1"')
        + text(LEFT + col_w * (i + .5), 112, label, 16, MUTED, 500, "middle")
        for i, (num, label) in enumerate(STATS))
    dividers = "".join(f'<path d="M{LEFT + col_w * i:.0f} 40V116" stroke="#fff" stroke-opacity=".14"/>' for i in range(1, len(STATS)))
    accent = f'<rect x="{WIDTH / 2 - 75}" y="{height - 14}" width="150" height="4" rx="2" fill="url(#glow)"/>'
    return svg(height, "; ".join(f"{n} {l}" for n, l in STATS), panel(height) + tiles + dividers + accent)


def card_frame(i, x, y, w, h, icon_name, title, dashed=False):
    border = 'fill="#fff" fill-opacity=".06" stroke="#fff" stroke-opacity=".22" stroke-dasharray="6 6"' if dashed \
        else 'fill="#0b1220" fill-opacity=".55" stroke="#fff" stroke-opacity=".12"'
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" {border}/>'
            f'<rect x="{x + 24}" y="{y + 24}" width="52" height="52" rx="14" fill="url(#t{i})"/>'
            + icon(icon_name, x + 34, y + 34, 1, "#fff", 2.4)
            + text(x + 92, y + 58, title, 24, "#fff", 700, extra='letter-spacing="-.5"'))


def build_clients():
    cols, card_w, card_h, gap, top = 2, 540, 250, 24, 40
    slots = len(CLIENTS) + 1  # last slot is the "private repositories" note
    rows = (slots + cols - 1) // cols
    height = top + rows * card_h + (rows - 1) * gap + 40
    defs = "".join(gradient(f"t{i}", a, b) for i, (a, b) in enumerate(CLIENT_TILES))

    def origin(i):
        return LEFT + (i % cols) * (card_w + gap), top + (i // cols) * (card_h + gap)

    cards = []
    for i, (icon_name, title, lines, stack) in enumerate(CLIENTS):
        x, y = origin(i)
        desc = "".join(text(x + 24, y + 112 + n * 26, line, 17, TEXT) for n, line in enumerate(lines))
        chips, _ = chip_row(x + 24, y + 160, stack, x + card_w - 20, size=14)  # room for two rows
        cards.append(f'<g class="rise" style="animation-delay:{i * .1:.1f}s">'
                     + card_frame(i, x, y, card_w, card_h, icon_name, title) + desc + chips + '</g>')
    i = len(CLIENTS)
    x, y = origin(i)
    cards.append(f'<g class="rise" style="animation-delay:{i * .1:.1f}s">'
                 + card_frame(i, x, y, card_w, card_h, "lock", "Private repositories", dashed=True)
                 + text(x + 24, y + 112, "Client products built at List & Sell GmbH, Berlin.", 17, TEXT)
                 + text(x + 24, y + 138, "Code stays private; architecture details on request.", 17, TEXT) + '</g>')
    label = "Client work: " + "; ".join(f"{t}: {' '.join(l)} Stack: {', '.join(s)}" for _, t, l, s in CLIENTS)
    return svg(height, label, panel(height) + "".join(cards), defs)


def build_ai():
    line_h, win_y, size = 36, 36, 18
    win_h = 44 + 30 + (len(AI_STEPS) + 2) * line_h  # prompt + steps + done line
    height = win_y + win_h + 36
    x0, base = LEFT + 28, win_y + 44 + 40
    done_msg = "✓  shipped to real users"
    prompt = (f'<text x="{x0}" y="{base}" font-size="{size}" class="mono" xml:space="preserve">'
              f'<tspan fill="#34d399">➜  </tspan><tspan fill="{ICE}">~/app </tspan><tspan fill="#fff">claude</tspan></text>')
    steps = "".join(
        f'<g class="rise" style="animation-delay:{.3 + i * .2:.1f}s"><text x="{x0}" y="{base + (i + 1) * line_h}" font-size="{size}" class="mono" xml:space="preserve">'
        f'<tspan fill="{SKY}">›  </tspan><tspan fill="#fff" font-weight="700">{escape(key.ljust(9))}</tspan>'
        f'<tspan fill="{TEXT}">{escape(desc)}</tspan></text></g>'
        for i, (key, desc) in enumerate(AI_STEPS))
    done_y = base + (len(AI_STEPS) + 1) * line_h
    done = (f'<g class="rise" style="animation-delay:{.3 + len(AI_STEPS) * .2:.1f}s">'
            f'<text x="{x0}" y="{done_y}" font-size="{size}" class="mono" fill="#34d399" xml:space="preserve">{done_msg}</text></g>'
            f'<rect class="blink" x="{x0 + len(done_msg) * size * .602 + 8:.0f}" y="{done_y - 17}" width="10" height="22" fill="{SKY}"/>')
    lights = "".join(f'<circle cx="{LEFT + 24 + i * 18}" cy="{win_y + 22}" r="5" fill="{c}"/>'
                     for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
    window = (f'<rect x="{LEFT}" y="{win_y}" width="{RIGHT - LEFT}" height="{win_h}" rx="14" fill="#020617" fill-opacity=".82" '
              f'stroke="#fff" stroke-opacity=".14" filter="url(#shadow)"/>'
              f'<path d="M{LEFT} {win_y + 44}H{RIGHT}" stroke="#fff" stroke-opacity=".1"/>{lights}'
              + text(WIDTH / 2, win_y + 27, "claude — ~/app", 14, MUTED, 500, "middle", 'class="mono"'))
    label = "How I work with AI coding agents: " + "; ".join(f"{k}: {d}" for k, d in AI_STEPS)
    return svg(height, label, panel(height) + window + prompt + steps + done)


def build_stack():
    y, parts, label_w = 40, [], 230
    for n, ((group, items), dot) in enumerate(zip(STACK, STACK_DOTS)):
        if n:
            parts.append(f'<path d="M{LEFT} {y - 11}H{RIGHT}" stroke="#fff" stroke-opacity=".07"/>')
        parts.append(text(LEFT, y + 22, group, 17, "#fff", 700))
        chips, bottom = chip_row(LEFT + label_w, y, items, RIGHT, size=15, dot=dot)
        parts.append(chips)
        y = bottom + 22
    height = y + 18
    label = "Tech stack: " + "; ".join(f"{g}: {', '.join(i)}" for g, i in STACK)
    return svg(height, label, panel(height) + "".join(parts))


# budgetSum showcase: same blue panel as the rest of the profile, app icon + product and engineering details.
BS_PRODUCT = ["Reminders before every bill is due", "Loans & instalments tracked to the last rate",
              "See what's left this month after all bills", "Invite your partner for free",
              "No bank login · GDPR, hosted in the EU"]
BS_ENGINEERING = ["React Native + TypeScript client", "NestJS + MongoDB API",
                  "RevenueCat + StoreKit, server-side entitlements", "Idempotent webhooks · push notifications",
                  "6 subscription tiers · 8 languages"]
BS_LINKS = [("Download on the App Store", "#000"), ("budgetsum.app", BLUE)]


def bs_list(x, y, title, items):
    rows = "".join(
        f'<circle cx="{x + 10}" cy="{y + 30 + i * 36}" r="10" fill="{SKY}" fill-opacity=".18"/>'
        f'<path d="M{x + 5.5} {y + 30 + i * 36}l3 3 6-6" fill="none" stroke="{ICE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        + text(x + 30, y + 36 + i * 36, item, 17, TEXT, 500)
        for i, item in enumerate(items))
    return text(x, y, title, 13, ICE, 700, extra='letter-spacing="2"') + rows


def build_budgetsum():
    height = 430
    icon_data = base64.b64encode((ASSETS / "budgetsum-icon.svg").read_bytes()).decode("ascii")
    head = (f'<image x="{LEFT}" y="44" width="96" height="96" href="data:image/svg+xml;base64,{icon_data}" filter="url(#shadow)"/>'
            + text(LEFT + 124, 92, "budgetSum", 44, "#fff", 700, extra='letter-spacing="-1"')
            + text(LEFT + 126, 126, "Never miss a bill again. A bills & payments app I build and run solo.", 19, MUTED, 500))
    links, ly = [], 52
    for label, color in BS_LINKS:
        w = 250
        links.append(f'<rect x="{RIGHT - w}" y="{ly}" width="{w}" height="48" rx="24" fill="{color}" stroke="{SKY}" stroke-opacity=".45"/>'
                     + text(RIGHT - w / 2, ly + 30, label, 16, "#fff", 700, "middle"))
        ly += 60
    divider = f'<rect x="{LEFT}" y="168" width="{RIGHT - LEFT}" height="1" fill="#fff" fill-opacity=".14"/>'
    col_w = (RIGHT - LEFT) / 2
    lists = bs_list(LEFT, 210, "PRODUCT", BS_PRODUCT) + bs_list(LEFT + col_w + 12, 210, "ENGINEERING", BS_ENGINEERING)
    accent = f'<rect x="{WIDTH / 2 - 75}" y="{height - 14}" width="150" height="4" rx="2" fill="url(#glow)"/>'
    label = ("budgetSum, a bills and payments app built and run solo. Product: " + "; ".join(BS_PRODUCT)
             + ". Engineering: " + "; ".join(BS_ENGINEERING) + ". Download on the App Store.")
    return svg(height, label, panel(height) + head + "".join(links) + divider + lists + accent)


def build_buttons():
    outputs = {}
    for name, label, icon_name, color in BUTTONS:
        width = round(58 + text_width(label, 17) + 24)
        body = (f'<rect x="1" y="1" width="{width - 2}" height="50" rx="25" fill="#0f2a5a" stroke="{SKY}" stroke-opacity=".45"/>'
                f'<circle cx="27" cy="26" r="17" fill="{color}"/>'
                + icon(icon_name, 17.4, 16.4, .6, "#fff", 3)
                + text(54, 32, label, 17, "#fff", 600))
        outputs[name] = svg(52, label, body, width=width)
    return outputs


def main():
    outputs = {"stats": build_stats(), "clients": build_clients(), "ai-workflow": build_ai(),
               "stack": build_stack(), "budgetsum-banner": build_budgetsum(), **build_buttons()}
    for name, content in outputs.items():
        ET.fromstring(content)  # fail fast on malformed XML
        (ASSETS / f"{name}.svg").write_text(content, encoding="utf-8")
    print(f"wrote {len(outputs)} SVGs to {ASSETS}")


if __name__ == "__main__":
    main()
