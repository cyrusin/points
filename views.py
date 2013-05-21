# Create your views here.
from Points.models import  Operation_points, History_points, User_points
from django.shortcuts import  render_to_response
from django.http import HttpResponse
from utils.CheckRequestUser import checkRequestUserValidate
from roxedu.settings import logger
import traceback
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, Http404
from utils.common import utilResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from utils.decorators import *
from School.models import SchoolInfo, ClassInfo
from User.models import User, Teacher, Student
def current_points(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            return render_to_response("Points/bonus_info.html", \
                                      {'user': user, 'points': points})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        raise Http404


def points_history(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            history_items = History_points.objects.filter(user_id = user)
            return render_to_response("Points/bonus_history.html", \
                                      {'user': user, 'history_items': history_items})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)


def get_all_info(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            history_items = History_points.objects.filter(user_id = user)
            return render_to_response("Points/bonus_history.html", \
                                      {'user': user, 'points': points, 'history_items': history_items})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        raise Http404


def get_bonus_rule(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            try:
                user_item = User_points.objects.get(user_id = user)
            except ObjectDoesNotExist:
                points = 0
            else:
                points = user_item.points_of_user

            operation_items = Operation_points.objects.all()
            operation_names = [item.operation_name for item in operation_items if item.in_use]

            return render_to_response("Points/bonus_rule.html", \
                                      {'points': points, 'operation': operation_names})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        raise Http404


def get_some_bonus_record(request):
    result = {
        "Flage": False,
        "msg": None,
        "info": None

    }
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            try:
                user_item = User_points.objects.get(user_id = user)
            except ObjectDoesNotExist:
                return render_to_response("Points/bonus_info.html", \
                                            {'points': 0, 'record': []})
            points = user_item.points_of_user
            history_items = History_points.objects.filter(user_id = user)
            if not history_items:
                return render_to_response('Points/bonus_info.html', \
                                            {'points': points, 'record': []})
            if len(history_items) > 8:
                history_items_part = history_items[0:8]
            else:
                history_items_part = history_items
            return render_to_response("Points/bonus_info.html", \
                                      {'points': points, 'record': history_items_part})
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        return utilResponse(result,status=500)


@csrf_protect
def bonus_record(request):
    result = {
        "Flage": False,
        "msg": None,
        "info": None

    }
    try:
        web_client,user_validate,user = checkRequestUserValidate(request,logger)
        if not user_validate:
            msg="user authorized faile,please login or check parameter"
            result["msg"]=msg
            logger.debug(msg)

        try:
            page = int(request.GET.get("page", 1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        page_size = 12
        after_range_num = 5
        before_range_num = 6
        page_range = []
        if user:
            try:
                user_item = User_points.objects.get(user_id = user)
            except ObjectDoesNotExist:
                return render_to_response('Points/bonus_info.html', \
                                          {'points': 0, 'record': []})
            points = user_item.points_of_user
            history_items = History_points.objects.filter(user_id = user)
            paginator = Paginator(history_items, page_size)
            try:
                page_record = paginator.page(page)
            except (EmptyPage, InvalidPage, PageNotAnInteger):
                page_record = paginator.page(1)
            if page >= after_range_num:
                page_range = paginator.page_range[page - after_range_num : page + before_range_num]
            else:
                page_range = paginator.page_range[0: page+before_range_num]
            return  render_to_response("Points/bonus_record_pages.html", \
                                        {'points': points, \
                                         'record': page_record, \
                                         'page_range': page_range})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        return utilResponse(result,status=500)

@staff_member_required
def bonus_info(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        result = {
            "Flage": False,
            "msg": None,
            "info": None
        }

        if not user_validate:
            msg="user authorized faile,please login or check parameter"
            result["msg"]=msg
            logger.debug(msg)

            if web_client:
                return HttpResponseRedirect("/user/login")
            else:
                return utilResponse(result,status=400)
        all_item = Operation_points.objects.all()
        return render_to_response("Points/bonus_manage_rule.html", {"record": all_item}, context_instance=RequestContext(request))


    except Exception, e:
        msg = "School.view.bonus_info.Exception %s" % str(e)
        return HttpResponse(msg)


@staff_member_required
def bonus_modify(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        result = {
            "Flage": False,
            "msg": None,
            "info": None
        }

        if not user_validate:
            msg="user authorized faile,please login or check parameter"
            result["msg"]=msg
            logger.debug(msg)

            if web_client:
                return HttpResponseRedirect("/user/login")
            else:
                return utilResponse(result,status=400)
        if request.method == "POST":
            try:
                operation_items = Operation_points.objects.all()
                for item in operation_items:
                    if item.points != int(request.POST.get('in_points_' + str(item.id))):
                        set_points = int(request.POST.get('in_points_' + str(item.id)))
                        Operation_points.objects.filter(id = item.id).update(points = set_points)
                    if (not item.in_use) and request.POST.get('in_use_'+ str(item.id),''):
                        Operation_points.objects.filter(id = item.id).update(in_use = True)
                    if item.in_use and ('in_use_' + str(item.id) not in request.POST):
                        Operation_points.objects.filter(id = item.id).update(in_use = False)
                return HttpResponseRedirect('/admin/bonus')

            except ObjectDoesNotExist, e:
                msg2 = traceback.format_exc()
                logger.debug(msg2)
                msg = "Points.models.Operation_points.Exception %s" % str(e)
                logger.debug(msg)

    except Exception, e:
        msg = "School.view.bonus_modify.Exception %s" % str(e)
        return HttpResponse(msg)

@staff_member_required
@requires_login
def displayRankUser(request, user=None):
    '''displayRankUser(request)

    '''
    if request.method == 'GET':
        return render_to_response("Points/bonus_manage_rank.html")


@staff_member_required
@requires_login
@catch_view_exceptions
@transacted_view
def getRankedUser(request, user=None):
    '''getRankUser(request)

    Get the user ranked by the bonus points in some school or class.
    '''

    if request.method == 'GET' and not request.GET.get('school', ''):
         return render_to_response("Points/bonus_manage_rank.html")
    if request.method == 'GET' and request.GET['school']:
        schoolName = request.GET.get('school', '')
        className = request.GET.get('class', '')
        page = request.GET.get('page', 1)

        if schoolName:
            schoolInfo = SchoolInfo.objects.get(name = schoolName)
            if className:
                classInfo = ClassInfo.objects.filter(school = schoolInfo, name = className)
            else:
                classInfo = ClassInfo.objects.filter(school = schoolInfo)
            choose_t = set()
            for item in classInfo:
                temp = Teacher.objects.filter(classinfo = item)
                for t in temp:
                    choose_t.add(t)

            choose_s = set()
            for item in classInfo:
                temp = Student.objects.filter(classinfo = classInfo)
                for s in temp:
                    choose_s.add(s)
            all_item = []
            for item in choose_t:
                user = item.teacher
                all_item.append(User_points.objects.get(user_id = user))
            for item in choose_s:
                user = item.student
                all_item.append(User_points.objects.get(user_id = user))

            all_item.sort(key = lambda x: x.points_of_user, reverse=True)
            page_size = 15
            after_range_num = 5
            before_range_num = 6
            page_range = []

            paginator = Paginator(all_item, page_size)
            try:
                page_record = paginator.page(page)
            except (EmptyPage, InvalidPage, PageNotAnInteger):
                page_record = paginator.page(1)
            if page >= after_range_num:
                page_range = paginator.page_range[page - after_range_num : page + before_range_num]
            else:
                page_range = paginator.page_range[0: page+before_range_num]
            return  render_to_response("Points/bonus_manage_rank.html", \
                                   {'record': page_record, \
                                    'page_range': page_range, \
                                    'school_name': schoolName, \
                                    'class_name': className}, context_instance=RequestContext(request))