#coding:utf-8
from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist
from User.models import User, Teacher, Student
from School.models import SchoolInfo, ClassInfo
from File.models import File
from Task.models import Task
from Task.models import Commit
from signals import login_in_news, upload_news
from roxedu.settings import logger
import traceback

#import signals
import datetime

# The operation name and the points of any kind of operation
class Operation_points(models.Model):
    '''DataModel:Operation_points

    '''
    operation_name = models.CharField(max_length=50)
    points = models.IntegerField()
    in_use = models.BooleanField(default=True)


    def __unicode__(self):
        return self.operation_name


# The history of the operation, the points and the user
class History_points(models.Model):
    '''DataModel:History_points

    '''
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
    '''DataModel:User_points

    '''
    user_id = models.ForeignKey(User)
    points_of_user = models.IntegerField()

    def __unicode__(self):
        return self.user_id.email


# Handle the signals from user register event
def register_handler(sender, **kwargs):
    '''register_handler(sender, **kwargs)

    Processing the signal of user registering event.
    '''
    # add reward points history for new user register event
    try:
        if kwargs['created'] == True:
            accessDB(kwargs['instance'], 'register', datetime.datetime.now())
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = "Points.models.register_handler.Exception %s" % str(e)
        logger.debug(msg)

post_save.connect(register_handler, sender = User)


# Handle the signals from user upload file
def upload_handler(sender, **kwargs):
    '''upload_handler(sender, **kwargs)

    Processing the signal of user uploading file event.
    '''
    if 'instance' in kwargs:
        file_item = kwargs['instance']
    else:
        return
    try:
        if (kwargs['created'] == True) and \
                (not file_item.path.startswith(repr(file_item.user.id)[0:-1] + u'/作业')) and \
                (file_item.file_type != 10):
            accessDB(file_item.user, 'uploadfile', datetime.datetime.now())
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = "Points.models.upload_handler.Exception %s" % str(e)
        logger.debug(msg)

upload_news.connect(upload_handler, sender = File)


# Handle the signals from teacher send new task
def send_task_handler(sender, **kwargs):
    '''send_task_handler(sender, **kwargs)

    Processing the signal of teacher sending task event.
    '''
    # sender==receiver declares that this is teacher sending task
    if 'instance' in kwargs:
        task = kwargs['instance']
    else:
        return
    try:
        if (kwargs['created'] == True) and (task.sender == task.receiver):
            accessDB(task.sender, 'sendtask', datetime.datetime.now())
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = "Points.models.send_task_handler.Exception %s" % str(e)
        logger.debug(msg)

post_save.connect(send_task_handler, sender = Task)


# Handle the signals from student commit task
def commit_task_handler(sender, **kwargs):
    '''commit_task_handler(sender, **kwargs) -> bool

    Processing the signal of student committing task event.
    '''
    if 'instance' in kwargs:
        commit = kwargs['instance']
    else:
        return
    try:
        if kwargs['created'] == True:
            accessDB(commit.sender, 'committask', datetime.datetime.now())
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = "Points.models.commit_task_handler.Exception %s" % str(e)
        logger.debug(msg)

post_save.connect(commit_task_handler, sender = Commit)


# Handle the signals from user first login in everyday
def first_login_in_handler(sender, **kwargs):
    '''first_login_in_handler(sender, **kwargs)

    Processing the signal of user first login in everyday event.
    '''
    if 'instance' in kwargs:
        user = kwargs['instance']
    else:
        return
    try:
        if (user.last_login is None) or (user.last_login.date() != kwargs['login_time'].date()):
            accessDB(user, 'firstlogin', kwargs['login_time'])
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = "Points.models.first_login_in_handler.Exception %s" %str(e)
        logger.debug(msg)

login_in_news.connect(first_login_in_handler, sender = User)


def add_history_to_db(user, operation, time_of_operation):
    '''add_history_to_db(user, operation, time_of_operation)

    Add one record of user's operation to db.
    '''

    new_history_item = History_points()
    new_history_item.operation_id = operation
    new_history_item.reward_points = operation.points
    new_history_item.user_id = user
    new_history_item.operation_time = time_of_operation
    new_history_item.save()


def add_points_to_user(user, operation):
    '''add_points_to_user(user, operation)

    Add points to user based on user's specific operation.
    '''
    #operation = Operation_points.objects.get(operation_name = operation_name)
    try:
        user_points_item = User_points.objects.get(user_id = user)
    except ObjectDoesNotExist:
        user_points_item = User_points.objects.create(user_id = user, points_of_user = 10L)
    user_points_item.points_of_user += operation.points
    user_points_item.save()


def accessDB(user, operation_name, time_of_operation):
    '''accessDB(instance, str, datetime)

    Main function  used to accessing database.
    '''
    try:
        operation = Operation_points.objects.get(operation_name = operation_name)
        if (operation.in_use == False): #operation is no longer in use.
            return
        add_history_to_db(user, operation, time_of_operation)
        add_points_to_user(user, operation)
    except ObjectDoesNotExist, e:
        msg2 = traceback.format_exc()
        # logger.debug(msg2)
        msg = "Points.models.Operation_history.Exception %s" %str(e)
        # logger.debug(msg)


def getAllUserPoints():
    '''getUserPoints()

     Used to get all user-points info from the database.
    '''
    try:
        all_item = User_points.objects.all()
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = "Points.models.getUserPoints.Exception %s" % str(e)
        logger.debug(e)
        all_item = []
    return all_item


def getUserPointsBySchool(schoolName = None):
    '''getUserPoints(string)

    Used to get  bonus info of some special users of some school.
    '''
    try:
        all_item = []
        if schoolName:
            schoolInfo = SchoolInfo.objects.get(name = schoolName)
            if schoolInfo:
                all_user = User.objects.filter(school = schoolInfo)
                all_item = [User_points.objects.get(user_id = item) \
                            for item in all_user if item]
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = 'Points.models.getUserPointsBySchool.Exception %s' % str(e)

    return all_item


def getUserPointsByClass(className = None, schoolName = None):
    '''getUserPointsByClass(string, string)

    Used to get bonus info of special users of some class.
    '''
    try:
        all_item = []
        if schoolName:
            schoolInfo = SchoolInfo.objects.get(name = schoolName)
            if schoolInfo:
                classInfo = ClassInfo.objects.get(name = className, school = schoolInfo)
                if classInfo:
                    teachers = Teacher.objects.filter(classInfo = classInfo)
                    students = Student.objects.filter(classInfo = classInfo)
                    for t in teachers:
                        all_item.append(User_points.objects.get(user_id = t.teacher))
                    for s in students:
                        all_item.append(User_points.objects.get(user_id = s.student))

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        msg = 'Points.models.getUserPointsByClass.Exception %s' % str(e)

    return all_item