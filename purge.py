import pymysql
import pickle

def main():
	db = pymysql.connect("localhost", "qasys", "321@demo", "QA_system")
	cursor = db.cursor()
	fp = open('document-index.txt', 'rb')
	doc_index = pickle.load(fp)
	fp.close()
	docs = [int(i) for i in doc_index.values()]
	for doc in range(min(docs), max(docs) + 1):
		if doc not in docs:
			try:
				sql = "DELETE FROM user_clicks WHERE DOC_ID = " + str(doc)
				cursor.execute(sql)
				db.commit()
				print str(doc) + " deleted"
			except Exception as e:
				print e
				db.rollback()
	db.close()


if __name__ == '__main__':
	main()
