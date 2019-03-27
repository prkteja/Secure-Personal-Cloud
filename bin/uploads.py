import pickle
import sys
import requests
from getpass import getpass
import os
import tempfile
from sjcl import SJCL
import json
import base64
import hashlib

red = '\033[91m'
green = '\033[92m'
end_c = '\033[0m'
fullpath = sys.argv[0]
path = os.path.dirname(fullpath)
files = dict()
data = dict()
	
try:
	print("Reading User information ...")
	f = open(path+'/spc_user_data', 'rb')
	data = pickle.load(f)
except IOError:
	print(red+"Authentication credentials not found"+end_c)
	u = input("Enter Username:")
	p = getpass("Enter Password:")
	url = input("Enter Server URL:")
	enc = input("Enter Encryption Scheme:")
	key = input("Enter Encryption key:")
	if url[len(url)-1] != '/':
		url = url + '/'
	data['username'] = u
	data['password'] = p
	data['url'] = url
	data['enc_scheme'] = enc
	data['key'] = key
	save = input('Would you like to save the configuration? [y/n]:')
	if save == 'y' or save == 'Y':
		f = open(path+'/spc_user_data','wb')
		pickle.dump(data,f)
		print("User credentials updated")
		f.close()
# key = 'shared_secret'
red = '\033[91m'
green = '\033[92m'
end_c = '\033[0m'
md5sum = ""
files = {}
try:
	# print(sys.argv[1])
	file = open(sys.argv[1], 'rb')
	hash = hashlib.md5()
	blocksize=65536
	for block in iter(lambda: file.read(blocksize), b""):
		hash.update(block)
	md5sum = hash.hexdigest()
	file.close()
	file = open(sys.argv[1], 'rb')
	text = file.read()
	# print(text)
	b = base64.b64encode(text)
	#b = text
	# print(b)
	strr = data['key']
	cyphertext = SJCL().encrypt(b, str(strr))
	# sys.exit()
	for key in cyphertext:
		if type(cyphertext[key]) is bytes:
			cyphertext[key] = cyphertext[key].decode('ascii')
	temp = tempfile.NamedTemporaryFile(mode='w+')
	temp.name = file.name
	temp.write(json.dumps(cyphertext))
	temp.seek(0)
	# f = open('newnewtemp.file','w')
	# f.write(json.dumps(cyphertext))
	# f.close()
	# f = open('newnewtemp.file', 'r')
	files = {'document' : temp}
except IOError:
	print("file {} not found".format(sys.argv[1]))
	sys.exit()
print("Reading file {}".format(sys.argv[1]))
filepath = sys.argv[2]


base_url = data['url']
url = base_url+'login/'
client = requests.session()
try:
	print("connecting to server ...")
	client.get(url)
except requests.ConnectionError as e:
	print(red+"The following error occured connecting to the server: {}\n Please try again".format(e)+end_c)
	client.close()
	sys.exit()

try:
	csrf = client.cookies['csrftoken']
except():
	print(red+"Error obtaining csrf token"+end_c)
	client.close()
	sys.exit()
payload = dict(username=data['username'], password=data['password'], csrfmiddlewaretoken=csrf, next='/upload_file/')
try:
	print("Sending request ...")
	r = client.post(url, data=payload, headers=dict(Referer=url))
	r.raise_for_status()
	if r.status_code == 200:
		print("Request sent ...")
		if r.url == url:
			print(red+"User authentication failed. Please try again"+end_c)
			client.close()
			sys.exit()
		else:
			try:
				print("Uploading file ...")
				r2 = client.post(base_url+'upload_file/', data={'filepath': filepath,'md5sum' : md5sum, 'csrfmiddlewaretoken': r.cookies['csrftoken']}, files=files )
				r2.raise_for_status()
				if r2.status_code != 200:
					print(red+"An error occured . status_code = {}".format(r2.status_code)+end_c)
					sys.exit()
				elif r2.url == base_url:
					print(green+"File upload successful"+end_c)
				else:
					print(red+"An error occured"+end_c)
			except() as e:
				print(red+"error posting file: {}".format(e)+end_c)
except requests.exceptions.HTTPError as e:
	print(red+'HTTP error: {}'.format(e)+end_c)
except requests.exceptions.RequestException as e:
	print(red+'Connection Error: {}'.format(e)+end_c)
	client.close()
	sys.exit()
