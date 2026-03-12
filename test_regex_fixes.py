#!/usr/bin/env python3
"""
Test script to verify the regex fixes for inconsistent task matching in the Todo AI Chatbot
"""

import re

def test_extract_task_title_to_complete():
    """Test the extract_task_title_to_complete function logic"""
    print("Testing extract_task_title_to_complete function:")

    def extract_task_title_to_complete(message):
        message = message.strip()
        message_lower = message.lower()

        # Check for numbered task completion patterns (e.g., "complete task 1", "complete #1", "complete task number 1", "mark task 1 as complete")
        # This pattern captures "task 1", "task #1", "task number 1", "#1", etc.
        number_patterns = [
            r'(?:complete|finish|done|mark as complete|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)(?:\s+as\s+complete)?',
            r'(?:complete|finish|done|mark as complete|mark)\s+(?:the\s+|a\s+|an\s+)?task\s+(\d+)',
            r'(?:complete|finish|done|mark as complete|mark)\s+(\d+)(?:\s+as\s+complete)?'
        ]

        for pattern in number_patterns:
            number_match = re.search(pattern, message_lower)
            if number_match:
                return number_match.group(1)  # Just return the number

        # Special handling for phrases like "Finish the groceries task" -> "groceries"
        # This pattern looks for verbs like finish/complete followed by article and some words before "task"
        special_pattern = re.search(r'(?:complete|finish|done|mark as done|mark as complete)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+task', message_lower)
        if special_pattern:
            extracted = special_pattern.group(1).strip()
            # Remove common words like "the", "a", "an" from the extracted phrase
            extracted = re.sub(r'\b(the|a|an)\b\s*', '', extracted).strip()
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
                # Remove common articles and "task" from the end
                extracted = re.sub(r'\b(task|the|a|an)$', '', extracted).strip()
                return extracted

        # If no prefix matches, return the full message as the task to complete
        return message

    test_cases = [
        ("Complete task 1", "1"),
        ("Mark task 1 as complete", "1"),
        ("Finish task 2", "2"),
        ("Complete task #3", "3"),
        ("Mark task number 4 as complete", "4"),
        ("Complete 5", "5"),
        ("Finish 6", "6"),
        ("Mark 7 as complete", "7"),
        ("Complete buy groceries", "buy groceries"),
        ("Finish the project", "project"),
        ("Mark task as complete", "task as complete"),  # edge case
    ]

    for input_msg, expected in test_cases:
        result = extract_task_title_to_complete(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' -> '{result}' (expected: '{expected}')")

    print()

def test_extract_task_details_for_update():
    """Test the extract_task_details_for_update function logic"""
    print("Testing extract_task_details_for_update function:")

    def extract_task_details_for_update(message):
        message = message.strip()
        message_lower = message.lower()

        # Pattern for numbered task updates (e.g., "update task 1 to buy organic groceries")
        number_pattern = r"(?:update|change|modify)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s+to\s+(.+)"
        number_match = re.search(number_pattern, message_lower)
        if number_match:
            task_number = number_match.group(1).strip()
            new_details = number_match.group(2).strip()
            # Return the task number as a string to be handled by the task matching logic
            return task_number, new_details, None

        # Look for patterns like "change X to Y", "update X to Y", "modify X to Y"
        # where X is the current task and Y is the new information

        # Pattern 1: "change 'current task' to 'new title'"
        pattern1 = r"change ['\"](.+?)['\"] to ['\"](.+?)['\"]"
        match1 = re.search(pattern1, message_lower)
        if match1:
            current_task = match1.group(1).strip()
            new_title = match1.group(2).strip()
            return current_task, new_title, None

        # Pattern 2: "update 'current task' to 'new title'"
        pattern2 = r"update ['\"](.+?)['\"] to ['\"](.+?)['\"]"
        match2 = re.search(pattern2, message_lower)
        if match2:
            current_task = match2.group(1).strip()
            new_title = match2.group(2).strip()
            return current_task, new_title, None

        # Pattern 3: "modify 'current task' to 'new title'"
        pattern3 = r"modify ['\"](.+?)['\"] to ['\"](.+?)['\"]"
        match3 = re.search(pattern3, message_lower)
        if match3:
            current_task = match3.group(1).strip()
            new_title = match3.group(2).strip()
            return current_task, new_title, None

        # Pattern 4: More general patterns like "change buy groceries to buy organic groceries"
        # Look for phrases like "change X to Y" without quotes
        pattern4 = r"change (.+?) to (.+)"
        match4 = re.search(pattern4, message_lower)
        if match4:
            current_task = match4.group(1).strip()
            new_title = match4.group(2).strip()
            return current_task, new_title, None

        # Pattern 5: "update X to Y" without quotes
        pattern5 = r"update (.+?) to (.+)"
        match5 = re.search(pattern5, message_lower)
        if match5:
            current_task = match5.group(1).strip()
            new_title = match5.group(2).strip()
            return current_task, new_title, None

        # Pattern 6: "modify X to Y" without quotes
        pattern6 = r"modify (.+?) to (.+)"
        match6 = re.search(pattern6, message_lower)
        if match6:
            current_task = match6.group(1).strip()
            new_title = match6.group(2).strip()
            return current_task, new_title, None

        # Pattern 7: Update description specifically
        pattern7 = r"update ['\"](.+?)['\"] description to ['\"](.+?)['\"]"
        match7 = re.search(pattern7, message_lower)
        if match7:
            current_task = match7.group(1).strip()
            new_description = match7.group(2).strip()
            return current_task, None, new_description

        # Pattern 8: Update description without quotes
        pattern8 = r"update (.+?) description to (.+)"
        match8 = re.search(pattern8, message_lower)
        if match8:
            current_task = match8.group(1).strip()
            new_description = match8.group(2).strip()
            return current_task, None, new_description

        # Pattern 9: Change both title and description
        pattern9 = r"change ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]"
        match9 = re.search(pattern9, message_lower)
        if match9:
            current_task = match9.group(1).strip()
            new_title = match9.group(2).strip()
            new_description = match9.group(3).strip()
            return current_task, new_title, new_description

        # Pattern 10: Update both title and description
        pattern10 = r"update ['\"](.+?)['\"] title to ['\"](.+?)['\"] and description to ['\"](.+?)['\"]"
        match10 = re.search(pattern10, message_lower)
        if match10:
            current_task = match10.group(1).strip()
            new_title = match10.group(2).strip()
            new_description = match10.group(3).strip()
            return current_task, new_title, new_description

        # If no patterns match, return None
        return None, None, None

    test_cases = [
        ("Update task 1 to buy organic groceries", ("1", "buy organic groceries", None)),
        ("Change task 2 to walk the dog", ("2", "walk the dog", None)),
        ("Update 'buy groceries' to 'buy organic groceries'", ("buy groceries", "buy organic groceries", None)),
        ("Change 'walk the dog' to 'walk the cat'", ("walk the dog", "walk the cat", None)),
        ("Modify task 3 to call mom", ("3", "call mom", None)),
        ("Update task 5 to something else", ("5", "something else", None)),
        ("Update task to something", (None, None, None)),  # No match case
    ]

    for input_msg, expected in test_cases:
        result = extract_task_details_for_update(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' -> {result} (expected: {expected})")

    print()

def test_extract_task_title_to_delete():
    """Test the extract_task_title_to_delete function logic"""
    print("Testing extract_task_title_to_delete function:")

    def extract_task_title_to_delete(message):
        message = message.strip()
        message_lower = message.lower()

        # Check for numbered task deletion (e.g., "delete task 1", "delete #1", "remove task number 1")
        number_match = re.search(r'(?:delete|remove|erase|cancel)\s+(?:task\s+)?(?:number\s+|#)?(\d+)', message_lower)
        if number_match:
            return number_match.group(1)  # Just return the number, not with # prefix

        # Special handling for phrases like "delete the groceries task" -> "groceries"
        # This pattern looks for verbs like delete/remove followed by article and some words before "task"
        special_pattern = re.search(r'(?:delete|remove|erase|cancel)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+task', message_lower)
        if special_pattern:
            extracted = special_pattern.group(1).strip()
            # Remove common words like "the", "a", "an" from the extracted phrase
            extracted = re.sub(r'\b(the|a|an)\b\s*', '', extracted).strip()
            return extracted

        # Remove common task deletion phrases
        prefixes = [
            "delete task: ",
            "delete task ",
            "delete a task: ",
            "delete a task ",
            "remove task: ",
            "remove task ",
            "remove a task: ",
            "remove a task ",
            "delete ",
            "remove ",
            "erase ",
            "cancel ",
            "get rid of "
        ]

        for prefix in prefixes:
            if message_lower.startswith(prefix):
                extracted = message[len(prefix):].strip()
                # Remove common articles and "task" from the end
                extracted = re.sub(r'\b(task|the|a|an)$', '', extracted).strip()
                return extracted

        # If no prefix matches, return the full message as the task to delete
        return message

    test_cases = [
        ("Delete task 1", "1"),
        ("Remove task 2", "2"),
        ("Cancel task 3", "3"),
        ("Delete task #4", "4"),
        ("Remove task number 5", "5"),
        ("Delete buy groceries", "buy groceries"),
        ("Remove the project", "project"),  # with article removal
        ("Cancel task", "task"),
    ]

    for input_msg, expected in test_cases:
        result = extract_task_title_to_delete(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' -> '{result}' (expected: '{expected}')")

    print()

def test_regex_patterns():
    """Test the regex patterns directly"""
    print("Testing regex patterns directly:")

    # Test numbered completion patterns
    completion_patterns = [
        r'(?:complete|finish|done|mark as complete|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)(?:\s+as\s+complete)?',
        r'(?:complete|finish|done|mark as complete|mark)\s+(?:the\s+|a\s+|an\s+)?task\s+(\d+)',
        r'(?:complete|finish|done|mark as complete|mark)\s+(\d+)(?:\s+as\s+complete)?'
    ]

    completion_tests = [
        ("Complete task 1", "1"),
        ("Mark task 1 as complete", "1"),
        ("Finish task 2", "2"),
        ("Complete 3", "3"),
        ("Mark 4 as complete", "4"),
        ("Complete task #5", "5"),
        ("Mark task number 6 as complete", "6"),
    ]

    for i, pattern in enumerate(completion_patterns):
        print(f"  Pattern {i+1}: {pattern}")
        for test_input, expected in completion_tests:
            match = re.search(pattern, test_input.lower())
            if match:
                result = match.group(1)
                status = "✅" if result == expected else "❌"
                print(f"    {status} '{test_input}' -> '{result}' (expected: '{expected}')")
            else:
                status = "❌"
                print(f"    {status} '{test_input}' -> no match (expected: '{expected}')")

    # Test numbered update pattern
    print(f"\n  Numbered update pattern: r\"(?:update|change|modify)\\s+(?:task\\s+)?(?:number\\s+|#)?(\\d+)\\s+to\\s+(.+)\"")
    update_pattern = r"(?:update|change|modify)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s+to\s+(.+)"
    update_tests = [
        ("Update task 1 to buy organic groceries", ("1", "buy organic groceries")),
        ("Change task 2 to walk the dog", ("2", "walk the dog")),
        ("Modify task 3 to call mom", ("3", "call mom")),
        ("Update 4 to something", ("4", "something")),
        ("Change task #5 to new task", ("5", "new task")),
        ("Update task number 6 to complete task", ("6", "complete task")),
    ]

    for test_input, expected in update_tests:
        match = re.search(update_pattern, test_input.lower())
        if match:
            result = (match.group(1), match.group(2))
            status = "✅" if result == expected else "❌"
            print(f"    {status} '{test_input}' -> {result} (expected: {expected})")
        else:
            status = "❌"
            print(f"    {status} '{test_input}' -> no match (expected: {expected})")

    print()

if __name__ == "__main__":
    print("Testing fixes for inconsistent task matching in Todo AI Chatbot")
    print("=" * 70)

    test_regex_patterns()
    test_extract_task_title_to_complete()
    test_extract_task_details_for_update()
    test_extract_task_title_to_delete()

    print("All tests completed!")