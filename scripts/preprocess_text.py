import re
from typing import List
import unicodedata
from nltk.corpus import stopwords
import inflect
import contractions


def replace_contractions(text: str) -> str:
    """Replace contractions in string of text"""
    return contractions.fix(text)


def remove_URL(sample: str) -> str:
    """Remove URLs from a sample string"""
    return re.sub(r"http\S+", "", sample)


def remove_non_ascii(words: List[str]) -> List[str]:
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode(
            'ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words


def replace_numbers(words: List[str]) -> List[str]:
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words


def preprocess(sample: str) -> str:
    try:
        # 1. Remove non-letters
        sample = re.sub("[^a-zA-Z]", " ", sample)

        # 2. Remove URL
        sample = remove_URL(sample)

        # 3. Remove contractions
        sample = replace_contractions(sample)

        # 4. Convert to lower case, split into individual words
        words = sample.lower().split()

        # 5. Remove Non ASCII words
        words = remove_non_ascii(words)

        # 6. Replace numbers into words
        words = replace_numbers(words)

        # 7. In Python, searching a set is much faster than searching
        #   a list, so convert the stop words to a set
        stops = set(stopwords.words("english"))

        # 8. Remove stop words
        meaningful_words = [w for w in words if not w in stops]

        # 9. Join the words back into one string separated by space,
        # and return the result.
        return " ".join(meaningful_words)
    except TypeError as ex:
        print(ex)
        return ""
