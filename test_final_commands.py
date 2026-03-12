#!/usr/bin/env python3
"""
Test the exact 5 commands with the logic specified by the user
"""

def test_command_logic():
    # Test the exact 5 commands the user specified
    test_messages = [
        'find report',
        'add work tag to task 1',
        'show high priority tasks',
        'what do red yellow green mean',
        'sort alphabetically'
    ]

    print('Testing the 5 commands with specified logic:')
    print('='*60)

    for msg in test_messages:
        user_message = msg.strip('\"\'').lower()

        print(f'Message: "{msg}" -> processed as: "{user_message}"')

        # Apply the logic in the exact order specified by user

        # FIRST: Priority color help (look for phrases like "color mean", "red means")
        priority_color_help = (
            'color mean' in user_message or
            'red means' in user_message or
            'yellow means' in user_message or
            'green means' in user_message or
            'what do red' in user_message or
            'what do yellow' in user_message or
            'what do green' in user_message or
            'priority color' in user_message or
            'mean' in user_message and any(color in user_message for color in ['red', 'yellow', 'green'])
        )
        print(f'  Priority color help check: {priority_color_help}')

        if priority_color_help:
            print('  -> Result: Priority color explanation')
            print('-' * 50)
            continue

        # SECOND: Search commands (look for "find ", "search ", "look for ")
        search_cmd = any(pattern in user_message for pattern in ['find ', 'search ', 'look for '])
        print(f'  Search commands check: {search_cmd}')

        if search_cmd:
            print('  -> Result: Search functionality')
            print('-' * 50)
            continue

        # THIRD: Tag operations (look for "add tag" AND "task" in same message)
        import re
        tag_operation = (
            ('add' in user_message and 'tag' in user_message and 'task' in user_message) or
            ('remove' in user_message and 'tag' in user_message and 'task' in user_message) or
            re.search(r'add\s+\w+\s+tag\s+to\s+task\s+\d+', user_message) or
            re.search(r'remove\s+\w+\s+tag\s+from\s+task\s+\d+', user_message)
        )
        print(f'  Tag operations check: {tag_operation}')

        if tag_operation:
            print('  -> Result: Tag operation')
            print('-' * 50)
            continue

        # FOURTH: Filter commands (look for messages starting with "show " or "filter ")
        filter_cmd = user_message.startswith('show ') or user_message.startswith('filter ')
        print(f'  Filter commands check: {filter_cmd}')

        if filter_cmd:
            print('  -> Result: Filter functionality')
            print('-' * 50)
            continue

        # FIFTH: Sort commands (look for "sort" in message)
        sort_cmd = 'sort' in user_message
        print(f'  Sort commands check: {sort_cmd}')

        if sort_cmd:
            print('  -> Result: Sort functionality')
            print('-' * 50)
            continue

        # LAST: Task creation (look for "add" AND "task" in message)
        task_creation = 'add' in user_message and 'task' in user_message
        print(f'  Task creation check: {task_creation}')

        if task_creation:
            print('  -> Result: Task creation')
        else:
            print('  -> Result: No match - fallback')

        print('-' * 50)

if __name__ == "__main__":
    test_command_logic()