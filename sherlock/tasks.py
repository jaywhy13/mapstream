from celery.task import Task
from celery.registry import tasks
import time

class TestTask(Task):
    def run(self, **kwargs):
    	print "going to sleep"
    	logger = self.get_logger(**kwargs)
    	time.sleep(10)
        # print "I slept!!"
        logger.info("Woke up")

tasks.register(TestTask)