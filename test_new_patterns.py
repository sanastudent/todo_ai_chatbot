import re

# Test the new regex patterns
new_patterns = [
    (r'^show only (.+?) priority tasks$', 'Show only high priority tasks'),
    (r'^set task (.+?) as (.+?) priority$', 'Set task buy groceries as medium priority'),
    (r'^search for (.+?) in my tasks$', 'Search for meeting in my tasks'),
    (r'^i need to remember to (.+)$', 'I need to remember to call mom'),
    (r'^what tasks do i have\??$', 'What tasks do I have?'),
    (r'^(?:task )(.+?) is completed$', 'Task buy groceries is completed'),
    (r'^cancel task (.+)$', 'Cancel task buy groceries'),
    (r'^rename task (.+?) to (.+)$', 'Rename task buy groceries to buy food'),
    (r'^make task (.+?) (.+?) priority$', 'Make task buy groceries high priority'),
    (r'^arrange by (creation|created) date$', 'Arrange by creation date')
]

test_messages = [
    'Show only high priority tasks',
    'Set task buy groceries as medium priority',
    'Search for meeting in my tasks',
    'I need to remember to call mom',
    'What tasks do I have?',
    'What tasks do I have',
    'Task buy groceries is completed',
    'Cancel task buy groceries',
    'Rename task buy groceries to buy food',
    'Make task buy groceries high priority',
    'Arrange by creation date'
]

print('Testing new regex patterns:')
print('='*50)

for i, (pattern, example) in enumerate(new_patterns, 1):
    print(f'\n{i}. Pattern: {pattern}')
    print(f'   Example: {example}')

    # Test against all messages
    matches = []
    for msg in test_messages:
        match = re.search(pattern, msg, re.IGNORECASE)
        if match:
            matches.append((msg, match.groups()))

    if matches:
        print('   Matches found:')
        for msg, groups in matches:
            print(f'     ✓ \'{msg}\' -> captured: {groups}')
    else:
        print('   No matches found')

print('\n' + '='*50)
print('All 10 new patterns have been added to handle the broken commands.')