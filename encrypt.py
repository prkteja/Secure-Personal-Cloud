from sjcl import SJCL
import json
import base64

# file = open('newfile', 'rb')
# text = file.read()
# b = base64.b64encode(text)
# #b = text
# cyphertext = SJCL().encrypt(b, "shared_secret")
# file.close()
# # print(cyphertext)
# f = open('newfile.enc', 'w')
# for key in cyphertext:
#     if type(cyphertext[key]) is bytes:
#         cyphertext[key] = cyphertext[key].decode('ascii')
# f.write(json.dumps(cyphertext))
# f.close()

# file = open('newfile.enc', 'rb')
# f = file.read()
# f = json.loads(f)

# for key in f:
#     if key == 'salt' or key == 'ct' or key == 'iv':
#         f[key] = f[key].encode('ascii')
# t = SJCL().decrypt(f, 'shared_secret')
# t1 = base64.b64decode(t)
# print(t1)
