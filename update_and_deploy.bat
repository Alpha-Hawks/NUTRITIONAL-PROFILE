@echo off
echo ===================================================
echo   Syncing and Deploying to GitHub and Vercel
echo ===================================================
echo.

echo [1/3] Updating static assets...
.\.venv\Scripts\python.exe manage.py collectstatic --no-input

echo.
echo [2/3] Staging and committing changes...
git add .
set msg=%~1
if "%msg%"=="" set msg=Update project
git commit -m "%msg%"

echo.
echo [3/3] Pushing to GitHub (triggers auto-deployment on Vercel)...
git push origin main

echo.
echo ===================================================
echo  SUCCESS! Changes are on GitHub.
echo  Vercel is now automatically deploying your live site!
echo ===================================================
pause
