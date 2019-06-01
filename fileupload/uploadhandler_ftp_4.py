import os
import errno
import logging
import time

from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException, SkipFile
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.cache import cache
import datetime
from io import BytesIO
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


from ftplib import FTP

import pdb; # for debugging
#from pudb import set_trace;

from django.core.cache import cache

class FTPUploadHandler(FileUploadHandler):

    # ftp_host = 'ftp.wremeart.com'
    # ftp_username = 'ftpuser_wm_uploads@wremeart.com'
    # ftp_pwd = 'Crazy4You@dm'

    ftp_host = settings.FTP_HOST
    ftp_username = settings.FTP_UN
    ftp_pwd = settings.FTP_PWD

    def __init__(self, *args, **kwargs):
        FileUploadHandler.__init__(self, *args, **kwargs)

        ' ----- Class variables Initialization ----- '
        self._progress_id = None
        self._cache_key = "upload_status"
        cache.set(self._cache_key, {
                'length': 0,
                'uploaded' : 0
            })

        # print("ARGS  : {}".format(*args) )
        self._file = FTPFile(file=BytesIO(),name="tempname.jpeg")
        self._file._starttime = 0
        self._file._processed_size = 0
        self._file._chunk_index = 0
        self._activated = False

        # data = dict(*args)
        ' --------------- '

        ' ----- Chunk Size Configuration ----- '
        print("Default Chunk size = %d" % FileUploadHandler.chunk_size)
        custom_chunk_size = 102400
        FileUploadHandler.chunk_size = custom_chunk_size
        self._file._python_chunk_size = FileUploadHandler.chunk_size # default was 65536
        self._file._ftplib_chunk_size = custom_chunk_size  # default is 64 kb i.e 64000
        print("New Chunk size = %d" % FileUploadHandler.chunk_size)
        ' --------------- '

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self._file._assumed_contentsize = content_length
        # print("Assumed Content Size : {}".format(self._file._assumed_contentsize))
        self._activated = True
        if self._cache_key:
            data = cache.get(self._cache_key)
            data['length'] = self._file._assumed_contentsize
            cache.set(self._cache_key, data)

    def new_file(self, field_name, file_name, *args, **kwargs):
        super().new_file(*args, **kwargs)

        ' ----- File Name, Path & Remote Directory Configuration ----- '
        self._file._uploaded_file_name = file_name
        name_,ext_ = os.path.splitext(file_name)

        # print("SELF REQUEST : {}".format(self.request))
        data = self.request

        project_dir = data['project'] + " _ " + data['project_code']
        asset_dir = data['asset'] + " _ " + data['asset_code']
        self._file._ftp_remoteDir = os.path.join(project_dir, asset_dir)
        self._file._ftp_file_name = "%s_%s_%s_V(%s)_%s" %(data['project_code'],data['asset_code'],data['process_department'][0].upper(),data['version'].replace(".", "_"),data['user'].replace(".", "_"))
        self._file._ftp_file_name += ext_
        self._file._ftp_file_path = os.path.join(self._file._ftp_remoteDir, self._file._ftp_file_name)
        # print("FTP File Name : {}".format(self._file._ftp_file_name))
        ' --------------- '

        # print('Uploading File : %s' % (self._file._ftp_file_path))

        connect_ftp_and_make_directories()

        self._file._starttime = time.time()

        raise StopFutureHandlers()



    def connect_ftp_and_make_directories():
        try:
            ftp = FTP(self.ftp_host)
            ftp.login(self.ftp_username,self.ftp_pwd)
            self.mkdir_p(ftp, self._file._ftp_remoteDir)
        except Exception as e:
            Common.log_exception(e)
        except ftplib.all_errors as e:
            Common.log_exception(e)
        else:
            if self._file._ftp_file_name in ftp.nlst():
                # change the original file's name and upload new
                ftp.rename(self._file._ftp_file_name, self._file._ftp_file_name + "__ARCHIVE__" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                print()
                print ("Duplicate file found! Archiving File : " + self._file._ftp_file_path )
                print()
            else:
                print()
                print ("Duplicate file not found! CURRENT DIR : " + ftp.pwd() )
                print()

            ftp.close()


    def receive_data_chunk(self, raw_data, start):

        if not self._activated:
            return raw_data
        # self._file._chunk_size = len(raw_data)
        if True:
            chunk = BytesIO(raw_data)

            ftp = FTP(self.ftp_host)
            ftp.login(self.ftp_username,self.ftp_pwd)

            ftp.cwd(self._file._ftp_remoteDir)
            #ftp.storbinary('STOR ' + self.file.name, self.file)
            ftp.storbinary('APPE ' + self._file._ftp_file_name, chunk, callback = self.append_callback)
            ftp.close()
    # except IOError, e:
    #     print("Exception caught")
    #      LOG.exception(e)
    #     raise StopUpload(True)

        return None

    def mkdir_p(self,ftp, remote):
        """
        emulates mkdir_p if required.
        sftp - is a valid sftp object
        remote - remote path to create.
        """
        dirs_ = []
        dir_ = remote

        while len(dir_) > 1:
            dir_, dir_last  = os.path.split(dir_)
            dirs_.append(dir_last)

        if len(dir_) == 1 and not dir_.startswith("/"):
            dirs_.append(dir_) # For a remote path like y/x.txt
            print ("DIRS_ 123 : {}".format(dirs_));

        # mkdirs_p(ftp,dirs_)

        while len(dirs_):
            dir_ = dirs_.pop()
            mkdir(ftp,dir_)


        print ("current Dir : {}".format(ftp.pwd()))


    def mkdir(ftp,dir_):
        try:
            print ("DIR_ : {}".format(dir_))
            print ("current Dir : {}".format(ftp.pwd()))

            if dir_ in ftp.nlst():
                print ("directory already exists ... dir %s in %s" % (dir_,ftp.pwd()))
                ftp.cwd(dir_)
            else:
                print ("making ... dir %s in %s" % (dir_,ftp.pwd()))
                ftp.mkd(dir_)
                ftp.cwd(dir_)
        except ftplib.all_errors as e:
            print( 'Ftp fail -> ', e )
            return False
        except requests.ConnectionError as e:
            print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
            print(str(e))
            # continue
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
            # continue
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
            # continue
        except KeyboardInterrupt:
            print("Someone closed the program")



        except:
            mkdir(ftp,dir_)
            pass


    def append_callback(self,data):

        self._file._chunk_index += 1
        self._file._processed_size += len(data)

        if self._cache_key:
            data = cache.get(self._cache_key)
            data['uploaded'] = self._file._processed_size
            cache.set(self._cache_key, data)

        per = round(self._file._processed_size / self._file._assumed_contentsize * 100, 2)
        self._file._upload_per = per;
        print("Step No : {}, Upload Percentage : {}%".format(self._file._chunk_index,per))



    def file_complete(self, file_size):

        per = round(self._file._processed_size / self._file._assumed_contentsize * 100, 2)
        per1 = '{0:.2f}'.format((self._file._processed_size / self._file._assumed_contentsize * 100))
        print("")
        print("Step No : {}, Upload Percentage : {}% , {}%".format(self._file._chunk_index,per,per1))
        print("Processed Size={}, Assumed Total Size={}, File Size = {}".format(self._file._processed_size,self._file._assumed_contentsize, file_size));
        if not self._activated:
            print("Not Activated")
            return None
        try:
            self._file._file_size = file_size;

            print("File Name : {}, File Size = {}".format(self._file._ftp_file_name, self._file._file_size))
            #selffinish_upload(file_size)
            # newfile = UploadedFile(BytesIO(), self.FTP_file_name,self.content_type, file_size )
            # self.file = newfile
        except IOError:
            print('Error closing uploaded file "%s"' %(self._file._ftp_file_name))
            raise

        elapsed = time.time() - self._file._starttime
        self._file._time_to_upload = int(elapsed)
        print('Uploaded %s bytes to FTP in %s seconds' % (file_size, int(elapsed)))


        print("file_complete File : {}".format(self._file._ftp_file_name))

        # self._file.file = BytesIO()

        # new_file = FTPFile(file=BytesIO(), name=self._file._ftp_file_name, content_type="image/jpeg", size=self._file._file_size)
        # # return self.file or None
        # new_file.file_path = self._file._ftp_file_path
        return self._file or None

    def upload_complete(self):
        if self._cache_key:
            cache.delete(self._cache_key)


class FTPFile(UploadedFile):
    def __init__(self, *args, **kwargs):
        super(FTPFile, self).__init__(*args, **kwargs)

        # print ("MyProjectUploadedFile args : {}".format(*args))
        print ("self type : {}".format(type(self)))
        # print ("args type : {}".format(type(args)))
        # self = args
