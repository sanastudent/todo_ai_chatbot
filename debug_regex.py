import re

def extract_task_title_to_complete(message):
    message = message.strip()
    message_lower = message.lower()

    print(f"Input: '{message}'")

    # Check for numbered task completion patterns (e.g., "complete task 1", "complete #1", "complete task number 1", "mark task 1 as complete")
    # This pattern captures "task 1", "task #1", "task number 1", "#1", etc.
    number_patterns = [
        r'(?:complete|finish|done|mark as complete|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s*(?:as\s+complete)?',
        r'(?:complete|finish|done|mark as complete|mark)\s+(?:the\s+|a\s+|an\s+)?task\s+(\d+)',
        r'(?:complete|finish|done|mark as complete|mark)\s+(\d+)\s*(?:as\s+complete)?'
    ]

    for i, pattern in enumerate(number_patterns):
        print(f"Pattern {i+1}: {pattern}")
        number_match = re.search(pattern, message_lower)
        if number_match:
            result = number_match.group(1)
            print(f"  MATCH: '{result}'")
            return result
        else:
            print(f"  NO MATCH")

    print("No numbered pattern matched, using fallback logic...")
    return message

# Test the problematic case
result = extract_task_title_to_complete("Mark task 1 as complete")
print(f"Final result: '{result}'")