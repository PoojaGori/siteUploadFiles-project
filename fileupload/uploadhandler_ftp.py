import os
import errno
import logging
import time

from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException, SkipFile
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File
from django.core.files.base import ContentFile

from django.core.cache import cache
import datetime
from io import BytesIO
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


# from ftplib import FTP

import pdb; # for debugging
#from pudb import set_trace;

from django.core.cache import cache

from .class_ftp import class_ftp
from .common import Common
from .logger import log

class FTPUploadHandler(FileUploadHandler):

    def __init__(self, *args, **kwargs):
        FileUploadHandler.__init__(self, *args, **kwargs)

        ' ----- Class variables Initialization ----- '
        self._progress_id = None
        self._cache_key = "upload_status"
        cache.set(self._cache_key, {
                'length': 0,
                'uploaded' : 0,
                'start' : 0,
                'abort' : 0
            })

        # print("ARGS  : {}".format(*args) )
        self._file = FTPFile(file=BytesIO(),name="tempname.jpeg")
        self._file._starttime = 0
        self._file._processed_size = 0
        self._file._ftp_chunk_index = 0
        self._chunk_index = 0
        self._file._test_ftp_upload_time = 0
        self._activated = False


        self._test_lst = []

        # data = dict(*args)
        ' --------------- '

        ' ----- Chunk Size Configuration ----- '

        # Blocksize  Time
        # 102400       40
        #  51200       30
        #  25600       28
        #  32768       30
        #  24576       31
        #  19200       34
        #  16384       61
        #  12800      144
        #
        # But if I used wireless instead, I got these times:
        #
        # Blocksize  Time
        # 204800       78
        # 102400       76
        #  51200       79
        #  25600       76
        #  32768       89
        #  24576       86
        #  19200       75
        #  16384      166
        #  12800      178
        #  64000      223   ftplib default
        #  65536            python upload handler default

        # 2.5 Megabytes = 2621440 Bytes

        # print("Default Chunk size = %d" % FileUploadHandler.chunk_size)
        # #  Upload in chunks of 10 million bytes.
        # chunkSize = 10000000

        custom_chunk_size = 2621440 # 819200 # 409600
        FileUploadHandler.chunk_size = custom_chunk_size
        self._file._python_chunk_size = FileUploadHandler.chunk_size # default was 65536
        self._file._ftplib_chunk_size = 819200 #204800  # default is 64 kb i.e 64000
        print("New Chunk size = %d" % FileUploadHandler.chunk_size)
        ' --------------- '

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        try:
            self._file._assumed_contentsize = content_length
            self._activated = True
            if self._cache_key:
                data = cache.get(self._cache_key)
                data['length'] = self._file._assumed_contentsize
                cache.set(self._cache_key, data)
        except Exception as e:
            log.exception(e)

    def new_file(self, field_name, file_name, *args, **kwargs):
        super().new_file(*args, **kwargs)

        try:
            ' ----- File Name, Path & Remote Directory Configuration ----- '
            self._file._uploaded_file_name = file_name

            data = self.request
            a,b,c = class_ftp.get_remote_file_configurations(file_name, data['project'], data['project_code'], data['asset'], data['asset_code'], data['process_department'], data['version'], data['user'] )

            self._file._ftp_remoteDir = a
            self._file._ftp_file_name = b
            self._file._ftp_file_path = c

            ' --------------- '

            ftp = class_ftp.ftp_connect_host()
            class_ftp.makeDirPath(self._file._ftp_remoteDir, ftp)
            class_ftp.archive_existing_duplicate_file(self._file._ftp_file_name, ftp)
            if ftp:
                ftp.close()

            self._file._starttime = time.time()
            if self._cache_key:
                data = cache.get(self._cache_key)
                data['start'] = 1
                cache.set(self._cache_key, data)
        except Exception as e:
            log.exception(e)
            raise StopFutureHandlers()
            raise e

        raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):

        try:
            if not self._activated:
                return raw_data
            if True:

                chunk = BytesIO(raw_data)
                ftp = class_ftp.ftp_connect_host()

                _start_time = time.time()
                if class_ftp.upload_data(ftp, self._file._ftp_remoteDir, chunk, self._file._ftp_file_name, func_callback=self.append_callback, chunk_size=self._file._ftplib_chunk_size):
                    _end_time = time.time()
                    self._chunk_index += 1
                    time_taken = _end_time -  _start_time
                    self._file._test_ftp_upload_time += time_taken

                    self._test_lst.append({'index':self._chunk_index,'time_taken': time_taken, 'length': len(raw_data), 'speed': round(len(raw_data) / time_taken)})
                if ftp:
                    ftp.close()
        except Exception as e :
            Common.log_exception(e)
            log.exception(e)
            ftp.abort()
            if self._cache_key:
                data = cache.get(self._cache_key)
                data['abort'] = 1
                cache.set(self._cache_key, data)
            raise StopUpload(True)
            raise
            # raise SkipFile(True)

        return None

    def append_callback(self,data):
        self._file._ftp_chunk_index += 1
        self._file._processed_size += len(data)

        if self._cache_key:
            data = cache.get(self._cache_key)
            data['uploaded'] = self._file._processed_size
            cache.set(self._cache_key, data)

        per = round(self._file._processed_size / self._file._assumed_contentsize * 100, 2)
        self._file._upload_per = per;
        print("Step No : {}, Upload Percentage : {}%".format(self._file._ftp_chunk_index,per))

    def file_complete(self, file_size):

        per = round(self._file._processed_size / self._file._assumed_contentsize * 100, 2)
        per1 = '{0:.2f}'.format((self._file._processed_size / self._file._assumed_contentsize * 100))
        print("")
        print("Step No : {}, Upload Percentage : {}% , {}%".format(self._file._ftp_chunk_index,per,per1))
        print("Processed Size={}, Assumed Total Size={}, File Size = {}".format(self._file._processed_size,self._file._assumed_contentsize, file_size));
        if not self._activated:
            print("Not Activated")
            return None

        self._file._file_size = file_size;

        print("File Name : {}, File Size = {}".format(self._file._ftp_file_name, self._file._file_size))
        #selffinish_upload(file_size)
        # newfile = UploadedFile(BytesIO(), self.FTP_file_name,self.content_type, file_size )
        # self.file = newfile


        elapsed = time.time() - self._file._starttime
        self._file._time_to_upload = int(elapsed)
        print('Uploaded %s bytes to FTP in %s seconds' % (file_size, int(elapsed)))

        try:

            N = float(len(self._test_lst))
            # av_dictn = { k : sum(t[k] for t in self._test_lst)/N for k in self._test_lst[0] }

            _dictn = { k : sum(t[k] for t in self._test_lst) for k in self._test_lst[0]}

            av_speed = sum(t['speed'] for t in self._test_lst)/N

            _dictn["speed"] = Common.bytes_to_readable_size(av_speed)
            _dictn["time_taken"] = Common.seconds_to_hhminss(_dictn["time_taken"])

            self._file._test_average_upload_speed = _dictn["speed"]
            _dictn["ftplib_chunks_no"] = self._file._ftp_chunk_index

            print()

            self._file._logs = "{} |||| {}".format(_dictn,self._test_lst)
            print()
            print(" LOGS : {}".format(self._file._logs))
            print()
            self._file._test_ftp_upload_time = _dictn["time_taken"]

            print("file_complete File : {}".format(self._file._ftp_file_name))

        except Exception as ex:
            log.exception(ex)

        if not self._file:
            self._file = FTPFile(file=BytesIO(),name="tempname.jpeg")
        return self._file or None

    def upload_complete(self):
        if self._cache_key:
            cache.delete(self._cache_key)


class FTPFile(UploadedFile):
    def __init__(self, *args, **kwargs):
        super(FTPFile, self).__init__(*args, **kwargs)

        # print ("MyProjectUploadedFile args : {}".format(*args))
        # print ("self type : {}".format(type(self)))
        # print ("args type : {}".format(type(args)))
        # self = args
