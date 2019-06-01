from django.shortcuts import render, redirect, reverse

import urllib.parse

import base64

def encode1(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode1(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def maybeencode(qs, encode = True):
    if encode:
        try:
            test = dict(urllib.parse.parse_qsl(qs))
            print("Test : {} ".format(test) )
            # enc = base64.b64encode(encrypt_token(qs))
            # print("enc : {} ".format(enc) )
            # return enc.decode()
            if test and "p" in test:
                print("p found");
                enc = encode1("123", qs)
            else:
                enc = ""
                print("p not found");

            # print("enc : {} ".format(enc) )
            return enc

        except Exception as e:
            return ""
    else:
        return ""


def maybedecode(qs):

    # Check if qs is encrypted
    try:

            test = urllib.parse.parse_qsl(qs)
            if not test or "p" not in test:


            # if not test:
                # print("Request URL is encrypted. Decrypting request URL")
                # dec = decrypt_token(base64.b64decode(qs)).decode('utf-8')
                # print("dec : {} ".format(dec) )

                dec = decode1("123", qs)
                print("dec : {} ".format(dec) )
                return dec
            else:
                return qs


    except Exception as e:
        pass


def add_qsForTest():
    qs = "process_department=modelling&process_ent_id=123&user=Pooja&project=ABC&asset=Chair"
    qs = "p=modelling&pe_id=123&u=Pooja Mahesh Gori&pr=Some Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Long Project Name&as=Some Very Long Asset Name"
    # qs = "p:modelling,pe_id:123,u:'Pooja Mahesh Gori'&pr=Some Very Long Project Name&as=Some Very Long Asset Name"
    return qs
    # process_department= process_entry_id= process_form_id= user_name= project= asset = 0

count = 0
def home(request):

    queryStr =request.META['QUERY_STRING']

    if not queryStr: # no querystring found in url
        queryStr = add_qsForTest()
        # return redirect(reverse('home') + "?" + qs)

    # qs = maybeencode(queryStr).decode()
    # qs = maybeencode(queryStr, False)
    qs = maybeencode(queryStr)
    # print("qs  : {} ".format(qs) )

    if not qs:
        # print("If qs is empty")
        pass
    else:
        global count
        queryStr = qs
        # print("qs : {} ".format(queryStr) )
        count = count + 1
        print("COUNT  : {} ".format(count) )
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
