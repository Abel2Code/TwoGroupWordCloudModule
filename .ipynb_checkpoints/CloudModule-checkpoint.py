from wordcloud import (WordCloud, get_single_color_func)
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

DEFAULT_THRESHOLDS = [0.2, 0.4, 0.6, 0.8, 1]
DEFAULT_COLORS = ["#ff0000", "#ffa6a6", "grey", "#a6c5ff", "#0059ff"]

PUNCTUATION = '.,?!'

"""
Generate a word cloud comparing word frequencies between two groups.

Required Parameters
----------
group_1_text : str
 Concatenated text from first group. 
 - Note: Text should already be preprocessed to only include only lower case words. Any punctuation should be removed.

group_2_text : str
 Concatenated text from first group.
 - Note: Text should already be preprocessed to only include only lower case words. Any punctuation should be removed.
 
Optional Parameters
----------
thresholds : List[float]
 List of frequency thresholds for color assignment. 
 - Intuition: The algorithm generates a score for each word. The score is computed by:
         (frequency of word in group 1) / (frequency of word in both groups 1 and 2). 
    (Note that these frequencies are normalized by the total number of words from each group)
    A lower score indicates the word was said more (after normalization) by group 1 than group 2.
    If the first threshold is 0.2, words said 20% or less by group 1 (as compared to group 2) will fall under this threshold and colored by the first color of this list.
 - Warning: Must be in sorted order
 - Warning: Last threshold must always be 1

colors : List[str]
 Colors corresponding to frequency thresholds. (Must be same length as thresholds).
 
wc_height: int
 Height of the canvas.

wc_width: int
 Width of the canvas.

wc_background_color: color value
 Background color for the word cloud image.
 
EXAMPLE:
    Input
     group_1_text: "hello"
     group_2_text: "world"
     thresholds: [0.5, 1]
     threshold_color: ["blue", "red"]
    Output:
     hello (in blue)
     world (in red)
"""
def generateTwoGroupWordCloud(group_1_text, group_2_text, thresholds=DEFAULT_THRESHOLDS, colors=DEFAULT_COLORS, wc_height=1000, wc_width=2000, wc_background_color='white'):
    # Validate Input
    if not all(thresholds[i] <= thresholds[i+1] for i in range(len(thresholds) - 1)):
        raise Exception("Thresholds list is not sorted")
        
    if not thresholds[-1] == 1: 
        raise Exception(f"Last threshold should be 1. (It is currently {thresholds[-1]})")
        
    if len(thresholds) != len(colors):
        raise Exception("Thresholds list must be same length as colors. (Each threshold corresponds to a color.)")
        
    if any(p in group for group in [group_1_text, group_2_text] for p in PUNCTUATION):
        print("Warning: Text has punctuation. Consider removing punctuation for better results.")
        
    if not group_1_text.islower() and group_2_text.islower():
        print("Warning: Text is not lowercase. Consider preprocessing with .lower() for improved results.")
    
    # Compute Frequencies
    group_1_words = group_1_text.split(' ')
    group_2_words = group_2_text.split(' ')
    
    group_1_word_counter = Counter(group_1_words)
    group_2_word_counter = Counter(group_2_words)
    
    #    Normalize by size
    group_1_word_counter = {word: (group_1_word_counter[word] / len(group_1_words)) for word in group_1_word_counter}
    group_2_word_counter = {word: (group_2_word_counter[word] / len(group_2_words)) for word in group_2_word_counter}
    
    group_1_word_counter = defaultdict(float, group_1_word_counter)
    group_2_word_counter = defaultdict(float, group_2_word_counter)

    #    Generate word scores
    words = set(group_1_words).union(group_2_words)
    word_scores = {}
    for word in words:
        group_1_score = group_1_word_counter[word]
        group_2_score = group_2_word_counter[word]
        word_scores[word] = group_1_score / (group_1_score + group_2_score)
        
    # Generate Word Cloud
    combined_text = group_1_text + ' ' + group_2_text
    wc = WordCloud(height=wc_height, width=wc_width, background_color=wc_background_color).generate(combined_text)
    wc.recolor(color_func=__create_choose_color_func__(word_scores, thresholds, colors))
    
    return wc

def __create_choose_color_func__(word_scores, thresholds, colors):
    def __choose_color__(word, **kwargs):
        if word not in word_scores:
            raise Exception(f"No score created for {word}")

        score = word_scores[word]
        for t, c in zip(thresholds, colors):
            if score <= t:
                return c

        raise Exception(f'Invalid Score. All scores should be < 1.')
        
    return __choose_color__