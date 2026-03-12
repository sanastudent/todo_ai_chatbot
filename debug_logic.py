import re

def extract_task_title_to_complete(message):
    message = message.strip()
    message_lower = message.lower()

    print(f"Processing message: '{message}' -> '{message_lower}'")

    # Check for numbered task completion patterns (e.g., "complete task 1", "complete #1", "complete task number 1", "mark task 1 as complete")
    # This pattern captures "task 1", "task #1", "task number 1", "#1", etc.
    number_patterns = [
        r'(?:complete|finish|done|mark as complete|mark as done|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)(?:\s+as\s+(?:complete|done))?',
        r'(?:complete|finish|done|mark as complete|mark as done|mark)\s+(?:the\s+|a\s+|an\s+)?task\s+(\d+)',
        r'(?:complete|finish|done|mark as complete|mark as done|mark)\s+(\d+)(?:\s+as\s+(?:complete|done))?'
    ]

    for i, pattern in enumerate(number_patterns):
        print(f"  Testing pattern {i+1}: {pattern}")
        number_match = re.search(pattern, message_lower)
        if number_match:
            result = number_match.group(1)
            print(f"    MATCH! Captured: '{result}'")
            return result
        else:
            print(f"    No match")

    # If no numbered patterns match, try other logic
    print("  No numbered pattern matched, using fallback logic...")

    # Special handling for phrases like "Finish the groceries task" -> "groceries"
    # This pattern looks for verbs like finish/complete followed by article and some words before "task"
    special_pattern = re.search(r'(?:complete|finish|done|mark as done|mark as complete)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+task', message_lower)
    if special_pattern:
        extracted = special_pattern.group(1).strip()
        print(f"  Special pattern matched: '{extracted}'")
        # Remove common words like "the", "a", "an" from the extracted phrase
        extracted = re.sub(r'\b(the|a|an)\b\s*', '', extracted).strip()
        print(f"  After cleanup: '{extracted}'")
        return extracted

    # Remove common task completion phrases
    prefixes = [
        "complete task: ",
        "complete task ",
        "complete a task: ",
        "complete a task ",
        "finish task: ",
        "finish task ",
        "finish a task: ",
        "finish a task ",
        "mark task: ",
        "mark task ",
        "mark as complete: ",
        "mark as complete ",
        "done with ",
        "completed task: ",
        "completed task ",
        "finish ",
        "complete ",
        "done ",
        "mark "
    ]

    for prefix in prefixes:
        if message_lower.startswith(prefix):
            extracted = message[len(prefix):].strip()
            print(f"  Prefix '{prefix}' matched, extracted: '{extracted}'")
            # Remove common articles and "task" from the end
            extracted = re.sub(r'\b(task|the|a|an)$', '', extracted).strip()
            print(f"  After cleanup: '{extracted}'")
            return extracted

    # If no prefix matches, return the full message as the task to complete
    print(f"  No patterns matched, returning original: '{message}'")
    return message

# Test the problematic cases
print("Test 1:")
result1 = extract_task_title_to_complete("Mark task 1 as complete")
print(f"Result: '{result1}'\n")

print("Test 2:")
result2 = extract_task_title_to_complete("Complete task 1")
print(f"Result: '{result2}'\n")

print("Test 3:")
result3 = extract_task_title_to_complete("Finish task 2")
print(f"Result: '{result3}'\n")