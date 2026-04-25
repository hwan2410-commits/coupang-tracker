@echo off
echo === 쿠팡 최저가 트래커 시작 ===
echo.

cd /d "%~dp0backend"

echo [1/3] Python 패키지 설치 중...
pip install -r requirements.txt -q

echo [2/3] Playwright 브라우저 설치 중...
playwright install chromium

echo [3/3] 백엔드 서버 시작...
start cmd /k "cd /d %~dp0backend && uvicorn main:app --reload --port 8000"

echo.
echo [4/4] 프론트엔드 서버 시작...
start cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ✅ 완료! 잠시 후 브라우저에서 http://localhost:5173 을 열어주세요.
pause
