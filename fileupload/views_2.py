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

import binascii
from Crypto.Cipher import AES

# Create your views here.




def home(request):

    # process_department= process_entry_id= process_form_id= user_name= project= asset = 0


    my_password = b"mysecretpassword"
    # my_data = b"input_string_to_encrypt/decrypt"
    my_data = request.META['QUERY_STRING'].encode('utf-8')

    # encrypted = encrypt(my_password, my_data)
    # decrypted = decrypt(my_password, encrypted)
    #
    # encrypted0 = {
    #     'encoded': encrypted,
    #     'decoded': decrypted,
    # }
    #
    # cipher = AESCipher("mysecretpassword")
    # encrypted = cipher.encrypt(request.META['QUERY_STRING'])
    # decrypted = cipher.decrypt(encrypted)
    #
    #
    # encrypted1 = {
    #     'encoded': encrypted,
    #     'decoded': decrypted,
    # }

    data = "abcdefghijklmnopqrstuvwxyz"
    key = "pqrstuvwxyz$abcdefghijAB"
    iv = "DEFGHTABCIESPQXO"

    encrypted = "2324ab5ec7a901247bf01b08bd1956688843dad5a8e15106ca3a5b9258918527"

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(binascii.unhexlify(encrypted))

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

    # return render(request, 'fileupload/submit.html', {'decrypted' : decrypted,'data' :data, 'metadata' : metadata,'encrypted' : encrypted0,'encrypted1' : encrypted1})
    return render(request, 'fileupload/submit.html', {'decrypted' : decrypted})
