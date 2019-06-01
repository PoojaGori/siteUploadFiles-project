from django.shortcuts import render, redirect, reverse
from .uploadhandler_ftp import FTPUploadHandler

import urllib.parse
import base64
from Crypto.Cipher import AES

from .forms import SubmitForm
from .models import SubmissionDetails

from django.views.decorators.csrf import csrf_exempt, csrf_protect

def _unpad(s): return s[0:-s[-1]]
def _pad(s): return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
def _cipher(): return AES.new(key='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', mode=AES.MODE_CBC, IV='AAAAAAAAAAAAAAAA')
def encrypt_token(data): return _cipher().encrypt(_pad(data))
def decrypt_token(data): return _unpad(_cipher().decrypt(data))
def add_qsForTest(): return "process_department=riging&process_ent_id=123&user=Pooja&project=Pogo&asset=Chair&version=0.3"

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



# def home(request):
#     submit(request)

@csrf_exempt
def submit_form(request):

    if request.method == 'GET':
        return submit_form_get(request)
    else:
        data = request.session.get('data')
        print(" data : {}".format(data))

        request.upload_handlers.insert(0, FTPUploadHandler(data))
        return submit_form_post(request)



@csrf_protect
def submit_form_get(request):
    queryStr =request.META['QUERY_STRING']

    redirectpage , queryStr = test_makeQS(request,queryStr)
    if redirectpage:
        return redirect(reverse('submit_form') + "?" +  queryStr)

    # print("queryStr :  {}".format(queryStr))
    queryStr = maybe_decode(queryStr)
    # print("maybe_decode queryStr :  {}".format(queryStr))

    data = dict(urllib.parse.parse_qsl(queryStr))
    # print("DATA :  {}".format(data))

    request.session['data'] = data

    if not request.META['QUERY_STRING']:
        return render(request, 'fileupload/submit.html', {'qs': data})
    else:

        submit_form = SubmitForm();
        # print("process_department :  {}".format(data['process_department']))
        # submit_form.process_department = data['process_department'];
        # print("submit_form :  {}".format(submit_form))
        # print("submit_form.process_department :  {}".format(submit_form.process_department))
        return render(request, 'fileupload/submit.html', {'submitForm': submit_form, 'qs': data})

@csrf_protect
def submit_form_post_1(request):

    # print(" REQUEST POST : {}".format(dict(request.POST)))
    # print(" REQUEST POST : {}".format(request.POST))
    submitted_form = SubmitForm(request.POST)

    if submitted_form.is_valid():

        print(" SUBMITED FORM cleaned data : {}".format(submitted_form.cleaned_data))

        form_cleaned_data = submitted_form.cleaned_data
        post = request._post
        # post1 = dict(request.POST)

        print(" SUBMITED FORM post : {}".format(post))
        # print(" SUBMITED FORM post1 : {}".format(post1))

        submitted_form = submitted_form.save(commit=False)
        submitted_form.process_department = post["process_department"];
        submitted_form.process_ent_id = post["process_ent_id"];
        submitted_form.submitted_by = post["user"];
        submitted_form.project = post["project"];
        submitted_form.asset = post["asset"];
        submitted_form.version = post["version"];
        submitted_form.file_path = "%s/%s" %(post["project"],post["process_department"])

        submitted_form.save()
        note = "Form has been submitted successfully with values %s %s. Version No : %s" %(submitted_form.process_department,form_cleaned_data['comments'], submitted_form.version );


        new_form = SubmitForm();
        return render(request, 'fileupload/submit.html', {'submitForm': new_form, 'note': note})

@csrf_protect
def submit_form_post(request):

    # print(" REQUEST POST : {}".format(dict(request.POST)))
    # print(" REQUEST POST : {}".format(request.POST))
    print (" REQUEST Files : {}".format(request.FILES['file1']))
    submitted_form = SubmitForm(request.POST)

    submitted_files = SubmitForm(request.POST,request.FILES)
    # if submitted_files.is_valid():


    print (" SUBMITED Files : {}".format(submitted_files))

    if submitted_form.is_valid():

        print(" SUBMITED FORM cleaned data : {}".format(submitted_form.cleaned_data))

        form_cleaned_data = submitted_form.cleaned_data
        post = request._post
        # post1 = dict(request.POST)

        print(" SUBMITED FORM post : {}".format(post))
        # print(" SUBMITED FORM post1 : {}".format(post1))

        submitted_form = submitted_form.save(commit=False)
        submitted_form.process_department = post["process_department"];
        submitted_form.process_ent_id = post["process_ent_id"];
        submitted_form.submitted_by = post["user"];
        submitted_form.project = post["project"];
        submitted_form.asset = post["asset"];
        submitted_form.version = post["version"];
        submitted_form.file_path = "%s/%s" %(post["project"],post["process_department"])

        submitted_form.save()
        note = "Form has been submitted successfully with values %s %s. Version No : %s" %(submitted_form.process_department,form_cleaned_data['comments'], submitted_form.version );



        new_form = SubmitForm();
        return render(request, 'fileupload/submit.html', {'submitForm': new_form, 'note': note})
