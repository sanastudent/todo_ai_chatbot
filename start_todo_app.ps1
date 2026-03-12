# Function to check backend health
function Test-BackendHealth {
    $retries = 30
    $retryInterval = 2
    $attempt = 0

    Write-Host "🔍 Checking backend health..."

    while ($attempt -lt $retries) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -TimeoutSec 5
            if ($response.status -eq "healthy") {
                Write-Host "✅ Backend health check passed!"
                return $true
            } else {
                Write-Host "❌ Backend health check failed with status: $($response.status)"
            }
        } catch {
            Write-Host "⚠️  Backend not reachable yet (Attempt $($attempt + 1)/$retries)"
        }

        Start-Sleep -Seconds $retryInterval
        $attempt++
    }

    Write-Host "💥 Backend health check failed after maximum retries"
    return $false
}

# Start backend server in a new window
Write-Host "🚀 Starting backend server on port 8001..."
Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit -Command `"cd '$PWD\backend'; python run_server.py`""

# Wait for backend to be ready using health check
if (Test-BackendHealth) {
    Write-Host "🎉 Backend is healthy and ready!"
    Write-Host "🚀 Starting frontend server on port 5174..."

    # Start frontend server in a new window
    Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit -Command `"cd '$PWD\frontend'; npm run dev`""

    Write-Host "✅ Both servers started successfully. Open http://localhost:5174 in browser."

    # Optionally open browser
    try {
        Start-Process "http://localhost:5174"
        Write-Host "🌐 Browser opened to http://localhost:5174"
    } catch {
        Write-Host "💡 Please open http://localhost:5174 in your browser"
    }
} else {
    Write-Host "💥 Failed to start: Backend did not become healthy within timeout period."
    Write-Host "❌ Frontend will not be started due to backend health check failure."
    exit 1
}