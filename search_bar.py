import spellcheck
from trie import TrieNode
import pickle
from collections import defaultdict
import sys

def check_spellings(spellchecker, input_query):
	return ' '.join(spellchecker.correct_phrase(input_query))


def automatic_complete(spellchecker, my_trie, input_query, my_words):
	if my_trie.autocomplete(input_query) is not None:
		if len(my_trie.autocomplete(input_query)) >=10:
			return my_trie.autocomplete(input_query)[0:10]
		return my_trie.autocomplete(input_query)
	input_query = check_spellings(spellchecker, input_query)
	list_of_suggestions = set()
	if my_trie.autocomplete(input_query) is None:
		tokens = input_query.split(' ')
		last_three_words, last_two_words, last_word = [], [], []
		if len(tokens) >= 3: 
			last_three_words = tokens[len(tokens)-3: len(tokens)]
		if len(tokens) >= 2:
			last_two_words = tokens[len(tokens)-2: len(tokens)]
		last_word = tokens[len(tokens)-1]
		if last_three_words:
			if my_trie.autocomplete(' '.join(last_three_words)) is None:
				for word in my_words:
					if last_three_words[0] in word and last_three_words[1] in word and last_three_words[2] in word:
						list_of_suggestions.add(' '.join(tokens[0: len(tokens)-3]) + ' ' + word.replace('_',' '))
						if len(list_of_suggestions) > 10:
							break
			else:
				list_of_suggestions.update([' '.join(tokens[0: len(tokens)-3]) + ' ' + word for word in my_trie.autocomplete(' '.join(last_three_words))])
		if last_two_words and not list_of_suggestions:
			if my_trie.autocomplete(' '.join(last_two_words)) is None:
				for word in my_words:
					if last_two_words[0] in word and last_two_words[1] in word:
						list_of_suggestions.add(' '.join(tokens[0: len(tokens)-2]) + ' ' + word.replace('_',' '))
						if len(list_of_suggestions) > 10:
							break
			else:
				list_of_suggestions.update([' '.join(tokens[0: len(tokens)-2]) + ' ' + word for word in my_trie.autocomplete(' '.join(last_two_words))])
		if last_word and not list_of_suggestions:
			if my_trie.autocomplete(last_word) is None:
				for word in my_words:
					if last_word in word:
						list_of_suggestions.add(' '.join(tokens[0: len(tokens)-1]) + ' ' + word.replace('_',' '))
						if len(list_of_suggestions) > 10:
							break
			else:
				list_of_suggestions.update([' '.join(tokens[0: len(tokens)-1]) + ' ' + word for word in my_trie.autocomplete(last_word)])					
	else:
		list_of_suggestions.update(my_trie.autocomplete(input_query))
		#Try to complete with last few words here ?
	if len(list_of_suggestions) > 10:
		return list(list_of_suggestions)[0:10]
	else:
		return list(list_of_suggestions)
		 
	

def main():
	fp = open('my-trie.txt', 'rb')
	my_trie = pickle.load(fp)
	fp.close()
	fp = open('unstemmed-words.txt', 'rb')
	spell_vocabulary = defaultdict(int)
	for line in fp:
		spellcheck.train(spell_vocabulary, spellcheck.words(line)) 
	fp.close()
	spellchecker = spellcheck.SpellChecker(spell_vocabulary)
	with open("spelling-vocab.txt", "rb") as fp:  
		my_words = pickle.load(fp)
	fp.close()
	while True:
		input_query = raw_input('Enter your query: ')
		print automatic_complete(spellchecker, my_trie, input_query, my_words)
		print '*********************'


def browser_main(input_query, my_trie, spell_vocabulary, spellchecker):	
	return automatic_complete(spellchecker, my_trie, input_query, spell_vocabulary)


if __name__ == '__main__':
	main()





	


