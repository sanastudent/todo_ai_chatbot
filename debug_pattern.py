import re

pattern = r'how many tasks (?:did I |have I )(complete|completed) (.+?)'
test_string = "how many tasks did I complete this week"

match = re.search(pattern, test_string)
if match:
    print(f"Match found!")
    print(f"Group 1: {match.group(1)}")  # should be "complete"
    print(f"Group 2: {match.group(2)}")  # should be "this week"
else:
    print("No match found")

# Let's also test the original version from the file
pattern_orig = r'how many tasks (?:did I |have I )?completed (.+?)'
match_orig = re.search(pattern_orig, test_string)
if match_orig:
    print(f"Original pattern match found: {match_orig.group(1)}")
else:
    print("Original pattern did not match")