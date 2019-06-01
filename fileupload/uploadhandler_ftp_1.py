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
        self._file = None
        self._starttime = 0
        self._activated = False
        # self.request = request

        # self.url =  'ftp.some-server.com',
        # self.username = 'your-account-name'
        # self.password = 'your-password'
        # self.remotedirectory = '/path/to/files'
        LOG.debug("Chunk size = %d" % FileUploadHandler.chunk_size)

    # def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
    #     self.activated = True

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.contentsize = content_length


    def upload_complete(self):
        pass

    def new_file(self, field_name, file_name, *args, **kwargs):
        super().new_file(*args, **kwargs)
        LOG.error('Using FTPUploadHandler to handle file upload.')

        currentDT = datetime.datetime.now()

        self.FTP_file_name = '';
        #self.FTP_file_name = "t{}__ ".format(currentDT.strftime("%Y-%m-%d %H:%M:%S"))
        self.FTP_file_name += file_name
        print("File Name : {}".format(self.FTP_file_name))

        # newfile = UploadedFile(BytesIO(), self.FTP_file_name,self.content_type, file_size )
        print("Content Size : {}".format(self.contentsize))
        self._file = FTPFile(BytesIO(), self.FTP_file_name,self.content_type, self.contentsize)

        self.file_path = os.path.join(self.ftp_remoteDir, self.FTP_file_name)
        LOG.error('Upload attempt to %s' % (self.file_path))
        self._activated = True
        self._starttime = time.time()
        self.processed_size = 0;
        # print("File Path : {}".format(self.file_path))

        # print("self.file_name File Name : {}".format(self.file_name))
        # print("file_name File Name : {}".format(file_name))

        raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):
        LOG.debug("FTPUploadHandler receive_data_chunk")

        if not self._activated:
            return raw_data

        self._file.chunk_size = len(raw_data)
        # print ("Length of chunk data : {}".format(len(raw_data)))

        # pdb.set_trace()
        # set_trace()
    # try:
        #LOG.error("if is always false")
        if True:
            chunk = BytesIO(raw_data)

            ftp = FTP(self.ftp_host)
            ftp.login(self.ftp_username,self.ftp_pwd)
            ftp.cwd(self.ftp_remoteDir)
            #ftp.storbinary('STOR ' + self.file.name, self.file)
            ftp.storbinary('APPE ' + self.FTP_file_name, chunk, callback = self.append_callback)
            ftp.close()
    # except IOError, e:
    #     print("Exception caught")
    #      LOG.exception(e)
    #     raise StopUpload(True)

        return None

    def append_callback(self,data):
        self._file.chunk_index += 1
        self.processed_size += len(data)

        per = round(self.processed_size / self.contentsize * 100, 2)
        #per1 = '{0:.2f}'.format((self.processed_size / self.contentsize * 100))
        # print ("Length of chunk data : {}".format(len(data)))
        # print("Content Length : {}".format(self.contentsize))
        self._file.upload_per = per;
        print("Step No : {}, Upload Percentage : {}%".format(self._file.chunk_index,per))

        # print ("Chunk Data : {}".format(data))



    def file_complete(self, file_size):
        LOG.error("File Upload Complete")
        per = round(self.processed_size / self.contentsize * 100, 2)
        per1 = '{0:.2f}'.format((self.processed_size / self.contentsize * 100))
        print("Step No : {}, Upload Percentage : {}% , {}%".format(self._file.chunk_index,per,per1))
        print("Processed Size={}, Total Size={}, File Size = {}".format(self.processed_size,self.contentsize, file_size));
        if not self._activated:
            LOG.error("Not Activated")
            return None
        try:
            self._file.size = file_size;
            self._file.contentsize = file_size;
            print("File Name : {}, File Size = {}".format(self._file.name, self._file.size))
            #self._file.finish_upload(file_size)
            # newfile = UploadedFile(BytesIO(), self.FTP_file_name,self.content_type, file_size )
            # self.file = newfile
        except IOError:
            LOG.error('Error closing uploaded temporary file "%s"' %(self._file.get_temp_path(),))
            raise

        elapsed = time.time() - self._starttime
        self._file.time_to_upload = int(elapsed)
        LOG.error('Uploaded %s bytes to FTP in %s seconds' % (file_size, int(elapsed)))
        return self._file
        # return FTPFile(self.file, "")


class FTPFile(UploadedFile):
    def __init__(self, *args, **kwargs):
        super(FTPFile, self).__init__(*args, **kwargs)
        self.chunk_index = 0;
        self.chunk_size = 0;
        self.contentsize = 0;
        self.time_to_upload = 0;
        self.upload_per = 0;
        # self.metadata = file
        # self.upload_path = upload_path
        # self._size = self.metadata.size
