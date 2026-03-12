# Start backend server and wait for it to be ready using health check

Write-Host "🚀 Starting Todo AI Chatbot with health check synchronization..." -ForegroundColor Green

# Start backend server in background
Write-Host "📍 Starting backend server on port 8001..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$PWD\backend'; python run_server.py" -PassThru

# Wait for backend to be ready using health check script
Write-Host "🔍 Waiting for backend to be ready using health check..." -ForegroundColor Cyan

try {
    # Run the health check script which will wait for backend to be ready
    $exitCode = & python "$PWD\scripts\health-check.py" "npm run dev --prefix frontend"

    if ($exitCode -eq 0) {
        Write-Host "✅ Todo AI Chatbot started successfully!" -ForegroundColor Green
        Write-Host "🌐 Access the application at http://localhost:5174" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start application due to health check failure" -ForegroundColor Red
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "💥 Error during startup: $_" -ForegroundColor Red
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

# Cleanup function
function Cleanup {
    Write-Host "🛑 Shutting down processes..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
}

# Register cleanup on script termination
Register-ObjectEvent -InputObject ([console]) -EventName "CancelKeyPress" -Action {
    Cleanup
    exit
} -ErrorVariable eventRegistrationError -ErrorAction SilentlyContinue