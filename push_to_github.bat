@echo off
echo ==============================================================
echo Pushing Personal Expense Tracker (SpendWise AI) to GitHub
echo ==============================================================
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push failed. If the repository does not exist on GitHub yet:
    echo 1. Open your browser and go to: https://github.com/new
    echo 2. Repository Name: personal-expense-tracker-insights
    echo 3. Set visibility to: Public
    echo 4. Do NOT check README, .gitignore, or license (they are already created).
    echo 5. Click "Create repository"
    echo 6. Re-run this batch script!
) else (
    echo.
    echo [SUCCESS] Successfully pushed all commits to https://github.com/khushiyadav35/personal-expense-tracker-insights
    echo.
    echo [GITHUB PAGES ACTIVATION]:
    echo 1. Go to: https://github.com/khushiyadav35/personal-expense-tracker-insights/settings/pages
    echo 2. Source: Deploy from a branch
    echo 3. Branch: main, Folder: /docs
    echo 4. Click Save. Your live web app will be live at:
    echo    https://khushiyadav35.github.io/personal-expense-tracker-insights/
)
pause
