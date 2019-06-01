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

LOG = logging.getLogger(__name__)


class FTPUploadHandler(FileUploadHandler):

    ftp_host = 'ftp.wremeart.com'
    ftp_username = 'ftpuser_wm_uploads@wremeart.com'
    ftp_pwd = 'Crazy4You@dm'
    ftp_remoteDir = ''

    # def __init__(self, *args, **kwargs):
    #     super(FTPUploadHandler, self).__init__(*args, **kwargs)
    #     pass

    def __init__(self, *args, **kwargs):
        FileUploadHandler.__init__(self, *args, **kwargs)
        # print("ARGS  : {}".format(*args) )
        # self._file = None
        self._starttime = 0
        self._activated = False
        # data = dict(*args)
        print("SELF REQUEST : {}".format(self.request))
        data = self.request
        # self.ftp_remoteDir = "{}/{}".format(*args) data['project'] + data['process_department']
        self._ftp_remoteDir = os.path.join(data['project'], data['asset'], data['process_department'])
        # self.request = request

        # self.url =  'ftp.some-server.com',
        # self.username = 'your-account-name'
        # self.password = 'your-password'
        # self.remotedirectory = '/path/to/files'
        print("Chunk size = %d" % FileUploadHandler.chunk_size)

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self._assumed_contentsize = content_length
        self._activated = True

    def new_file(self, field_name, file_name, *args, **kwargs):
        super().new_file(*args, **kwargs)
        print('Using FTPUploadHandler to handle file upload.')

        currentDT = datetime.datetime.now()
        self._ftp_file_name = '';
        #self.FTP_file_name = "t{}__ ".format(currentDT.strftime("%Y-%m-%d %H:%M:%S"))
        self._ftp_file_name += file_name
        print("File Name : {}".format(self._ftp_file_name))

        # newfile = UploadedFile(BytesIO(), self.FTP_file_name,self.content_type, file_size )
        print("Assumed Content Size : {}".format(self._assumed_contentsize))
        # self.file = UploadedFile(self.FTP_file_name, self.content_type, self._assumed_contentsize, self.charset, self.content_type_extra)
        # self._file = FTPFile(BytesIO(), self.FTP_file_name,self.content_type, self._assumed_contentsize)

        self._file_path = os.path.join(self._ftp_remoteDir, self._ftp_file_name)
        LOG.error('Upload attempt to %s' % (self._file_path))
        # self._activated = True
        self._starttime = time.time()
        self._chunk_index = 0
        self._processed_size = 0;

        ftp = FTP(self.ftp_host)
        ftp.login(self.ftp_username,self.ftp_pwd)

        # self.cdTree(self.ftp_remoteDir,ftp)

        self.mkdir_p(ftp, self._ftp_remoteDir)
        # print("File Path : {}".format(self.file_path))

        # print("self.file_name File Name : {}".format(self.file_name))
        # print("file_name File Name : {}".format(file_name))

        raise StopFutureHandlers()



    def receive_data_chunk(self, raw_data, start):

        if not self._activated:
            return raw_data

        # self._chunk_size = len(raw_data)
        # self.file.write(BytesIO('1234'))

        if True:

            chunk = BytesIO(raw_data)

            ftp = FTP(self.ftp_host)
            ftp.login(self.ftp_username,self.ftp_pwd)

            # ftp.cwd(self.ftp_remoteDir)
            #ftp.storbinary('STOR ' + self.file.name, self.file)
            ftp.storbinary('APPE ' + self._ftp_file_name, chunk, callback = self.append_callback)
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
            # dirs_.append(dir_)
            dir_, dir_last  = os.path.split(dir_)
            dirs_.append(dir_last)
            # print ("DIRS_ : {}".format(dirs_));
            # print ("DIR_ 1 : {}".format(dir_));
            # print ("DIR_ 2 : {}".format(dir2_));

        if len(dir_) == 1 and not dir_.startswith("/"):
            dirs_.append(dir_) # For a remote path like y/x.txt
            print ("DIRS_ 123 : {}".format(dirs_));

        print ("DIRS_ 1234 : {}".format(dirs_));
        while len(dirs_):
            dir_ = dirs_.pop()
            print ("DIR_ : {}".format(dir_))
            print ("current Dir : {}".format(ftp.pwd()))

            if dir_ in ftp.nlst():
                print ("directory already exists ... dir %s in %s" % (dir_,ftp.pwd()))
                ftp.cwd(dir_)
            else:
                print ("making ... dir %s in %s" % (dir_,ftp.pwd()))
                ftp.mkd(dir_)
                ftp.cwd(dir_)

        print ("current Dir : {}".format(ftp.pwd()))

    def append_callback(self,data):
        self._chunk_index += 1
        self._processed_size += len(data)

        per = round(self._processed_size / self._assumed_contentsize * 100, 2)
        #per1 = '{0:.2f}'.format((self.processed_size / self._assumed_contentsize * 100))
        # print ("Length of chunk data : {}".format(len(data)))
        # print("Content Length : {}".format(self._assumed_contentsize))
        self._upload_per = per;
        print("Step No : {}, Upload Percentage : {}%".format(self._chunk_index,per))

        # print ("Chunk Data : {}".format(data))

    def file_complete(self, file_size):
        per = round(self._processed_size / self._assumed_contentsize * 100, 2)
        per1 = '{0:.2f}'.format((self._processed_size / self._assumed_contentsize * 100))
        print("Step No : {}, Upload Percentage : {}% , {}%".format(self._chunk_index,per,per1))
        print("Processed Size={}, Assumed Total Size={}, File Size = {}".format(self._processed_size,self._assumed_contentsize, file_size));
        if not self._activated:
            LOG.error("Not Activated")
            return None
        try:
            self._file_size = file_size;

            print("File Name : {}, File Size = {}".format(self._ftp_file_name, self._file_size))
            #selffinish_upload(file_size)
            # newfile = UploadedFile(BytesIO(), self.FTP_file_name,self.content_type, file_size )
            # self.file = newfile
        except IOError:
            LOG.error('Error closing uploaded file "%s"' %(self._ftp_file_name))
            raise

        elapsed = time.time() - self._starttime
        self._time_to_upload = int(elapsed)
        LOG.error('Uploaded %s bytes to FTP in %s seconds' % (file_size, int(elapsed)))


        print("file_complete File : {}".format(self._ftp_file_name))






        new_file = FTPFile(file=BytesIO(), name=self._ftp_file_name, content_type="image/jpeg", size=self._file_size)
        # return self.file or None
        new_file.file_path = self._file_path
        return new_file or None




    # def upload_complete(self):
    #     print("upload_complete File : {}".format(self._file))
    #     return self.file


# class FTPFile(UploadedFile):
#     def __init__(self, *args, **kwargs):
#         super(FTPFile, self).__init__(*args, **kwargs)
#         # data = dict(*args)
#         # print("args : {}".format(args))
#         self._chunk_index = 0;
#         self.chunk_size = 0;
#         self._assumed_contentsize = 0;
#         self.time_to_upload = 0;
#         self.upload_per = 0;
#         # self.metadata = file
#         # self.upload_path = upload_path
#         # self._size = self.metadata.size

class FTPFile(UploadedFile):
    def __init__(self, *args, **kwargs):
        super(FTPFile, self).__init__(*args, **kwargs)

        # print ("MyProjectUploadedFile args : {}".format(*args))
        print ("self type : {}".format(type(self)))
        # print ("args type : {}".format(type(args)))
        # self = args
