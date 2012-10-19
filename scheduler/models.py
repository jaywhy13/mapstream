from django.db import models
from djcelery.models import PeriodicTask, CrontabSchedule, IntervalSchedule
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class ProjectTask(models.Model):
    name = models.CharField(max_length=255)
    celery_task_name = models.CharField(max_length=255)
    periodic_task = models.ForeignKey(PeriodicTask, blank=True, null=True)

    def schedule_every(self, every, period, args=None, kwargs=None):
        print "Scheduling %s to run every %s %s" % (self.name, every, period)
        if self.periodic_task:
            self.periodic_task.delete()
        
        print "Cleared all current periodic tasks"

        permissible_periods = ['days', 'hours', 'minutes', 'seconds']
        if period not in permissible_periods:
            raise Exception('Invalid period specified: %s, must be one of: %s' % (period, ','.join(permissible_periods)))
        # create the periodic task and the interval
        ptask_name = "%s_%s" % (self.celery_task_name, self.name)
        interval_schedules = IntervalSchedule.objects.filter(period=period, every=every)
        if interval_schedules: # just check if interval schedules exist like that already and reuse em
            interval_schedule = interval_schedules[0]
        else:
            interval_schedule = IntervalSchedule()
            interval_schedule.every = every
            interval_schedule.period = period
            interval_schedule.save()
        
        print "Creating new periodic task"
        periodic_task = PeriodicTask(name=ptask_name, task=self.celery_task_name, interval=interval_schedule)
        if args:
            periodic_task.args = args
        if kwargs:
            periodic_task.kwargs = kwargs
        periodic_task.save()
        print "Attached the periodic task to the project task"
        self.periodic_task = periodic_task

        print "Saving project task"
        self.save()

    @staticmethod
    def schedule_task_every(task_name, every, period, args=None, kwargs=None):
        permissible_periods = ['days', 'hours', 'minutes', 'seconds']
        if period not in permissible_periods:
            raise Exception('Invalid period specified')
        # create the periodic task and the interval
        ptask_name = "%s_%s" % (task_name, datetime.datetime.now())
        interval_schedules = IntervalSchedule.objects.filter(period=period, every=every)
        if interval_schedules: # just check if interval schedules exist like that already and reuse em
            interval_schedule = interval_schedules[0]
        else:
            interval_schedule = IntervalSchedule()
            interval_schedule.every = every
            interval_schedule.period = period
            interval_schedule.save()
        ptask = PeriodicTask(name=ptask_name, task=task_name, interval=interval_schedule)
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        ptask.save()
        return ProjectTask.objects.create(periodic_task=ptask, name=task_name)

    @staticmethod
    def schedule_with_crontab(task_name, crontab_schedule, args=None, kwargs=None):
        ptask_name = "%s_%s" % (task_name, datetime.datetime.now())
        ptask = PeriodicTask(name=ptask_name,
                             task=task.name,
                             crontab=crontab_schedule
                             )
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        ptask.save()
        return ProjectTask.objects.create(periodic_task=ptask)

    @staticmethod
    def schedule(task_name, minute, args=None, kwargs=None):
        results = CrontabSchedule.objects.filter(minute=minute)
        if results:
            c = results[0]
        else:
            c = CrontabSchedule()
            c.minute = minute
            c.save()
        return ProjectTask.schedule_with_crontab(task_name,c, args, kwargs)

    def stop(self):
        if self.periodic_task:
            ptask = self.periodic_task
            ptask.enabled = False
            ptask.save()

    def start(self):
        ptask = self.periodic_task
        if ptask:
            ptask.enabled = True
            ptask.save()

    @staticmethod
    def terminate_all():
        for task in ProjectTask.objects.all():
            task.terminate()



@receiver(pre_delete, sender=ProjectTask, dispatch_uid="scheduler.project_task_deleted")
def project_task_deleted(sender, instance, **kwargs):
    instance.stop() # properly terminate the periodic tasks and delete them
