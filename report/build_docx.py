"""Збирає ПЗ2 у .docx на основі чернетки команди (report/draft/draft.docx).

Оформлення, титулка, Частина 1 і текст user flow беруться з чернетки без змін;
sitemap, мудборд, Частина 4 і висновок будуються заново під реальний код (ui-kit/)
та скріншоти (report/moodboard, report/ui-shots).

Запуск:  python report/build_docx.py   →   report/build/ПЗ2_Cassiopeia.docx
"""
import io
import json
import pathlib
import re
import subprocess
import zipfile

from PIL import Image

from diagrams import sitemap

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "build"
DRAFT = ROOT / "draft" / "draft.docx"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEXT_W = 5731510  # ширина тексту на сторінці, EMU
EMU_CM = 360000

# ------------------------------------------------------------------ чернетка
zin = zipfile.ZipFile(DRAFT)
doc_xml = zin.read("word/document.xml").decode("utf8")
b0 = doc_xml.index("<w:body>") + 8
b1 = doc_xml.rindex("</w:body>")
PREFIX, SUFFIX = doc_xml[:b0], doc_xml[b1:]
body = doc_xml[b0:b1]
blocks, i = [], 0
while i < len(body):
    if body.startswith("<w:tbl>", i):
        j = body.index("</w:tbl>", i) + 8
    elif body.startswith("<w:sectPr", i):
        j = body.index("</w:sectPr>", i) + 11
    else:
        j = body.index("</w:p>", i) + 6
    blocks.append(body[i:j])
    i = j
SECT = blocks[-1]


# ------------------------------------------------------------------ XML-хелпери
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


FONT = '<w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/>'


def run(text, sz=28, b=False, i=False, u=False, mono=False):
    font = '<w:rFonts w:ascii="Consolas" w:cs="Consolas" w:hAnsi="Consolas"/>' if mono else FONT
    props = font + ("<w:b/><w:bCs/>" if b else "") + ("<w:i/><w:iCs/>" if i else "")
    props += '<w:u w:val="single"/>' if u else ""
    props += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    return f'<w:r><w:rPr>{props}</w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def body_p(*parts):
    """Звичайний абзац; parts — рядки або (текст, {b:1}) кортежі."""
    runs = "".join(run(p) if isinstance(p, str) else run(p[0], **p[1]) for p in parts)
    return ('<w:p><w:pPr><w:spacing w:after="0" w:before="0" w:line="360"/><w:ind w:firstLine="709"/>'
            f'<w:jc w:val="both"/></w:pPr>{runs}</w:p>')


def heading(level, text):
    if level == 1:
        return ('<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:spacing w:before="240" w:after="240" w:line="360" w:lineRule="auto"/>'
                '<w:ind w:firstLine="709"/><w:jc w:val="both"/></w:pPr>' + run(text, b=True, u=True) + "</w:p>")
    return ('<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto"/>'
            '<w:ind w:firstLine="709"/></w:pPr>' + run(text, b=True, i=True) + "</w:p>")


def table_caption(text):
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="0" w:line="360" w:lineRule="auto"/><w:jc w:val="right"/></w:pPr>'
            + run(text, u=True) + "</w:p>")


def fig_caption(text):
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="240" w:line="360" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>'
            + run(text, u=True) + "</w:p>")


def item_title(text):
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="0" w:line="360" w:lineRule="auto"/><w:ind w:firstLine="709"/>'
            '<w:jc w:val="both"/></w:pPr>' + run(text, i=True, u=True) + "</w:p>")


def list_item(text, num_id=2):
    return (f'<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr>'
            '<w:spacing w:after="0" w:line="360" w:lineRule="auto"/><w:ind w:left="0" w:firstLine="709"/><w:jc w:val="both"/></w:pPr>'
            + run(text) + "</w:p>")


def code_p(lines):
    out = ""
    for ln in lines:
        out += ('<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/><w:spacing w:after="0" w:before="0" w:line="260"/>'
                '<w:ind w:left="709"/></w:pPr>' + run(ln, sz=20, mono=True) + "</w:p>")
    return out + '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>'


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


# ------------------------------------------------------------------ таблиці
def cell(text, w, head=False, shade=False, bold=False):
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="CCCCCC"/>' if (shade and not head) else ""
    jc = '<w:jc w:val="center"/>' if head else ""
    r = run(text, sz=22, b=head or bold, i=head or bold)
    return (f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{w}"/><w:tcBorders>'
            + "".join(f'<w:{s} w:val="single" w:color="666666" w:sz="4"/>' for s in ("top", "left", "bottom", "right"))
            + f'</w:tcBorders>{shd}<w:tcMar><w:top w:type="dxa" w:w="60"/><w:left w:type="dxa" w:w="100"/>'
              f'<w:bottom w:type="dxa" w:w="60"/><w:right w:type="dxa" w:w="100"/></w:tcMar></w:tcPr>'
              f'<w:p><w:pPr><w:spacing w:line="252"/>{jc}</w:pPr>{r}</w:p></w:tc>')


def table(rows, widths):
    """rows[0] — заголовок; перший стовпець виділено сірим, як у чернетці."""
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    out = ('<w:tbl><w:tblPr><w:tblW w:type="dxa" w:w="9026"/><w:tblBorders>'
           + "".join(f'<w:{s} w:val="single" w:color="auto" w:sz="4"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
           + f"</w:tblBorders></w:tblPr><w:tblGrid>{grid}</w:tblGrid>")
    for n, row in enumerate(rows):
        out += "<w:tr>" + ("<w:trPr><w:tblHeader/></w:trPr>" if n == 0 else '<w:trPr><w:cantSplit/></w:trPr>')
        for c, (text, w) in enumerate(zip(row, widths)):
            out += cell(text, w, head=n == 0, shade=(c == 0), bold=(c == 0 and n > 0))
        out += "</w:tr>"
    return out + "</w:tbl>" + '<w:p><w:pPr><w:spacing w:after="0" w:before="0"/></w:pPr></w:p>'


# ------------------------------------------------------------------ зображення
media = {}  # ім'я файла в docx -> bytes
rels = []  # (rId, target)
_ids = {"doc": 1000, "rid": 100}


def add_image(img, name, max_w=1500):
    """img — PIL.Image; повертає (rId, w_px, h_px)."""
    img = img.convert("RGB")
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88)
    fname = f"media/{name}.jpg"
    media[fname] = buf.getvalue()
    _ids["rid"] += 1
    rid = f"rId{_ids['rid']}"
    rels.append((rid, fname))
    return rid, img.width, img.height


def drawing(rid, w_px, h_px, width_cm):
    cx = int(width_cm * EMU_CM)
    cx = min(cx, TEXT_W)
    cy = int(cx * h_px / w_px)
    _ids["doc"] += 1
    return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:effectExtent t="0" r="0" b="0" l="0"/><wp:docPr id="{_ids["doc"]}" name="Image{_ids["doc"]}" descr=""/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
            '</wp:cNvGraphicFramePr><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr>'
            f'<pic:cNvPr id="{_ids["doc"]}" name="Image{_ids["doc"]}" descr=""/><pic:cNvPicPr><a:picLocks noChangeAspect="1"/></pic:cNvPicPr></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>")


def image_p(img, name, width_cm=15.9, max_h_cm=None):
    rid, w, h = add_image(img, name)
    if max_h_cm:
        width_cm = min(width_cm, max_h_cm * w / h)
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:after="60" w:before="120"/><w:jc w:val="center"/></w:pPr>'
            + drawing(rid, w, h, width_cm) + "</w:p>")


def grid(items, cols, width_cm):
    """items: [(img, name, підпис)] у таблиці без рамок; підписи дрібним шрифтом."""
    cw = 9026 // cols
    out = ('<w:tbl><w:tblPr><w:tblW w:type="dxa" w:w="9026"/><w:jc w:val="center"/></w:tblPr><w:tblGrid>'
           + f'<w:gridCol w:w="{cw}"/>' * cols + "</w:tblGrid>")
    for r in range(0, len(items), cols):
        out += '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
        for k in range(cols):
            out += f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{cw}"/></w:tcPr>'
            if r + k < len(items):
                img, name, cap = items[r + k]
                out += image_p(img, name, width_cm).replace("<w:keepNext/>", "")
                out += ('<w:p><w:pPr><w:spacing w:after="120" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>'
                        + run(cap, sz=20) + "</w:p>")
            else:
                out += "<w:p/>"
            out += "</w:tc>"
        out += "</w:tr>"
    return out + "</w:tbl>" + '<w:p><w:pPr><w:spacing w:after="0" w:before="0"/></w:pPr></w:p>'


def shot(name):
    return Image.open(ROOT / "ui-shots" / f"{name}.png")


def mood(n):
    for ext in ("png", "jpg", "webp"):
        p = ROOT / "moodboard" / f"{n:02d}.{ext}"
        if p.exists():
            return Image.open(p)
    raise FileNotFoundError(n)


# sitemap: SVG → PNG через Chrome
def sitemap_png():
    svg = sitemap()
    h = int(re.search(r'viewBox="0 0 740 (\d+)', svg).group(1))
    OUT.mkdir(exist_ok=True)
    html = OUT / "sitemap.html"
    html.write_text(f'<html><body style="margin:0;background:#fff">{svg.replace("<svg ", "<svg width=740 height=%d " % h, 1)}</body></html>', encoding="utf8")
    png = OUT / "sitemap.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size=740,{h}", f"--screenshot={png}", html.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(png)


# ------------------------------------------------------------------ зміст
def txt(b):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", b))


def keep(a, b_=None, replace=()):
    out = "".join(blocks[a:(b_ + 1) if b_ is not None else a + 1])
    for old, new in replace:
        assert old in out, old
        out = out.replace(old, new)
    return out


def build_body():
    out = []
    # --- Титулка, вступ, Частина 1 (без змін, окрім заповнених місць)
    out.append(keep(0, 44))                  # титулка, мета, Частина 1 до таблиці 1
    out.append(keep(45, 54))                 # таблиці 1–2 і заголовок «Оцінка інструментів»
    out.append(body_p("Щоб вибір не виглядав «на око», оцінюємо чотири основні інструменти за п’ятибальною шкалою за критеріями, "
                      "важливими саме для нашого проєкту."))
    out.append(table_caption("Таблиця 3. Оцінка інструментів (1 – погано, 5 – відмінно)"))
    scores = [
        ("UI-kit і компоненти зі станами", 5, 4, 3, 5),
        ("Реальна інтерактивність і навігація", 3, 4, 4, 5),
        ("Повторне використання в ПЗ № 3", 1, 3, 2, 5),
        ("Контроль над структурою коду", 1, 3, 2, 5),
        ("Поріг входу для команди", 4, 4, 4, 3),
        ("Безкоштовний доступ", 4, 3, 2, 1),
    ]
    rows = [["Критерій", "Figma", "v0", "Lovable", "Claude Code"]] + [[s[0], *map(str, s[1:])] for s in scores]
    rows.append(["Разом (з 30)"] + [str(sum(s[k] for s in scores)) for k in (1, 2, 3, 4)])
    out.append(table(rows, [3626, 1350, 1350, 1350, 1350]))
    out.append(body_p("Найбільше балів набрав Claude Code (24 з 30). Він випереджає решту там, де для нас важливіше за все: "
                      "компоненти зі станами, справжня навігація, повторне використання коду в ПЗ № 3 і контроль над структурою. "
                      "Програє він лише за безкоштовним доступом і порогом входу, адже потрібна підписка та базова робота з терміналом. "
                      "Figma, навпаки, найдоступніша, але її макет у ПЗ № 3 доведеться реалізовувати в коді заново."))
    out.append(keep(59))                     # заголовок «Обраний інструмент…»
    out.append(body_p("Цю роботу зроблено за допомогою Claude Code: він створив design tokens, компоненти зі stories для Storybook "
                      "та екрани прямо в репозиторії Cassiopeia."))
    out.append(keep(61))
    out.append(body_p("Уточнимо, що саме ми «розвиваємо». UI-kit і прототип зроблено як новий фронтенд у папці ui-kit/ на основі палітри "
                      "та екранів наявного застосунку (FastAPI із шаблонами). До бекенду й справжнього ШІ-агента його буде підключено "
                      "в ПЗ № 3."))
    out.append(keep(62, 81))                 # решта обґрунтування + джерела

    # --- Частина 2
    out.append(keep(82))
    out.append(body_p(
        "Структуру застосунку ми виводили з функцій MVP, описаних у PRD. Головне рішення, на якому тримається вся архітектура, – центр "
        "Cassiopeia не меню і не календар, а чат. Майже будь-яка дія (додати справу, перенести її, змінити пріоритет чи навіть оцінити "
        "сферу життя в Колесі балансу) починається з розмови. Решта розділів, по суті, показує результат цієї розмови в зручному, "
        "структурованому вигляді. Схеми user flow побудовано в draw.io, а sitemap зведено за реальною навігацією прототипу з Частини 4."))
    out.append(keep(84))                     # Sitemap
    out.append(body_p("Sitemap вийшов трирівневим. Нагорі – сам застосунок, під ним – шість розділів нижньої навігації (Today, Week, "
                      "Month, Year, Wheel, Chat), а всередині розділів – окремі екрани та стани. Vision & Mission і Task Tracker "
                      "відкриваються з Wheel of Balance, а деталі дня (Day) – з Week і Month."))
    out.append(image_p(sitemap_png(), "sitemap", 15.9))
    out.append(fig_caption("Рисунок 1. Sitemap Cassiopeia"))
    out.append(body_p("Ядро продукту – Chat та Today: з ними користувач працює щодня. У чаті справи з’являються, на Today – "
                      "стають планом із Top 3. Week, Month і Year потрібні, щоб бачити день у контексті тижня, місяця й року: саме "
                      "тут видно справи, які не вмістилися в реалістичний план і були перенесені. Wheel of Balance та Vision & "
                      "Mission відкриваються рідше, проте саме вони дають системі контекст – що для людини важливо, – без якого "
                      "вибір Top 3 зводився б до звичайного сортування за дедлайном."))
    out.append(body_p("Щоб було зрозуміло, як між цими розділами рухатися, ми окремо розписали точки входу та основні дії:"))
    out.append(table_caption("Таблиця 4. Навігація між розділами"))
    out.append(table([
        ["Розділ", "Як потрапити", "Основні дії"],
        ["Chat", "Нижня навігація; кнопка «Plan with chat» на Today", "Описати справи, перевірити картку плану, виправити назви, підтвердити"],
        ["Today", "Нижня навігація; автоматично після підтвердження плану", "Переглянути Top 3, відмітити виконане, перенести завдання (з Undo), швидко додати справу"],
        ["Week", "Нижня навігація", "Переглянути сім днів із завданнями"],
        ["Month", "Нижня навігація; плитка місяця на екрані Year", "Обрати день у календарі й переглянути його завдання (Day)"],
        ["Year", "Нижня навігація", "Побачити навантаження за місяцями, перейти в потрібний місяць"],
        ["Wheel of Balance", "Нижня навігація", "Переглянути радар, Priority Board, AI-інсайти; перейти у Vision & Mission чи Task Tracker"],
        ["Vision & Mission / Task Tracker", "Кнопки на екрані Wheel", "Редагувати текст «чому я планую»; переглянути ефективність за часом; «Back to Wheel»"],
    ], [2100, 3200, 3726]))
    out.append(body_p("Зверніть увагу: до чату веде кілька шляхів – з нижньої навігації та з кнопки «Plan with chat» на Today, "
                      "зокрема й з порожнього стану цього екрана. Це навмисно. Якщо щось пішло не за планом, користувач має дістатися "
                      "до перепланування в один дотик, а не шукати потрібний розділ."))
    out.append(keep(93, 94))
    out.append(body_p("Схема нижче описує цільовий сценарій повної версії продукту. У прототипі Частини 4 реалізовано його центральну "
                      "частину, про що сказано після опису розгалужень."))
    out.append(keep(95, 96, replace=[("Рисунок 2. User flow «від хаосу в голові до плану дня»",
                                      "Рисунок 2. User flow «від хаосу в голові до плану дня» (цільовий сценарій)")]))
    out.append(keep(97, 102))                # опис розгалужень (без змін)
    out.append(body_p("У прототипі реалізовано центральну частину цього сценарію: від чату через картку плану до екрана Today, а також "
                      "виконання й перенесення завдання з можливістю скасування (Undo). Реєстрація, онбординг, розділ «Заплановані», "
                      "уточнювальні запитання та перепланування через чат у прототип не входять, а перенесені справи користувач бачить у "
                      "Week на наступний день. Проходження сценарію крок за кроком описано в Частині 4."))
    out.append(keep(103, 105))               # заголовок, вступ і рисунок user flow 2
    out.append(keep(106, 106, replace=[("Рисунок 3. User flow «оцінка Колеса балансу»",
                                        "Рисунок 3. User flow «оцінка Колеса балансу» (цільовий сценарій)")]))
    out.append(keep(107))                    # опис user flow 2 (без змін)
    out.append(body_p("У прототипі реалізовано результат цього сценарію: радар із вісьмома сферами на шкалі 1–9 і Priority Board із трьома "
                      "найслабшими сферами та підказкою дії. Послідовний діалог оцінювання й історія змін у прототип не входять."))

    # --- Частина 3
    out.append(keep(109))
    out.append(body_p(
        "Збираючи мудборд, ми відштовхувалися від головної ідеї продукту – менше розумового навантаження. Якщо застосунок обіцяє "
        "зняти хаос із голови, то сам він точно не має виглядати хаотично. Тому шукали інтерфейси спокійні, з великою кількістю "
        "повітря, чіткою ієрархією й мінімумом елементів на екрані. Стиль Cassiopeia ми визначили як «Old Money»: теплий кремовий "
        "фон, глибокий синій, темно-зелений і золотий акцент, а для заголовків – serif із характером. Перші три референси задають "
        "настрій і типографіку, решта п’ять – це робочі інтерфейси планувальників і чату, з яких ми беремо структуру екранів, але "
        "не їхню яскраву палітру."))
    items = [
        ("1. Aesop (aesop.com)", 1,
         "Світлий кремовий фон і дуже багато повітря: товар стоїть у центрі, а інтерфейс «мовчить». Заголовки легкі, основний текст – "
         "чистий гротеск, кнопки – темні прямокутні на всю ширину картки, а службові мітки (наприклад, «Limited release») – "
         "приглушеного бурштинового кольору. Від Aesop ми беремо відчуття дорогої тиші: кремовий фон, великі відступи, стримані темні кнопки."),
        ("2. Kinfolk (kinfolk.com)", 2,
         "Редакційна подача: serif-заголовок із тонкою лінією-розділювачем, дрібний рядок категорії над назвою матеріалу, акуратна "
         "сітка однакових карток. Звідси – типографічна ієрархія й тонкі лінії між секціями, які ми використовуємо в заголовках екранів."),
        ("3. Ralph Lauren (ralphlauren.com)", 3,
         "Класичний serif-логотип із великим міжлітерним інтервалом, великі serif-заголовки та посилання великими літерами з підкресленням "
         "замість звичайних кнопок. Ми беремо serif-заголовки та дрібні мітки великими літерами з розрядкою над заголовком (у UI-kit це "
         "стиль eyebrow), а також поєднання темно-синього з теплими акцентами."),
        ("4. Sunsama (sunsama.com)", 4,
         "Екран «Сьогодні» з картками завдань, де видно час початку й тривалість, кружечком-чекбоксом, смугою прогресу дня й календарем-"
         "таймлайном поруч. Для Cassiopeia це орієнтир структури картки завдання та екрана Today. Яскраві кольори ми не беремо."),
        ("5. Things 3 (culturedcode.com/things)", 5,
         "Мінімалістичні списки з прямокутними чекбоксами, дрібним сірим підписом проєкту під назвою завдання, групами за часом дня "
         "(наприклад, «This Evening») і круглою кнопкою «+». Беремо вигляд списку завдань, групування й швидке додавання."),
        ("6. Claude (claude.ai)", 6,
         "Привітання serif-шрифтом по центру, великий закруглений інпут як єдиний фокус екрана й акуратні картки з мініатюрами нижче. "
         "Оскільки головний екран у нас – чат, без цього референсу не обійтися: одне велике поле введення й мінімум елементів – "
         "люди вже звикли до такого формату, і ламати цю звичку немає сенсу."),
        ("7. Day One (dayoneapp.com)", 7,
         "Список записів із великою датою зліва (день тижня й число) та широкою зоною читання; інтерфейс відступає на другий план. "
         "Беремо блок дати для екранів Week і Day та спокійну зону тексту для Vision & Mission."),
        ("8. Notion Calendar (notion.com/calendar)", 8,
         "Чисті сітки місяця й тижня, виразна позначка сьогоднішнього дня (червоне коло), події з кольоровою смужкою зліва та "
         "пластини-картки з жирними заголовками. Беремо позначку «сьогодні» й чисту сітку для екранів Week і Month."),
    ]
    for title, n, text in items:
        out.append(item_title(title))
        out.append(image_p(mood(n), f"mood{n}", 14.5, max_h_cm=7.5))
        out.append(body_p(text))
    out.append(body_p("Джерела: aesop.com, kinfolk.com, ralphlauren.com, sunsama.com, culturedcode.com/things, claude.ai, "
                      "dayoneapp.com, notion.com/calendar (скріншоти зроблено в листопаді 2026 р.)."))
    out.append(keep(141, 143))               # Висновок мудборду + вступ + підпис таблиці 5
    out.append(table([
        ["Референс", "Що беремо", "Де використовуємо"],
        ["Aesop, Kinfolk", "Кремовий фон, повітря, serif-заголовки, тонкі лінії-розділювачі", "Загальний фон, заголовки екранів, картки"],
        ["Ralph Lauren", "Serif-заголовки, дрібні великі літери з розрядкою, поєднання navy з теплими акцентами", "Primary navy, стиль eyebrow над заголовком"],
        ["Sunsama", "Картка завдання з часом і тривалістю, смуга прогресу дня", "Екран Today, компоненти TaskItem і ProgressBar"],
        ["Things 3", "Чекбокси, мінімалістичні списки, групування за часом", "TaskItem, списки на Week і Month"],
        ["Claude", "Привітання, велике поле введення, мінімум елементів", "Екран Chat, компонент Input"],
        ["Day One", "Блок дати, широка зона читання", "Day, Vision & Mission"],
        ["Notion Calendar", "Чиста сітка, позначка «сьогодні»", "Екрани Week і Month"],
    ], [2248, 3184, 3594]))
    out.append(body_p(
        "Виявилося, що при всій різноманітності в цих прикладів чимало спільного. Світлий фон і лише один-два виразні акцентні "
        "кольори. Чіткий гротеск для тексту й виразний serif для заголовків. Великі відступи, м’які заокруглення карток і кнопок, "
        "мінімум елементів на екрані. Саме ці рішення ми й переносимо в UI-kit: темно-синій стає primary, темно-зелений – secondary, "
        "нейтральні кремові відтінки відповідають за фон і поверхні, а для успіху, помилки та попередження заведено окремі "
        "семантичні кольори. Золотий акцент ми приберегли для виділення головного: фон картки Top 3, мітки часу й дрібні заголовки "
        "над розділами, щоб головні справи дня справді впадали в око."))
    out.append(image_p(shot("colors"), "palette", 12.5, max_h_cm=15))
    out.append(fig_caption("Рисунок 4. Палітра Cassiopeia, виведена з мудборду (Storybook, Foundations → Colors)"))
    return out


def build_part4():
    o = []
    o.append(heading(1, "Частина 4 – UI-kit та прототип екранів (Варіант B)"))
    o.append(keep(149))
    o.append(body_p("Результат Частини 4 – працююче рішення в репозиторії; нижче наведено посилання, стек і порядок запуску."))
    o.append(body_p(("Посилання на репозиторій: ", {"b": True}), "https://github.com/Katrusevich/Cassiopeia (код UI-kit – у папці ui-kit/)."))
    o.append(body_p(("Стек: ", {"b": True}), "React 19, Vite 8, Storybook 10, іконки lucide-react. Стилі – чистий CSS без фреймворків, "
                    "побудований на design tokens; мова – JavaScript."))
    o.append(body_p(("Інструкція запуску:", {"b": True})))
    for t in ["Клонувати репозиторій: git clone https://github.com/Katrusevich/Cassiopeia.git",
              "Перейти в папку UI-kit і встановити залежності: cd ui-kit, потім npm install",
              "Запустити Storybook: npm run storybook (відкриється на http://localhost:6006)",
              "Запустити клікабельний прототип: npm run dev (відкриється на http://localhost:5173)"]:
        o.append(list_item(t, 3))
    o.append(body_p("Прототип також доступний усередині Storybook як історія Screens → Prototype. Для статичної збірки Storybook "
                    "є команда npm run build-storybook."))

    o.append(heading(2, "Як ми працювали"))
    o.append(body_p("Порядок роботи був таким. Спочатку ми винесли всі візуальні значення в один файл tokens.css, і лише потім писали "
                    "компоненти, а після них – екрани. Правило для Claude Code було одне: жодних кольорів чи відступів у самих "
                    "компонентах, лише змінні з tokens.css. Дотримання перевірили пошуком по коду: hex-коди зустрічаються тільки в "
                    "tokens.css. Кожен компонент одразу супроводжується stories у Storybook, а екрани складаються виключно з цих "
                    "компонентів. Результат перевірено в браузері: пройдено весь сценарій від чату до перенесення завдання."))

    o.append(heading(2, "UI-kit"))
    o.append(body_p("Design tokens ми не вигадували окремо – їх виведено з мудборду й палітри застосунку, що вже існувала (рисунок 4), "
                    "тож UI-kit і мудборд говорять однією візуальною мовою. Усі значення живуть в одному файлі tokens.css у три шари: "
                    "primitives (сира палітра), semantic (ролі: primary, surface, text, success…) і themes (перепризначення ролей). "
                    "Компоненти посилаються лише на семантичні токени, тому змінити вигляд продукту можна в одному місці."))
    o.append(table_caption("Таблиця 6. Design tokens"))
    o.append(table([
        ["Група", "Токени", "Значення"],
        ["Primary", "--color-primary, -hover, -active, --color-on-primary", "Navy #1A2639 → #2B3B55 → #0F1826; текст на ньому #F8F5EE"],
        ["Secondary", "--color-secondary, -hover, -active", "Forest green #2C4C3B → #3F6B53 → #1F3829"],
        ["Accent", "--color-accent, -strong, -soft", "Золото #C9A227, #A8851A, світлий фон #F6EDC9"],
        ["Neutral", "--color-bg, surface, surface-alt, border, text, text-muted, disabled-*", "Кремові #F0EAD6 / #F8F5EE / #EBE5D9, camel #D4BD9E, сірий текст #6A717D"],
        ["Semantic", "--color-success, error, warning (+ -bg)", "#2F6B45, #8B3A3A, #8A5A0B на приглушених фонах"],
        ["Типографіка", "--font-heading, --font-body, --fs-h1 … --fs-caption", "Playfair Display / Lato; H1 28–36 px, H2 24, H3 20, body 16, small 14, caption 12"],
        ["Відступи", "--space-1 … --space-8", "Крок 4 px: 4, 8, 12, 16, 24, 32, 48, 64"],
        ["Форма", "--radius-sm/md/lg/xl, --shadow-sm/md", "8, 15, 20, 30 px; м’які тіні кольору navy"],
    ], [1500, 3500, 4026]))
    o.append(image_p(shot("typography"), "typography", 15.9))
    o.append(fig_caption("Рисунок 5. Типографічна шкала: H1–H3, body, small, caption, eyebrow (Storybook, Foundations → Typography)"))
    o.append(image_p(shot("spacing"), "spacing", 13.5, max_h_cm=12))
    o.append(fig_caption("Рисунок 6. Відступи, радіуси та тіні (Storybook, Foundations → SpacingAndShape)"))

    o.append(body_p("Щоб компоненти поводилися передбачувано, для всіх станів діють спільні правила:"))
    o.append(table_caption("Таблиця 7. Правила станів компонентів"))
    o.append(table([
        ["Стан", "Правило"],
        ["default", "primary – фон navy #1A2639, текст #F8F5EE; secondary – фон forest green #2C4C3B; outline – рамка navy на прозорому фоні; ghost – без рамки; danger – #8B3A3A"],
        ["hover", "primary #2B3B55; secondary #3F6B53; outline і ghost – фон #EBE5D9; danger яскравішає; у поля рамка стає navy; в інтерактивної картки – рамка navy і тінь"],
        ["active", "primary #0F1826; secondary #1F3829; кнопка зміщується на 1 px вниз"],
        ["focus", "обведення 2 px золотого кольору #C9A227 з відступом 2 px; у поля – рамка #A8851A і світлий ореол #F6EDC9"],
        ["disabled", "фон #EBE5D9, текст #A5AAB3, курсор not-allowed"],
        ["error (input)", "рамка та підказка кольору #8B3A3A, ореол #F2DEDC"],
    ], [1800, 7226]))
    o.append(body_p("Окремо про focus. Його часто пропускають, а дарма: людина, яка працює з клавіатури, інакше просто не бачить, де вона "
                    "зараз. Тому обведення в нас помітне, золотого кольору, і з невеликим відступом від самого елемента. Стани hover, "
                    "active і focus додатково доступні як класи .is-hover, .is-active, .is-focus, тому в Storybook усі стани видно "
                    "в одній таблиці без наведення миші."))

    o.append(table_caption("Таблиця 8. Компоненти UI-kit у Storybook"))
    o.append(table([
        ["Елемент", "Що показано в Storybook", "Скріншот"],
        ["Кольори (tokens)", "primary, secondary, accent, neutral, success, error, warning з hex-значеннями; перемикач теми", "рис. 4"],
        ["Типографіка", "H1, H2, H3, body, small, caption, eyebrow", "рис. 5"],
        ["Button", "primary, secondary, outline, ghost, danger; sm / md / lg; default, hover, active, focus, disabled", "рис. 7"],
        ["Input (у коді – Field)", "default, hover, focus, error (з повідомленням), disabled; textarea для чату", "рис. 8"],
        ["Card", "default, elevated, accent, interactive (hover), з блоком дій", "рис. 9"],
        ["TaskItem", "звичайне, Top 3, виконане, перенесене; чекбокс, час, кнопка переносу", "рис. 10"],
        ["Navigation", "меню шести розділів з активним, hover і вимкненим пунктами", "рис. 11"],
        ["ChatMessage", "повідомлення користувача й асистента, індикатор «ШІ думає»", "рис. 12"],
        ["Badge, ProgressBar, Toast", "нейтральний, gold, success, warning, error; прогрес зі станами; тост із дією Undo", "рис. 13"],
        ["BalanceWheel", "радар-діаграма «Колесо балансу»: 8 сфер зі шкалою 1–9, на SVG з токенів", "рис. 14"],
    ], [2200, 5226, 1600]))
    figs = [("button", "Рисунок 7. Button: п’ять варіантів у п’яти станах", 15.5),
            ("input", "Рисунок 8. Input: default, hover, focus, error, disabled", 11.5),
            ("card", "Рисунок 9. Card: варіанти та інтерактивний стан", 15.5),
            ("taskitem", "Рисунок 10. TaskItem: todo, Top 3, виконане, перенесене", 13),
            ("navbar", "Рисунок 11. Navigation: активний і вимкнений пункти", 13),
            ("chatmessage", "Рисунок 12. ChatMessage: користувач, асистент, індикатор набору", 13)]
    for name, cap, w in figs:
        o.append(image_p(shot(name), name, w, max_h_cm=9))
        o.append(fig_caption(cap))
    o.append(grid([(shot("badges"), "badges", "Badge"), (shot("progress"), "progress", "ProgressBar"), (shot("toasts"), "toasts", "Toast")], 3, 4.6))
    o.append(fig_caption("Рисунок 13. Badge, ProgressBar та Toast"))
    o.append(image_p(shot("wheel"), "wheel", 11, max_h_cm=8))
    o.append(fig_caption("Рисунок 14. BalanceWheel: радар-діаграма на SVG"))

    o.append(heading(2, "Реюзабельність: заміна кольору в одному файлі"))
    o.append(body_p("Окремо виділимо головну вимогу до UI-kit – щоб змінити стиль, не доводилося переписувати екрани. Для цього "
                    "в tokens.css є друга тема forest, яка перепризначає лише роль primary: темно-синій стає зеленим. "
                    "Змінюються три рядки, а кнопки, активний пункт навігації, повідомлення користувача в чаті й позначка "
                    "сьогоднішнього дня в календарі перефарбовуються автоматично."))
    o.append(code_p(["[data-theme='forest'] {",
                     "  --color-primary: var(--green-600);        /* було navy */",
                     "  --color-primary-hover: var(--green-800);  /* було navy-700 */",
                     "  --color-primary-active: var(--green-900); /* було navy-950 */",
                     "}"]))
    o.append(body_p("Тему можна перемикати прямо в тулбарі Storybook (Theme), тож заміну видно за секунди, а не за години."))
    o.append(grid([(shot("screen-today"), "today-navy", "Тема «Old Money» (primary – navy)"),
                   (shot("screen-today-forest"), "today-forest", "Тема «Forest» (primary – green)")], 2, 6.2))
    o.append(fig_caption("Рисунок 15. Той самий екран Today у двох темах без змін у компонентах"))

    o.append(heading(2, "Екрани"))
    o.append(keep(166))
    o.append(table_caption("Таблиця 9. Ключові екрани"))
    o.append(table([
        ["Екран (за sitemap)", "Компоненти UI-kit", "Переходи"],
        ["Today", "Card, ProgressBar, TaskItem, Input, Button, Badge, Toast, Navigation", "→ Chat («Plan with chat»), перенесення завдання з Undo"],
        ["Chat", "ChatMessage, Card (картка плану), Input, Badge, Button", "→ Today після підтвердження плану"],
        ["Week", "Card, TaskItem, Badge", "Нижня навігація"],
        ["Month (з Day)", "Card, TaskItem", "Вибір дня показує його завдання"],
        ["Year", "Card (interactive)", "→ Month"],
        ["Wheel of Balance", "BalanceWheel, Card, Badge, Button", "→ Vision & Mission, → Task Tracker, AI-інсайти"],
        ["Vision & Mission", "Input, Button, Toast", "→ Wheel (Back)"],
        ["Task Tracker", "Card, ProgressBar, Badge", "→ Wheel (Back)"],
    ], [2100, 3900, 3026]))
    wheel = shot("screen-wheel").crop((0, 0, 516, 1150))
    week = shot("screen-week").crop((0, 0, 516, 1150))
    o.append(grid([(shot("screen-today"), "s-today", "Today"), (shot("screen-chat"), "s-chat", "Chat (план від ШІ)"),
                   (week, "s-week", "Week"), (shot("screen-month"), "s-month", "Month"),
                   (shot("screen-year"), "s-year", "Year"), (wheel, "s-wheel", "Wheel of Balance"),
                   (shot("screen-vision"), "s-vision", "Vision & Mission"), (shot("screen-tracker"), "s-tracker", "Task Tracker")], 4, 3.7))
    o.append(fig_caption("Рисунок 16. Екрани прототипу (ширина телефона)"))

    o.append(heading(2, "Проходження user flow у прототипі"))
    o.append(body_p("Головний сценарій з Частини 2 проходиться в прототипі від початку до кінця. Усі переходи справжні, тобто це не "
                    "клікабельні картинки, а працюючий код."))
    o.append(table_caption("Таблиця 10. Сценарій «Чат → план дня» у прототипі"))
    o.append(table([
        ["№", "Крок user flow", "Що відбувається в прототипі"],
        ["1", "Відкриття застосунку", "Екран Today: прогрес дня, Top 3, решта справ. Якщо справ немає, показується порожній стан із кнопкою «Plan with chat»"],
        ["2", "Перехід у чат", "Пункт Chat у навігації або кнопка «Plan with chat»"],
        ["3", "Ввід тексту", "Поле повідомлення; кнопка «Use an example» підставляє приклад із PRD"],
        ["4", "ШІ аналізує", "Індикатор «ШІ думає» близько секунди"],
        ["5", "Завдання розпізнано?", "Ні – відповідь «What exactly needs to be done?» і повтор вводу. Так – картка плану"],
        ["6", "План влаштовує?", "Назви редагуються просто в картці, зайве видаляється; порожня назва дає помилку поля й блокує підтвердження"],
        ["7", "Підтвердження", "«Add to my day» → перехід на Today, повідомлення «3 tasks added to your day»"],
        ["8", "Кінцеві стани", "Виконано (чекбокс, закреслення, оновлений прогрес) або перенесено на наступний слот із повідомленням і дією Undo"],
    ], [500, 2500, 6026]))
    o.append(body_p("Один важливий нюанс. Розбір повідомлення ШІ в прототипі імітується простими правилами (файл src/data/parse.js): "
                    "текст ділиться за комами та словами «and» і «then», з нього витягуються час, слово «tomorrow» і ключові слова "
                    "для категорії. Справжню модель буде підключено в ПЗ № 3 через наявний ШІ-агент застосунку, а інтерфейс і "
                    "всі переходи при цьому не зміняться. Стан «помилка мережі» з user flow покрито компонентом Toast у варіанті "
                    "error, але в прототипі він не викликається, бо мережі тут немає."))
    o.append(heading(2, "Межі прототипу та відхилення від PRD"))
    o.append(body_p("Щоб не було розбіжностей зі специфікацією з ПЗ № 1, прямо скажемо, чого в прототипі ще немає. Не реалізовано: "
                    "нагадування, перепланування через чат («перенеси тренування на завтра»; у прототипі є лише перенесення кнопкою на "
                    "наступний слот з Undo), справжній ШІ, уточнювальне запитання при неоднозначній даті, реєстрація й онбординг. "
                    "Усе це залежить від підключення моделі, тому це ПЗ № 3."))
    o.append(body_p("Інтерфейс прототипу англомовний, як і наявний застосунок: назви розділів і сфер Колеса балансу в ньому англійські. "
                    "З цієї ж причини імітація розбору в parse.js розуміє англійські слова («and», «then», «tomorrow»), а українські "
                    "приклади з PRD вона не розбере. Українську мову інтерфейсу й розбору заплановано разом зі справжнім ШІ."))
    o.append(body_p("І навпаки, дещо виходить за межі MVP з PRD: екрани Week, Month, Year і Task Tracker та швидке додавання завдання "
                    "(Quick Add) у PRD віднесено до наступних версій, але вони вже були у вашому застосунку, тому ми показали їх у "
                    "прототипі, щоб sitemap відповідав реальній навігації."))
    o.append(heading(2, "Бонус: мобільна адаптація"))
    o.append(body_p("Інтерфейс побудовано mobile-first: контент має максимальну ширину 720 px і центрується, нижня навігація "
                    "фіксована, календар і сітки перебудовуються без горизонтального скролу. Усі екрани на рисунку 16 показано "
                    "саме на ширині телефона, а на широкому екрані той самий код виглядає так:"))
    o.append(image_p(shot("screen-today-desktop"), "desktop", 14, max_h_cm=9))
    o.append(fig_caption("Рисунок 17. Екран Today на широкому екрані (той самий код, без окремої версії)"))
    return o


def build_conclusion():
    o = [keep(170)]
    o.append(body_p(
        "Друге практичне завдання стало для нас моментом, коли Cassiopeia перестала бути лише текстом. Ми порівняли інструменти – від "
        "класичної Figma до AI-інструментів, що працюють з кодом, – і свідомо обрали шлях через код, бо так робота над прототипом "
        "не пропаде в ПЗ № 3. Побудували трирівневий sitemap та два user flow, де кожне розгалуження спирається на UX-принципи з PRD. "
        "Зібрали мудборд і вже з нього вивели палітру, шрифт і форму елементів. У Частині 4 ці рішення перетворилися на UI-kit у коді: "
        "design tokens в одному файлі, десять компонентів зі станами в Storybook і вісім екранів із робочою навігацією, зібраних "
        "лише з компонентів. Вимогу реюзабельності підтверджує друга тема: щоб змінити головний колір, достатньо трьох рядків у tokens.css."))
    return o


def main():
    OUT.mkdir(exist_ok=True)
    parts = build_body()
    parts += build_part4() + build_conclusion() + [SECT]
    xml = PREFIX + "".join(parts) + SUFFIX
    rels_xml = zin.read("word/_rels/document.xml.rels").decode("utf8")
    add = "".join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{t}"/>'
                  for rid, t in rels)
    rels_xml = rels_xml.replace("</Relationships>", add + "</Relationships>")
    ct = zin.read("[Content_Types].xml").decode("utf8")
    if 'Extension="jpg"' not in ct:
        ct = ct.replace("<Default ", '<Default Extension="jpg" ContentType="image/jpeg"/><Default ', 1)
    target = OUT / "ПЗ2_Cassiopeia.docx"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, xml.encode("utf8"))
            elif item.filename == "word/_rels/document.xml.rels":
                zout.writestr(item, rels_xml.encode("utf8"))
            elif item.filename == "[Content_Types].xml":
                zout.writestr(item, ct.encode("utf8"))
            else:
                zout.writestr(item, zin.read(item.filename))
        for name, data in media.items():
            zout.writestr("word/" + name, data)
    print("DOCX:", target, round(target.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
