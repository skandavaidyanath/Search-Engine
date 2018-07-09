import pickle
import gensim

stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]


def preprocess(file_name):
	fp = open("unstemmed-words.txt", "wb")
	for line in file_name:
		preprocess_list = gensim.utils.simple_preprocess(line, max_len = 20)
		for word in preprocess_list:
			fp.write(word.encode('utf-8'))
			fp.write(' ')
		fp.write('\n')
	fp.close()


def get_word2vec(number_of_documents):
	documents = gensim.models.word2vec.LineSentence("unstemmed-words.txt")
	bigram = gensim.models.Phrases(documents)
	trigram = gensim.models.Phrases(bigram[documents])      
	model = gensim.models.Word2Vec(trigram[bigram[documents]],size=300,window=10,min_count=5,workers=10)
	model.train(documents, total_examples=number_of_documents, epochs=10)
	return model

def main():
	file_name = open("cmptext.txt","rb")
	preprocess(file_name)	
	file_name.close()
	with open("preprocessed.txt","rb") as file_name:
		number_of_documents = pickle.load(file_name)
		file_name.close()
	print 'Preprocessing done'
	model = get_word2vec(number_of_documents)       #includes trigrams
	spelling_vocab = model.wv.vocab.keys()
	with open("spelling-vocab.txt", "wb") as fp:   
        	pickle.dump(spelling_vocab, fp)
	fp.close()


if __name__ == '__main__':
	main()





