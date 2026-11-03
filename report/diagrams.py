"""Генерує SVG-діаграми для звіту ПЗ2: sitemap і user flow.

Кольори беруться з тих самих токенів, що й UI-kit (ui-kit/src/tokens.css),
тому діаграми виглядають як частина продукту.
"""

NAVY = "#1A2639"
GREEN = "#2C4C3B"
GOLD = "#C9A227"
CAMEL = "#BFA07A"
PANEL = "#F8F5EE"
CREAM = "#F0EAD6"
GRAY = "#6A717D"
DANGER = "#8B3A3A"

FONT = "font-family=\"Lato, 'Segoe UI', Calibri, sans-serif\""

DEFS = f"""<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0L10 5L0 10z" fill="{NAVY}"/></marker>
<marker id="arr-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0L10 5L0 10z" fill="{GRAY}"/></marker>
</defs>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, lines, size=12, fill=NAVY, weight=400, anchor="middle"):
    """Багаторядковий текст, центрований по вертикалі навколо y."""
    lh = size * 1.25
    y0 = y - lh * (len(lines) - 1) / 2 + size * 0.35
    out = []
    for i, ln in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y0 + i * lh:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}" {FONT}>{esc(ln)}</text>'
        )
    return "".join(out)


def box(cx, cy, w, h, lines, fill=PANEL, stroke=CAMEL, color=NAVY, rx=8, weight=400, dash=False, size=12):
    d = ' stroke-dasharray="5 3"' if dash else ""
    return (
        f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"{d}/>'
        + text(cx, cy, lines, size=size, fill=color, weight=weight)
    )


def diamond(cx, cy, w, h, lines):
    pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
    return (
        f'<polygon points="{pts}" fill="{CREAM}" stroke="{GOLD}" stroke-width="1.6"/>'
        + text(cx, cy, lines, size=11.5, weight=700)
    )


def line(d, grey=False, dash=False):
    col = GRAY if grey else NAVY
    da = ' stroke-dasharray="4 3"' if dash else ""
    mk = "arr-g" if grey else "arr"
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.4"{da} marker-end="url(#{mk})"/>'


def label(x, y, s, anchor="middle", color=GREEN):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="11" font-weight="700" fill="{color}" {FONT}>{esc(s)}</text>'


# ---------------------------------------------------------------- SITEMAP
def sitemap():
    # (назва L1, [L2 ...]); L2 = (назва, [L3 ...], ref?)
    tree = [
        ("Today", [("Top 3 завдань", [], False), ("Список завдань\n(виконано / перенести)", [], False), ("Quick Add", [], False)]),
        ("Chat", [("Історія діалогу", [], False), ("Картка плану\n(підтвердити / виправити)", [], False)]),
        ("Wheel of Balance", [
            ("Priority Board", [], False),
            ("AI Insights", [], False),
            ("Vision & Mission", [], False),
            ("Task Tracker", ["Log Time", "Efficiency"], False),
        ]),
        ("Week", [("Day: деталі дня", [], False)]),
        ("Month", [("Day: деталі дня", [], True)]),
        ("Year", [("Month: перехід\nдо місяця", [], True)]),
    ]
    row_h, gap = 40, 12
    x_root, x1, x2, x3 = 70, 215, 395, 600
    w_root, w1, w2, w3 = 120, 140, 170, 130
    y = 24
    parts = []
    l1_pos = []
    for name1, kids in tree:
        kid_pos = []
        group_top = y
        for name2, subs, ref in kids:
            if subs:
                sub_pos = []
                for s in subs:
                    sub_pos.append((y + row_h / 2, s))
                    y += row_h
                cy2 = (sub_pos[0][0] + sub_pos[-1][0]) / 2
                kid_pos.append((cy2, name2, sub_pos, ref))
            else:
                kid_pos.append((y + row_h / 2, name2, [], ref))
                y += row_h
        cy1 = (kid_pos[0][0] + kid_pos[-1][0]) / 2
        l1_pos.append((cy1, name1, kid_pos))
        y += gap
    height = y + 70
    root_cy = (l1_pos[0][0] + l1_pos[-1][0]) / 2

    def elbow(x_from, y_from, x_to, y_to):
        mid = (x_from + x_to) / 2
        return f'<path d="M{x_from} {y_from} H{mid} V{y_to} H{x_to}" fill="none" stroke="{CAMEL}" stroke-width="1.4"/>'

    out = [f'<svg viewBox="0 0 740 {height:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sitemap Cassiopeia">', DEFS]
    out.append(box(x_root, root_cy, w_root, 52, ["Cassiopeia", "(нижня навігація)"], fill=NAVY, stroke=NAVY, color=CREAM, weight=700))
    for cy1, name1, kid_pos in l1_pos:
        out.append(elbow(x_root + w_root / 2, root_cy, x1 - w1 / 2, cy1))
        out.append(box(x1, cy1, w1, 34, [name1], fill=GREEN, stroke=GREEN, color=CREAM, weight=700))
        for cy2, name2, sub_pos, ref in kid_pos:
            out.append(elbow(x1 + w1 / 2, cy1, x2 - w2 / 2, cy2))
            lines = name2.split("\n")
            out.append(box(x2, cy2, w2, 34 if len(lines) == 1 else 38, lines, dash=ref, size=11.5))
            for cy3, s in sub_pos:
                out.append(elbow(x2 + w2 / 2, cy2, x3 - w3 / 2, cy3))
                out.append(box(x3, cy3, w3, 30, [s], fill=CREAM, size=11.5))
    # легенда
    ly = height - 38
    out.append(box(100, ly, 26, 14, [""], fill=GREEN, stroke=GREEN, rx=3))
    out.append(text(120, ly, ["екран із нижньої навігації"], size=11, anchor="start"))
    out.append(box(300, ly, 26, 14, [""], fill=PANEL, rx=3))
    out.append(text(320, ly, ["розділ / стан екрана"], size=11, anchor="start"))
    out.append(box(470, ly, 26, 14, [""], fill=PANEL, rx=3, dash=True))
    out.append(text(490, ly, ["перехід на вже існуючий екран"], size=11, anchor="start"))
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- USER FLOW
def user_flow():
    cx, W, H = 330, 230, 46
    o = ['<svg viewBox="0 0 760 960" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="User flow Cassiopeia">', DEFS]

    def pill(cy, lines, fill=NAVY, color=CREAM, stroke=NAVY, x=cx, w=W):
        return box(x, cy, w, 40, lines, fill=fill, stroke=stroke, color=color, rx=20, weight=700)

    # основна колонка
    o.append(pill(34, ["Старт: відкриття Cassiopeia"]))
    o.append(box(cx, 104, W, H, ["Екран Today", "(порожній стан або Top 3)"], fill=CREAM))
    o.append(box(cx, 174, W, H, ["Перехід у Chat", "(нижня навігація)"]))
    o.append(box(cx, 244, W, H, ["Ввід вільного тексту:", "«Сьогодні звіт до 18:00…»"]))
    o.append(box(cx, 314, W, H, ["Надсилання повідомлення", "ШІ аналізує (loading)"]))
    o.append(diamond(cx, 398, 250, 80, ["ШІ розпізнав", "завдання?"]))
    o.append(box(cx, 490, W, H, ["Картка плану:", "завдання, строки, пріоритет"], fill=CREAM))
    o.append(diamond(cx, 574, 250, 80, ["План влаштовує?"]))
    o.append(box(cx, 662, W, H, ["Підтвердження плану"]))
    o.append(box(cx, 732, W, H, ["Екран Today:", "Top 3 і оновлений список"], fill=CREAM))
    o.append(diamond(cx, 822, 260, 80, ["Дія із завданням?"]))

    # стрілки вниз
    for y0, y1 in [(54, 81), (127, 151), (197, 221), (267, 291), (337, 358)]:
        o.append(line(f"M{cx} {y0} V{y1}"))
    o.append(line(f"M{cx} 438 V467"))
    o.append(label(cx + 8, 457, "Так", "start"))
    o.append(line(f"M{cx} 513 V534"))
    o.append(line(f"M{cx} 614 V639"))
    o.append(label(cx + 8, 631, "Так", "start"))
    o.append(line(f"M{cx} 685 V709"))
    o.append(line(f"M{cx} 755 V782"))

    # гілка F: ні
    o.append(line(f"M{cx + 125} 398 H520"))
    o.append(label(488, 391, "Ні"))
    o.append(box(635, 398, 230, 46, ["Відповідь ШІ: «Уточни,", "що саме треба зробити»"], fill=PANEL, stroke=GOLD))
    o.append(line(f"M635 375 V244 H{cx + W / 2}", dash=True))
    o.append(label(646, 320, "повтор вводу", "start", GRAY))

    # гілка H: ні
    o.append(line(f"M{cx + 125} 574 H520"))
    o.append(label(488, 567, "Ні"))
    o.append(box(635, 574, 230, 46, ["Редагування: назва,", "час, пріоритет"], fill=PANEL, stroke=GOLD))
    o.append(line(f"M635 551 V490 H{cx + W / 2}", dash=True))
    o.append(label(646, 524, "картку оновлено", "start", GRAY))

    # кінцеві стани
    o.append(line(f"M{cx - 130} 822 H128"))
    o.append(label(166, 814, "Виконано"))
    o.append(box(68, 822, 116, 56, ["✔ Кінець:", "завдання", "виконано"], fill=GREEN, stroke=GREEN, color=CREAM, weight=700))
    o.append(line(f"M{cx} 862 V896"))
    o.append(label(cx + 8, 884, "Перенести", "start"))
    o.append(box(cx, 925, 300, 52, ["↷ Кінець: завдання перенесено", "на наступний слот (є «Скасувати»)"], fill=GOLD, stroke=GOLD, color=NAVY, weight=700))
    o.append(line(f"M{cx + 130} 822 H520"))
    o.append(label(488, 814, "Збій"))
    o.append(box(635, 822, 230, 62, ["⚠ Кінець: помилка мережі", "Повідомлення «Спробуй ще»,", "дані не змінено"], fill=DANGER, stroke=DANGER, color=CREAM, weight=700))
    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    import pathlib

    out = pathlib.Path(__file__).parent / "build"
    out.mkdir(exist_ok=True)
    (out / "sitemap.svg").write_text(sitemap(), encoding="utf-8")
    (out / "user-flow.svg").write_text(user_flow(), encoding="utf-8")
    print("ok")
