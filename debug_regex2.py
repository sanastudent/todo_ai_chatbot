import re

# Test the exact pattern from the server code
pattern = r'(?:complete|finish|done|mark as complete|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s*(?:as\s+complete)?'

test_string = "mark task 1 as complete"
print(f"Testing pattern: {pattern}")
print(f"On string: '{test_string}'")

match = re.search(pattern, test_string)
if match:
    print(f"Match found! Captured group: '{match.group(1)}'")
else:
    print("No match found")

# Let's also test the other patterns
patterns = [
    r'(?:complete|finish|done|mark as complete|mark)\s+(?:task\s+)?(?:number\s+|#)?(\d+)\s*(?:as\s+complete)?',
    r'(?:complete|finish|done|mark as complete|mark)\s+(?:the\s+|a\s+|an\s+)?task\s+(\d+)',
    r'(?:complete|finish|done|mark as complete|mark)\s+(\d+)\s*(?:as\s+complete)?'
]

for i, pat in enumerate(patterns):
    print(f"\nPattern {i+1}: {pat}")
    match = re.search(pat, test_string)
    if match:
        print(f"  Match found! Captured: '{match.group(1)}'")
    else:
        print(f"  No match")