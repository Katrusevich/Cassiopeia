"""Збирає звіт ПЗ2: підставляє діаграми й мудборд у template.html та друкує PDF через Chrome.

Запуск:  python report/build.py
Результат: report/build/report.html (самодостатній, скріншоти вбудовані) і report.pdf.
Скріншоти мудборду лежать у report/moodboard/01 … 08 (png/jpg/webp).
"""
import base64
import mimetypes
import pathlib
import re
import subprocess
import sys

from diagrams import sitemap, user_flow

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "build"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# (назва, сайт, що приваблює, що беремо в Cassiopeia)
MOODBOARD = [
    ("Aesop", "aesop.com",
     "Світлий кремовий фон, дуже багато повітря, продукт у центрі. Заголовки легкі, текст — чистий гротеск. Темні прямокутні кнопки на всю ширину картки й приглушені бурштинові мітки.",
     "Кремовий фон, великі відступи, суворі темні кнопки."),
    ("Kinfolk", "kinfolk.com",
     "Редакційна подача: serif-заголовок із тонкою лінією-розділювачем, дрібний рядок категорії над назвою, акуратна сітка однакових карток.",
     "Типографічну ієрархію й тонкі лінії-розділювачі між секціями."),
    ("Ralph Lauren", "ralphlauren.com",
     "Класичний serif-логотип із великим міжлітерним інтервалом, великі serif-заголовки, посилання великими літерами з підкресленням замість кнопок.",
     "Serif-заголовки та великі літери з розрядкою для мітки над заголовком (eyebrow)."),
    ("Sunsama", "sunsama.com",
     "Екран «Сьогодні»: картки завдань із часом початку й тривалістю, кружечок-чекбокс, смуга прогресу дня, поруч календар-таймлайн.",
     "Структуру картки завдання (час, тривалість, статус) і ідею Today + таймлайн. Яскраві кольори не беремо."),
    ("Things 3", "culturedcode.com/things",
     "Мінімалістичні списки з прямокутними чекбоксами, дрібний сірий підпис проєкту під завданням, групи «This Evening», кругла кнопка «+».",
     "Вигляд списку завдань, групування за часом дня й швидке додавання."),
    ("Claude", "claude.ai",
     "Привітання serif-шрифтом по центру, великий закруглений інпут як єдиний фокус екрана, акуратні картки з мініатюрами нижче.",
     "Структуру екрана Chat: одне велике поле вводу, привітання, мінімум елементів."),
    ("Day One", "dayoneapp.com",
     "Список записів із великою датою зліва (день тижня й число) і широкою зоною читання. Інтерфейс відступає на другий план.",
     "Блок дати для екранів Day / Week і спокійну зону тексту для Vision & Mission."),
    ("Notion Calendar", "notion.com/calendar",
     "Чисті сітки місяця й тижня, виразна позначка сьогоднішнього дня (червоне коло), події з кольоровою смужкою зліва, пластини-картки з жирними заголовками.",
     "Позначку «сьогодні» та чисту сітку для Week і Month."),
]


def data_uri(path):
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def moodboard_html():
    cards = []
    for i, (name, site, attracts, take) in enumerate(MOODBOARD, 1):
        shot = f"<span>Скріншот: {name}</span>"
        for ext in ("png", "jpg", "jpeg", "webp"):
            p = ROOT / "moodboard" / f"{i:02d}.{ext}"
            if p.exists():
                shot = f'<img src="{data_uri(p)}" alt="{name}">'
                break
        cards.append(
            f'<div class="card"><div class="shot">{shot}</div>'
            f'<h3>{i}. {name} <span style="font-weight:400;color:#6A717D">· {site}</span></h3>'
            f"<p><b>Приваблює:</b> {attracts}</p><p><b>Беремо:</b> {take}</p></div>"
        )
    return "\n".join(cards)


def embed_shots(html):
    """Замінює src="@shot/name" на data-URI зі скріншота ui-shots/name.png."""
    return re.sub(r'src="@shot/([\w-]+)"', lambda m: f'src="{data_uri(ROOT / "ui-shots" / (m.group(1) + ".png"))}"', html)


def main():
    OUT.mkdir(exist_ok=True)
    html = (ROOT / "template.html").read_text(encoding="utf-8")
    part4 = ROOT / "part4.html"
    html = (
        html.replace("{{SITEMAP}}", sitemap())
        .replace("{{FLOW}}", user_flow())
        .replace("{{MOODBOARD}}", moodboard_html())
        .replace("{{PART4}}", part4.read_text(encoding="utf-8") if part4.exists() else "")
    )
    html = embed_shots(html)
    page = OUT / "report.html"
    page.write_text(html, encoding="utf-8")
    pdf = OUT / "report.pdf"
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=15000", f"--print-to-pdf={pdf}", page.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print("PDF:", pdf)


if __name__ == "__main__":
    sys.exit(main())
