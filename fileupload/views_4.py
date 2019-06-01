from django.shortcuts import render, redirect, reverse

import urllib.parse
import base64
from Crypto.Cipher import AES

from .forms import SubmitForm
from .models import SubmissionDetails

def _unpad(s): return s[0:-s[-1]]
def _pad(s): return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
def _cipher():
    key = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    iv = 'AAAAAAAAAAAAAAAA'
    return AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
def encrypt_token(data): return _cipher().encrypt(_pad(data))
def decrypt_token(data): return _unpad(_cipher().decrypt(data))

def test_makeQS(request,queryStr):
    redirect = False
    debug = True
    if debug:
        if not queryStr: # no querystring found in url
            queryStr = add_qsForTest()

        qs = maybe_encode(queryStr, True)

        if not qs:
            if not request.META['QUERY_STRING']:
                redirect = True
                # return redirect(reverse('submit_form') + "?" +  queryStr)
        else:
            global count
            queryStr = qs
            redirect = True
            # return redirect(reverse('submit_form') + "?" +  queryStr)
    return redirect, queryStr;
def maybe_encode(qs, encode = True):
    if encode:
        try:
            test = dict(urllib.parse.parse_qsl(qs))
            if test and "process_department" in test:
                enc = base64.b64encode(encrypt_token(qs)).decode()
            else:
                enc = ""
            # print("enc : {} ".format(enc) )
            return enc

        except Exception as e:
            return ""
    else:
        return ""

def maybe_decode(qs):
    try:
        test = dict(urllib.parse.parse_qsl(qs))
        # print("test :  {}".format(test))

        if not test or "process_department" not in test:
            dec = decrypt_token(base64.b64decode(qs)).decode('utf-8')
            qs = dec

        return qs
    except Exception as e:
        pass

def add_qsForTest():
    qs = "process_department=modelling&process_ent_id=123&user=Pooja&project=Some Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Long Project Name&asset=Chair&version=0.3"
    # qs = "p=modelling&pe_id=123&u=Pooja Mahesh Gori&pr=Some Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Very Long Project Name&as=Some Very Long Asset Name"
    # qs = "p:modelling,pe_id:123,u:'Pooja Mahesh Gori'&pr=Some Very Long Project Name&as=Some Very Long Asset Name"
    return qs
    # process_department= process_entry_id= process_form_id= user_name= project= asset = 0

# def home(request):
#     submit(request)

def submit_form_1(request):

    queryStr =request.META['QUERY_STRING']

    if not queryStr: # no querystring found in url
        queryStr = add_qsForTest()

    qs = maybe_encode(queryStr, False)

    if not qs:
        if not request.META['QUERY_STRING']:
            return redirect(reverse('submit_form') + "?" +  queryStr)
    else:
        global count
        queryStr = qs
        return redirect(reverse('submit_form') + "?" +  queryStr)

    queryStr = maybe_decode(queryStr)

    data = dict(urllib.parse.parse_qsl(queryStr))

    return render(request, 'fileupload/submit.html', {'qs': data})

def submit_form(request):
    if request.method == 'GET':
        return submit_form_get(request)
    else:
        return submit_form_post(request)




def submit_form_get(request):
    queryStr =request.META['QUERY_STRING']

    redirectpage , queryStr = test_makeQS(request,queryStr)
    if redirectpage:
        return redirect(reverse('submit_form') + "?" +  queryStr)

    print("queryStr :  {}".format(queryStr))
    queryStr = maybe_decode(queryStr)
    print("maybe_decode queryStr :  {}".format(queryStr))

    data = dict(urllib.parse.parse_qsl(queryStr))
    # print("DATA :  {}".format(data))

    if not request.META['QUERY_STRING']:
        return render(request, 'fileupload/submit.html', {'qs': data})
    else:
        submit_form = SubmitForm();
        # print("process_department :  {}".format(data['process_department']))
        # submit_form.process_department = data['process_department'];
        # print("submit_form :  {}".format(submit_form))
        # print("submit_form.process_department :  {}".format(submit_form.process_department))
        return render(request, 'fileupload/submit.html', {'submitForm': submit_form, 'qs': data})

def submit_form_post(request):
    # print(" REQUEST POST : {}".format(dict(request.POST)))
    # print(" REQUEST POST : {}".format(request.POST))
    submitted_form = SubmitForm(request.POST)

    if submitted_form.is_valid():
        submitted_form = submitted_form.save(commit=False)
        # print(" SUBMITED FORM : {}".format(submitted_form.cleaned_data))
        # post = dict(request.POST);

        post = request._post
        print(" REQUEST POST : {}".format(request.POST))

        submitted_form.process_department = post["process_department"][0];
        submitted_form.version = post["version"][0];


        submitted_form.save()
        note = "Form has been submitted successfully with values %s %s. Version No : %s" %(submitted_form.process_department,submitted_form.cleaned_data['comments'], submitted_form.version );

        new_form = SubmitForm();
        return render(request, 'fileupload/submit.html', {'submitForm': new_form, 'note': note})
