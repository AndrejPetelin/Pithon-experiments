"""
main.py
Test harness for analysis_utils functions using hardcoded Lorem Ipsum text.
"""
from analisis import Word_count, sentence_count

test_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris! 
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum? 
Excepteur sint occaecat cupidatat non proident. 
Sunt in culpa qui officia deserunt mollit anim id est laborum."""

print("Word count:", Word_count(test_text))
print("Sentence count:", sentence_count(test_text))
