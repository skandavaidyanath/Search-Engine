import json
import urllib
import pickle

def download_file(download_url):
	web_file = urllib.urlopen(download_url)
	json_object = json.loads(web_file.read())
	return json_object

lst = dict()
for item in download_file('http://10.30.1.21/index/ajaxfileserver'):
	lst[item['ID']] = item['Filename']
with open('id_links.txt','wb') as fp:
	pickle.dump(lst,fp)
