import re
from collections import defaultdict


class SpellChecker(object):

    def __init__(self, vocabulary):
	self.vocabulary = vocabulary

    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def _edits1(self, word):
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
        replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts = [a + c + b for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)

    def _known_edits2(self, word):
        return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1) if e2 in self.vocabulary)

    def _known(self, words):
        return set(w for w in words if w in self.vocabulary)

    def correct_token(self, token):
        candidates = self._known([token]) or self._known(self._edits1(token)) or self._known_edits2(token) or [token]
        return max(candidates, key = self.vocabulary.get)

    def correct_phrase(self, text):
        tokens = text.split()
        return [self.correct_token(token) for token in tokens]



def words(text):
        return re.findall('[a-z]+', text.lower())          #is phrases necessary ? '_' ?
 
def train(model, features):
        for f in features:
            model[f] += 1


'''fp = open("unstemmed-words.txt", "rb")
spell_vocabulary = defaultdict(int)
for line in fp:
	train(spell_vocabulary, words(line)) 
fp.close()
spellchecker = SpellChecker(spell_vocabulary)
tokens = spellchecker.correct_phrase("primery sodiu bump")
print tokens'''
