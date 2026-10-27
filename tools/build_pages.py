"""Builds the public "how it is built" pages (docs/*.html) from src/content.json.

Run from anywhere:  python tools/build_pages.py
Writes docs/index.html and one docs/<slug>.html per product. docs/style.css and docs/app.js are hand-written.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "content.json"
OUT = ROOT / "docs"
LANGS = ("vi", "en")
SITE_NAME = "Truong Dang Khoa — Exomaly Code"
FACEBOOK = "https://www.facebook.com/Exomaly"
ZALO = "https://zalo.me/0334934592"
EMAIL = "tdk.exomaly@gmail.com"

Text = dict[str, str]


def esc(value: str) -> str:
    """HTML-escape a text value."""
    return html.escape(value, quote=True)


def both(vi: str, en: str) -> str:
    """Return the same fragment in both languages; CSS shows the one that matches the page language."""
    return f'<span lang="vi">{vi}</span><span lang="en">{en}</span>'


def both_text(value: Text) -> str:
    """Return a {vi, en} text pair as two escaped language spans."""
    return both(esc(value["vi"]), esc(value["en"]))


def stat_value(raw: Any) -> Text:
    """A stat value is either a plain string (same in both languages) or a {vi, en} pair."""
    if isinstance(raw, dict):
        return {"vi": str(raw["vi"]), "en": str(raw["en"])}
    return {"vi": str(raw), "en": str(raw)}


def shell(title: str, description: str, accent: str, body: str, back: bool = True) -> str:
    """Wrap a page body in the shared document skeleton; `back` adds the link to the product list."""
    back_link = f'<a class="back" href="index.html">{both("← Tất cả sản phẩm", "← All products")}</a>' if back else "<span></span>"
    return f"""<!doctype html>
<html lang="vi" data-lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="stylesheet" href="style.css">
<script src="app.js"></script>
</head>
<body style="--accent: {esc(accent)}">
<header class="top">
  {back_link}
  <div class="langs" role="group" aria-label="Language">
    <button type="button" data-set-lang="vi">VI</button>
    <button type="button" data-set-lang="en">EN</button>
  </div>
</header>
{body}
<footer>
  <p>{both("Mã nguồn các sản phẩm nằm ở kho riêng tư.", "Source code is kept in private repositories.")}</p>
  <p>{both("Liên hệ", "Contact")}: <a href="{FACEBOOK}">Facebook</a> · <a href="{ZALO}">Zalo</a> · {esc(EMAIL)}</p>
  <p class="brand">{esc(SITE_NAME)}</p>
</footer>
</body>
</html>
"""


def list_block(items: dict[str, list[str]]) -> str:
    """A bullet list in both languages."""
    parts: list[str] = []
    for lang in LANGS:
        lis = "".join(f"<li>{esc(line)}</li>" for line in items[lang])
        parts.append(f'<ul lang="{lang}">{lis}</ul>')
    return "".join(parts)


def render_stats(stats: list[dict[str, Any]]) -> str:
    """Grid of big number + caption."""
    cells: list[str] = []
    for stat in stats:
        value = stat_value(stat["v"])
        cells.append(
            '<div class="stat">'
            f'<div class="v">{both_text(value)}</div>'
            f'<div class="k">{both(esc(stat["vi"]), esc(stat["en"]))}</div>'
            "</div>"
        )
    return f'<div class="stats">{"".join(cells)}</div>'


def render_decisions(decisions: list[dict[str, Text | dict[str, str]]]) -> str:
    """One card per decision: what, why, rejected alternative."""
    cards: list[str] = []
    for dec in decisions:
        cards.append(
            '<article class="dec">'
            f'<h3>{both_text(dec["what"])}</h3>'
            f'<dl><dt>{both("Vì sao", "Why")}</dt><dd>{both_text(dec["why"])}</dd>'
            f'<dt>{both("Phương án đã loại", "Rejected alternative")}</dt><dd>{both_text(dec["alt"])}</dd></dl>'
            "</article>"
        )
    return "".join(cards)


def render_product(product: dict[str, Any]) -> str:
    """Full page of one product."""
    name = str(product["name"])
    asof = str(product["asof"])
    body = f"""<main>
  <p class="eyebrow">{both("Cách sản phẩm này được làm", "How this product is built")}</p>
  <h1>{esc(name)}</h1>
  <p class="tagline">{both_text(product["tagline"])}</p>
  <p><a class="cta" href="{esc(product["url"])}">{both("Mở sản phẩm", "Open the product")} →</a></p>

  <section>
    <h2><span class="n">1</span>{both("Tóm tắt", "Summary")}</h2>
    {list_block(product["summary"])}
  </section>

  <section>
    <h2><span class="n">2</span>{both("Số liệu", "By the numbers")}</h2>
    {render_stats(product["stats"])}
    <p class="asof">{both(f"Số liệu lấy từ các lần chạy thật, tính đến {esc(asof)}.", f"Figures come from real runs, as of {esc(asof)}.")}</p>
  </section>

  <section>
    <h2><span class="n">3</span>{both("Quyết định thiết kế", "Design decisions")}</h2>
    {render_decisions(product["decisions"])}
  </section>

  <section>
    <h2><span class="n">4</span>{both("Cách kiểm chứng", "How it is verified")}</h2>
    {list_block(product["verify"])}
  </section>
</main>"""
    return shell(f"{name} · Cách làm", product["tagline"]["vi"], str(product["accent"]), body)


def render_index(products: list[dict[str, Any]]) -> str:
    """Landing page listing every product."""
    cards = "".join(
        f'<a class="card" href="{esc(p["slug"])}.html" style="--accent: {esc(p["accent"])}">'
        f'<h2>{esc(p["name"])}</h2>'
        f'<p>{both_text(p["tagline"])}</p>'
        f'<span class="go">{both("Xem cách làm", "See how it is built")} →</span></a>'
        for p in products
    )
    body = f"""<main>
  <p class="eyebrow">{esc(SITE_NAME)}</p>
  <h1>{both("Các sản phẩm Exomaly được làm như thế nào", "How the Exomaly products are built")}</h1>
  <p class="tagline">{both(
        "Mỗi sản phẩm có một trang ngắn: tóm tắt, số liệu thật, các quyết định thiết kế kèm phương án đã loại, và cách kiểm chứng.",
        "One short page per product: a summary, real figures, the design decisions with the alternatives rejected, and how it is verified.",
    )}</p>
  <div class="cards">{cards}</div>
</main>"""
    return shell(f"{SITE_NAME} · Cách làm", "Cách các sản phẩm Exomaly được làm", "#8B5CF6", body, back=False)


def main() -> int:
    """Build every page; return a process exit code."""
    try:
        data = json.loads(SRC.read_text(encoding="utf-8"))
        products: list[dict[str, Any]] = data["products"]
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "index.html").write_text(render_index(products), encoding="utf-8", newline="\n")
        for product in products:
            (OUT / f"{product['slug']}.html").write_text(render_product(product), encoding="utf-8", newline="\n")
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    print(f"built {len(products) + 1} pages in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
