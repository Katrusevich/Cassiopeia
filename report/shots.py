"""Знімає скріншоти історій Storybook для Частини 4 звіту.

Передумова: зібраний Storybook (npm run build-storybook у ui-kit) віддається на :6007
  python -m http.server 6007 -d ui-kit/storybook-static
Запуск:  python report/shots.py
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "ui-shots"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:6007/iframe.html?viewMode=story&id="

# (файл, id історії, тема, ширина, висота)
SHOTS = [
    ("colors", "foundations--colors", "classic", 980, 1060),
    ("colors-forest", "foundations--colors", "forest", 980, 1060),
    ("typography", "foundations--typography", "classic", 980, 380),
    ("spacing", "foundations--spacing-and-shape", "classic", 980, 760),
    ("button", "components-button--all-states", "classic", 980, 560),
    ("input", "components-input--all-states", "classic", 700, 640),
    ("card", "components-card--variants", "classic", 980, 520),
    ("taskitem", "components-taskitem--all-states", "classic", 700, 340),
    ("navbar", "components-navbar--states", "classic", 700, 260),
    ("chatmessage", "components-chatmessage--conversation", "classic", 700, 300),
    ("badges", "components-feedback--badges", "classic", 700, 120),
    ("progress", "components-feedback--progress", "classic", 700, 160),
    ("toasts", "components-feedback--toasts", "classic", 700, 260),
    ("wheel", "components-balancewheel--default", "classic", 700, 380),
    ("screen-today", "screens--today", "classic", 516, 1150),
    ("screen-chat", "screens--chat-plan-proposal", "classic", 516, 1250),
    ("screen-week", "screens--week", "classic", 516, 1500),
    ("screen-month", "screens--month", "classic", 516, 1000),
    ("screen-year", "screens--year", "classic", 516, 900),
    ("screen-wheel", "screens--wheel-of-balance", "classic", 516, 1500),
    ("screen-vision", "screens--vision-and-mission", "classic", 516, 700),
    ("screen-tracker", "screens--task-tracker", "classic", 516, 820),
    ("screen-today-forest", "screens--today", "forest", 516, 1150),
    ("screen-today-desktop", "screens--today", "classic", 1100, 820),
]


def main():
    OUT.mkdir(exist_ok=True)
    for name, story, theme, w, h in SHOTS:
        url = f"{BASE}{story}&globals=theme:{theme}"
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
             "--virtual-time-budget=8000", f"--screenshot={OUT / (name + '.png')}", url],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print("ok", name)


if __name__ == "__main__":
    main()
