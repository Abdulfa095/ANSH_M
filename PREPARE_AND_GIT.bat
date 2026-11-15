@echo off
TITLE ANSH-M Migration & GitHub Prep
echo ----------------------------------------------------------------
echo   ANSH-M SECURITY & GITHUB PREPARATION
echo ----------------------------------------------------------------
echo.

echo [1/4] Creating Secret Folder in D:\antigravity...
mkdir "D:\antigravity\secret" 2>nul

echo [2/4] Backing up sensitive files to D:\antigravity\secret...
copy "backend\.env" "D:\antigravity\secret\.env" /y
copy "frontend\.env.local" "D:\antigravity\secret\.env.local" /y
copy "backend\data\anshm.db" "D:\antigravity\secret\anshm.db" /y

echo.
echo [3/4] Initializing Git and committing project code...
git init

:: Check for Git identity and set defaults if missing
git config user.email >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Setting default Git identity...
    git config --global user.email "ashok@anshm-agri.com"
    git config --global user.name "Ashok Kumar"
)

git add .
git commit -m "🎉 ANSH-M Project: Finished Product with SMS Automation"

echo.
echo [4/4] Connecting to GitHub...
echo Please create a NEW repository at https://github.com/new named 'fyp_project1'
set /p github_url="PASTE your GitHub Repository URL (e.g., https://github.com/a-s-h-o-k-Code/fyp_project1.git): "
git remote add origin %github_url%
git branch -M main

echo.
echo Uploading to GitHub...
git push -u origin main

echo.
echo ----------------------------------------------------------------
echo   SUCCESS! 
echo   1. Your keys are safe at: D:\antigravity\secret
echo   2. Your code is now live on GitHub.
echo ----------------------------------------------------------------
pause
