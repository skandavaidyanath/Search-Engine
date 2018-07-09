from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
import QAlive2
import search_bar
import gensim
import pickle
from collections import defaultdict
import spellcheck
from trie import TrieNode
#import hover-live




@dispatcher.add_method
def run_search_engine(input_query):
	return QAlive2.live(model, input_query, vocabulary, length_preprocessed, inverted_index, document_dictionary, norms, nod, list_of_document_tfidf_dicts)

@dispatcher.add_method
def autocomplete(input_query):
	return search_bar.browser_main(input_query, my_trie, spell_vocabulary, spellchecker)

	    	
@Request.application
def application(request):
    	response = JSONRPCResponseManager.handle(request.data, dispatcher)
    	return Response(response.json, mimetype='application/json', headers={'Access-Control-Allow-Headers':['access-control-allow-origin', 'content-type'],'Access-Control-Allow-Origin':'*'})
	


if __name__ == '__main__':
    	model = gensim.models.Word2Vec.load('vocab.txt')
	vocabulary = list()
	length_preprocessed = 0
	inverted_index = dict()
	vocabulary = model.wv.vocab.keys()
	fp = open("preprocessed.txt", "rb") 
	length_preprocessed = pickle.load(fp)
	fp.close()
	fp = open("inverted-index.txt", "rb") 
	inverted_index = pickle.load(fp)
	fp.close()
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
	with open("document-index.txt", "rb") as fp:
		document_dictionary = pickle.load(fp)
	with open('norms.txt', 'rb') as fp:
		norms = pickle.load(fp)
	with open('tfidf-scores.txt', 'rb') as fp:
		nod = pickle.load(fp)		
		list_of_document_tfidf_dicts = pickle.load(fp)
	fp.close()
    	run_simple('10.19.1.166', 4000, application)

