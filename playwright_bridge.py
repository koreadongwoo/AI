"""KLING / VEO3.1 / GROK 웹페이지를 열고, 영상 프롬프트를 클립보드에 복사해두는 보조 스크립트.

로그인과 최종 Generate 클릭은 각 서비스 계정·이용권·결제 권한에 묶여 있으므로
이 스크립트가 대신하지 않는다. 사용자가 직접 로그인하고, 붙여넣은 뒤, 직접 눌러야 한다.

사용법:
    python playwright_bridge.py KLING "Scene: ... Constraints: NO dialogue..."
    python playwright_bridge.py VEO3.1 "..."
    python playwright_bridge.py GROK "..."
"""

import argparse
import sys

from playwright.sync_api import sync_playwright

try:
    import pyperclip
except ImportError:
    pyperclip = None

# 각 서비스의 공식 웹 주소. 서비스 쪽 UI가 바뀌면 이 URL도 업데이트가 필요할 수 있다.
SERVICE_URLS = {
    "KLING": "https://klingai.com",
    "VEO3.1": "https://labs.google/fx/tools/flow",
    "GROK": "https://grok.com",
}


def open_service_with_prompt(service: str, prompt: str, headless: bool = False, wait_for_user: bool = True):
    """서비스 웹페이지를 열고 프롬프트를 클립보드에 복사해둔다."""
    service = service.upper()
    url = SERVICE_URLS.get(service)
    if not url:
        raise ValueError(f"알 수 없는 서비스: {service}. 선택 가능: {list(SERVICE_URLS)}")

    if pyperclip:
        pyperclip.copy(prompt)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)
        print(f"[{service}] 페이지를 열었습니다: {url}")

        if pyperclip:
            print("프롬프트가 클립보드에 복사됐어요. 로그인 후 입력창에 붙여넣고, 직접 Generate를 눌러주세요.")
        else:
            print("pyperclip이 없어 클립보드 복사를 건너뜁니다. 아래 프롬프트를 직접 복사해 붙여넣어 주세요:\n")
            print(prompt)

        if wait_for_user:
            input("작업을 마쳤으면 Enter를 눌러 브라우저를 닫으세요...")
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="KLING/VEO3.1/GROK 웹페이지를 열고 영상 프롬프트를 클립보드에 복사해두는 보조 스크립트"
    )
    parser.add_argument("service", choices=list(SERVICE_URLS), help="KLING / VEO3.1 / GROK 중 하나")
    parser.add_argument("prompt", help="붙여넣을 영상 프롬프트")
    parser.add_argument("--headless", action="store_true", help="브라우저를 화면에 띄우지 않고 실행")
    args = parser.parse_args()

    open_service_with_prompt(args.service, args.prompt, headless=args.headless)
    sys.exit(0)
