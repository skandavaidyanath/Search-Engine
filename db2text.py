import pymysql
import random
import pickle

def db2text():
	db = pymysql.connect('localhost','qasys','321@demo','QA_system')
	cursor = db.cursor()
	fp = open('document-index.txt', 'rb')
	doc_index = pickle.load(fp)
	doc_ids = doc_index.values()	
	fp.close()
	fp1 = open('q1.test', 'w+')
	fp2 = open('q1.base', 'w+')
	try:
		sql = "SELECT MIN(ID), MAX(ID) FROM user_clicks"
		cursor.execute(sql)
		row = cursor.fetchone()
		min_index = row[0]
		max_index = row[1]
		num_of_rows = max_index - min_index + 1
		test_cases = 0.2 * num_of_rows
		test_indices = random.sample(range(min_index, max_index+1), int(test_cases))
		for index in test_indices:
			try:
				sql = "SELECT * FROM user_clicks WHERE ID = " + str(index)
				cursor.execute(sql)
				row = cursor.fetchone()
                		userId = row[1]
				docId = row[2]
				clicks = row[3]
				fp1.write(str(userId) + '\t' + str(docId) + '\t' + str(clicks) + '\n')
				print 'Written to test'
			except Exception as e:
				print e
				print "Error in generating test-cases"
				db.rollback()
		training_indices = list(filter((lambda x: x not in test_indices), range(min_index, max_index+1)))
		for index in training_indices:
			try:
				sql = "SELECT * FROM user_clicks WHERE ID = " + str(index)
				cursor.execute(sql)
				row = cursor.fetchone()
                		userId = row[1]
				docId = row[2]
				clicks = row[3]
				fp2.write(str(userId) + '\t' + str(docId) + '\t' + str(clicks) + '\n')
				print 'Written to train'
			except Exception as e:
				print e
				print "Error in generating training-cases"
				db.rollback()
	except Exception as e:
		print e
		print "Error in getting total number of rows"
		db.rollback()
	fp1.close()
	fp2.close()
	db.close()

if __name__ == '__main__':
	db2text()

