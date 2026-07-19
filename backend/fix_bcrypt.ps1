# Fix bcrypt compatibility issue
Write-Host "🔧 Fixing bcrypt compatibility..." -ForegroundColor Cyan

# Activate virtual environment
.\.venv\Scripts\activate

Write-Host "📦 Uninstalling incompatible bcrypt..." -ForegroundColor Yellow
pip uninstall bcrypt -y

Write-Host "📦 Installing bcrypt 4.0.1..." -ForegroundColor Yellow
pip install bcrypt==4.0.1

Write-Host "✅ Done! Restart your backend server (python main.py)" -ForegroundColor Green
Write-Host ""
Write-Host "If you still have issues, try:" -ForegroundColor Cyan
Write-Host "  pip install bcrypt==3.2.0" -ForegroundColor White
