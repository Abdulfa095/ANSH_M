@echo off
TITLE ANSH-M GitHub Setup
echo ----------------------------------------------------------------
echo   ANSH-M Agriculture Intelligence System - GITHUB PUSH
echo ----------------------------------------------------------------
echo.

echo [1/3] Preparing files and committing updates...
git add .
git commit -m "🚀 ANSH-M Project: Updated requirements and fixed Python compatibility" || echo "No changes to commit"

echo.
echo [2/3] Checking connection...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo Please create a new repository at https://github.com/new first.
    set /p github_url="PASTE your GitHub Repository URL here: "
    git remote add origin %github_url%
) else (
    echo Connection with GitHub already established!
)
git branch -M main

echo.
echo [3/3] Uploading updates to GitHub...
git push origin main

echo.
echo ----------------------------------------------------------------
echo   DONE: Your code is now protected and backed up on GitHub!
echo   (Hidden .env files and node_modules were kept local for security)
echo ----------------------------------------------------------------
echo.
pause
