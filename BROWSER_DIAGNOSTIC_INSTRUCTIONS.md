# Browser Diagnostic Instructions

## CRITICAL: You Must Hard Refresh First

Before any testing, you **MUST** hard refresh your browser to load the updated JavaScript:

**Windows/Linux**: `Ctrl + Shift + R`
**Mac**: `Cmd + Shift + R`

Or use an **Incognito/Private window** to ensure no cached files.

---

## Step 1: Open Browser DevTools

1. Open your browser to `http://localhost:5174`
2. Press `F12` to open DevTools
3. Go to the **Network** tab
4. Check "Preserve log" checkbox
5. Clear the network log (trash icon)

---

## Step 2: Capture the Request

1. In the chat input, type: **"add buy fresh lobster"**
2. Click Send
3. In the Network tab, find the request to `/api/user-xxx/chat`
4. Click on that request

---

## Step 3: Check Request Details

In the request details, check:

### Headers Tab:
- **Request URL**: Should be `http://localhost:5174/api/user-xxx/chat`
- **Request Method**: Should be `POST`
- **Status Code**: What is it? (200, 400, 500?)

### Payload Tab:
- What is the exact JSON being sent?
- Should be: `{"message":"add buy fresh lobster"}`

### Response Tab:
- What is the exact response?
- Copy the entire response JSON

---

## Step 4: Check Console Logs

Go to the **Console** tab in DevTools and look for:

```
[DEBUG] Backend URL: /api
[DEBUG] Fetching from: /api/health
[DEBUG] Health check status: 200
[FRONTEND REQUEST] POST /api/user-xxx/chat Data: {"message":"add buy fresh lobster"}
[FRONTEND RESPONSE] 200 OK
[FRONTEND RESPONSE DATA] {...}
```

---

## Step 5: Report Back

Please provide:

1. **Did you hard refresh the browser?** (Yes/No)
2. **Request URL from Network tab**:
3. **Request Payload (exact JSON)**:
4. **Response Status Code**:
5. **Response Body (exact JSON)**:
6. **Console logs** (copy all logs related to the request):
7. **What message appeared in the chat**:

---

## Expected vs Actual

### Expected (if working correctly):

**Request**:
```json
POST http://localhost:5174/api/user-xxx/chat
{"message":"add buy fresh lobster"}
```

**Response**:
```json
{
  "response": "✅ Task added: 'buy fresh lobster'\n\nYou can view your tasks by typing 'list tasks'.",
  "conversation_id": "...",
  "message_id": "..."
}
```

**Chat Display**:
```
✅ Task added: 'buy fresh lobster'

You can view your tasks by typing 'list tasks'.
```

### Actual (what you're seeing):

**Chat Display**:
```
I couldn't understand your request: '"add buy fresh lobster"' ⚠️ Note: AI natural language processing is not available...
```

---

## Quick Test: Bypass Frontend

To verify the backend is working, open a new terminal and run:

```bash
curl -X POST http://localhost:8001/api/browser-test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy fresh lobster"}'
```

**Expected Result**:
```json
{"response":"✅ Task added: 'buy fresh lobster'..."}
```

If curl works but browser doesn't, the issue is in the frontend or how the browser is making the request.

---

## Alternative: Test Frontend Proxy

Test if the frontend proxy is working:

```bash
curl -X POST http://localhost:5174/api/proxy-test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy fresh lobster"}'
```

This tests the Vite proxy from frontend to backend.

---

## Common Issues

### Issue 1: Browser Cache
**Symptom**: Old JavaScript still running
**Solution**: Hard refresh (Ctrl+Shift+R) or use Incognito

### Issue 2: Frontend Dev Server Not Reloaded
**Symptom**: Changes not picked up
**Solution**: Restart frontend dev server
```bash
cd frontend
npm run dev
```

### Issue 3: Backend Using Wrong Code Path
**Symptom**: Backend returns error for browser but not curl
**Solution**: Check backend logs for the specific request

### Issue 4: User ID Mismatch
**Symptom**: Different behavior for different users
**Solution**: Check what user ID the browser is using (localStorage)

---

## Next Steps

After you provide the diagnostic information above, I can:

1. Identify the exact point of failure
2. Determine if it's frontend, backend, or proxy issue
3. Apply the precise fix needed
4. Verify the fix works in your browser

**Please complete Steps 1-5 above and report back with the information.**
