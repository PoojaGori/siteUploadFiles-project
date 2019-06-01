from django.conf import settings

import os
import errno
import datetime
import ftplib as fl
from ftplib import FTP



class class_ftp():

    ftp_host = settings.FTP_HOST
    ftp_username = settings.FTP_UN
    ftp_pwd = settings.FTP_PWD

    retries = 3

    @staticmethod
    def ftp_connect_host():
        ftp = None
        for _ in range(class_ftp.retries):
            try:
                ftp = FTP(class_ftp.ftp_host)
                ftp.login(class_ftp.ftp_username,class_ftp.ftp_pwd)
            except fl.all_errors as e:
                ex = e
                continue
            else:
                return ftp

        e = Exception("Login to host %s failed even after %s attempts. Exception : %s" %(class_ftp.ftp_host,class_ftp.retries, ex))
        log_exception(e)
        raise ex

    @staticmethod
    def makeDirPath(dir_path, ftp):

        dirs_ = []
        dir_ = dir_path

        while len(dir_) > 1:
            dir_, dir_last  = os.path.split(dir_)
            dirs_.append(dir_last)

        if len(dir_) == 1 and not dir_.startswith("/"):
            dirs_.append(dir_) # For a remote path like y/x.txt

        while len(dirs_):
            dir_ = dirs_.pop()
            class_ftp.mkdir(dir_,ftp)

        # print ("current Dir : {}".format(ftp.pwd()))
        return True


    def mkdir(dir_, ftp):
        for _ in range(class_ftp.retries):
            try:
                # print ("DIR_ : {}".format(dir_))
                # print ("current Dir : {}".format(ftp.pwd()))

                if dir_ in ftp.nlst():
                    # print ("Directory already exists ... dir %s in %s" % (dir_,ftp.pwd()))
                    ftp.cwd(dir_)
                else:
                    print ("Making ... dir %s in %s" % (dir_,ftp.pwd()))
                    ftp.mkd(dir_)
                    ftp.cwd(dir_)
            except fl.all_errors as e:
                ex = e
                continue
            else:
                return True

        e = Exception("Make Dir dor Dir '%s' failed even after %s attempts. Exception : %s" %(dir_,class_ftp.retries, ex))
        log_exception(e)
        raise ex

    @staticmethod
    def archive_existing_duplicate_file(file_name, ftp):
        for _ in range(class_ftp.retries):
            try:
                if file_name in ftp.nlst():
                    name_,ext_ = os.path.splitext(file_name)
                    # change the original file's name and upload new
                    ftp.rename(file_name, name_ + "__ARCHIVE__" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ext_ )
                    print()
                    print ("Duplicate file found! Archiving File : " + file_name )
                    print()
            except fl.all_errors as e:
                ex = e
                continue
            else:
                return True

        e = Exception("Existing File Check And Archive failed even after %s attempts. File : '%s' Exception : %s" %(class_ftp.retries, file_name , ex))
        log_exception(e)
        raise ex



    @staticmethod
    def upload_data(ftp, remote_dir, data, file_name, func_callback, chunk_size = None, append = True):
        if not chunk_size:
            chunk_size = 102400

        # print ("Inside upload data")
        for _ in range(class_ftp.retries):
            try:
                ftp.cwd(remote_dir)

                if append:
                    ftp.storbinary('APPE ' + file_name, data, callback = func_callback, blocksize=chunk_size)
                else:
                    ftp.storbinary('STOR ' + file_name, data, callback = func_callback, blocksize=chunk_size)
                # end_time = time.time()

                # time_taken = start_time - end_time

            except fl.all_errors as e:
                ex = e
                continue
            else:
                ftp.close()
                return True

        e = Exception("Chunk upload failed even after %s attempts.File Name : %s. Remote Dir : %s. Exception : %s" %(class_ftp.retries, file_name, remote_dir, ex))
        # log_exception(e)
        raise ex

    @staticmethod
    def get_remote_file_configurations(uploaded_file_name, project_name, project_code, asset_name, asset_code, department_name, file_version, user_name):
        # class_ftp._file._uploaded_file_name = file_name
        name_,ext_ = os.path.splitext(uploaded_file_name)

        project_dir = project_name + "_" + project_code
        asset_dir = asset_name + "_" + asset_code
        _ftp_remoteDir = os.path.join(project_dir, asset_dir)
        _ftp_file_name = "%s_%s_%s_V(%s)_%s" %(project_code,asset_code,department_name[0].upper(),file_version.replace(".", "_"),user_name.replace(".", "_"))
        _ftp_file_name += ext_
        _ftp_file_path = os.path.join(_ftp_remoteDir, _ftp_file_name)

        return _ftp_remoteDir, _ftp_file_name, _ftp_file_path
