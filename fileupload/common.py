import datetime

class Common():

    @staticmethod
    def bytes_to_readable_size(B, return_specific=None):
        'Return the given bytes as a human friendly KB, MB, GB, or TB string'
        B = float(B)
        KB = float(1024)
        MB = float(KB ** 2) # 1,048,576
        GB = float(KB ** 3) # 1,073,741,824
        TB = float(KB ** 4) # 1,099,511,627,776

        b = "{0} {1}".format(B,'Bytes' if 0 == B > 1 else 'Byte')
        kb = "{0:.2f} KB".format(B/KB)
        mb = "{0:.2f} MB".format(B/MB)
        gb = "{0:.2f} GB".format(B/GB)
        tb = "{0:.2f} TB".format(B/TB)

        if return_specific:
           return {'B': b, 'KB': kb, 'MB': mb, 'GB': gb, 'TB': tb }[return_specific]
        elif B < KB:
            return b
        elif KB <= B < MB:
            return kb
        elif MB <= B < GB:
            return mb
        elif GB <= B < TB:
            return gb
        elif TB <= B:
            return tb

        #
        #
        # if B < KB:
        #     return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
        # elif KB <= B < MB:
        #     return '{0:.2f} KB'.format(B/KB)
        # elif MB <= B < GB:
        #     return '{0:.2f} MB'.format(B/MB)
        # elif GB <= B < TB:
        #     return '{0:.2f} GB'.format(B/GB)
        # elif TB <= B:
        #     return '{0:.2f} TB'.format(B/TB)

    @staticmethod
    def seconds_to_hhminss(seconds):
        'Return the given bytes as a human friendly KB, MB, GB, or TB string'
        a = datetime.timedelta(0, seconds)
        return str(a)



    @staticmethod
    def log_exception(exc):
        print()
        print ("############## EXCEPTION CAUGHT ##############")
        print(exc)
        print ("##############################################")
        print()


# tests = [1, 1024, 500000, 1048576, 50000000, 1073741824, 5000000000, 1099511627776, 5000000000000]
#
# for t in tests: print '{0} == {1}'.format(t,humanbytes(t))
