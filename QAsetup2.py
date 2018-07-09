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
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import sys, getopt

stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

document_index = dict()


def read_pdf(filename):
	pdfFileObj = open(filename, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	num_pages = pdfReader.numPages
	count = 0
	text = ""
	scanned = False
	try:
		while count < num_pages:
			pageObj = pdfReader.getPage(count)
			count += 1
			text += pageObj.extractText()
		if text != "":
			text = text
		else:
			text = textract.process(filename, method = 'tesseract', language = 'eng')
			scanned = True
	except Exception as e:
		raise e 
	return text, scanned



def recursive_read(path,file3):
	number_of_documents = 0
	global document_index
	for filename in os.listdir(path):
     		filenm = path + "/" + filename
     		if(os.path.isdir(filenm)):
			number_of_documents += recursive_read(filenm,file3)
		else:
			ID = filenm.split('_')[1].split('.')[0]
			try:
				text, scanned = read_pdf(filenm)
				if not scanned:
					text = text.encode('utf-8').split('\n')
				else:
					text = text.split('\n')
				for word in text:
					file3.write(word)
					file3.write(' ')
				del text[:]
				file3.write('\n')
				print 'Document Read ' + str(ID)
				number_of_documents += 1
				document_index[number_of_documents] = ID
			except Exception as e:
				print e
				print '!!!!!!!!! WARNING READ FAILED !!!!!!!! ' + str(ID)
	return number_of_documents	


def preprocess(file_name, number_of_documents):
	stemmer = PorterStemmer()
	fp1 = open("preprocessed.txt", "wb")
	fp2 = open("preprocessed-cmptext.txt", "wb")
	pickle.dump(number_of_documents, fp1)
	for line in file_name:
		preprocess_list1 = gensim.utils.simple_preprocess(line, max_len = 20)
		preprocess_list2 = []
		for word in preprocess_list1:
			if word not in stop_words:
				preprocess_list2.append(word)
		pickle.dump(stemmer.stem_documents(preprocess_list2), fp1)
		for word in preprocess_list2:
			fp2.write(stemmer.stem(word.encode('utf-8')))
			fp2.write(' ')
		fp2.write('\n')
	fp1.close()
	fp2.close()


def get_word2vec(number_of_documents):
	documents = gensim.models.word2vec.LineSentence("preprocessed-cmptext.txt")
	bigram = gensim.models.Phrases(documents)
	trigram = gensim.models.Phrases(bigram[documents])
	model = gensim.models.Word2Vec(trigram[bigram[documents]],size=300,window=10,min_count=5,workers=10) #increase min_count ?
	model.train(documents, total_examples=number_of_documents, epochs=10)  #increase epochs ?
	return model


def get_inverted_index(dictionary):
	inverted_index = dict((el,[]) for el in dictionary)
	fp = open("preprocessed.txt", "rb")
	length_preprocessed = pickle.load(fp)
	doc_number = 1
	for _ in range(length_preprocessed):
		document = pickle.load(fp)
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
	fp.close()
	return inverted_index


def calc_wt(text, word, inverted_index, length_preprocessed): 		
	if "_" in word:
		if len(text) > 30:
			n_words = word.split("_")
			number_of_occurences = 0
			if (len(n_words) == 2):
				for i in range(len(text)-1):
					if text[i] == n_words[0] and text[i+1] == n_words[1]:
						number_of_occurences += 1
			if (len(n_words) == 3):
				for i in range(len(text)-2):
					if text[i] == n_words[0] and text[i+1] == n_words[1] and text[i+2] == n_words[2]:
						number_of_occurences += 1
			if (len(n_words) == 4):
				for i in range(len(text)-3):
					if text[i] == n_words[0] and text[i+1] == n_words[1] and text[i+2] == n_words[2] and text[i+3] == n_words[3]:
						number_of_occurences += 1
				
			tf = log(1 + number_of_occurences,10)
		else:
			tf = log(1 + text.count(word),10)
		idf = log((float(length_preprocessed)/len(inverted_index[word])),10)	
			
	else:
		tf = log((1 + text.count(word)),10)
		idf = log((float(length_preprocessed)/len(inverted_index[word])),10)	
	return tf*idf


def get_tfidf_vectors(inverted_index, length_preprocessed):
	list_of_document_tfidf_dicts = list()
	document_tfidf = dict()
	fp1 = open("tfidf-scores.txt", "wb")
	pickle.dump(length_preprocessed, fp1)
	fp2 = open("preprocessed.txt", "rb")
	length_preprocessed = pickle.load(fp2)
	for i in range(length_preprocessed):
		document = pickle.load(fp2)
		for word in inverted_index.keys():
			value = calc_wt(document, word, inverted_index, length_preprocessed)
			document_tfidf[word] = value
		list_of_document_tfidf_dicts.append(document_tfidf)  
		print 'Document number ' + str(i+1) + ' tfidf done' 
		document_tfidf = dict()
       	pickle.dump(list_of_document_tfidf_dicts, fp1)
	fp1.close()
	fp2.close()


def get_norms():
	fp1 = open("norms.txt", "wb")
	fp2 = open("tfidf-scores.txt", "rb")
	nod = pickle.load(fp2)
	dic_of_norms = dict()
	doc_number = 1
	lst = pickle.load(fp2)
	for i in range(nod):
		norm = 0
		dic = lst[i]
		for item in dic.values():
			norm += item**2
		norm = norm**0.5
		dic_of_norms[doc_number] = norm
		doc_number += 1
		print 'Document number ' + str(i+1) + ' norm calc done' 
	pickle.dump(dic_of_norms, fp1)
	fp1.close()
	fp2.close()


def main():
############################## Setup Code #####################################
	global document_index
	path = "./myroot"
	file3 = open("cmptext.txt","w+")
	number_of_documents = recursive_read(path,file3)
	file3.close() 
	print 'All files read'
	file3 = open("cmptext.txt","r")
	preprocess(file3, number_of_documents)	
	file3.close()
	print 'All files processed'
	print 'Word2Vec begins'
	model = get_word2vec(number_of_documents)       #includes trigrams
	model.save('vocab.txt')
	print 'Word2Vec done'
	vocabulary = model.wv.vocab.keys()
	inverted_index = get_inverted_index(vocabulary)
	for item in inverted_index.keys():
		if not inverted_index[item]:
			del inverted_index[item]
	with open("inverted-index.txt", "wb") as fp:   
        	pickle.dump(inverted_index, fp)
	fp.close()
	get_tfidf_vectors(inverted_index, number_of_documents)
	get_norms()
	doc_num = 0
	file1 = open("cmptext.txt","r")
	stemmer = PorterStemmer() 
	for document in file1: 
		spreprocessed = []
		doc_num += 1
		for line in document.split('. '):
			temp1 = []
			temp2 = []
			temp1 = gensim.utils.simple_preprocess(line, max_len = 20)
			for word in temp1:
				if word not in stop_words:
					temp2.append(word)
			spreprocessed.append(stemmer.stem_documents(temp2))
		with open("spreprocessed" + str(doc_num) + ".txt", "w+") as fp:  
			pickle.dump(spreprocessed,fp)
		fp.close()
		del spreprocessed[:]
	file1.close()
	with open("document-index.txt", "wb") as fp:   
        	pickle.dump(document_index, fp)
	fp.close()

if __name__ == '__main__':
	main()
