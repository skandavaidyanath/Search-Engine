import json
import urllib

def download_file(download_url):
	web_file = urllib.urlopen(download_url)
	json_object = json.loads(web_file.read())
	return json_object


def construct_pdf(ID, filename):
	url = 'http://10.30.1.21/showFile.php?file=' + str(filename)
	fpw = open('./my_root/file_' + str(ID) + '.pdf', 'wb')
	web_file = urllib.urlopen(url)
	for line in web_file.read():
		fpw.write(line)
	fpw.close()	

def main():
	json_object = download_file('http://10.30.1.21/index/ajaxfileserver')
	for item in json_object:
    		ID = item['ID']
		filename = item['Filename']
		construct_pdf(ID, filename)
		print 'file number ' + str(ID) + ' done'

if __name__ == '__main__':
	main()


