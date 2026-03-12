"""
Test the exact regex pattern used in parse_basic_command
"""
import re

# The exact patterns from agent.py:286-290
add_patterns = [
    r'^add\s+(?:a\s+)?(?:new\s+)?(?:task\s+)?(?:to\s+)?(?:the\s+)?(?:tasks?\s+)?(?:my\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
    r'^create\s+(?:a\s+)?(?:new\s+)?(?:task\s+)?(?:to\s+)?(?:the\s+)?(?:tasks?\s+)?(?:my\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
    r'^(?:i\s+)?(?:need\s+to|want\s+to|have\s+to)\s+(.+)$',
]

# Test messages
test_messages = [
    "add buy fresh flowers",
    "Add buy fresh flowers",
    "ADD BUY FRESH FLOWERS",
    "add task buy fresh flowers",
    "add a task to buy fresh flowers",
    "create buy fresh flowers",
    "I need to buy fresh flowers",
]

print("=" * 60)
print("REGEX PATTERN TESTING")
print("=" * 60)

for message in test_messages:
    message_lower = message.lower().strip()
    print(f"\nTesting: '{message}'")
    print(f"Lowercased: '{message_lower}'")

    matched = False
    for i, pattern in enumerate(add_patterns, 1):
        match = re.match(pattern, message_lower, re.IGNORECASE)
        if match:
            task_title = match.group(1).strip()
            print(f"  ✓ MATCHED pattern {i}")
            print(f"  Extracted: '{task_title}'")

            # Apply the cleanup logic from agent.py:298-308
            task_title = re.sub(r'\s+to\s+(?:the\s+)?tasks?$', '', task_title, flags=re.IGNORECASE)

            while True:
                old_title = task_title
                task_title = re.sub(r'^(?:a|an|the|new|task|tasks|my|to)\s+', '', task_title, flags=re.IGNORECASE)
                task_title = re.sub(r'\s+(?:a|an|the|new|task|tasks|my|to)$', '', task_title, flags=re.IGNORECASE)
                task_title = task_title.strip()
                if task_title == old_title:
                    break

            if not task_title or task_title.lower() in ['a', 'an', 'the', 'task', 'tasks', 'new', 'my', 'to']:
                task_title = 'new task'

            print(f"  Final title: '{task_title}'")
            matched = True
            break

    if not matched:
        print(f"  ✗ NO MATCH")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print("If 'add buy fresh flowers' shows ✓ MATCHED, the regex works.")
print("If it shows ✗ NO MATCH, the regex is broken.")
