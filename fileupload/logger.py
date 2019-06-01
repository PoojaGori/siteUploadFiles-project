import sys, traceback

import logging

class log():

    # logging.basicConfig(filename="logs/wreme_media.log",
    #                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #                     # datefmt='%d/%m/%Y %I:%M:%S %p',
    #                     datefmt='%d/%m/%Y %H:%M:%S %p',
    #
    #                     level=logging.DEBUG)
    logger = logging.getLogger(__name__)
        # filemode='w',

    formatter = logging.Formatter('\n %(asctime)s \n MESSAGE :  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # formatter = logging.Formatter('\n %(name)s - %(asctime)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # create a file handler
    handler = logging.FileHandler('logs/wreme_debug.log', mode='w')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # create a file handler
    handler = logging.FileHandler('logs/wreme_exceptions.log', mode='w')
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(' ################ %(levelname)s ################ \n %(asctime)s \n MESSAGE : %(message)s \n ################################', datefmt='%m/%d/%Y %I:%M:%S %p')
    # formatter = logging.Formatter('################ %(levelname)s ################ \n %(name)s - %(asctime)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # handler = logging.FileHandler('logs/wreme_debug.log', mode='w')
    # handler.setLevel(logging.DEBUG)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    #
    # handler = logging.FileHandler('logs/wreme_warnings.log', mode='w')
    # handler.setLevel(logging.WARNING)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    # create a logging format
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    @staticmethod
    def exception(ex = None, message = None):

        if ex:
            log.logger.exception(ex)
        elif message:
            log.logger.exception(message)
        else:
            log.logger.exception("Error in Execution. Please contact administrator.")


    @staticmethod
    def info(info):
        log.logger.info(info, exc_info=True)

    @staticmethod
    def warn(warning):
        log.logger.warn(warning, exc_info=True)

    @staticmethod
    def debug(info):
        log.logger.debug(traceback.format_exc())



#
#
#
#
#
#
# #Create and configure logger
# logging.basicConfig(filename="newfile.log",
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     filemode='w')
#
# logging.basicConfig(level=logging.DEBUG)
#
# # initialize the log settings
# logging.basicConfig(filename='app.log',level=logging.INFO)
# log = logging.getLogger(__name__)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # The Python 3 version. It's a little less work
#
# def log_traceback(ex):
#     tb_lines = traceback.format_exception(ex.__class__, ex, ex.__traceback__)
#     tb_text = ''.join(tb_lines)
#     # I'll let you implement the ExceptionLogger class,
#     # and the timestamping.
#     exception_logger.log(tb_text)
#
#
# def trace_log(error):
#
#     log.error('Error occurred ' + str(e))
#
#     try:
#         pass
#     except Exception as e:
#         e.error("Exception occurred", exc_info=True)
#
#     log.exception(error)
#
#
#     log.debug(traceback.format_exc
#
#     log.info('General exception noted.', exc_info=True)
#
#     exc_type, exc_value, exc_traceback = sys.exc_info()
#     print "*** print_tb:"
#     traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
#     # *** print_tb:
#     # File "<doctest...>", line 10, in <module>
#     # lumberjack()
#
#     print "*** print_exception:"
#     traceback.print_exception(exc_type, exc_value, exc_traceback,
#                               limit=2, file=sys.stdout)
#     # *** print_exception:
#     # Traceback (most recent call last):
#     #   File "<doctest...>", line 10, in <module>
#     #     lumberjack()
#     #   File "<doctest...>", line 4, in lumberjack
#     #     bright_side_of_death()
#     # IndexError: tuple index out of range
#
#
#
#
#
#     print "*** print_exc:"
#     traceback.print_exc()
#     # *** print_exc:
#     # Traceback (most recent call last):
#     #   File "<doctest...>", line 10, in <module>
#     #     lumberjack()
#     #   File "<doctest...>", line 4, in lumberjack
#     #     bright_side_of_death()
#     # IndexError: tuple index out of range
#
#     print "*** format_exc, first and last line:"
#     formatted_lines = traceback.format_exc().splitlines()
#     print formatted_lines[0]
#     print formatted_lines[-1]
#     # *** format_exc, first and last line:
#     # Traceback (most recent call last):
#     # IndexError: tuple index out of range
#
#     print "*** format_exception:"
#     print repr(traceback.format_exception(exc_type, exc_value,
#                                           exc_traceback))
#     # *** format_exception:
#     # ['Traceback (most recent call last):\n',
#     #  '  File "<doctest...>", line 10, in <module>\n    lumberjack()\n',
#     #  '  File "<doctest...>", line 4, in lumberjack\n    bright_side_of_death()\n',
#     #  '  File "<doctest...>", line 7, in bright_side_of_death\n    return tuple()[0]\n',
#     #  'IndexError: tuple index out of range\n']
#
#     print "*** extract_tb:"
#     print repr(traceback.extract_tb(exc_traceback))
#     # *** extract_tb:
#     # [('<doctest...>', 10, '<module>', 'lumberjack()'),
#     #  ('<doctest...>', 4, 'lumberjack', 'bright_side_of_death()'),
#     #  ('<doctest...>', 7, 'bright_side_of_death', 'return tuple()[0]')]
#
#     print "*** format_tb:"
#     print repr(traceback.format_tb(exc_traceback))
#     # *** format_tb:
#     # ['  File "<doctest...>", line 10, in <module>\n    lumberjack()\n',
#     #  '  File "<doctest...>", line 4, in lumberjack\n    bright_side_of_death()\n',
#     #  '  File "<doctest...>", line 7, in bright_side_of_death\n    return tuple()[0]\n']
#
#     print "*** tb_lineno:", exc_traceback.tb_lineno
#     # *** tb_lineno: 10
