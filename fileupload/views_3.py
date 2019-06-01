from django.shortcuts import render, redirect, reverse

import urllib.parse

from Crypto.Cipher import AES
import base64




def _unpad(s): return s[0:-s[-1]]
def _pad(s): return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
def _cipher():
    key = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    iv = 'AAAAAAAAAAAAAAAA'
    return AES.new(key=key, mode=AES.MODE_CBC, IV=iv)

def encrypt_token(data):
    return _cipher().encrypt(_pad(data))

def decrypt_token(data):
    return _unpad(_cipher().decrypt(data))

def maybeencode(qs, encode = True):
    if encode:
        try:
            qstr = dict(urllib.parse.parse_qsl(qs))

            temp_qs = ""

            # for k, v in qstr.items():
            #     encval = base64.b64encode(encrypt_token(v)).decode()
            #     if temp_qs:
            #         temp_qs += "&"
            #     temp_qs += "{}={}".format(k, encval)

            enc = base64.b64encode(encrypt_token(qs))
            print("enc : {} ".format(enc) )
            return enc.decode()
        except Exception as e:
            return ""
    else:
        return ""


def maybedecode(qs):

    # Check if qs is encrypted
    try:

            test = urllib.parse.parse_qsl(qs)
            if not test:
                print("Request URL is encrypted. Decrypting request URL")
                dec = decrypt_token(base64.b64decode(qs)).decode('utf-8')
                print("dec : {} ".format(dec) )
                return dec
            else:
                return qs


    except Exception as e:
        pass


    # enc = base64.b64encode(encrypt_token(qs))
    # print("enc : {} ".format(enc) )
    # qs = enc



def add_qsForTest():
    qs = "process_department=modelling&process_ent_id=123&user=Pooja&project=ABC&asset=Chair"
    qs = "p=modelling&pe_id=123&u=Pooja Mahesh Gori&pr=Some Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Long Project Name&as=Some Very Long Asset Name"
    # qs = "p:modelling,pe_id:123,u:'Pooja Mahesh Gori'&pr=Some Very Long Project Name&as=Some Very Long Asset Name"
    return qs
    # process_department= process_entry_id= process_form_id= user_name= project= asset = 0

def home(request):

    queryStr =request.META['QUERY_STRING']

    if not queryStr: # no querystring found in url
        queryStr = add_qsForTest()
        # return redirect(reverse('home') + "?" + qs)

    # qs = maybeencode(queryStr).decode()
    # qs = maybeencode(queryStr, False)
    qs = maybeencode(queryStr)

    if not qs:
        # print("If qs is empty")
        pass
    else:
        queryStr = qs
        print("qs : {} ".format(queryStr) )
        return redirect(reverse('home') + "?" +  queryStr)

        # return redirect(reverse('home') + qs)

    queryStr = maybedecode(queryStr)

    # print("qs : {} ".format(queryStr) )

    data = dict(urllib.parse.parse_qsl(queryStr))

    # verification_code = urllib.parse.unquote_plus(request.GET.get('a'))
    # userid = urllib.parse.unquote_plus(request.GET.get('b'))

    # metadata = {
    #     'verification_code': verification_code,
    #     'userid': userid,
    # }

    # return render(request, 'fileupload/submit.html', {'decrypted' : decrypted,'data' :data, 'metadata' : metadata,'encrypted' : encrypted0,'encrypted1' : encrypted1})
    return render(request, 'fileupload/submit.html', {'qs': data})
