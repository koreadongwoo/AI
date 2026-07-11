@echo off
REM AI 뮤직비디오 프롬프트 생성기 - 로컬 실행 스크립트 (Windows)
cd /d "%~dp0"

where claude >nul 2>nul
if errorlevel 1 (
    echo Claude Code CLI가 설치되어 있지 않아요.
    echo 설치: npm install -g @anthropic-ai/claude-code
    echo 로그인(구독 인증): claude setup-token
    exit /b 1
)

if not exist ".venv" (
    echo 가상환경을 만들어요...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo 필요한 패키지를 설치해요...
pip install -q -r requirements.txt

echo Playwright Chromium을 확인해요...
python -m playwright install chromium

echo 서버를 시작해요: http://127.0.0.1:8000
start "" "http://127.0.0.1:8000"
uvicorn main:app --host 127.0.0.1 --port 8000
