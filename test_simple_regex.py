"""
Simple test without Unicode characters
"""
import re

# The exact patterns from agent.py
add_patterns = [
    r'^add\s+(?:a\s+)?(?:new\s+)?(?:task\s+)?(?:to\s+)?(?:the\s+)?(?:tasks?\s+)?(?:my\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
    r'^create\s+(?:a\s+)?(?:new\s+)?(?:task\s+)?(?:to\s+)?(?:the\s+)?(?:tasks?\s+)?(?:my\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
    r'^(?:i\s+)?(?:need\s+to|want\s+to|have\s+to)\s+(.+)$',
]

message = "add buy fresh flowers"
message_lower = message.lower().strip()

print("Testing:", message)
print("Lowercased:", message_lower)
print()

matched = False
for i, pattern in enumerate(add_patterns, 1):
    match = re.match(pattern, message_lower, re.IGNORECASE)
    if match:
        task_title = match.group(1).strip()
        print(f"MATCHED pattern {i}")
        print(f"Extracted: {task_title}")
        matched = True
        break

if not matched:
    print("NO MATCH - REGEX FAILED")
else:
    print("SUCCESS - REGEX WORKS")
