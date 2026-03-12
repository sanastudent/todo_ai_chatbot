---
id: 012
title: Frontend Backend Desync Fix
stage: green
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 003-openrouter-auth-fix
branch: 003-openrouter-auth-fix
user: User
command: /sp.implement
labels: ["frontend", "caching", "health-check", "desync-fix", "implementation"]
links:
  spec: specs/003-openrouter-auth-fix/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/services/apiService.js
  - FRONTEND_FIX_VERIFICATION.md
tests:
  - Backend curl test (SUCCESS - 100%)
  - Frontend proxy test (SUCCESS - 100%)
  - Browser testing (PENDING - requires user hard refresh)
---

## Prompt

## CRITICAL FRONTEND-BACKEND DESYNC ISSUE

**BACKEND STATUS: ✅ WORKING**
- curl tests confirm backend works: `"✅ Task added: 'buy fresh fruits'"`
- MCP tools are functional
- API endpoint responds correctly

**FRONTEND STATUS: ❌ BROKEN**
- Shows: "I couldn't understand your request... ⚠️ AI not available"
- This is OLD error text from when system was broken
- Frontend is NOT showing actual backend responses

## ROOT CAUSE IDENTIFICATION

### 1. FRONTEND ERROR HANDLING LOGIC IS FLAWED
The frontend has code like:
```javascript
if (error || !apiKey) {
  showMessage("I couldn't understand... ⚠️ AI not available");
  // DOESN'T SHOW ACTUAL BACKEND RESPONSE
}
```

## Response snapshot

**ROOT CAUSE IDENTIFIED AND FIXED**

The issue was in `frontend/src/services/apiService.js` - the health check was caching results indefinitely, causing the frontend to remain stuck in "backend unhealthy" state even after the backend was fixed.

### Fix Applied

**1. TTL-based Cache Expiration (5 seconds)**
```javascript
this.healthCheckTTL = 5000; // 5 seconds TTL
const cacheExpired = now - this.lastHealthCheck > this.healthCheckTTL;
```

**2. Periodic Health Checks (every 10 seconds)**
```javascript
const intervalId = setInterval(() => {
  checkHealth(true);
}, 10000);
```

**3. Force Refresh Capability**
```javascript
async checkBackendHealth(forceRefresh = false) {
  if (this.healthCheckPromise && !cacheExpired && !forceRefresh) {
    return this.healthCheckPromise;
  }
  // ... perform fresh health check
}
```

**4. Better Cache Management**
- Cache cleared on errors: `this.healthCheckPromise = null;`
- Cache updated on successful requests: `this.lastHealthCheck = Date.now();`
- Proper timestamp tracking for TTL enforcement

**5. Enhanced Logging**
```javascript
console.log('[FRONTEND REQUEST]', method, endpoint, data);
console.log('[FRONTEND RESPONSE]', status, statusText);
console.log('[FRONTEND RESPONSE DATA]', data);
```

### Verification Results

**Backend Tests (Already Proven)**:
- ✅ Direct backend API: `curl http://localhost:8001/api/user-1768582812475/chat` → SUCCESS
- ✅ MCP tools: 7/7 tests passed (100% success rate)
- ✅ Natural language parsing: All variations working

**Frontend Tests**:
- ✅ Frontend proxy: `curl http://localhost:5174/api/user-test-frontend/chat` → SUCCESS
- ⏳ Browser testing: **Requires user to hard refresh browser (Ctrl+Shift+R)**

### Key Changes to apiService.js

**Before**: Indefinite caching
```javascript
if (this.healthCheckPromise) {
  return this.healthCheckPromise; // Never expires!
}
```

**After**: TTL-based caching with force refresh
```javascript
const cacheExpired = now - this.lastHealthCheck > this.healthCheckTTL;
if (this.healthCheckPromise && !cacheExpired && !forceRefresh) {
  return this.healthCheckPromise;
}
```

**Before**: Only check health if unhealthy
```javascript
if (!this.isBackendHealthy) {
  const isHealthy = await this.checkBackendHealth();
}
```

**After**: Always check health (respects TTL)
```javascript
const isHealthy = await this.checkBackendHealth();
```

**Before**: No periodic checks
```javascript
useEffect(() => {
  checkHealth();
}, []);
```

**After**: Periodic checks every 10 seconds
```javascript
useEffect(() => {
  checkHealth(true);
  const intervalId = setInterval(() => checkHealth(true), 10000);
  return () => clearInterval(intervalId);
}, []);
```

### User Action Required

**CRITICAL**: User must hard refresh browser to load updated JavaScript:
- Windows/Linux: `Ctrl+Shift+R`
- Mac: `Cmd+Shift+R`
- Or use incognito/private window

### Expected Behavior After Fix

1. Health check runs immediately on page load
2. Health check retries every 10 seconds automatically
3. Backend status updates within 10 seconds when backend comes online
4. Successful requests update health status immediately
5. Error messages clear when backend becomes available
6. Chat messages show actual backend responses, not cached errors

### Documentation Created

Created `FRONTEND_FIX_VERIFICATION.md` with:
- Detailed issue summary and root cause analysis
- Complete fix explanation with code examples
- Step-by-step verification instructions
- Browser testing scenarios
- Troubleshooting guide
- Success criteria checklist

## Outcome

- ✅ Impact: Fixed frontend-backend desync by implementing proper cache management with TTL, periodic health checks, and better error handling
- 🧪 Tests: Backend 100% working, frontend proxy 100% working, browser testing pending user hard refresh
- 📁 Files: Modified apiService.js, created FRONTEND_FIX_VERIFICATION.md
- 🔁 Next prompts: User must hard refresh browser (Ctrl+Shift+R) to load updated JavaScript and verify fix in browser
- 🧠 Reflection: The desync was caused by indefinite health check caching - frontend cached "backend unhealthy" state and never rechecked. Fix implements TTL-based cache expiration and periodic retries to automatically detect backend status changes.

## Evaluation notes (flywheel)

- Failure modes observed: Indefinite caching of health check results caused frontend to remain stuck in error state even after backend was fixed
- Graders run and results (PASS/FAIL): Backend tests PASS (100%), Frontend proxy PASS (100%), Browser testing PENDING (requires user action)
- Prompt variant (if applicable): N/A - bug fix implementation
- Next experiment (smallest change to try): User should hard refresh browser and test in browser to verify frontend displays actual backend responses instead of cached errors
