from django.core.files.uploadhandler import *
from hashlib import sha256
# from myproject.upload.files import MyProjectUploadedFile
from django.core.files.uploadedfile import UploadedFile

class MyProjectUploadHandler(FileUploadHandler):
    def __init__(self, *args, **kwargs):
        super(MyProjectUploadHandler, self).__init__(*args, **kwargs)

    def handle_raw_input(self, input_data, META, content_length, boundary,
            encoding = None):
        self.activated = True

    def new_file(self, *args, **kwargs):
        super(MyProjectUploadHandler, self).new_file(*args, **kwargs)

        self.digester = sha256()
        raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):
        self.digester.update(raw_data)

    def file_complete(self, file_size):
        new_file = MyProjectUploadedFile(file=self.digester.hexdigest(), name="ABC.jpeg", content_type="image/jpeg", size=file_size)
        # return self.file or None
        new_file.file_path = "some custom file path"
        return new_file or None

class MyProjectUploadedFile(UploadedFile):
    def __init__(self, *args, **kwargs):
        super(MyProjectUploadedFile, self).__init__(*args, **kwargs)

        # print ("MyProjectUploadedFile args : {}".format(*args))
        print ("self type : {}".format(type(self)))
        # print ("args type : {}".format(type(args)))
        # self = args

    file_path = "";
