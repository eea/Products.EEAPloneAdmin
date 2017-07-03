'''
Created on Sep 28, 2014

@author: mike
TextStatistics for Python

https://github.com/mikedawson/textstatistics-python
'''

import re
import math

class TextStatistics(object):
    '''
    classdocs
    '''


    def __init__(self, text):
        '''
        Constructor
        '''
        self.text = self.clean_text(text)

    def clean_text(self, text):
        if text is None:
            return self.text

        full_stop_tags = ['li', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dd']

        for tag_name in full_stop_tags:
            text = text.replace("</%s>" % tag_name, ".")

        """
        Regular expressions that are to be replaced
        """
        replacement_expressions = [ ["<[^>]+>", ""], #Strip tags
                                   ["[,:;()\\-]", " "],  #Replace commas, hyphens etc (count them as spaces)
                                   ["[\\.!?]", "."], #unify terminators
                                   ["^\\s+", ""], #strip leading whitespace
                                   ["[ ]*(\\n|\\r\\n|\\r)[ ]*", " "], #Replace new lines with spaces
                                   ["([\\.])[\\. ]+", "."],#check for duplicated terminators
                                   ["[ ]*([\\.])", ". "], #Pad sentence terminators
                                   ["\\s+", " "], #Remove multiple spaces
                                   ["\\s+$", ""]] #strip trailing white space

        for replacement_set in replacement_expressions:
            text = re.compile(replacement_set[0]).sub(
                                          replacement_set[1], text)

        #Add final terminator in case it's missing.
        if len(text) > 0 and text[-1] != '.':
            text += '.'

        return text

    def flesch_kincaid_reading_ease(self, text = None):
        text = self.clean_text(text)
        return round((206.835 - (1.015 * self.average_words_per_sentence(text)) - (84.6 * self.average_syllables_per_word(text)))*10)/10

    def flesch_kincaid_grade_level(self, text = None):
        text = self.clean_text(text)
        return round(((0.39 * self.average_words_per_sentence(text)) + (11.8 * self.average_syllables_per_word(text)) - 15.59)*10)/10

    def gunning_fog_score(self, text = None):
        text = self.clean_text(text)
        return round(((self.average_words_per_sentence(text) + self.percentage_words_with_three_syllables(text, False)) * 0.4)*10)/10

    def coleman_liau_index(self, text = None):
        text = self.clean_text(text)
        return round(((5.89 * (self.letter_count(text) / self.word_count(text))) - (0.3 * (self.sentence_count(text) / self.word_count(text))) - 15.8 ) *10)/10

    def smog_index(self, text = None):
        text = self.clean_text(text)
        return round(1.043 * math.sqrt((self.words_with_three_syllables(text) * (30 / self.sentence_count(text))) + 3.1291)*10)/10

    def automated_readability_index(self, text = None):
        text = self.clean_text(text)
        return round(((4.71 * (self.letter_count(text) / self.word_count(text))) + (0.5 * (self.word_count(text) / self.sentence_count(text))) - 21.43)*10)/10;




    def syllable_count(self, word):
        syllable_count = 0
        prefix_suffix_count = 0
        word_part_count = 0

        word = word.lower()
        word = re.compile("[^a-z]").sub("", word)

        problem_words = {
            "simile":        3,
            "forever":        3,
            "shoreline":    2
        }

        if word in problem_words:
            return problem_words[word]

        #These syllables would be counted as two but should be one
        sub_syllables = [
            "cial",
            "tia",
            "cius",
            "cious",
            "giu",
            "ion",
            "iou",
            "sia$",
            "[^aeiuoyt]{2,}ed$",
            ".ely$/",
            "[cg]h?e[rsd]?$",
            "rved?$",
            "[aeiouy][dt]es?$",
            "[aeiouy][^aeiouydt]e[rsd]?$",
            "^[dr]e[aeiou][^aeiou]+$", # Sorts out deal, deign etc
            "[aeiouy]rse$" # Purse, hearse
        ]

        #These syllables would be counted as one but should be two
        add_syllables = [
            "ia",
            "riet",
            "dien",
            "iu",
            "io",
            "ii",
            "[aeiouym]bl$",
            "[aeiou]{3}",
            "^mc",
            "ism$",
            "([^aeiouy])\\1l$",
            "[^l]lien",
            "^coa[dglx].",
            "[^gq]ua[^auieo]/",
            "dnt$",
            "uity$",
            "ie(r|st)$"
        ]

        # Single syllable prefixes and suffixes
        prefix_suffix = [
            "^un",
            "^fore",
            "ly$",
            "less$",
            "ful$",
            "ers?$",
            "ings?$"
        ]

        #Remove prefixes and suffixes and count how many were taken
        for current_prefix_suffix in prefix_suffix:
            pattern = re.compile(current_prefix_suffix)
            if pattern.match(word) is not None:
                word = pattern.sub("", word)
                prefix_suffix_count = prefix_suffix_count + 1

        word_parts = filter(textstats_is_not_whitespace,
                             re.split("[^aeiouy]+", word))

        word_part_count = len(word_parts)
        x = 5

        syllable_count = word_part_count + prefix_suffix_count
        for current_sub in sub_syllables:
            if re.match(current_sub, word) is not None:
                syllable_count = syllable_count - 1

        for current_sub in add_syllables:
            if re.match(current_sub, word) is not None:
                syllable_count = syllable_count + 1

        return max(syllable_count, 1)

    def text_length(self, text = None):
        text = self.clean_text(text)
        return len(text)

    def letter_count(self, text = None):
        text = self.clean_text(text)
        #strangely - re.IGNORECASE will leave the last . on text
        repl = re.sub("[^a-z|A-Z]+", "", text)
        return len(repl)


    def sentence_count(self, text = None):
        text = self.clean_text(text)
        text = re.sub("[^\\.!?]", "", text)
        return max(len(text), 1)

    def words_with_three_syllables(self, text = None, count_proper_nouns = True):
        text = self.clean_text(text)
        long_word_count = 0

        word_parts = re.split("s+", text)
        for word in word_parts:
            # We don't count proper nouns or capitalised words if the countProperNouns attribute is set.
            #Defaults to true.
            if re.match("^[A-Z]", text) is None or count_proper_nouns:
                if self.syllable_count(word) > 2:
                    long_word_count += 1

        return long_word_count

    def percentage_words_with_three_syllables(self, text = None, count_proper_nouns = True):
        text = self.clean_text(text)
        return self.words_with_three_syllables(text, count_proper_nouns) / self.word_count(text)

    def word_count(self, text = None):
        text = self.clean_text(text)

        #In case of a zero length item... split will return an array of length 1
        if len(text) == 0:
            return 0

        return len(self.get_words(text))

    def get_words(self, cleaned_text):
        return re.split("[^a-zA-Z0-9]+",cleaned_text)

    def get_distinct_words(self, text = None):
        text = self.clean_text(text)
        word_arr = re.split("[^a-zA-Z0-9]+", text)
        distinct_word_arr = []
        for word in word_arr:
            word = word.lower()
            word = re.sub("[^a-zA-Z]","", word)
            if word not in distinct_word_arr:
                distinct_word_arr.append(word)

        return distinct_word_arr

    def word_count_distinct(self, text = None):
        """Count the number of distinct different words"""
        word_arr = self.get_distinct_words(text)
        return len(word_arr)



    def average_syllables_per_word(self, text = None):
        text = self.clean_text(text)

        syllable_count = 0
        word_count = self.word_count(text)
        word_arr = self.get_words(text)
        for word in word_arr:
            syllable_count += self.syllable_count(word)

        return float(max(syllable_count, 1)) / float(max(word_count, 1))

    def max_syllables_per_word(self, text = None):
        text = self.clean_text(text)

        max_value = 0
        word_arr = self.get_words(text)
        for word in word_arr:
            num_syllables = self.syllable_count(word)
            if num_syllables > max_value:
                max_value = num_syllables

        return max_value


    def average_words_per_sentence(self, text = None):
        text = self.clean_text(text)
        return float(self.word_count(text)) / float(self.sentence_count(text))

    def max_words_per_sentence(self, text = None):
        #split into sentences
        text = self.clean_text(text)
        sentence_arr = re.split("[\\.!?]", text)
        max_words = 0
        for sentence in sentence_arr:
            word_count = self.word_count(sentence)
            if word_count > max_words:
                max_words = word_count

        return max_words

def textstats_is_not_whitespace(word):
    """Utility method for filter to filter out blank words"""
    if len(re.sub("[^aeiouy]+", "", word)) > 0:
        return True
    else:
        return False

