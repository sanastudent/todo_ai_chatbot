# Todo AI Chatbot - Production Runbook

**Version**: 1.0
**Last Updated**: 2026-02-06
**Audience**: Operations, DevOps, On-call Engineers

---

## Overview

This runbook provides operational procedures for maintaining the Todo AI Chatbot in production. Use this guide for troubleshooting, monitoring, and routine maintenance.

**System Components**:
- Backend API (FastAPI/Python)
- OpenRouter AI API integration
- SQLite/PostgreSQL database
- MCP (Model Context Protocol) tools
- In-memory cache (pending operations, task lists)

---

## Quick Reference

### Service Health Check
```bash
# Check if backend is running
curl http://localhost:8001/health

# Expected: {"status": "healthy"}
```

### View Logs
```bash
# Real-time logs
tail -f backend/logs/app.log

# Last 100 lines
tail -n 100 backend/logs/app.log

# Search for errors
grep -i error backend/logs/app.log | tail -n 50
```

### Restart Service
```bash
# Stop backend (if running in terminal)
# Press Ctrl+C

# Start backend
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Check API Credits
```bash
# Visit OpenRouter dashboard
# https://openrouter.ai/settings/credits

# Or check logs for credit errors
grep -i "402\|payment required" backend/logs/app.log
```

---

## Common Issues and Solutions

### Issue 1: "AI agent is not available" / HTTP 402 Errors

**Symptoms**:
- Users report "I couldn't understand your request"
- Delete commands don't work
- Backend logs show: "Error code: 402 - Payment Required"

**Root Cause**: OpenRouter API credits exhausted

**Diagnosis**:
```bash
# Check backend logs
grep "402\|Payment Required" backend/logs/app.log

# Check recent API errors
grep "OpenRouter API call failed" backend/logs/app.log | tail -n 10
```

**Solution**:
1. Visit https://openrouter.ai/settings/credits
2. Add credits to account ($10-20 recommended)
3. Wait 1-2 minutes for credits to be available
4. Restart backend service
5. Verify with health check

**Prevention**:
- Set up billing alerts at 50% and 80% credit usage
- Monitor daily credit consumption
- Budget $20-50/month depending on traffic

**Priority**: 🔴 Critical (affects all AI-dependent operations)

---

### Issue 2: Slow Response Times

**Symptoms**:
- Add task takes >10 seconds
- List tasks takes >2 seconds
- Users report system is slow

**Root Cause**: Cache not working, API slow, or database issues

**Diagnosis**:
```bash
# Check response times in logs
grep "Response: 200" backend/logs/app.log | tail -n 20

# Check cache performance
grep "Task cache" backend/logs/app.log | tail -n 20

# Expected: Mix of HIT and MISS, hit rate >50% after warmup
```

**Solution**:

**If cache not working**:
1. Restart backend service (cache is in-memory)
2. Verify cache logs show "Task cache SET" and "Task cache HIT"
3. Check cache TTL is 30 seconds (in agent.py)

**If API is slow**:
1. Check OpenRouter status: https://status.openrouter.ai
2. Consider switching to faster model (gpt-3.5-turbo-instruct)
3. Reduce max_tokens further if needed (currently 2048)

**If database is slow**:
1. Check database connection
2. Verify database file is not corrupted
3. Consider database optimization (VACUUM, REINDEX)

**Prevention**:
- Monitor response times continuously
- Set alerts for p95 latency >15s
- Regular database maintenance

**Priority**: 🟡 High (affects user experience)

---

### Issue 3: Delete Commands Not Asking for Confirmation

**Symptoms**:
- Delete commands execute immediately without confirmation
- Users accidentally delete tasks

**Root Cause**: AI agent not being used (falling back to basic parser)

**Diagnosis**:
```bash
# Check if AI agent is being called
grep "Invoking AI agent" backend/logs/app.log | tail -n 10

# Check for API errors
grep "OpenRouter API call failed" backend/logs/app.log | tail -n 10

# Check if basic parser is being used
grep "Using basic command parser" backend/logs/app.log | tail -n 10
```

**Solution**:
1. Verify API credits are available (see Issue 1)
2. Check API key is valid: `echo $OPENROUTER_API_KEY`
3. Restart backend service
4. Test delete command: should ask "Are you sure?"

**Prevention**:
- Ensure API credits never run out
- Monitor AI agent usage rate
- Set up alerts for basic parser fallback

**Priority**: 🔴 Critical (data loss risk)

---

### Issue 4: Conversation Context Lost

**Symptoms**:
- User says "yes" but nothing happens
- Update requests don't remember previous context
- Pending operations not working

**Root Cause**: Pending operations cleared or backend restarted

**Diagnosis**:
```bash
# Check pending operations logs
grep "pending operation" backend/logs/app.log | tail -n 20

# Look for: "Set pending operation", "Retrieved pending operation", "Cleared pending operation"
```

**Solution**:

**If backend was restarted**:
- Pending operations are in-memory and lost on restart
- User must start operation again
- This is expected behavior

**If pending operations not being set**:
1. Check AI agent is working (see Issue 1)
2. Verify delete/update commands trigger pending operations
3. Check logs for "Set pending operation for user"

**If pending operations not being retrieved**:
1. Check conversation_id is consistent across requests
2. Verify user_id matches between requests
3. Check logs for "Retrieved pending operation"

**Prevention**:
- Minimize backend restarts during business hours
- Consider persistent storage for pending operations (Redis)
- Document to users that context is lost on restart

**Priority**: 🟡 High (affects user experience)

---

### Issue 5: High Error Rate

**Symptoms**:
- Many HTTP 500 errors
- Users report frequent errors
- Error rate >5%

**Root Cause**: Various (database, API, code bugs)

**Diagnosis**:
```bash
# Count errors in last hour
grep "ERROR" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l

# Find most common errors
grep "ERROR" backend/logs/app.log | tail -n 50

# Check for specific error types
grep "ValueError\|Exception\|Traceback" backend/logs/app.log | tail -n 20
```

**Solution**:

**For ValueError (user errors)**:
- These are expected (invalid input)
- Verify error messages are helpful
- No action needed unless rate is very high

**For Exception (system errors)**:
- Check database connectivity
- Check API availability
- Check for code bugs in traceback
- Consider rollback if critical

**For HTTP 500 errors**:
- Check backend logs for root cause
- Verify all dependencies are available
- Check for resource exhaustion (memory, disk)

**Prevention**:
- Monitor error rate continuously
- Set alerts for error rate >5%
- Regular code reviews and testing

**Priority**: 🔴 Critical (if >20%), 🟡 High (if >5%)

---

### Issue 6: Cache Not Working

**Symptoms**:
- No "Task cache HIT" in logs
- All requests show "Task cache MISS"
- Performance not improved

**Root Cause**: Cache not being set or TTL too short

**Diagnosis**:
```bash
# Check cache activity
grep "Task cache" backend/logs/app.log | tail -n 50

# Expected pattern:
# - Task cache MISS (first request)
# - Task cache SET (after database query)
# - Task cache HIT (subsequent requests within 30s)
# - Task cache EXPIRED (after 30s)
# - Invalidated task cache (after mutations)
```

**Solution**:

**If no cache SET logs**:
1. Check list_tasks is being called
2. Verify cache code is present in agent.py (lines 49-92)
3. Restart backend service

**If no cache HIT logs**:
1. Verify requests are within 30-second window
2. Check cache is not being invalidated too often
3. Verify user_id is consistent across requests

**If cache EXPIRED too quickly**:
1. Check _CACHE_TTL_SECONDS is 30 (line 27 in agent.py)
2. Consider increasing TTL if appropriate
3. Verify system clock is correct

**Prevention**:
- Monitor cache hit rate (target >50%)
- Alert if hit rate <30% for extended period
- Regular cache performance reviews

**Priority**: 🟡 High (affects performance)

---

### Issue 7: Database Errors

**Symptoms**:
- "Database connection failed" errors
- "Task not found" for existing tasks
- Data corruption

**Root Cause**: Database connectivity, corruption, or schema issues

**Diagnosis**:
```bash
# Check database file exists
ls -lh backend/todo.db

# Check database integrity (SQLite)
sqlite3 backend/todo.db "PRAGMA integrity_check;"

# Check recent database errors
grep -i "database\|sqlite" backend/logs/app.log | tail -n 20
```

**Solution**:

**For connection errors**:
1. Verify database file exists and is readable
2. Check file permissions
3. Verify database path in configuration

**For corruption**:
1. Restore from backup
2. Run integrity check
3. Consider database migration if needed

**For schema issues**:
1. Check database schema matches code expectations
2. Run migrations if needed
3. Verify all tables exist

**Prevention**:
- Regular database backups (daily)
- Monitor database size and growth
- Regular integrity checks
- Test backup restoration

**Priority**: 🔴 Critical (data loss risk)

---

## Monitoring and Alerts

### Key Metrics to Monitor

**Response Times** (check every 5 minutes):
```bash
# Extract response times from logs
grep "Response: 200" backend/logs/app.log | tail -n 100 | \
  awk '{print $(NF-1)}' | sed 's/in//;s/s//' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count "s"}'
```

**Error Rate** (check every 5 minutes):
```bash
# Count errors in last hour
total=$(grep "Response:" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
errors=$(grep "Response: 500" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
echo "Error rate: $(echo "scale=2; $errors * 100 / $total" | bc)%"
```

**Cache Hit Rate** (check every 15 minutes):
```bash
# Calculate cache hit rate
hits=$(grep "Task cache HIT" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
misses=$(grep "Task cache MISS" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
total=$((hits + misses))
echo "Cache hit rate: $(echo "scale=2; $hits * 100 / $total" | bc)%"
```

**API Credit Usage** (check daily):
- Visit https://openrouter.ai/settings/credits
- Check daily usage trend
- Verify credits remaining >$5

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Response time (p95) | >15s | >20s | Investigate performance |
| Error rate | >5% | >20% | Check logs, consider rollback |
| Cache hit rate | <30% | <10% | Check cache is working |
| API credits | <$5 | <$1 | Add credits immediately |
| Disk space | >80% | >90% | Clean up logs, expand disk |
| Memory usage | >80% | >90% | Restart service, investigate leak |

---

## Routine Maintenance

### Daily Tasks

**Morning Check** (5 minutes):
- [ ] Check service is running
- [ ] Review error logs from previous day
- [ ] Verify API credits are sufficient
- [ ] Check response times are within targets

**Evening Check** (5 minutes):
- [ ] Review daily metrics
- [ ] Check for any alerts
- [ ] Verify backups completed
- [ ] Plan for next day if issues found

### Weekly Tasks

**Monday** (15 minutes):
- [ ] Review weekly metrics and trends
- [ ] Check cache performance
- [ ] Review API credit usage
- [ ] Plan capacity for week

**Friday** (15 minutes):
- [ ] Review week's incidents
- [ ] Update runbook if needed
- [ ] Check for pending updates
- [ ] Prepare for weekend monitoring

### Monthly Tasks

**First Monday** (30 minutes):
- [ ] Review monthly metrics
- [ ] Analyze error patterns
- [ ] Review and update alerts
- [ ] Plan capacity for month
- [ ] Database maintenance (VACUUM, REINDEX)
- [ ] Review and rotate logs
- [ ] Update documentation

---

## Performance Optimization

### Current Performance Targets

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Add task | <10s | ~8s | ✅ |
| List tasks | <2s | ~1.5s | ✅ |
| Complete task | <10s | ~5s | ✅ |
| Delete task | <10s | ~5s | ✅ |
| Update task | <10s | ~5s | ✅ |

### Optimization Checklist

**If response times degrade**:
- [ ] Check cache is working (hit rate >50%)
- [ ] Verify conversation history is limited to 10 messages
- [ ] Check max_tokens is 2048
- [ ] Verify HTTP timeout is 30s
- [ ] Check database performance
- [ ] Consider API model change

**If cache hit rate is low**:
- [ ] Verify TTL is appropriate (30s)
- [ ] Check cache invalidation is not too aggressive
- [ ] Verify user_id consistency
- [ ] Consider increasing TTL if appropriate

**If API costs are high**:
- [ ] Verify max_tokens is 2048 (not 4096)
- [ ] Check conversation history is limited
- [ ] Consider cheaper model
- [ ] Review API usage patterns

---

## Backup and Recovery

### Backup Procedures

**Daily Backup** (automated):
```bash
# Backup database
cp backend/todo.db backups/todo-$(date +%Y%m%d).db

# Backup configuration
cp backend/.env backups/env-$(date +%Y%m%d).bak

# Keep last 7 days
find backups/ -name "todo-*.db" -mtime +7 -delete
```

**Pre-Deployment Backup** (manual):
```bash
# Create backup branch
git branch backup-pre-deployment-$(date +%Y%m%d-%H%M%S)
git push origin backup-pre-deployment-$(date +%Y%m%d-%H%M%S)

# Backup database
cp backend/todo.db backups/todo-pre-deployment-$(date +%Y%m%d-%H%M%S).db
```

### Recovery Procedures

**Restore Database**:
```bash
# Stop backend
# (Use your process manager)

# Restore from backup
cp backups/todo-YYYYMMDD.db backend/todo.db

# Verify integrity
sqlite3 backend/todo.db "PRAGMA integrity_check;"

# Start backend
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

**Restore Code**:
```bash
# Checkout backup branch
git checkout backup-pre-deployment-YYYYMMDD-HHMMSS

# Or revert specific commit
git revert <commit-hash>

# Restart backend
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## Security

### Security Checklist

**API Keys**:
- [ ] OPENROUTER_API_KEY stored in .env (not in code)
- [ ] .env file not committed to git
- [ ] API key rotated every 90 days
- [ ] API key has minimum required permissions

**Database**:
- [ ] Database file has restricted permissions (600)
- [ ] Database backups are encrypted
- [ ] No sensitive data in logs
- [ ] Regular security audits

**Network**:
- [ ] HTTPS enabled in production
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] CORS configured correctly

### Incident Response

**If API key is compromised**:
1. Immediately revoke old key at https://openrouter.ai/settings/keys
2. Generate new API key
3. Update .env file with new key
4. Restart backend service
5. Review logs for unauthorized usage
6. Document incident

**If database is compromised**:
1. Immediately take system offline
2. Assess scope of compromise
3. Restore from clean backup
4. Change all credentials
5. Review logs for unauthorized access
6. Document incident and notify users

---

## Escalation Procedures

### Severity Levels

**P0 - Critical** (respond immediately):
- System completely down
- Data loss or corruption
- Security breach
- Error rate >50%

**P1 - High** (respond within 15 minutes):
- Major functionality broken
- Error rate >20%
- Performance degradation >50%
- API credits exhausted

**P2 - Medium** (respond within 1 hour):
- Minor functionality broken
- Error rate >5%
- Performance degradation >20%
- Cache not working

**P3 - Low** (respond within 4 hours):
- Cosmetic issues
- Error rate >2%
- Performance degradation >10%
- Documentation updates needed

### Escalation Path

1. **On-call Engineer** (first response)
   - Acknowledge incident
   - Initial diagnosis
   - Attempt resolution

2. **Technical Lead** (if unresolved in 15 minutes for P0/P1)
   - Review diagnosis
   - Provide guidance
   - Approve rollback if needed

3. **Engineering Manager** (if unresolved in 1 hour for P0)
   - Coordinate response
   - Communicate with stakeholders
   - Approve major changes

---

## Contact Information

### Team Contacts
- **On-call Engineer**: [Phone/Email]
- **Backup Engineer**: [Phone/Email]
- **Technical Lead**: [Phone/Email]
- **Engineering Manager**: [Phone/Email]

### External Contacts
- **OpenRouter Support**: support@openrouter.ai
- **Hosting Provider**: [Contact info]
- **Database Admin**: [Contact info]

---

## Appendix

### A. Log Locations
- Application logs: `backend/logs/app.log`
- Error logs: `backend/logs/error.log`
- Access logs: `backend/logs/access.log`

### B. Configuration Files
- Environment: `backend/.env`
- Agent config: `backend/src/services/agent.py`
- Database: `backend/todo.db`

### C. Useful Commands
```bash
# Check Python version
python --version

# Check dependencies
pip list | grep -E "fastapi|uvicorn|openai|httpx"

# Check disk space
df -h

# Check memory usage
free -h

# Check process
ps aux | grep uvicorn

# Check port
netstat -tulpn | grep 8001
```

### D. Related Documentation
- DEPLOYMENT_CHECKLIST.md - Deployment procedures
- QUICK_START_GUIDE.md - Quick reference
- COMPREHENSIVE_FIX_SUMMARY.md - Recent changes
- RELEASE_NOTES.md - Version history

---

**Runbook Version**: 1.0
**Last Updated**: 2026-02-06
**Next Review**: After first production incident
**Maintained By**: Operations Team

---

**End of Production Runbook**
