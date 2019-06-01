from django.shortcuts import render

import urllib.parse

# import base64
# import sys
#
# import hashlib
#
#
# from Crypto.Cipher import AES
# import base64
#
# from Crypto import Random
# from Crypto.Cipher import AES

import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

# Create your views here.

def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding



def home(request):


    my_password = b"mysecretpassword"
    # my_data = b"input_string_to_encrypt/decrypt"
    my_data = request.META['QUERY_STRING'].encode('utf-8')

    encrypted = encrypt(my_password, my_data)
    decrypted = decrypt(my_password, encrypted)

    encrypted0 = {
        'encoded': encrypted,
        'decoded': decrypted,
    }

    cipher = AESCipher("mysecretpassword")
    encrypted = cipher.encrypt(request.META['QUERY_STRING'])
    decrypted = cipher.decrypt(encrypted)


    encrypted1 = {
        'encoded': encrypted,
        'decoded': decrypted,
    }

    # cipher = AESCipher('mysecretpassword')
    # encrypted = cipher.encrypt('Secret Message A')
    # decrypted = cipher.decrypt(encrypted)
    #
    # encrypted2 = {
    #     'encoded': encrypted,
    #     'decoded': decrypted,
    # }


    queryStr =request.META['QUERY_STRING']
    data = urllib.parse.parse_qs(queryStr)

    verification_code = urllib.parse.unquote_plus(request.GET.get('a'))
    userid = urllib.parse.unquote_plus(request.GET.get('b'))

    metadata = {
        'verification_code': verification_code,
        'userid': userid,
    }

    return render(request, 'fileupload/submit.html', {'data' :data, 'metadata' : metadata,'encrypted' : encrypted0,'encrypted1' : encrypted1})

BS = 16
def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
def unpad(s):
    return s[0:-s[-1]]

class AESCipher:

    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))
