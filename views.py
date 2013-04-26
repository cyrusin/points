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

def current_points(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            return render_to_response("Points/bonus_info.html", {'user': user, 'points': points})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)


def points_history(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            history_items = History_points.objects.filter(user_id = user)
            return render_to_response("Points/bonus_history.html", {'user': user, 'history_items': history_items})

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
            return render_to_response("Points/bonus_history.html", {'user': user, 'points': points, 'history_items': history_items})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        raise Http404

def get_bonus_rule(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            return render_to_response("Points/bonus_rule.html", {'points': points})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        raise Http404


def get_some_bonus_record(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            history_items = History_points.objects.filter(user_id = user)
            if len(history_items) > 8:
                history_items_part = history_items[0:8]
            else:
                history_items_part = history_items
            return render_to_response("Points/bonus_info.html", {'points': points, 'record': history_items_part})
    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)

def get_all_bonus_record(request):
    page_offset = 1
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            history_items = History_points.objects.filter(user_id = user)
            if len(history_items) % 8 == 0:
                page_num = range(len(history_items) / 8)
            else:
                page_num = range((len(history_items) / 8) + 1)
            return render_to_response("Points/bonus_all_history.html", \
                                      {'points': points, \
                                       'record':history_items[0:8], \
                                       'page_num': page_num, \
                                       'page_offset': page_offset})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)


def get_bonus_record(request, page_offset):
    try:
        page_offset = int(page_offset)
    except ValueError:
        raise Http404

    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            history_items = History_points.objects.filter(user_id = user)
            if len(history_items) % 8 == 0:
                page_num = range(len(history_items) / 8)
            else:
                page_num = range((len(history_items) / 8) + 1)
            return render_to_response("Points/bonus_all_history.html", \
                                      {'points': points, \
                                       'record':history_items[8*(page_offset - 1):(8*(page_offset-1)+8)], \
                                       'page_num': page_num, \
                                       'page_offset': page_offset})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
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
        page_size = 8
        after_range_num = 5
        before_range_num = 6
        page_range = []
        if user:
            user_item = User_points.objects.get(user_id = user)
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