# Post-Deployment Monitoring Guide

**Version**: 2.0
**Last Updated**: 2026-02-06
**Audience**: Operations, DevOps, Engineering

---

## Overview

This guide provides detailed monitoring procedures for the first 7 days after deploying Version 2.0. Use this to ensure the deployment is successful and identify any issues early.

**Monitoring Phases**:
- **Phase 1**: First Hour (Critical)
- **Phase 2**: First 24 Hours (High Priority)
- **Phase 3**: First Week (Standard)

---

## Phase 1: First Hour (Critical Monitoring)

### Objectives
- Verify deployment successful
- Catch critical issues immediately
- Ensure no data loss or corruption

### Monitoring Frequency: **Every 5 minutes**

### Key Metrics to Watch

#### 1. Service Health
```bash
# Check every 5 minutes
curl http://localhost:8001/health

# Expected: {"status": "healthy"}
# Alert if: No response or status != "healthy"
```

#### 2. Error Rate
```bash
# Check error rate
grep "Response: 500" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l

# Expected: 0-2 errors in first hour
# Alert if: >5 errors in first hour
```

#### 3. Response Times
```bash
# Check recent response times
grep "Response: 200" backend/logs/app.log | tail -n 20 | \
  awk '{print $(NF-1)}' | sed 's/in//;s/s//'

# Expected: Most responses <10s
# Alert if: >50% of responses >15s
```

#### 4. AI Agent Availability
```bash
# Check for API errors
grep "OpenRouter API call failed" backend/logs/app.log | tail -n 10

# Expected: No API errors
# Alert if: Any HTTP 402 errors (credits exhausted)
```

#### 5. Conversation Context
```bash
# Check pending operations are working
grep "pending operation" backend/logs/app.log | tail -n 10

# Expected: See "Set pending operation", "Retrieved pending operation"
# Alert if: No pending operations logs (feature not working)
```

### Critical Issues Checklist

**If any of these occur, consider immediate rollback**:
- [ ] Error rate >20%
- [ ] Service crashes or becomes unresponsive
- [ ] Data corruption detected
- [ ] All operations failing
- [ ] Security vulnerability discovered

### Rollback Decision Matrix

| Issue | Severity | Action |
|-------|----------|--------|
| Error rate >50% | Critical | Rollback immediately |
| Error rate 20-50% | High | Investigate, prepare rollback |
| Error rate 10-20% | Medium | Monitor closely, investigate |
| Error rate 5-10% | Low | Monitor, investigate when possible |
| Error rate <5% | Normal | Continue monitoring |

---

## Phase 2: First 24 Hours (High Priority Monitoring)

### Objectives
- Verify performance improvements
- Confirm conversation context working
- Validate cache effectiveness
- Monitor API credit usage

### Monitoring Frequency: **Every 30 minutes**

### Performance Metrics

#### 1. Response Time Trends
```bash
# Calculate average response time per hour
for hour in {00..23}; do
  echo -n "Hour $hour: "
  grep "Response: 200" backend/logs/app.log | \
    grep "$(date +%Y-%m-%d) $hour:" | \
    awk '{print $(NF-1)}' | sed 's/in//;s/s//' | \
    awk '{sum+=$1; count++} END {if(count>0) print sum/count "s"; else print "No data"}'
done

# Expected: Average <10s per hour
# Alert if: Any hour averages >15s
```

#### 2. Operation-Specific Performance
```bash
# Add task performance
grep "add_task" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | \
  grep -A 1 "Response: 200" | grep "in" | \
  awk '{print $(NF-1)}' | sed 's/in//;s/s//' | \
  awk '{sum+=$1; count++} END {print "Add task avg:", sum/count "s"}'

# Expected: <8s average
# Alert if: >10s average

# List tasks performance
grep "list_tasks" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | \
  grep -A 1 "Response: 200" | grep "in" | \
  awk '{print $(NF-1)}' | sed 's/in//;s/s//' | \
  awk '{sum+=$1; count++} END {print "List tasks avg:", sum/count "s"}'

# Expected: <1.5s average
# Alert if: >2s average
```

#### 3. Cache Performance
```bash
# Calculate cache hit rate
hits=$(grep "Task cache HIT" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
misses=$(grep "Task cache MISS" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
expired=$(grep "Task cache EXPIRED" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)

total=$((hits + misses + expired))
if [ $total -gt 0 ]; then
  hit_rate=$(echo "scale=2; $hits * 100 / $total" | bc)
  echo "Cache hit rate: $hit_rate%"
  echo "Hits: $hits, Misses: $misses, Expired: $expired"
fi

# Expected: Hit rate >50% after first hour
# Alert if: Hit rate <30% consistently
```

#### 4. Conversation Context Success
```bash
# Check delete confirmations
grep "Are you sure" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l

# Expected: >0 if users are deleting tasks
# Alert if: 0 (feature not working)

# Check pending operations flow
grep "Set pending operation" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l
grep "Retrieved pending operation" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l
grep "Cleared pending operation" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l

# Expected: Set ≈ Retrieved ≈ Cleared (complete flow)
# Alert if: Set >> Retrieved (operations not being retrieved)
```

### API Credit Monitoring

#### Daily Credit Usage
```bash
# Count API calls
api_calls=$(grep "OpenRouter API call succeeded" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
echo "API calls today: $api_calls"

# Estimate cost (assuming $0.002 per call average)
cost=$(echo "scale=2; $api_calls * 0.002" | bc)
echo "Estimated cost: \$$cost"

# Expected: <1000 calls/day for small deployment
# Alert if: >2000 calls/day (unexpected usage spike)
```

#### Credit Exhaustion Check
```bash
# Check for credit errors
grep "402\|Payment Required" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l

# Expected: 0
# Alert if: >0 (credits running low)
```

### User Experience Metrics

#### Success Rate
```bash
# Calculate success rate
total_requests=$(grep "Response:" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
successful=$(grep "Response: 200" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)
errors=$(grep "Response: 500" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | wc -l)

if [ $total_requests -gt 0 ]; then
  success_rate=$(echo "scale=2; $successful * 100 / $total_requests" | bc)
  error_rate=$(echo "scale=2; $errors * 100 / $total_requests" | bc)
  echo "Success rate: $success_rate%"
  echo "Error rate: $error_rate%"
fi

# Expected: Success rate >85%, Error rate <5%
# Alert if: Success rate <80% or Error rate >10%
```

---

## Phase 3: First Week (Standard Monitoring)

### Objectives
- Establish baseline metrics
- Identify optimization opportunities
- Validate long-term stability

### Monitoring Frequency: **Daily**

### Daily Health Check (15 minutes)

#### Morning Check
```bash
#!/bin/bash
# Save as: daily_health_check.sh

echo "=== Daily Health Check - $(date) ==="
echo

# 1. Service Status
echo "1. Service Status:"
curl -s http://localhost:8001/health && echo " ✓ Healthy" || echo " ✗ Down"
echo

# 2. Yesterday's Metrics
echo "2. Yesterday's Metrics:"
yesterday=$(date -d "yesterday" +%Y-%m-%d)

total=$(grep "Response:" backend/logs/app.log | grep "$yesterday" | wc -l)
success=$(grep "Response: 200" backend/logs/app.log | grep "$yesterday" | wc -l)
errors=$(grep "Response: 500" backend/logs/app.log | grep "$yesterday" | wc -l)

echo "  Total requests: $total"
echo "  Successful: $success"
echo "  Errors: $errors"

if [ $total -gt 0 ]; then
  success_rate=$(echo "scale=1; $success * 100 / $total" | bc)
  echo "  Success rate: $success_rate%"
fi
echo

# 3. Performance
echo "3. Average Response Times:"
grep "Response: 200" backend/logs/app.log | grep "$yesterday" | \
  awk '{print $(NF-1)}' | sed 's/in//;s/s//' | \
  awk '{sum+=$1; count++} END {if(count>0) print "  Average:", sum/count "s"; else print "  No data"}'
echo

# 4. Cache Performance
echo "4. Cache Performance:"
hits=$(grep "Task cache HIT" backend/logs/app.log | grep "$yesterday" | wc -l)
misses=$(grep "Task cache MISS" backend/logs/app.log | grep "$yesterday" | wc -l)
total_cache=$((hits + misses))

if [ $total_cache -gt 0 ]; then
  hit_rate=$(echo "scale=1; $hits * 100 / $total_cache" | bc)
  echo "  Hit rate: $hit_rate%"
else
  echo "  No cache data"
fi
echo

# 5. API Usage
echo "5. API Usage:"
api_calls=$(grep "OpenRouter API call succeeded" backend/logs/app.log | grep "$yesterday" | wc -l)
api_errors=$(grep "OpenRouter API call failed" backend/logs/app.log | grep "$yesterday" | wc -l)
echo "  Successful calls: $api_calls"
echo "  Failed calls: $api_errors"
echo

# 6. Top Errors
echo "6. Top Errors (if any):"
grep "ERROR" backend/logs/app.log | grep "$yesterday" | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -5
echo

echo "=== End of Health Check ==="
```

### Weekly Trend Analysis

#### Performance Trends
```bash
# Generate weekly performance report
echo "=== Weekly Performance Report ==="
echo "Week of: $(date -d '7 days ago' +%Y-%m-%d) to $(date +%Y-%m-%d)"
echo

for day in {6..0}; do
  date_str=$(date -d "$day days ago" +%Y-%m-%d)
  echo -n "$date_str: "

  avg=$(grep "Response: 200" backend/logs/app.log | grep "$date_str" | \
    awk '{print $(NF-1)}' | sed 's/in//;s/s//' | \
    awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "0"}')

  printf "%.2fs avg response time\n" $avg
done

# Expected: Stable or improving trend
# Alert if: Degrading trend (each day slower than previous)
```

#### Error Pattern Analysis
```bash
# Identify recurring errors
echo "=== Error Pattern Analysis ==="
echo "Last 7 days error summary:"
echo

for day in {6..0}; do
  date_str=$(date -d "$day days ago" +%Y-%m-%d)
  error_count=$(grep "ERROR" backend/logs/app.log | grep "$date_str" | wc -l)
  echo "$date_str: $error_count errors"
done

echo
echo "Most common errors:"
grep "ERROR" backend/logs/app.log | grep -E "$(date -d '7 days ago' +%Y-%m-%d)|$(date +%Y-%m-%d)" | \
  awk '{for(i=5;i<=NF;i++) printf "%s ", $i; print ""}' | \
  sort | uniq -c | sort -rn | head -10

# Expected: Low error count, no recurring patterns
# Alert if: Same error appearing frequently
```

---

## Metrics Dashboard

### Key Performance Indicators (KPIs)

#### Tier 1: Critical (Monitor Continuously)
| Metric | Target | Warning | Critical | Current |
|--------|--------|---------|----------|---------|
| Service Uptime | 99.9% | <99% | <95% | ___ |
| Error Rate | <5% | >5% | >20% | ___ |
| Response Time (p95) | <10s | >15s | >20s | ___ |
| API Credits | >$5 | <$5 | <$1 | ___ |

#### Tier 2: Important (Monitor Daily)
| Metric | Target | Warning | Critical | Current |
|--------|--------|---------|----------|---------|
| Success Rate | >85% | <80% | <70% | ___ |
| Cache Hit Rate | >50% | <30% | <10% | ___ |
| Add Task Time | <8s | >10s | >15s | ___ |
| List Tasks Time | <1.5s | >2s | >5s | ___ |

#### Tier 3: Informational (Monitor Weekly)
| Metric | Target | Notes |
|--------|--------|-------|
| Daily Active Users | Growing | Track trend |
| Tasks Created/Day | Growing | Track trend |
| Tasks Completed/Day | Growing | Track trend |
| API Calls/Day | <1000 | Monitor cost |

### Visualization Recommendations

**If using monitoring tools (Grafana, Datadog, etc.)**:

1. **Response Time Graph**
   - Line chart showing p50, p95, p99 over time
   - Alert threshold lines at 10s, 15s, 20s

2. **Error Rate Graph**
   - Stacked area chart showing success vs errors
   - Alert threshold line at 5%

3. **Cache Performance Graph**
   - Pie chart showing hit/miss/expired ratio
   - Target: >50% hits

4. **API Usage Graph**
   - Bar chart showing daily API calls
   - Cost projection overlay

---

## Alert Configuration

### Critical Alerts (Immediate Response)

```yaml
# Example alert configuration (adapt to your monitoring system)

alerts:
  - name: "Service Down"
    condition: "health_check_failed"
    severity: "critical"
    notification: "pagerduty, slack, email"

  - name: "High Error Rate"
    condition: "error_rate > 20%"
    duration: "5 minutes"
    severity: "critical"
    notification: "pagerduty, slack"

  - name: "API Credits Exhausted"
    condition: "http_402_errors > 0"
    severity: "critical"
    notification: "pagerduty, slack, email"

  - name: "Response Time Critical"
    condition: "p95_response_time > 20s"
    duration: "10 minutes"
    severity: "critical"
    notification: "slack, email"
```

### Warning Alerts (Review Within 1 Hour)

```yaml
  - name: "Elevated Error Rate"
    condition: "error_rate > 5%"
    duration: "15 minutes"
    severity: "warning"
    notification: "slack"

  - name: "Slow Response Times"
    condition: "p95_response_time > 15s"
    duration: "15 minutes"
    severity: "warning"
    notification: "slack"

  - name: "Low Cache Hit Rate"
    condition: "cache_hit_rate < 30%"
    duration: "1 hour"
    severity: "warning"
    notification: "slack"

  - name: "API Credits Low"
    condition: "api_credits < $5"
    severity: "warning"
    notification: "email"
```

---

## Success Validation

### Week 1 Success Criteria

**Must Achieve**:
- [ ] Service uptime >99%
- [ ] Error rate <5%
- [ ] Success rate >85%
- [ ] Response times meet targets
- [ ] No critical incidents
- [ ] No data loss

**Should Achieve**:
- [ ] Cache hit rate >50%
- [ ] API costs within budget
- [ ] User feedback positive
- [ ] No rollbacks required

**Nice to Have**:
- [ ] Performance better than expected
- [ ] Zero critical alerts
- [ ] User adoption increasing

### Validation Checklist

**End of Week 1**:
- [ ] Review all metrics against targets
- [ ] Analyze error patterns
- [ ] Review user feedback
- [ ] Document lessons learned
- [ ] Identify optimization opportunities
- [ ] Plan next phase improvements

---

## Troubleshooting Quick Reference

### Issue: High Error Rate

**Diagnosis**:
```bash
# Find most common errors
grep "ERROR" backend/logs/app.log | tail -n 100 | \
  awk '{for(i=5;i<=NF;i++) printf "%s ", $i; print ""}' | \
  sort | uniq -c | sort -rn | head -5
```

**Common Causes**:
1. API credits exhausted → Add credits
2. Database issues → Check database health
3. Code bug → Review recent changes
4. External dependency down → Check dependencies

### Issue: Slow Response Times

**Diagnosis**:
```bash
# Find slowest operations
grep "Response: 200" backend/logs/app.log | tail -n 100 | \
  sort -t' ' -k10 -rn | head -10
```

**Common Causes**:
1. Cache not working → Check cache logs
2. API slow → Check OpenRouter status
3. Database slow → Check database performance
4. High load → Check resource usage

### Issue: Cache Not Working

**Diagnosis**:
```bash
# Check cache activity
grep "Task cache" backend/logs/app.log | tail -n 50
```

**Common Causes**:
1. Backend restarted → Cache cleared (expected)
2. Cache invalidation too aggressive → Review invalidation logic
3. TTL too short → Consider increasing TTL
4. Code issue → Check cache implementation

---

## Reporting

### Daily Report Template

```
Daily Monitoring Report - [DATE]

1. Service Health: [UP/DOWN]
2. Requests: [TOTAL] (Success: [COUNT], Errors: [COUNT])
3. Success Rate: [PERCENTAGE]%
4. Avg Response Time: [TIME]s
5. Cache Hit Rate: [PERCENTAGE]%
6. API Calls: [COUNT]
7. Issues: [NONE/LIST]
8. Actions Taken: [NONE/LIST]

Status: [GREEN/YELLOW/RED]
```

### Weekly Report Template

```
Weekly Monitoring Report - Week of [START DATE] to [END DATE]

Executive Summary:
- Overall Status: [GREEN/YELLOW/RED]
- Key Achievements: [LIST]
- Issues Encountered: [LIST]
- Actions Taken: [LIST]

Metrics:
- Uptime: [PERCENTAGE]%
- Success Rate: [PERCENTAGE]%
- Avg Response Time: [TIME]s
- Error Rate: [PERCENTAGE]%
- Cache Hit Rate: [PERCENTAGE]%

Trends:
- Performance: [IMPROVING/STABLE/DEGRADING]
- Reliability: [IMPROVING/STABLE/DEGRADING]
- User Adoption: [GROWING/STABLE/DECLINING]

Recommendations:
- [LIST]

Next Week Focus:
- [LIST]
```

---

## Appendix

### Useful Commands

```bash
# Real-time log monitoring
tail -f backend/logs/app.log

# Search for specific user
grep "user_id: USER123" backend/logs/app.log

# Count requests per hour
grep "Response:" backend/logs/app.log | grep "$(date +%Y-%m-%d)" | \
  awk '{print $2}' | cut -d: -f1 | sort | uniq -c

# Find longest response times
grep "Response: 200" backend/logs/app.log | \
  awk '{print $(NF-1), $0}' | sort -rn | head -20

# Check database size
ls -lh backend/todo.db

# Check disk space
df -h

# Check memory usage
free -h

# Check process
ps aux | grep uvicorn
```

---

**Guide Version**: 1.0
**Last Updated**: 2026-02-06
**Next Review**: After first week of deployment
**Maintained By**: Operations Team

---

**End of Post-Deployment Monitoring Guide**
