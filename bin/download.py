import pickle
import sys
import requests
from getpass import getpass
from bs4 import BeautifulSoup
import os.path
from sjcl import SJCL
import json
import base64
import ast
import tempfile

fullpath = sys.argv[0]
path = os.path.dirname(fullpath)
data = dict()
filename = sys.argv[1]


red = '\033[91m'
green = '\033[92m'
end_c = '\033[0m'

try:
    print("Reading User information ...", end="      ")
    f = open(path+'/spc_user_data', 'rb')
    data = pickle.load(f)
    print("done")
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
base_url = data['url']
url = base_url + 'login/'
client = requests.session()
try:
    print("connecting to server ...", end="      ")
    client.get(url)
    print("done")
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
payload = dict(username=data['username'], password=data['password'], csrfmiddlewaretoken=csrf, next='/')
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
        print("Reading files ...")
    r1 = client.get(base_url)
    soup = BeautifulSoup(r1.text, 'html.parser')
    productDivs = soup.findAll('a', attrs = {"id" : "filename"})
    productDivs2 = soup.findAll(attrs = {"id" : "filepath"})
    print("Searching for {} ...".format(filename))
    for link,li in zip(productDivs,productDivs2):
        if link.string == filename and sys.argv[2] == li.string.split()[2]:
            # print('sdfs')
            var = base_url[:-1] + link['href']
            try:
                # print(var)
                r2 = client.get(var, allow_redirects=True)
                print("Downloading ...", end="      ")
                f = open(filename, 'wb')
                # print(r2.text)
                text = r2.text
                # print(text)
                # text = text.encode('utf-8')
                # text = base64.b64decode(text)
                # print(type(text))

                # print(text)
                # print(type(r2.content))
                text = json.loads(text)
                # print(text)
                # print(type(text))
                # for it in text:
                #     try:
                #         text[it] = int(text[it])
                #     except:
                #         pass
                # print(text)


                # class mydict(dict):
                #     def __str__(self):
                #         return json.dumps(self)
                # text = mydict(text)
                for key in text:
                    if key == 'salt' or key == 'ct' or key == 'iv':
                        text[key] = text[key].encode('ascii')
                # print(text)
                # text = {"salt": "1sMrwmhD9uo=", "iter": 10000, "ks": 128, "ct": "IY3k1LcEUSQ=", "iv": "JReeuzEISWe1PjLzNCLMXw==", "cipher": "aes", "mode": "ccm", "adata": "", "v": 1, "ts": 64}
                dec = SJCL().decrypt(text, 'shared_secret')
                # dec = dec.decode('ascii')
                # dec = base64.b64decode(dec)
                # dec = base64.decodebytes(dec)
                # dec = ('data:text/plain;base64,') + dec
                dec = base64.b64decode(dec)
                # dec = base64.b64decode('data:image/jpeg;base64,') + dec
                dec = dec.decode('ascii')
                # prepend_info = 'data:image/jpeg;base64'
                # dec = base64.decodebytes(dec)
                  #output file
                # print(dec)
                f.write(dec)
                f.close()
                print(green+"done"+end_c)
            except() as e:
                print(red+"Error connecting: {}".format(e)+end_c)


except requests.exceptions.HTTPError as e:
    print(red+'HTTP error: {}'.format(e)+end_c)
except requests.exceptions.RequestException as e:
    print(red+'Connection Error: {}'.format(e)+end_c)
    client.close()
    sys.exit()

client.close()
