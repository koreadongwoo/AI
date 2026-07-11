#!/usr/bin/env bash
# AI 뮤직비디오 프롬프트 생성기 - 로컬 실행 스크립트 (Mac/Linux/Git Bash)
set -e

cd "$(dirname "$0")"

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code CLI가 설치되어 있지 않아요."
  echo "설치: npm install -g @anthropic-ai/claude-code"
  echo "로그인(구독 인증): claude setup-token"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "가상환경을 만들어요..."
  python3 -m venv .venv
fi

source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate

echo "필요한 패키지를 설치해요..."
pip install -q -r requirements.txt

echo "Playwright Chromium을 확인해요..."
python -m playwright install chromium

echo "서버를 시작해요: http://127.0.0.1:8000"
uvicorn main:app --host 127.0.0.1 --port 8000
