#coding:utf-8
from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist
from User.models import User
from File.models import File
from Task.models import Task
from Task.models import Commit
from signals import login_in_news

#import signals
import datetime

# The operation name and the points of any kind of operation
class Operation_points(models.Model):
    operation_name = models.CharField(max_length=50)
    points = models.IntegerField()

    def __unicode__(self):
        return self.operation_name



# The history of the operation, the points and the user
class History_points(models.Model):
    operation_id = models.ForeignKey(Operation_points)
    reward_points = models.IntegerField()
    user_id = models.ForeignKey(User)
    operation_time = models.DateTimeField()

    def __unicode__(self):
        return self.user_id.email

    class Meta:
        ordering = ['-operation_time']
# The user's points
class User_points(models.Model):
    user_id = models.ForeignKey(User)
    points_of_user = models.IntegerField()
    def __unicode__(self):
        return self.user_id.email


# Handle the signals from user register event
def register_handler(sender, **kwargs):
    # add reward points history for new user register event
    #if ('instance' in kwargs) and (User_points.objects.filter(user_id = kwargs['instance']) is None):
    try:
        if kwargs['created'] == True:
            add_history_to_db(kwargs['instance'], 'register', datetime.datetime.now())

            # add user points, new user has 10 points
            add_points_to_user(kwargs['instance'], 'register')
    except Exception, e:
        print e
    finally:
        return
post_save.connect(register_handler, sender=User)


# Handle the signals from user upload file
def upload_handler(sender, **kwargs):
    if 'instance' in kwargs:
        file_item = kwargs['instance']
    else:
        return
    try:
        if (kwargs['created'] == True) and \
                (not file_item.path.startswith(repr(file_item.user.id)[0:-1] + u'/作业')) and \
                (file_item.file_type != 10):
        #if not file_item.path.startswith(repr(file_item.user.id) + '/作业'):
        #if kwargs['created'] == True:
            # add reward points history for user uploading file
            add_history_to_db(file_item.user, 'uploadfile', datetime.datetime.now())

            # add points of the user
            add_points_to_user(file_item.user, 'uploadfile')
    except Exception, e:
        print e
    finally:
        return
post_save.connect(upload_handler, sender=File)


# Handle the signals from teacher send new task
def send_task_handler(sender, **kwargs):
    # sender==receiver declares that this is teacher sending task
    if 'instance' in kwargs:
        task = kwargs['instance']
    else:
        return
    try:
        if (kwargs['created'] == True) and (task.sender == task.receiver):
            add_history_to_db(task.sender, 'sendtask', datetime.datetime.now())

            # add points of the teacher
            add_points_to_user(task.sender, 'sendtask')
    except Exception, e:
        print e
    finally:
        return
post_save.connect(send_task_handler, sender = Task)


# Handle the signals from student commit task
def commit_task_handler(sender, **kwargs):
    if 'instance' in kwargs:
        commit = kwargs['instance']
    else:
        return
    try:
        if kwargs['created'] == True:
            add_history_to_db(commit.sender, 'committask', datetime.datetime.now())

            #add points of the student
            add_points_to_user(commit.sender, 'committask')
    except Exception, e:
        print e
    finally:
        return
post_save.connect(commit_task_handler, sender=Commit)


# Handle the signals from user first login in everyday
def first_login_in_handler(sender, **kwargs):
    if 'instance' in kwargs:
        user = kwargs['instance']
    else:
        return
    try:
        if (user.last_login is None) or (user.last_login.date() != kwargs['login_time'].date()):
            add_history_to_db(user, 'firstlogin', kwargs['login_time'])

            add_points_to_user(user, 'firstlogin')
    except Exception, e:
        print e
    finally:
        return
login_in_news.connect(first_login_in_handler, sender = User)


def add_history_to_db(user, operation_name, time_of_operation):

    new_history_item = History_points()
    operation = Operation_points.objects.get(operation_name)
    new_history_item.operation_id = operation
    new_history_item.reward_points = operation.points
    new_history_item.user_id = user
    new_history_item.operation_time = time_of_operation
    new_history_item.save()

def add_points_to_user(user, operation_name):
    operation = Operation_points.objects.get(operation_name)
    try:
        user_points_item = User_points.objects.get(user_id = user)
    except ObjectDoesNotExist:
        user_points_item = User_points.objects.create(user_id = user, points_of_user = 0L)
    user_points_item.points_of_user += operation.points
    user_points_item.save()