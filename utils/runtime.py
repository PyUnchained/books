import sys

def is_test():
    """ Detects if the application is currently running as a celery worker. """
    return 'test' in sys.argv[1]

