from collections import Counter
import re

class TextAnalysis:
    def __init__(self, text):
        self.text = text
        self.words = re.findall(r'\b\w+\b', text.lower())
    
    def word_count(self): ...
    def sentence_count(self): ...
    def word_frequency(self, top_n=10): ...        # Counter, filter stopwords
    def repeated_words(self, threshold=5): ...     # flag overused words
    def avg_sentence_length(self): ...
    def spell_check(self): ...                     # pyspellchecker
    def to_prompt_context(self): ...               # packages it all for the LLM
