# AI 뮤직비디오 프롬프트 생성기

Suno로 만든 노래(음원 + 가사)를 넣으면, AI 뮤직비디오용 스토리라인 / 씬별 이미지 프롬프트(GPT이미지2·나노바나나2용) / 영상 프롬프트(KLING·VEO3.1·GROK용)를 순서대로 만들어주는 로컬 웹 도구입니다.

## 왜 로컬에서 실행하나요

AI 생성은 API 키가 아니라 **Claude Code 구독 계정**(`claude -p`)으로 동작합니다. 이 방식은 실행하는 사람의 로컬 로그인 세션에 묶여 있어서, 별도 서버(Vercel 등)에 올려 여러 사람이 접속하는 형태로는 배포하지 않았습니다. 대신 각자 자기 PC에서 자기 구독으로 실행합니다 — API 사용료가 따로 들지 않습니다.

## 준비물

- Python 3.10 이상
- Node.js (Claude Code CLI 설치용)
- [Claude Code](https://code.claude.com) 구독 계정

## 설치 및 실행

1. Claude Code CLI 설치 및 로그인
   ```bash
   npm install -g @anthropic-ai/claude-code
   claude setup-token
   ```
2. 이 저장소를 받은 뒤 실행 스크립트를 돌립니다.
   - Windows: `start.bat` 더블클릭 (또는 터미널에서 `start.bat`)
   - Mac/Linux/Git Bash: `bash start.sh`

   스크립트가 가상환경 생성, 패키지 설치(`requirements.txt`), Playwright Chromium 설치, 서버 실행까지 자동으로 처리합니다.
3. 브라우저에서 `http://127.0.0.1:8000` 접속 (Windows는 자동으로 열립니다).

## 사용법

1. 노래 음원(mp3/wav)과 가사를 넣고 "뮤직비디오 프롬프트 만들기"를 누릅니다.
2. 스토리라인 → 씬별 이미지/영상 프롬프트가 화면에 순서대로 나타납니다.
3. 각 프롬프트 옆 "복사" 버튼으로 복사해 GPT이미지2/나노바나나2/KLING/VEO3.1/GROK에 붙여넣습니다.
4. KLING/VEO3.1/GROK 웹페이지를 바로 열고 싶으면:
   ```bash
   python playwright_bridge.py KLING "복사한 영상 프롬프트"
   ```
   페이지가 열리고 프롬프트가 클립보드에 복사됩니다. 로그인과 최종 Generate 클릭은 각자 계정으로 직접 합니다(로그인·이용권·결제가 걸려 있어 자동화하지 않습니다).

## 파일 구성

- `main.py` — FastAPI 서버 (스토리라인/씬/프롬프트 생성 로직)
- `index.html` — 입력 화면 + 결과 카드 UI
- `playwright_bridge.py` — KLING/VEO3.1/GROK 웹페이지를 여는 보조 스크립트
- `start.sh` / `start.bat` — 설치 + 실행 스크립트

## 참고

- 나노바나나2·VEO3.1·GROK의 이미지/영상 생성 공식 API는 공개 정보가 부족해 직접 호출하지 않고, 복사 가능한 프롬프트 + 브라우저 보조 경로로 대응했습니다.
- `playwright_bridge.py`의 서비스 URL은 각 서비스 UI가 바뀌면 업데이트가 필요할 수 있습니다.
