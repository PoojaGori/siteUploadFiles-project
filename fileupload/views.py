from django.shortcuts import render, redirect, reverse
from .uploadhandler_ftp import FTPUploadHandler
# from .uploadhandler_test import MyProjectUploadHandler

import urllib.parse
import base64
from Crypto.Cipher import AES

from .forms import SubmitForm
from .models import SubmissionDetails

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import json

from django.conf import settings

from .common import Common
from .logger import log

def _unpad(s): return s[0:-s[-1]]
def _pad(s): return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
def _cipher(): return AES.new(key='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', mode=AES.MODE_CBC, IV='AAAAAAAAAAAAAAAA')
def encrypt_token(data): return _cipher().encrypt(_pad(data))
def decrypt_token(data): return _unpad(_cipher().decrypt(data))
def add_qsForTest(): return "process_department=lighting&process_ent_id=123&user=Pooja&project=Donald&project_code=DNLD&asset=Boat&asset_code=BT&version=0.0.1"

def test_makeQS(request,queryStr):
    redirect = False
    debug = settings.QS_DEBUG
    qs_encoding = settings.QS_ENCODING

    if not queryStr: # no querystring found in url
        queryStr = add_qsForTest()
        redirect = True

    if qs_encoding:
        qs = maybe_encode(queryStr, qs_encoding)
        if qs:
            queryStr = qs
            redirect = True

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
        # Query string not key value OR doesn't contain plain key, then encode
        if not test or "process_department" not in test:
            dec = decrypt_token(base64.b64decode(qs)).decode('utf-8')
            qs = dec
        else:
            raise AssertionError("Wrong OR No Query String supplied!")
        return qs
    except Exception as e:
        raise

# def home(request):
#     submit(request)

@csrf_exempt
def submit_form(request):

        if request.method == 'GET':
            return submit_form_get(request)
        else:
            data = request.session.get('data')
            request.upload_handlers.insert(0, FTPUploadHandler(data))
            return submit_form_post(request)

@csrf_protect
def submit_form_get(request):
    try:
        queryStr =request.META['QUERY_STRING']

        # FOR TESTING AND DEBUGGING
        debug = settings.QS_DEBUG
        qs_encoding = settings.QS_ENCODING

        if debug:
            log.warn("Debug Mode ON")
            redirectpage , queryStr = test_makeQS(request,queryStr)
            if redirectpage:
                return redirect(reverse('submit_form') + "?" +  queryStr)
        else:
            log.info("Live Mode ON")
            if not queryStr:
                raise AssertionError("No Query String has been supplied in Live mode")

        queryStr = maybe_decode(queryStr)

        data = dict(urllib.parse.parse_qsl(queryStr))
        request.session['data'] = data

        if debug:
            if not request.META['QUERY_STRING']:
                return render(request, 'fileupload/submit.html', {'qs': data})
            else:

                submit_form = SubmitForm()
                # print("process_department :  {}".format(data['process_department']))
                # submit_form.process_department = data['process_department'];
                # print("submit_form :  {}".format(submit_form))
                # print("submit_form.process_department :  {}".format(submit_form.process_department))
                return render(request, 'fileupload/submit.html', {'submitForm': submit_form, 'qs': data})
    except:
        log.exception()
        submit_form = SubmitForm()
        return render(request, 'fileupload/submit.html', {'submitForm': submit_form, 'error': 'Something went wrong. Please contact the administrator.'})




@csrf_protect
def submit_form_post(request):

    # print(" REQUEST POST : {}".format(dict(request.POST)))
    # print(" REQUEST POST : {}".format(request.POST))
    try:

        objfile = request.FILES['file1']
    except Exception as e:
        print("EXception : {}".format(e))
        raise
    # print (" REQUEST File Name : {}".format(objfile._ftp_file_name))
    # print (" REQUEST File Size : {}".format(objfile._file_size))
    # print (" REQUEST File Path : {}".format(objfile._ftp_file_path))
    # print (" REQUEST Time to upload : {} secs".format(objfile._time_to_upload))

    submitted_form = SubmitForm(request.POST)

    # submitted_files = SubmitForm(request.POST,request.FILES)
    # if submitted_files.is_valid():


    # print (" SUBMITED Files : {}".format(submitted_files))

    if submitted_form.is_valid():

        # print(" SUBMITED FORM cleaned data : {}".format(submitted_form.cleaned_data))

        form_cleaned_data = submitted_form.cleaned_data
        post = request._post

        submitted_form = submitted_form.save(commit=False)
        submitted_form.process_department = post["process_department"];
        submitted_form.process_ent_id = post["process_ent_id"];
        submitted_form.submitted_by = post["user"];
        submitted_form.project = post["project"];
        submitted_form.project_code = post["project_code"];
        submitted_form.asset = post["asset"];
        submitted_form.asset_code = post["asset_code"];
        submitted_form.version = post["version"];
        submitted_form.file_path = objfile._ftp_file_path
        submitted_form.uploaded_file_name =  objfile._uploaded_file_name #   post["uploaded_file_name"]

        submitted_form.file_size = objfile._file_size # post["file_size"]

        submitted_form.readable_file_size =  Common.bytes_to_readable_size(objfile._file_size)
        submitted_form.python_chunk_size = objfile._python_chunk_size
        submitted_form.ftplib_chunk_size = objfile._ftplib_chunk_size
        submitted_form.time_to_upload_in_seconds = objfile._time_to_upload # post["time_to_upload_in_seconds"]
        submitted_form.time_to_upload_in_hms = Common.seconds_to_hhminss(objfile._time_to_upload)


        submitted_form.test_ftp_upload_time = objfile._test_ftp_upload_time
        submitted_form.test_average_upload_speed = objfile._test_average_upload_speed
        submitted_form.logs = objfile._logs

        # N = float(len(objfile.speed))
        # avg = { k : sum(t[k] for t in self._file.speed)/N for k in self._file.speed[0] }
        #
        # print("avg : {}".format(avg))

        submitted_form.save()
        note = "Form has been submitted successfully with values %s %s. Version No : %s" %(submitted_form.process_department,form_cleaned_data['comments'], submitted_form.version );

        # return HttpResponse(json.dumps({'message': 'Upload complete!'}))

        new_form = SubmitForm();
        return render(request, 'fileupload/submit.html', {'submitForm': new_form, 'note': note})

# A view to report back on upload progress:

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseServerError

def upload_progress(request):

    """
    Return JSON object with information about the progress of an upload.
    """
    # print("")
    # print("CALL FROM JS");
    # print("")

    try:
        if request.method == 'GET':
            cache_key = "upload_status"
            if cache.get(cache_key):
                value = cache.get(cache_key)
                # print("CALL FROM JS . HttpResponse 1 : {}".format(json.dumps(value)));
                return HttpResponse(json.dumps(value))
            else:
                print("CALL FROM JS . HttpResponse 2 : ERROR - No csrf value in cache");
                return HttpResponse(json.dumps({'error':"No csrf value in cache"}), content_type="application/json")

        else:
            print("CALL FROM JS . HttpResponse 3 : {}".format(request.method));
            return HttpResponse(json.dumps({'error':'No GET request'}), content_type="application/json")

    except Exception as e:
        print ("ERROR : {}".format(e))
        return HttpResponse({'error':e})
        # raise
