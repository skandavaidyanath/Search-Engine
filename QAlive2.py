import os
import gensim
from collections import Counter
import heapq
from math import log
import PyPDF2
import textract
import gensim
import pickle
from gensim.parsing.porter import PorterStemmer
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data
from torch.autograd import Variable
from reco_sys import SAE
import pymysql


stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

			
def calc_wt(text, word, inverted_index, length_preprocessed): 		
	if "_" in word:
		if len(text) > 30:
			n_words = word.split("_")
			number_of_occurences = 0
			if (len(n_words) == 2):
				for i in range(len(text)-1):
					if document[i] == n_words[0] and document[i+1] == n_words[1]:
						number_of_occurences += 1
			if (len(n_words) == 3):
				for i in range(len(text)-2):
					if document[i] == n_words[0] and document[i+1] == n_words[1] and document[i+2] == n_words[2]:
						number_of_occurences += 1
			if (len(n_words) == 4):
				for i in range(len(text)-3):
					if document[i] == n_words[0] and document[i+1] == n_words[1] and document[i+2] == n_words[2] and document[i+3] == n_words[3]:
						number_of_occurences += 1
				
			tf = log(1 + number_of_occurences,10)
		else:
			tf = log(1 + text.count(word),10)
		idf = log((float(length_preprocessed)/len(inverted_index[word])),10)	
			
	else:
		tf = log((1 + text.count(word)),10)
		idf = log((float(length_preprocessed)/len(inverted_index[word])),10)	
	return tf*idf
	

def get_expanded_query(query, model, vocab):
	expanded_query = []
	for word in query:
		expanded_query.append(word)
	unnecessary = set()
	for i in range(len(query)-1):
		if (str(query[i]) + '_' + str(query[i+1])) in vocab:
			expanded_query.append(str(query[i]) + '_' + str(query[i+1]))
			unnecessary.add(query[i])
			unnecessary.add(query[i+1])
	
	for i in range(len(query)-2):
		if (str(query[i]) + '_' + str(query[i+1]) + '_' + str(query[i+2]) ) in vocab:
			expanded_query.append(str(query[i]) + '_' + str(query[i+1]) + '_' + str(query[i+2]))
			unnecessary.add(query[i])
			unnecessary.add(query[i+1])
			unnecessary.add(query[i+2])
			unnecessary.add(query[i] + '_' + query[i+1])
			unnecessary.add(query[i+1] + '_' + query[i+2])
	
	for i in range(len(query)-3):
		if (str(query[i]) + '_' + str(query[i+1]) + '_' + str(query[i+2]) + '_' + str(query[i+3])) in vocab:
			expanded_query.append(str(query[i]) + '_' + str(query[i+1]) + '_' + str(query[i+2]) + '_' + str(query[i+3]))
			unnecessary.add(query[i])
			unnecessary.add(query[i+1])
			unnecessary.add(query[i+2])
			unnecessary.add(query[i+3])
			unnecessary.add(query[i] + '_' + query[i+1])
			unnecessary.add(query[i+1] + '_' + query[i+2])
			unnecessary.add(query[i+2] + '_' + query[i+3])
		 	unnecessary.add(query[i] + '_' + query[i+1] + '_' + query[i+2])	
			unnecessary.add(query[i+1] + '_' + query[i+2] + '_' + query[i+3])		
	number_of_similar_words = 0
	for token in query:
		a = []
		if token not in vocab:
			continue
		a.extend([x[0] for x in model.wv.most_similar(token)[0:(number_of_similar_words)]])
		expanded_query.extend(a)
	expanded_query = set(expanded_query)
	for word in unnecessary:
		if word in expanded_query:
			expanded_query.remove(word)
	refined_expanded_query = list()
	for word in expanded_query:
		flag = 0
		for char in word:
			if not (('a'<= char <='z') or (char=='_')):				
				flag = 1
		if flag == 0:		
			refined_expanded_query.append(word)
	return refined_expanded_query


def get_relevantdocs(expanded_query, inverted_index):
	relevantdocs = set()
	for token in expanded_query:
		if(token not in inverted_index.keys()):
			continue
		relevantdocs.update(inverted_index[token])
	return relevantdocs


def get_eq_tfidf_vector(inverted_index, expanded_query, preprocessed_query, length_preprocessed):
	eq_tfidf = dict()
	expanded_query = list(expanded_query)
	for word in inverted_index.keys():
		value = calc_wt(expanded_query, word, inverted_index, length_preprocessed)
		if word in preprocessed_query and word in expanded_query:
			value = value * 1
		elif '_' in word:
			value = value * len(word.split('_'))
		elif word in expanded_query and word not in preprocessed_query:
			value = value * 0.5		
		eq_tfidf[word] = value
	return eq_tfidf 

def get_scores(relevant_docs, eq_vector, norm_dic, nod, list_of_document_tfidf_dicts):
	query_norm = 0
	for item in eq_vector.values():
		query_norm += item**2
	query_norm = query_norm**0.5
	doc_number = 1
	scores = dict((el,0) for el in relevant_docs)
	try:
		while doc_number <= nod:
			doc_vector = list_of_document_tfidf_dicts[doc_number - 1]	
			if doc_number in relevant_docs:
				for word in eq_vector.keys():
					scores[doc_number] += eq_vector[word]*doc_vector[word]
				scores[doc_number] /= float((query_norm)*(norm_dic[doc_number]))
			doc_number += 1
			
	except ZeroDivisionError as e:
		raise e
	return scores
        				
		
def get_bm25(relevant_sent, inverted_index, expanded_query, preprocessed_tuple):
	lengths = [len(sentence_tuple[1]) for sentence_tuple in preprocessed_tuple]	
	bm25_scores = dict((el,0) for el in relevant_sent)
	avg_dl = sum(lengths)/len(lengths)
	number_of_sent = len(preprocessed_tuple)
	idf_words = {word:0 for word in expanded_query}
	i = 0
	for word in expanded_query:
		if word not in inverted_index.keys():
			idf_words[word] = log(float(number_of_sent + 0.5)/(0.5),10)
			continue
		idf_words[word] = log(float(number_of_sent - len(inverted_index[word])+ 0.5)/(len(inverted_index[word]) + 0.5),10)

	for sent_number in relevant_sent:
		for word in expanded_query:	
			bm25_scores[sent_number] += float(idf_words[word]*preprocessed_tuple[sent_number-1][1].count(word)*2.5)/(preprocessed_tuple[sent_number-1][1].count(word) + 1.5*(0.25+ 0.75*(float(number_of_sent)/avg_dl)))
	return bm25_scores



def get_index_ans(preprocessed_tuple, sentence_number):
	doc_number = preprocessed_tuple[sentence_number-1][0]
	fp = open('spreprocessed' + str(doc_number) + '.txt', 'rb')
	list_temp = pickle.load(fp)
	index_ans = list_temp.index(preprocessed_tuple[sentence_number-1][1])	
	fp.close()
	return index_ans

def get_inverted_index_query_terms(document_tuples, dictionary):
	inverted_index = dict((el,[]) for el in dictionary)
	doc_number = 1
	for document_tuple in document_tuples:
		document = document_tuple[1]
		for el in inverted_index.keys():
			if el in document:
				inverted_index[el].append(doc_number)
			elif '_' in el:
				n_words = el.split('_')
				result = False
				if (len(n_words) == 2):
					for i in range(len(document)-1):
						if result:
							break
						if document[i] == n_words[0] and document[i+1] == n_words[1]:
							result = True
				if (len(n_words) == 3):
					for i in range(len(document)-2):
						if result:
							break
						if document[i] == n_words[0] and document[i+1] == n_words[1] and document[i+2] == n_words[2]:
							result = True
				if (len(n_words) == 4):
					for i in range(len(document)-3):
						if result:
							break
						if document[i] == n_words[0] and document[i+1] == n_words[1] and document[i+2] == n_words[2] and document[i+3] == n_words[3]:
							result = True
				if result:
					inverted_index[el].append(doc_number)	
			else:
				continue			
		doc_number += 1
	return inverted_index

	

def live(model, input_query, vocabulary, length_preprocessed, inverted_index, document_dictionary, norms, nod, list_of_document_tfidf_dicts, sae, id_links):
################################ Live Code ######################################## 
	ERROR_MESSAGE = ""
	ANSWER = {"error":None, "main_ans":None, "Ans_1":None, "Ans_2":None, "Ans_3":None, "Ans_4":None, "Ans_5":None, "Ans_6":None, "Ans_7":None, "Ans_8":None, "Ans_9":None, "Ans_10":None }
	stemmer = PorterStemmer()
	preprocessed_query = gensim.utils.simple_preprocess(input_query, max_len = 20)
	filtered_sentence = []
 	for word in preprocessed_query:
		if word not in stop_words:
			filtered_sentence.append(word)
	preprocessed_query = filtered_sentence
	preprocessed_query = stemmer.stem_documents(preprocessed_query)
	expanded_query = set(get_expanded_query(preprocessed_query, model, vocabulary)) 
	eq_vector = get_eq_tfidf_vector(inverted_index, expanded_query, preprocessed_query, length_preprocessed)
	relevant_docs = get_relevantdocs(expanded_query, inverted_index)
	try:
		tfidf_scores = get_scores(relevant_docs, eq_vector, norms, nod, list_of_document_tfidf_dicts)
		if not tfidf_scores:
			ANSWER['error'] =  'Match Not Found.'
			return ANSWER
	except ZeroDivisionError:
		ANSWER['error'] = 'Please be more specific.'
		return ANSWER	
	user_id = 50
	db = pymysql.connect("localhost", "qasys", "321@demo", "QA_system")
	cursor = db.cursor()
	fp = open('document-index.txt', 'rb')
	doc_index = pickle.load(fp)
	fp.close()
	nb_documents = len(doc_index) 	
	user_document_array = np.zeros(nb_documents)
	doc_ids = doc_index.values()
	userId = 46                 #Add this to main
	try:
		sql = "SELECT DOC_ID, CLICKS FROM user_clicks WHERE USER_ID = " + str(userId)
		cursor.execute(sql)		
		rows = cursor.fetchall()
		for row in rows:
			user_document_array[doc_ids.index(str(row[0]))] = row[1]
	except Exception as e:
		print e
		print "Error in getting user viewed documents"
		db.rollback()
	user_document_array = torch.FloatTensor(user_document_array)
  	reco_sys_scores = [item.item() for item in sae.forward(Variable(user_document_array).unsqueeze(0))[0]]
	db.close()
	scores = dict()
	factor = 0.03
	for doc_number in tfidf_scores.keys():
		scores[doc_number] = 0.9 * tfidf_scores[doc_number] + 0.1 * factor * reco_sys_scores[document_dictionary.keys().index(doc_number)]	#same as doc_number - 1 !
	heap_docs = [(-value, key) for key,value in scores.items()]
	largest_docs = heapq.nsmallest(10, heap_docs)
	largest_docs = [(key, -value) for value, key in largest_docs]	
############################### End of document ranking ######################################
	preprocessed_tuple = []
	for x in largest_docs:
		fp = open('spreprocessed' + str(x[0]) + '.txt', 'rb')
		list_temp = pickle.load(fp)
		preprocessed_tuple.extend([(x[0],y) for y in list_temp])
		fp.close()
	vocabulary2 = list(expanded_query)
	inverted_index2= get_inverted_index_query_terms(preprocessed_tuple, vocabulary2)
	relevant_sent = get_relevantdocs(expanded_query, inverted_index2)
	scores_bm25 = get_bm25(relevant_sent, inverted_index2, expanded_query, preprocessed_tuple)
	heap_sentences = [(-value, key) for key,value in scores_bm25.items()]
	largest_sentences = heapq.nsmallest(100, heap_sentences)
	largest_sentences = [(key, -value) for value, key in largest_sentences]
	sentenced_docs = set()
	for sentence in [x[0] for x in largest_sentences]:
		sentenced_docs.add(preprocessed_tuple[sentence-1][0])
		sentenced_docs_copy = [x for x in sentenced_docs]
	index_ans = get_index_ans(preprocessed_tuple, sentence_number = largest_sentences[0][0])	
	fp = open('cmptext.txt', 'rb')
	doc = 1
	for line in fp:
		if doc == preprocessed_tuple[largest_sentences[0][0]-1][0]:
			#ANSWER +=  'MAIN ANSWER : ' + str(line.split('. ')[index_ans]) + '\n'
			ANSWER['main_ans'] = str(line.split('. ')[index_ans])
		doc += 1
	fp.close()
	doc_num_ans = 0			
	for sentence in [x[0] for x in largest_sentences]:
		doc_number_of_sentence = preprocessed_tuple[sentence-1][0]
		if doc_number_of_sentence in sentenced_docs:
			#ANSWER += 'Document ' + str(doc_number_of_sentence) + '\n'
			doc_num_ans += 1
			index_ans = get_index_ans(preprocessed_tuple, sentence_number = sentence)
			fp = open('cmptext.txt', 'rb')
			doc = 1
			for line in fp:
				if doc == doc_number_of_sentence:
					#ANSWER += 'SENTENCE : ' + str(line.split('. ')[index_ans]) + '\n'
					ANSWER['Ans_' + str(doc_num_ans)] = document_dictionary[doc_number_of_sentence], str(line.split('. ')[index_ans]), str(id_links[document_dictionary[doc_number_of_sentence]]) ##
				doc += 1 
			fp.close()
			sentenced_docs.remove(doc_number_of_sentence)
		else:
			continue			
	return ANSWER


def main():
	input_query = 'primary argon purification circuit'
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
	with open("document-index.txt", "rb") as fp:
		document_dictionary = pickle.load(fp)
	fp.close()
	with open('norms.txt', 'rb') as fp:
		norms = pickle.load(fp)
	with open('tfidf-scores.txt', 'rb') as fp:
		nod = pickle.load(fp)		
		list_of_document_tfidf_dicts = pickle.load(fp)
	id_items = pickle.load(open('id_links.txt','rb'))
	sae = torch.load('my_sae.pt')
	print 'Executing function here'
	answer = live(model, input_query, vocabulary, length_preprocessed, inverted_index, document_dictionary, norms, nod, list_of_document_tfidf_dicts,  sae, id_items)
	print answer

if __name__ == '__main__':
	main()
	





