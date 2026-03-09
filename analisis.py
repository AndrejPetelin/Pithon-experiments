"""
analysis.py
Text analysis utilities for Qualia Editor.
Word count, sentence count, word frequency, repetition detection.
"""
import re


def Word_count(text):
    words =text.split()
    return len(words)

#counts sentences by .!?

def sentence_count(text):
    # Split text into sentences on punctuation marks .!?
    # The + means one or more consecutive punctuation characters
    # so "..." counts as one split point not three
    sentences = re.split(r'[.!?]+',text )
    sentences =[s for s in sentences if s.strip()]
    return len(sentences)
