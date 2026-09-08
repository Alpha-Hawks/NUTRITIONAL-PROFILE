param(
    [string]$Message = "Update project"
)

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Syncing and Deploying to GitHub and Vercel" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Updating static assets..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe manage.py collectstatic --no-input

Write-Host "`n[2/3] Staging and committing changes..." -ForegroundColor Yellow
git add .
git commit -m $Message

Write-Host "`n[3/3] Pushing to GitHub (Vercel auto-deploys)..." -ForegroundColor Yellow
git push origin main

Write-Host "`n===================================================" -ForegroundColor Green
Write-Host " SUCCESS! Pushed to GitHub." -ForegroundColor Green
Write-Host " Vercel is now automatically rebuilding and deploying!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
