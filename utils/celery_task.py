from celery import Task

from .runtime import is_test

class TestAwareTask(Task):
    _db = None

    def delay(self, *args, **kwargs):
        """ If a test is currently running, the task should not be delayed and instead
        run synchronously. This terminal output/exceptions raise by the task to be
        visible in the terminal during testing.
        """
        if is_test():
            return self.run(*args, **kwargs)
            
        return self.apply_async(args, kwargs)